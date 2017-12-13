import logging
import os.path
from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox
from GEMEditor.database import miriam_databases
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker


LOGGER = logging.getLogger(__name__)


Base = declarative_base()


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    mnx_prefix = Column(String)
    name = Column(String)
    type = Column(String)
    miriam_collection = Column(String)
    validator = Column(String)
    use_resource = Column(Boolean)


class Compartment(Base):
    __tablename__ = "compartments"

    id = Column(Integer, primary_key=True)
    mnx_id = Column(String)
    name = Column(String)


class Metabolite(Base):
    __tablename__ = 'metabolites'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    formula = Column(String)
    charge = Column(Integer)


class MetaboliteName(Base):
    __tablename__ = "metabolite_names"

    id = Column(Integer, primary_key=True)
    metabolite_id = Column(Integer, ForeignKey("metabolites.id"))
    name = Column(String)


class MetaboliteId(Base):
    __tablename__ = "metabolite_ids"

    id = Column(Integer, primary_key=True)
    metabolite_id = Column(Integer, ForeignKey("metabolites.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    identifier = Column(String)


class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True)
    string = Column(String)


class ReactionName(Base):
    __tablename__ = "reaction_names"

    id = Column(Integer, primary_key=True)
    reaction_id = Column(Integer, ForeignKey("reactions.id"))
    name = Column(String)


class ReactionId(Base):
    __tablename__ = "reaction_ids"

    id = Column(Integer, primary_key=True)
    reaction_id = Column(Integer, ForeignKey("reactions.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    identifier = Column(String)


class ReactionMember(Base):
    __tablename__ = "reaction_participants"

    id = Column(Integer, primary_key=True)
    reaction_id = Column(Integer, ForeignKey("reactions.id"))
    metabolite_id = Column(Integer, ForeignKey("metabolites.id"))
    stoichiometry = Column(Float)
    compartment_id = Column(Integer, ForeignKey("compartments.id"))


class Pathway(Base):
    __tablename__ = "pathways"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    string = Column(String)


class PathwayName(Base):
    __tablename__ = "pathway_names"

    id = Column(Integer, primary_key=True)
    pathway_id = Column(Integer, ForeignKey("pathways.id"))
    name = Column(String)


class PathwayItem(Base):
    __tablename__ = "pathway_members"

    id = Column(Integer, primary_key=True)
    pathway_id = Column(Integer, ForeignKey("pathways.id"))
    reaction_id = Column(Integer, ForeignKey("reactions.id"))


def setup_empty_database(path):
    """ Setup an empty database

    Create an empty database containing all relevant resources.
    The resulting database is populated using the information
    from MetaNetX.

    Parameters
    ----------
    path: str
        Path of the database file

    Returns
    -------
    bool
        True if database could be created, False otherwise

    """

    # Database already exists
    if os.path.isfile(path):
        reply = QMessageBox().question(None, "Warning", "{} exists already.\nDo you want to override it?".format(path))
        if reply != QDialogButtonBox.Yes:
            return False

        try:
            os.remove(path)
        except:
            LOGGER.debug("Could not remove existing database:", exc_info=True)
            QMessageBox().critical(None, "Error", "Could not remove the existing database. Is it currently in use?")
            return False

    # Setup the database engine
    engine = create_engine('sqlite:///{}'.format(path))
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # Load all resources
    session = Session()
    for database in miriam_databases:
        session.add(Resource(use_resource=True, **database._asdict()))
    session.commit()
    session.close()
    return True
