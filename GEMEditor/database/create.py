import logging
import re
import os
import sqlite3
from collections import defaultdict, Counter
from PyQt5.QtWidgets import QMessageBox, QApplication, QProgressDialog
from GEMEditor.database import metanetx_url, metanetx_files, missing_prefix
from GEMEditor.connect.urldownloader import DownloadProgressDialog, StopDownload
from GEMEditor.database.tables import setup_empty_database
from GEMEditor.database.base import DatabaseWrapper
from urllib.request import urlretrieve, ContentTooShortError, HTTPError, URLError


LOGGER = logging.getLogger(__name__)


def download_metanetx_files(parent=None):
    """ Download the data files from MetaNetX

    Parameters
    ----------
    mainwindow : GEMEditor.main

    Returns
    -------
    dict or None
    """

    local_files = dict()
    progress = DownloadProgressDialog(parent, minimum_duration=0, auto_close=False, window_title="Download")

    for key, value in metanetx_files.items():

        current_file = metanetx_url + value

        # Set label
        progress.setLabelText("Downloading: {}".format(current_file))
        LOGGER.debug("Trying to download {}".format(current_file))

        # Download file
        try:
            filename, _ = urlretrieve(url=current_file,
                                      reporthook=progress.set_progress)
        except (ContentTooShortError, HTTPError, URLError, TimeoutError):
            LOGGER.exception("An error occurred during the download:")
            progress.close()
            QMessageBox.critical(parent, "Download error", "There is a problem with your connection!")
            cleanup_files(local_files)
            return None
        except StopDownload:
            LOGGER.debug("Download cancelled by user")
            progress.close()
            cleanup_files(local_files)
            return None
        else:
            local_files[key] = filename
            LOGGER.debug("Download successful! Local file: {}".format(filename))

    progress.close()
    LOGGER.debug("All files successfully downloaded!")
    return local_files


def cleanup_files(files):
    """ Cleanup temp files
    
    Parameters
    ----------
    files : dict

    Returns
    -------

    """
    LOGGER.debug("Cleaning up temp files..")

    for file in files.values():
        try:
            os.remove(file)
        except OSError:
            LOGGER.warning("Temp file '{}' could not be removed.".format(file))
            pass
        else:
            LOGGER.debug("{} removed.".format(file))

    LOGGER.debug("Cleanup complete.")


def get_line_count(file_path):
    """ Get the number of rows in a file
    
    Parameters
    ----------
    file_path: str

    Returns
    -------

    """

    with open(file_path, encoding="UTF-8") as temp_file:
        i = 0
        for i, _ in enumerate(temp_file):
            pass
    return i


def get_resource_id(cursor, resource):
    """

    Parameters
    ----------
    conn : sqlite3.connection
    cursor : sqlite3.connection.cursor
    resource : str

    Returns
    -------
    """
    try:
        return cursor.execute("SELECT id from resources WHERE miriam_collection=?", (resource,)).fetchone()[0]
    except TypeError as e:
        raise e


def add_valid_identifier(cursor, metabolite_id, identifier, resource_id):
    """ Add identifier to table if the identifier matches the validator

    Parameters
    ----------
    metabolite_id : int
    cursor : sqlite3.connection.cursor
    validator : str
    resource : str
    identifier

    Returns
    -------
    """


    try:
        cursor.execute("INSERT INTO metabolite_ids VALUES (NULL, ?, ?, ?)", (metabolite_id,
                                                                             resource_id,
                                                                             identifier))
    except:
        print(metabolite_id, resource_id, identifier)
        raise TypeError


