from GEMEditor.rw import sbml3_ns, fbc_ns

valid_metabolite_with_annotation = """<sbml xmlns="{0}" xmlns:fbc="{1}">
<listOfSpecies>
<species boundaryCondition="false" constant="false" hasOnlySubstanceUnits="false" id="M_13GLUCAN" name="1,3-beta-D-Glucan" metaid="M_13GLUCAN" compartment="c" fbc:chemicalFormula="C18H32O16">
<annotation>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="#M_13GLUCAN">
<bqbiol:is xmlns:bqbiol="http://biomodels.net/biology-qualifiers/">
<rdf:Bag>
<rdf:li rdf:resource="http://identifiers.org/inchi/InChI=1S/C18H32O16/c19-1-4-7(22)10(25)11(26)17(31-4)34-15-9(24)6(3-21)32-18(13(15)28)33-14-8(23)5(2-20)30-16(29)12(14)27/h4-29H,1-3H2/t4-,5-,6-,7-,8-,9-,10+,11-,12-,13-,14+,15+,16-,17+,18+/m1/s1"/>
<rdf:li rdf:resource="http://identifiers.org/chebi/CHEBI:37671"/>
<rdf:li rdf:resource="http://identifiers.org/kegg.compound/C00965"/>
</rdf:Bag>
</bqbiol:is>
</rdf:Description>
</rdf:RDF>
</annotation>
</species>
</listOfSpecies></sbml>""".format(sbml3_ns, fbc_ns)


valid_metabolite_wo_annotation = """<sbml xmlns="{0}" xmlns:fbc="{1}">
<listOfSpecies>
<species boundaryCondition="false" constant="false" hasOnlySubstanceUnits="false" id="M_13GLUCAN" name="1,3-beta-D-Glucan" metaid="M_13GLUCAN" compartment="c">
</species>
</listOfSpecies></sbml>""".format(sbml3_ns, fbc_ns)