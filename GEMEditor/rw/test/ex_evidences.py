from GEMEditor.rw import ge_ns

minimal_evidence = """<sbml xmlns="{ns}">
<listOfEvidences>
    <evidence assertion="Presence" entity_id="Test" entity_type="Reaction">
    </evidence>
</listOfEvidences>
</sbml>""".format(ns=ge_ns)

full_evidence = """<sbml xmlns="{ns}">
<listOfEvidences>
    <evidence id="test_id" assertion="Catalyzed by" entity_id="Test" entity_type="Reaction" link_id="link_id" link_type="Gene" comment="test comment" eco="ECO:0000000" target_id="target_id" target_type="Gene">
        <listOfReferenceLinks>
            <referenceLink id="ref_id"/>
        </listOfReferenceLinks>
    </evidence>
</listOfEvidences>
</sbml>""".format(ns=ge_ns)