def add_identifier(cursor, metabolite_id, entry, prefix_resource_map, validators):
    """ Add the identifier to the table an associate it to the proper resource

    Parameters
    ----------
    conn : sqlite3.connection
    cursor : sqlite3.connection.cursor
    metabolite_id : int, The id of the corresponding metabolite in the database
    entry: str, The xref entry in MetaNetX consisting of prefix:source_id
    prefix_resource_map: dict, A dictionary containing a map between the prefixes and the resource ids in the database
    validators: dict, A dictionary containing a mapping between the resource id and the corresponding precompiled regex validator

    Returns
    -------
    None or True
    """

    # Split of prefix
    try:
        prefix, identifier = entry.split(":", 1)
    except ValueError:
        # No prefix for MetaNetX identifiers
        prefix = "mnx"
        identifier = entry

    # Substitute "deprecated:" prefix with MetaNetX prefix
    if prefix == "deprecated":
        prefix = "mnx"

    # Add the missing prefix for databases where the
    # original prefix has not been retained in MetaNetX
    identifier = "{}{}".format(missing_prefix[prefix], identifier)

    resource_ids = prefix_resource_map[prefix]

    # The prefix uniquely identifies a resource
    if len(resource_ids) == 1:
        validator = validators[resource_ids[0]]

        # The identifier is valid part of the collection
        if re.match(validator, identifier):
            add_valid_identifier(cursor, metabolite_id, identifier, resource_ids[0])
            return True
        else:
            LOGGER.warning("The metabolite xref {} was not added to the database, as the identifier is invalid.".format(entry))

    # The prefix corresponds to more than one resource
    elif len(resource_ids) > 1:
        for resource_id in resource_ids:
            validator = validators[resource_id]
            if re.match(validator, identifier):
                add_valid_identifier(cursor, metabolite_id, identifier, resource_id)
                return True

        # No match for any of the resources
        LOGGER.warning("The metabolite xref {} was not added to the database, as the identifier is no valid member of any collection.".format(entry))

    # The prefix corresponds to no resource
    else:
        LOGGER.warning("The metabolite xref {0} was not added to the database, as the prefix {1} is unknown.".format(entry, prefix))


def get_validators(conn, type="metabolite"):
    """ Get a mapping between the database id and a regex validator
    
    Parameters
    ----------
    conn : sqlite3.connection
    type : str

    Returns
    -------

    """

    cursor = conn.cursor()
    cursor.execute("SELECT id, validator FROM resources WHERE type=?", (type,))
    result = dict((x[0], re.compile(x[1])) for x in cursor.fetchall())
    cursor.close()
    return result


def get_prefix_resource_id_map(conn, type=None):
    """ Get MetaNetX prefix to resource id mapping
    
    Parameters
    ----------
    conn: sqlite3.connection

    Returns
    -------
    list
    """

    cursor = conn.cursor()
    result = defaultdict(list)
    if type is not None:
        cursor.execute("SELECT mnx_prefix, id FROM resources WHERE type=?;", (type,))
    else:
        cursor.execute("SELECT mnx_prefix, id FROM resources;")
    for prefix, id in cursor.fetchall():
        result[prefix].append(id)
    cursor.close()
    return result


def add_name(cursor, metabolite_id, name):
    """ Add a name to the metabolite in the database

    Parameters
    ----------
    cursor : sqlite3.connection.cursor
    metabolite_id : int
    name : str

    Returns
    -------
    None
    """

    cursor.execute("INSERT INTO metabolite_names VALUES (NULL, ?, ?)", (metabolite_id, name))


def add_names_from_description(cursor, metabolite_id, description, prefix_resource_map, metabolite_validators):
    """ Add all elements of the metabolite description to the

    Parameters
    ----------
    conn : sqlite3.connection
    cursor : sqlite3.connection.cursor
    metabolite_id : int
    description : str

    Returns
    -------
    None
    """

    split_description = description.split("|")

    for x in split_description:
        if ":" in x:
            split_string = x.split(":", 1)
            if split_string[0] in prefix_resource_map:
                if add_identifier(cursor, metabolite_id, x, prefix_resource_map, metabolite_validators):
                    return
            add_name(cursor, metabolite_id, x)
        else:
            add_name(cursor, metabolite_id, x)


def get_stoichiometry_from_str(input_str):
    """ Get the stoichiometry from individual parts of the reaction
    Parameters
    ----------
    input_str

    Returns
    -------
    dict -  keys: str of metabolite ids
            values: str of stoichiometric coefficient
    """

    # Try to split the string into: (stoich_coefficient, metabolite_id)
    split_str = input_str.split(" ")
    if len(split_str) == 1:
        if split_str[0] == "":
            return ()
        else:
            return (split_str[0], None)
    elif len(split_str) == 2:
        try:
            float(split_str[0])
        except ValueError:
            raise ValueError("The first part of the reaction substring {0} i.e. {1} does not evaluate to a float".format(input_str, split_str[0]))
        else:
            coefficient = split_str[0]
    elif len(split_str) > 2:
        raise ValueError("The reaction substring {0} contains more than 1 space characters".format(input_str))

    return (split_str[1], coefficient)


