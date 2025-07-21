import json
import xml.etree.ElementTree as ET

def json_to_pnml(json_path, pnml_path):
    # Load JSON
    with open(json_path, 'r') as f:
        data = json.load(f)

    net_name = data.get("name", "petri_net")

    # Create root PNML structure
    pnml = ET.Element("pnml")
    net = ET.SubElement(pnml, "net", id=net_name, type="http://www.pnml.org/version-2009/grammar/pnml")

    # Add places
    for place in data["places"]:
        place_elem = ET.SubElement(net, "place", id=place["name"])
        name_elem = ET.SubElement(place_elem, "name")
        ET.SubElement(name_elem, "text").text = place["name"]
        marking_elem = ET.SubElement(place_elem, "initialMarking")
        ET.SubElement(marking_elem, "text").text = str(place.get("tokens", 0))

    # Add transitions
    for trans in data["transitions"]:
        trans_elem = ET.SubElement(net, "transition", id=trans["name"])
        name_elem = ET.SubElement(trans_elem, "name")
        ET.SubElement(name_elem, "text").text = trans["name"]
        toolspec = ET.SubElement(trans_elem, "toolspecific", tool="timed-petri-net", version="1.0")
        ET.SubElement(toolspec, "duration").text = str(trans.get("duration", 0))

    # Add arcs
    for idx, arc in enumerate(data["arcs"], start=1):
        arc_elem = ET.SubElement(
            net,
            "arc",
            id=f"arc{idx}",
            source=arc["source"],
            target=arc["target"],
        )
        insc_elem = ET.SubElement(arc_elem, "inscription")
        ET.SubElement(insc_elem, "text").text = str(arc.get("weight", 1))

    # Write to file with pretty printing
    _indent(pnml)
    tree = ET.ElementTree(pnml)
    tree.write(pnml_path, encoding="utf-8", xml_declaration=True)
    print(f"PNML written to {pnml_path}")

def _indent(elem, level=0):
    """Helper for pretty-printing XML."""
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            _indent(child, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# Example usage:
# json_to_pnml("model.json", "model.pnml")


def pnml_to_json(pnml_path, json_path):
    tree = ET.parse(pnml_path)
    root = tree.getroot()

    # Find the <net> element
    net = root.find("net")
    if net is None:
        raise ValueError("No <net> element found in PNML.")

    # Net name
    net_name = net.attrib.get("id", "petri_net")

    # Places
    places = []
    for place in net.findall("place"):
        place_name = place.attrib.get("id", "")
        tokens_elem = place.find("initialMarking/text")
        tokens = int(tokens_elem.text) if tokens_elem is not None else 0
        places.append({
            "name": place_name,
            "tokens": tokens
        })

    # Transitions
    transitions = []
    for trans in net.findall("transition"):
        trans_name = trans.attrib.get("id", "")
        label_elem = trans.find("name/text")
        label = label_elem.text if label_elem is not None else ""
        # Duration from toolspecific
        duration = 0
        for ts in trans.findall("toolspecific"):
            if ts.attrib.get("tool") == "timed-petri-net":
                dur_elem = ts.find("duration")
                if dur_elem is not None:
                    duration = int(dur_elem.text)
        transitions.append({
            "name": trans_name,
            "label": label,
            "properties": {},    # Not available in PNML, so left as empty
            "priority": 0,       # Not available in PNML, so left as default
            "duration": duration
        })

    # Arcs
    arcs = []
    for arc in net.findall("arc"):
        source = arc.attrib["source"]
        target = arc.attrib["target"]
        weight_elem = arc.find("inscription/text")
        weight = int(weight_elem.text) if weight_elem is not None else 1
        arcs.append({
            "source": source,
            "target": target,
            "weight": weight
        })

    # Compose the final dictionary
    petri_dict = {
        "name": net_name,
        "places": places,
        "transitions": transitions,
        "arcs": arcs
    }

    # Write to JSON
    with open(json_path, "w") as f:
        json.dump(petri_dict, f, indent=4)
    print(f"JSON written to {json_path}")

# Example usage:
# pnml_to_json("model.pnml", "model_from_pnml.json")
