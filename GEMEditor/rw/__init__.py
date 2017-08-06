
ns_dummy = "{{{0}}}{1}"
rdf_ns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
bqbiol_ns = "http://biomodels.net/biology-qualifiers/"
sbml3_ns = "http://www.sbml.org/sbml/level3/version1/core"
fbc_ns = "http://www.sbml.org/sbml/level3/version1/fbc/version2"
ge_ns = "http://bitbucket.org/JuBra/gem-editor"

nsmap = {"rdf": rdf_ns,
         "bqbiol": bqbiol_ns,
         "sbml": sbml3_ns,
         "fbc": fbc_ns,
         "gem": ge_ns}

# Pre-formatted rdf items
rdf_description = ns_dummy.format(rdf_ns, "Description")
rdf_RDF = ns_dummy.format(rdf_ns, "RDF")
rdf_about = ns_dummy.format(rdf_ns, "about")
rdf_li = ns_dummy.format(rdf_ns, "li")
rdf_resource = ns_dummy.format(rdf_ns, "resource")
rdf_bag = ns_dummy.format(rdf_ns, "Bag")


# Pre-formatted bqbiol items
bqbiol_is = ns_dummy.format(bqbiol_ns, "is")
bqbiol_has = ns_dummy.format(bqbiol_ns, "property")


# Pre-formatted sbml3 items
sbml3_annotation = ns_dummy.format(sbml3_ns, "annotation")
sbml3_reaction = ns_dummy.format(sbml3_ns, "reaction")
sbml3_listOfReactions = ns_dummy.format(sbml3_ns, "listOfReactions")
sbml3_listOfReactants = ns_dummy.format(sbml3_ns, "listOfReactants")
sbml3_listOfProducts = ns_dummy.format(sbml3_ns, "listOfProducts")
sbml3_species = ns_dummy.format(sbml3_ns, "species")
sbml3_speciesReference = ns_dummy.format(sbml3_ns, "speciesReference")
sbml3_model = ns_dummy.format(sbml3_ns, "model")
sbml3_compartment = ns_dummy.format(sbml3_ns, "compartment")
sbml3_listOfSpecies = ns_dummy.format(sbml3_ns, "listOfSpecies")
sbml3_listOfCompartments = ns_dummy.format(sbml3_ns, "listOfCompartments")
sbml3_listOfParameters = ns_dummy.format(sbml3_ns, "listOfParameters")
sbml3_parameter = ns_dummy.format(sbml3_ns, "parameter")
sbml3_sbml = ns_dummy.format(sbml3_ns, "sbml")
sbml3_listOfUnitDefinitions = ns_dummy.format(sbml3_ns, "listOfUnitDefinitions")
sbml3_unitDefinition = ns_dummy.format(sbml3_ns, "unitDefinition")
sbml3_listOfUnits = ns_dummy.format(sbml3_ns, "listOfUnits")
sbml3_unit = ns_dummy.format(sbml3_ns, "unit")