def split_reaction_at_arrow(input_str):
    """ Split reaction string at an arrow to get individual sites of the equation """
    arrows = (" <-> ", " -> ", " <- ", " <=> ", " => ", " <= ", " <> ", " = ")
    for x in arrows:
        if x in input_str:
            return input_str.split(x)

    raise ValueError("There is no valid arrow {0} in the reaction {1}".format(arrows, input_str))


def parse_reaction_side(input_str, split_at=" + "):
    """ Parse individual sites of reaction equation

    Parameters
    ----------
    split_at - str of the split point
    input_str - str that is split
    """
    result = [x.strip() for x in input_str.split(split_at)]
    return result


def check_string(parse_string, processed_strings, ignore_chars):
    """ Test that the number of characters has not been modified by processing a string

    Parameters
    ----------
    parse_string: The original string that has been parsed
    processed_strings: List of tuples that are the result of the parsing
    ignore_chars: string or list of characters that are allowed to be removed

    Returns
    -------
    result: bool -  True if the number of characters match
                    False otherwise
    """

    old_counter = Counter(parse_string)
    new_counter = Counter()
    for element in processed_strings:
        for x in element:
            if x is not None:
                new_counter.update(x)

    for key in old_counter:
        if key not in ignore_chars:
            try:
                if old_counter[key] != new_counter[key]:
                    msg = 'Count of "{0}" in processed strings {2} does not match the count in input string {1}'.format(key, parse_string, str(processed_strings))
                    raise ValueError(msg)
            except KeyError:
                msg = 'A character "{0}" has been illegally removed from the input string or is missing in the ignored characters {1}'.format(key, ignore_chars)
                raise ValueError(msg)
        else:
            try:
                if new_counter[key] > old_counter[key]:
                    msg = "Number of ignored character {0} has increased!"
                    raise ValueError(msg)
            except KeyError:
                continue

    # Test that there have been no new characters introduced
    new_characters = set(new_counter.keys()) - set(old_counter.keys())
    if new_characters:
        msg = 'The characters {0} have been introduced to the processed strings.'.format(str(new_characters))
        raise ValueError(msg)

    return True


def parse_reaction_formula(parse_string):
    """ Parse model reaction string and return the stoichiometry dictionary containing the id and the stoichiometry
    as given in the reaction string. This means if the stoichiometric coefficient is obmitted for a coefficient of 1
    the coefficient is given as None.

    Parameters
    ----------
    parse_string - A reaction string

    Returns
    -------
    educt_stoichiometry - The stoichiometry of the left side of the reaction
    product_stoichiometry - The stoichiometry of the right side of the reaction

    NOTE: Missing stoichiometric coefficients are substituted with 1
    """

    if parse_string == "":
        raise ValueError("The reaction part is empty")

    educt_str, product_str = split_reaction_at_arrow(parse_string)

    educts = parse_reaction_side(educt_str)
    products = parse_reaction_side(product_str)

    educt_stoichiometry = []
    for x in educts:
        x_stoichiometry = get_stoichiometry_from_str(x)
        if x_stoichiometry:
            educt_stoichiometry.append(x_stoichiometry)

    product_stoichiometry = []
    for x in products:
        x_stoichiometry = get_stoichiometry_from_str(x)
        if x_stoichiometry:
            product_stoichiometry.append(x_stoichiometry)

    # Check the equality between processed elements and input reaction
    check_list = []
    for x in educt_stoichiometry:
        metabolite, coefficient = x
        check_list.append(metabolite)
        if coefficient is not None:
            check_list.append(coefficient)

    for x in product_stoichiometry:
        metabolite, coefficient = x
        check_list.append(metabolite)
        if coefficient is not None:
            check_list.append(coefficient)

    status = check_string(parse_string, check_list, ignore_chars="<>=- +")

    if status:
        educts_result = defaultdict(int)
        for x in educt_stoichiometry:
            metabolite, coefficient = x
            if coefficient is None:
                coefficient = 1.
            educts_result[metabolite] += float(coefficient)

        products_result = defaultdict(int)
        for x in product_stoichiometry:
            metabolite, coefficient = x
            if coefficient is None:
                coefficient = 1.
            products_result[metabolite] += float(coefficient)

    return educts_result, products_result


