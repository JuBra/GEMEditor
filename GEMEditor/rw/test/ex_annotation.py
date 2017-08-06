from GEMEditor.rw import sbml3_ns

valid_annotation = "http://identifiers.org/inchi/InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"
valid_annotation_provider = "inchi"
valid_annotation_id = "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"

invalid_annotation1 = "http://google.com/inchi/InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"
invalid_annotation2 = "http://identifiers.org/test123"

valid_annotation_xml = """<sbml xmlns="{0}"><annotation>
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="#M_PINSP">
      <bqbiol:is xmlns:bqbiol="http://biomodels.net/biology-qualifiers/">
        <rdf:Bag>
          <rdf:li rdf:resource="http://identifiers.org/chebi/CHEBI:17283"/>
          <rdf:li rdf:resource="http://identifiers.org/kegg.compound/C04549"/>
        </rdf:Bag>
      </bqbiol:is>
      <bqbiol:property xmlns:bqbiol="http://biomodels.net/biology-qualifiers/">
        <rdf:Bag>
          <rdf:li rdf:resource="http://identifiers.org/chebi/CHEBI:17283"/>
          <rdf:li rdf:resource="http://identifiers.org/kegg.compound/C04549"/>
        </rdf:Bag>
      </bqbiol:property>
    </rdf:Description>
  </rdf:RDF>
</annotation></sbml>""".format(sbml3_ns)