# Pre-formatted fbc items
fbc_required = ns_dummy.format(fbc_ns, "required")
fbc_strict = ns_dummy.format(fbc_ns, "strict")
fbc_listOfObjectives = ns_dummy.format(fbc_ns, "listOfObjectives")
fbc_activeObjective = ns_dummy.format(fbc_ns, "activeObjective")
fbc_objective = ns_dummy.format(fbc_ns, "objective")
fbc_id = ns_dummy.format(fbc_ns, "id")
fbc_type = ns_dummy.format(fbc_ns, "type")
fbc_listOfFluxObjectives = ns_dummy.format(fbc_ns, "listOfFluxObjectives")
fbc_charge = ns_dummy.format(fbc_ns, "charge")
fbc_chemicalFormula = ns_dummy.format(fbc_ns, "chemicalFormula")
fbc_or = ns_dummy.format(fbc_ns, "or")
fbc_and = ns_dummy.format(fbc_ns, "and")
fbc_geneProductRef = ns_dummy.format(fbc_ns, "geneProductRef")
fbc_geneProductAssociation = ns_dummy.format(fbc_ns, "geneProductAssociation")
fbc_listOfGeneProducts = ns_dummy.format(fbc_ns, "listOfGeneProducts")
fbc_geneProduct = ns_dummy.format(fbc_ns, "geneProduct")
fbc_name = ns_dummy.format(fbc_ns, "name")
fbc_label = ns_dummy.format(fbc_ns, "label")
fbc_upperFluxBound = ns_dummy.format(fbc_ns, "upperFluxBound")
fbc_lowerFluxBound = ns_dummy.format(fbc_ns, "lowerFluxBound")
fbc_reaction = ns_dummy.format(fbc_ns, "reaction")
fbc_coefficient = ns_dummy.format(fbc_ns, "coefficient")
fbc_fluxObjective = ns_dummy.format(fbc_ns, "fluxObjective")

# Pre_formatted GEMEditor items
ge_subsystem = ns_dummy.format(ge_ns, "subsystem")
ge_id = ns_dummy.format(ge_ns, "id")
ge_type = ns_dummy.format(ge_ns, "type")
ge_genome = ns_dummy.format(ge_ns, "genome")
ge_listOfReferences = ns_dummy.format(ge_ns, "listOfReferences")
ge_reference = ns_dummy.format(ge_ns, "reference")
ge_listOfAuthors = ns_dummy.format(ge_ns, "listOfAuthors")
ge_author = ns_dummy.format(ge_ns, "author")
ge_annotation = ns_dummy.format(ge_ns, "annotation")
ge_listOfTests = ns_dummy.format(ge_ns, "listOfTests")
ge_testCase = ns_dummy.format(ge_ns, "testCase")
ge_listOfSettings = ns_dummy.format(ge_ns, "listOfSettings")
ge_reactionSetting = ns_dummy.format(ge_ns, "reactionSetting")
ge_geneSetting = ns_dummy.format(ge_ns, "geneSetting")
ge_listOfOutcomes = ns_dummy.format(ge_ns, "listOfOutcomes")
ge_outcome = ns_dummy.format(ge_ns, "outcome")
ge_greaterThan = ns_dummy.format(ge_ns, "greaterThan")
ge_lessThan = ns_dummy.format(ge_ns, "lessThan")
ge_listOfReferenceLinks = ns_dummy.format(ge_ns, "listOfReferenceLinks")
ge_referenceLink = ns_dummy.format(ge_ns, "referenceLink")
ge_comment = ns_dummy.format(ge_ns, "comment")

# GEMEditor Evidence items
ge_listOfEvidences = ns_dummy.format(ge_ns, "listOfEvidences")
ge_evidence = ns_dummy.format(ge_ns, "evidence")
ge_listOfLinkedItems = ns_dummy.format(ge_ns, "listOfLinkedItems")
ge_linkedItem = ns_dummy.format(ge_ns, "linkedItem")
ge_baseItem = ns_dummy.format(ge_ns, "baseItem")
ge_methodItem = ns_dummy.format(ge_ns, "methodItem")


cobra_gene_prefix = "G_"
cobra_metabolite_prefix = "M_"
cobra_reaction_prefix = "R_"
cobra_default_lb_name = "cobra_default_lb"
cobra_default_lb_value = -1000.
cobra_default_ub_name = "cobra_default_ub"
cobra_default_ub_value = 1000.
cobra_default_zb_name = "cobra_0_bound"
cobra_default_zb_value = 0.

cobra_standard_boundaries = [(cobra_default_lb_value, cobra_default_lb_name, "SBO:0000626"),
                             (cobra_default_ub_value, cobra_default_ub_name, "SBO:0000626"),
                             (cobra_default_zb_value, cobra_default_zb_name, "SBO:0000626")]