def get_equation_inserts(metabolite_map, reaction_id, equation, compartment_map):
    """ Add the metabolites contained in the equation
    in the reaction to the reaction_metabolite_map.

    Parameters
    ----------
    metabolite_map: dict
    reaction_id : int
    equation : str

    Returns
    -------
    list
    """

    # Keep track of rows to insert
    inserts = []

    educts, products = parse_reaction_formula(equation)

    for key, value in educts.items():
        mnx_id, compartment = key.split("@")
        participant_id = metabolite_map[mnx_id]
        inserts.append((reaction_id, participant_id, -float(value), compartment_map[compartment]))

    for key, value in products.items():
        mnx_id, compartment = key.split("@")
        participant_id = metabolite_map[mnx_id]
        inserts.append((reaction_id, participant_id, float(value), compartment_map[compartment]))

    return inserts


def get_ec_numer_inserts(reaction_id, resource_id, ec, validator):
    """ Get the parameters for insertion of the ec number

    Parameters
    ----------
    validator: 
    resource_id: int
    reaction_id : int
    ec : str

    Returns
    -------
    list
    """

    inserts = []

    split_ec = [x.strip() for x in ec.split(";")]
    for x in split_ec:
        if not x:
            continue
        elif validator.match(x):
            inserts.append((reaction_id, resource_id, x))
        elif x.count(".") < 3 and x[-1].isnumeric():
            x += ".-"*(3-x.count("."))
            inserts.append((reaction_id, resource_id, x))
        else:
            LOGGER.warning("Invalid EC number '{}' not added to reaction with id '{}'.".format(x, str(reaction_id)))
    return inserts


def load_reactions(conn, files, progress):
    """ Add reactions to the database

    Parameters
    ----------
    conn : connection
    files : dict
    progress: PyQt5.QWidgets.QProgressDialog

    Returns
    -------
    """

    # Quit if user canceled
    if progress.wasCanceled():
        return

    # Create cursor
    cursor = conn.cursor()

    # Commit all changes if present
    conn.commit()

    # Get the database ids for the metanetx items
    mnx_reaction_resource_id = get_resource_id(cursor, 'metanetx.reaction')
    mnx_metabolite_resource_id = get_resource_id(cursor, 'metanetx.chemical')
    ec_number_resource_id = get_resource_id(cursor, 'ec-code')
    ec_validator = re.compile(r"^\d+\.-\.-\.-|\d+\.\d+\.-\.-|\d+\.\d+\.\d+\.-|\d+\.\d+\.\d+\.(n)?\d+$")

    # Get mapping between metanetx id and database id
    metabolite_map = dict(cursor.execute("SELECT identifier, metabolite_id FROM metabolite_ids WHERE resource_id=?",
                                         (mnx_metabolite_resource_id,)).fetchall())

    compartment_map = dict(cursor.execute("SELECT mnx_id, id FROM compartments"))

    # Get line count for updating the progress dialog
    num_lines = get_line_count(files["Reactions"])
    progress.setLabelText("Reading reactions..")
    progress.setMaximum(num_lines)

    with open(files["Reactions"], "r") as reaction_file:

        # Keep information for bulk insertion
        reaction_inserts = []
        identifier_inserts = []
        participants_inserts = []

        for i, line in enumerate(reaction_file):

            # Skip comments
            if line.startswith("#"):
                continue
            elif progress.wasCanceled():
                cursor.close()
                return
            else:
                progress.setValue(i)
                QApplication.processEvents()

            split_line = line.strip().split("\t")
            assert len(split_line) == 6

            mnx_id, equation, description, balance, ec, source = split_line

            # Generate reaction id for inserts
            reaction_id = i + 1

            try:
                equation_inserts = get_equation_inserts(metabolite_map, reaction_id, equation, compartment_map)
            except Exception as e:
                LOGGER.warning("Reaction '{}' skipped due to a parsing error. {}".format(mnx_id, str(e)))
                continue
            else:
                participants_inserts.extend(equation_inserts)

            # Add the inserts for later execution
            reaction_inserts.append((reaction_id, description))
            identifier_inserts.append((reaction_id, mnx_reaction_resource_id, mnx_id))

            # Add ec number insert
            ec_inserts = get_ec_numer_inserts(reaction_id, ec_number_resource_id, ec, ec_validator)
            identifier_inserts.extend(ec_inserts)

        # Insert data
        cursor.executemany("INSERT INTO reactions VALUES (?, ?)", reaction_inserts)
        cursor.executemany("INSERT INTO reaction_ids VALUES (NULL, ?, ?, ?)", identifier_inserts)
        cursor.executemany("INSERT INTO reaction_participants VALUES (NULL, ?, ?, ?, ?)", participants_inserts)
        conn.commit()


