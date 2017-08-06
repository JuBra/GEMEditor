from GEMEditor.rw import sbml3_ns

valid_compartment_list = """<sbml xmlns="{0}"><listOfCompartments>
    <compartment constant="true" id="p" name="Periplasm" />
    <compartment constant="true" id="c" name="Cytoplasm" />
    <compartment constant="true" id="e" name="Extracellular" />
</listOfCompartments></sbml>""".format(sbml3_ns)
