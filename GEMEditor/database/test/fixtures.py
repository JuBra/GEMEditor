import pytest
from GEMEditor.database.tables import *
from GEMEditor.database.base import DatabaseWrapper


@pytest.fixture(scope='module')
def database(tmpdir_factory):
    path = tmpdir_factory.mktemp('data').join('database.db')
    path = str(path)
    setup_empty_database(path)

    # Create sesssion for adding information
    engine = create_engine('sqlite:///{}'.format(path))
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add compartment
    comp = Compartment(mnx_id="MNXC3", name="cytoplasm")
    session.add(comp)
    session.commit()

    # Add metabolites
    met1 = Metabolite(name="Water", formula="H2O", charge=0)
    met2 = Metabolite(name="alpha-D-glucose 6-phosphate", formula="C6H11O9P", charge=-2)
    met3 = Metabolite(name="Phosphate", formula="HO4P", charge=-2)
    met4 = Metabolite(name="alpha-D-glucose", formula="C6H12O6", charge=0)
    met5 = Metabolite(name="Proton", formula="H", charge=1)
    metabolites = (met1, met2, met3, met4, met5)
    session.add_all(metabolites)
    session.commit()

    # Add metabolite names
    session.add_all((MetaboliteName(metabolite_id=m.id, name=m.name)
                     for m in metabolites))
    session.commit()

    # Add metabolite ids
    met1_id = MetaboliteId(metabolite_id=met1.id, resource_id=1, identifier="MNXM2")
    met2_id = MetaboliteId(metabolite_id=met2.id, resource_id=1, identifier="MNXM215")
    met3_id = MetaboliteId(metabolite_id=met3.id, resource_id=1, identifier="MNXM9")
    met4_id = MetaboliteId(metabolite_id=met4.id, resource_id=1, identifier="MNXM99")
    met5_id = MetaboliteId(metabolite_id=met5.id, resource_id=1, identifier="MNXM01")
    met5_id2 = MetaboliteId(metabolite_id=met5.id, resource_id=1, identifier="MNXM1")
    session.add_all((met1_id, met2_id, met3_id, met4_id, met5_id, met5_id2))
    session.commit()

    # Add reaction
    reaction = Reaction(string="1 `H2O` + 1 `alpha-D-glucose 6-phosphate` = 1 `phosphate` + 1 `alpha-D-glucose`")
    session.add(reaction)
    session.commit()

    # Add reaction id
    reaction_id = ReactionId(reaction_id=reaction.id, resource_id=17, identifier="MNXR14892")
    session.add(reaction_id)
    session.commit()

    # Add reaction participants
    part1 = ReactionMember(reaction_id=reaction.id, metabolite_id=met1.id, stoichiometry=-1, compartment_id=comp.id)
    part2 = ReactionMember(reaction_id=reaction.id, metabolite_id=met2.id, stoichiometry=-1, compartment_id=comp.id)
    part3 = ReactionMember(reaction_id=reaction.id, metabolite_id=met3.id, stoichiometry=1, compartment_id=comp.id)
    part4 = ReactionMember(reaction_id=reaction.id, metabolite_id=met4.id, stoichiometry=1, compartment_id=comp.id)
    session.add_all((part1, part2, part3, part4))
    session.commit()

    # Add reaction name
    r_name = ReactionName(reaction_id=reaction.id, name="Glucose-6-Phosphatase")
    session.add(r_name)
    session.commit()

    session.close()

    database = DatabaseWrapper(path)
    yield database
    database.close()