def load_reaction_xrefs(conn, files, progress):
    """ Add cross references to the database

    Parameters
    ----------
    conn : connection
    cursor : cursor
    file_path : str

    Returns
    -------
    None
    """

    # Quit if user canceled
    if progress.wasCanceled():
        return

    # Create cursor
    cursor = conn.cursor()

    # Get the MetaNetX reaction resource id
    mnx_reaction_resource_id = get_resource_id(cursor, 'metanetx.reaction')
    mnx_id_database_id_map = dict(cursor.execute("SELECT identifier, reaction_id FROM reaction_ids WHERE resource_id=?",
                                                 (mnx_reaction_resource_id,)).fetchall())

    reaction_validators = get_validators(conn, type="reaction")
    prefix_resource_map = get_prefix_resource_id_map(conn, type="reaction")

    num_lines = get_line_count(files["ReactionLinks"])
    progress.setLabelText("Reading reactions..")
    progress.setMaximum(num_lines)

    with open(files["ReactionLinks"], "r") as open_file:

        for i, line in enumerate(open_file):

            # Skip comments
            if line.startswith("#"):
                continue
            elif progress.wasCanceled():
                cursor.close()
                return
            else:
                progress.setValue(i)
                QApplication.processEvents()

            split_line = [x.strip() for x in line.split("\t")]
            assert len(split_line) == 2
            link, mnx_id = split_line

            try:
                # Find reaction in database
                reaction_id = mnx_id_database_id_map[mnx_id]
            except KeyError:
                # Reaction has been excluded in reaction loading
                continue

            try:
                resource, identifier = link.split(":", 1)
            except ValueError:
                resource = "mnx"
                identifier = link

            # Substitute deprecated with MetaNetX prefix
            if resource == "deprecated":
                resource = "mnx"

            # Reactome some of the reactome identifiers are missing the prefix
            resource_id = prefix_resource_map[resource]
            if len(resource_id) != 1:
                LOGGER.warning("Link '{link}' skipped for {metanetx_id}, does not map to a unique resource!".format(link=link,
                                                                                                                    metanetx_id=mnx_id))
                continue
            else:
                resource_id = resource_id[0]
            validator = reaction_validators[resource_id]

            if resource == "reactome" and not re.match(validator, identifier):
                identifier = "{}{}".format(missing_prefix[resource], identifier)

            # Check that the identifier matches the validator
            if re.match(validator, identifier):
                cursor.execute("INSERT INTO reaction_ids VALUES (NULL, ?, ?, ?)", (reaction_id, resource_id, identifier))
            else:
                LOGGER.warning("Identifier {0} has not been added to reactioin '{1}' the database, as it is invalid!".format(identifier, reaction_id))

        conn.commit()


