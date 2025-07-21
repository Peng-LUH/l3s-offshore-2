from gspn4py.core.models.base import BasePetriNet

def export_to_pdf(net: BasePetriNet, filename: str) -> None:
    """Exports net to a Python file (similar to MATLAB's createPDF)"""
    with open(filename, 'w') as f:
        f.write(f"# Petri Net: {net.name}\n")
        f.write(f"# Exported from EnhancedPetriNet\n\n")
        
        # Write places
        places = sorted([p.name for p in net.places 
                        if not p.name.startswith('V_')])  # Skip virtual places
        f.write(f"places = {places}\n\n")
        
        # Write transitions
        transitions = sorted([t.name for t in net.transitions])
        f.write(f"transitions = {transitions}\n\n")
        
        # Write arcs
        f.write("arcs = [\n")
        for arc in net.arcs:
            f.write(f"    ('{arc.source.name}', '{arc.target.name}'),\n")
        f.write("]\n\n")
        
        # Write inhibitor arcs
        if net.inhibitor_arcs:
            f.write("inhibitors = [\n")
            for trans, inhibitors in net.inhibitor_arcs.items():
                for place, weight in inhibitors:
                    f.write(f"    ('{place.name}', '{trans.name}', {weight}),\n")
            f.write("]\n")