def load_metabolites(conn, files, progress):
    """ Load MetaNetX metabolites into the database

    Parameters
    ----------
    conn : connection
    files : dict
    progress: PyQt5.QWidgets.QProgressDialog

    Returns
    -------
    None
    """

    # Quit if user canceled
    if progress.wasCanceled():
        return

    # Create cursor
    cursor = conn.cursor()

    # Get the resource_id for metanetx metabolites in the database
    mnx_resource_id = get_resource_id(cursor, 'metanetx.chemical')
    inchi_resource_id = get_resource_id(cursor, 'inchi')

    # Update progress dialog
    num_lines = get_line_count(files["Metabolites"])
    progress.setLabelText("Reading metabolites..")
    progress.setMaximum(num_lines)

    # Parse metabolite file
    LOGGER.debug("Importing metabolites to database.")
    with open(files["Metabolites"]) as metabolite_file:

        for i, line in enumerate(metabolite_file):

            if line.startswith("#"):
                continue
            elif progress.wasCanceled():
                cursor.close()
                LOGGER.debug("Metabolite import was aborted by user at line {0!s}".format(i))
                return
            else:
                progress.setValue(i)
                QApplication.processEvents()

            split_line = [x.strip() for x in line.split("\t")]
            assert len(split_line) == 9

            mnx_id, description, formula, charge, mass, inchi, smiles, _, _ = split_line

            cursor.execute("INSERT INTO metabolites VALUES (NULL, ?, ?, ?)", (description, formula, charge))

            # Get the id of inserted metabolite
            metabolite_id = cursor.lastrowid

            # Add MetaNetX id to identifier table
            cursor.execute("INSERT INTO metabolite_ids VALUES (NULL, ?, ?, ?)",
                           (metabolite_id, mnx_resource_id, mnx_id))

            # Add description to database
            cursor.execute("INSERT INTO metabolite_names VALUES (NULL, ?, ?)",
                           (metabolite_id, description))

            if inchi:
                cursor.execute("INSERT INTO metabolite_ids VALUES (NULL, ?, ?, ?)",
                               (metabolite_id, inchi_resource_id, inchi))

        # Commit table structure
        conn.commit()

    # Done
    LOGGER.debug("Metabolites successfully loaded into database.")


def load_metabolites_xref(conn, files, progress):
    """ Load the cross-references for the metabolites
    into the database.

    Parameters
    ----------
    conn : connection
    files : dict
    progress: PyQt5.QWidgets.QProgressDialog

    Returns
    -------
    None
    """

    # Quit if user canceled
    if progress.wasCanceled():
        return

    # Create cursor
    cursor = conn.cursor()

    # Get resource id
    mnx_resource_id = get_resource_id(cursor, 'metanetx.chemical')

    # Get a mapping between metanetx identifier and database ids
    metabolite_map = dict(cursor.execute("SELECT identifier, metabolite_id FROM metabolite_ids WHERE resource_id=?",
                                         (mnx_resource_id,)).fetchall())

    metabolite_validators = get_validators(conn, type="metabolite")
    prefix_resource_map = get_prefix_resource_id_map(conn, type="metabolite")

    # Update progress dialog
    num_lines = get_line_count(files["MetaboliteLinks"])
    progress.setLabelText("Reading metabolite xrefs..")
    progress.setMaximum(num_lines)

    LOGGER.debug("Importing metabolite cross-links to database.")
    with open(files["MetaboliteLinks"], encoding="UTF-8") as xref_file:

        for i, line in enumerate(xref_file):

            if line.startswith("#"):
                continue
            elif progress.wasCanceled():
                cursor.close()
                LOGGER.debug("Metabolite xref import was aborted by user at line {0!s}".format(i))
                return
            else:
                progress.setValue(i)
                QApplication.processEvents()

            # Split line in columns
            split_line = [x.strip() for x in line.split("\t")]
            entry, met_id, evidence, description = split_line

            # Skip entries that map to themselves
            if entry == met_id:
                LOGGER.info("Skipped line {0!s}: Entry references to itself".format(i))
                continue

            # Get metabolite_id
            try:
                metabolite_id = metabolite_map[met_id]
            except KeyError:
                LOGGER.warning("Xref {entry} skipped as no metabolite with ID '{mnx_id}' found in database".format(entry=entry,
                                                                                                                   mnx_id=met_id))
                continue

            # Add identifier to the identifier table
            add_identifier(cursor, metabolite_id, entry, prefix_resource_map, metabolite_validators)

            # Add names to the metabolite
            add_names_from_description(cursor, metabolite_id, description, prefix_resource_map, metabolite_validators)

        # Commit changes
        conn.commit()

    # Done
    LOGGER.debug("Metabolitesc cross-links successfully loaded into database.")


def load_compartments(conn, files, progress):
    # Quit if user canceled
    if progress.wasCanceled():
        return

    # Create cursor
    cursor = conn.cursor()

    # Update progress dialog
    num_lines = get_line_count(files["Compartments"])
    progress.setLabelText("Reading Compartments..")
    progress.setMaximum(num_lines)

    LOGGER.debug("Importing compartments to database.")
    with open(files["Compartments"], encoding="UTF-8") as open_file:

        for i, line in enumerate(open_file):
            if line.startswith("#"):
                continue
            elif progress.wasCanceled():
                cursor.close()
                LOGGER.debug("Compartment import was aborted by user at line {0!s}".format(i))
                return
            else:
                progress.setValue(i)
                QApplication.processEvents()

            # Split line in columns
            split_line = [x.strip() for x in line.split("\t")]
            mnx_id, description, source = split_line

            cursor.execute("INSERT INTO compartments VALUES (NULL, ?, ?)", (mnx_id, description))

    # Commit changes
    conn.commit()

    # Done
    LOGGER.debug("Compartments successfully loaded into database.")


def create_indices(conn, progress):
    """ Create indices on the databases
    
    Parameters
    ----------
    conn : sqlite3.Connection
    progress : PyQt5.QWidgets.QProgressDialog

    Returns
    -------

    """

    if progress.wasCanceled():
        return

    indices = ["CREATE INDEX idx_met_xref_identifier ON metabolite_ids (identifier);",  # User search
               "CREATE INDEX idx_met_names ON metabolite_names (name);",  # User search
               "CREATE INDEX idx_met_id ON metabolites (id);",  # Internal search
               "CREATE INDEX idx_met_names2 ON metabolite_names (metabolite_id);",  # User search
               "CREATE INDEX idx_met_xref_identifier2 ON metabolite_ids (metabolite_id);",  # User search
               "CREATE INDEX idx_met_formula ON metabolites (formula);",
               "CREATE INDEX idx_reactionid_participants ON reaction_participants (reaction_id)",  # Matching reaction to database
               "CREATE INDEX idx_metid_participants ON reaction_participants (metabolite_id)"  # Matching metabolite to database
               ]

    progress.setMaximum(len(indices))
    progress.setLabelText("Setting up indices..")

    cursor = conn.cursor()

    for i, index in enumerate(indices):
        progress.setValue(i)
        QApplication.processEvents()
        LOGGER.debug("Running: {}".format(index))
        cursor.execute(index)
    conn.commit()


def create_database_de_novo(parent, database_path):
    """ Setup a new database from the MetaNetX files
    
    Parameters
    ----------
    parent: GEMEditor.main.MainWindow
    database_path: str

    Returns
    -------

    """

    # Generate an empty database
    if not setup_empty_database(parent, database_path):
        return

    # Download files
    files = download_metanetx_files(parent)
    if not files:
        return

    connection = get_database_connection()
    if connection is None:
        # Delete temp files
        cleanup_files(files)
        return

    # Setup progress dialog
    progress = QProgressDialog()
    progress.setAutoClose(0)
    progress.setWindowTitle("Setting up tables..")

    load_metabolites(connection, files, progress)
    load_metabolites_xref(connection, files, progress)
    load_compartments(connection, files, progress)
    load_reactions(connection, files, progress)
    load_reaction_xrefs(connection, files, progress)
    create_indices(connection, progress)

    # Cleanup files
    connection.close()
    cleanup_files(files)

    if progress.wasCanceled():
        try:
            os.remove(database_path)
        except OSError:
            pass
        progress.close()
        return None

    progress.close()
    return True


def get_database_connection():
    """ Get a connection to the MetaNetX database

    Returns
    -------
    sqlite3.Connection or None
    """
    # Get database path
    database_path = DatabaseWrapper.get_database_path()

    if os.path.isfile(database_path):
        return sqlite3.connect(database_path)
    else:
        return None


def database_exists(parent=None, create_otherwise=True):
    """ Check that the database exists"""
    database_path = DatabaseWrapper.get_database_path()
    if os.path.isfile(database_path):
        return True
    elif create_otherwise:
        return create_database_de_novo(parent=parent, database_path=database_path)
    return False