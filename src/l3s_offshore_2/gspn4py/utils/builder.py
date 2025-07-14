from typing import Dict, List, Optional
import numpy as np
from gspn4py.core.models.base import BasePetriNet
from pm4py.objects.petri_net.obj import PetriNet
from copy import deepcopy


class PetriNetBuilder:
    """Factory for creating immutable EnhancedPetriNet instances."""

    @staticmethod
    def from_incidence_matrices(Ai: np.ndarray,
                              Ao: np.ndarray,
                              name: str = "GeneratedNet") -> BasePetriNet:
        """Creates a net from incidence matrices (like MATLAB's createPDF)."""
        net = BasePetriNet(name)
        ps = Ai.shape[1]  # Number of places
        ts = Ai.shape[0]  # Number of transitions

        # Create and add places using the EnhancedPetriNet API
        places = [net.add_place(f"p{i+1}") for i in range(ps)]

        # Create and add transitions using the EnhancedPetriNet API
        transitions = [net.add_transition(f"t{i+1}") for i in range(ts)]

        # Add arcs using the EnhancedPetriNet API
        for ti_idx, ti in enumerate(transitions):
            for pj_idx, pj in enumerate(places):
                # Input arcs (place -> transition)
                for _ in range(int(Ai[ti_idx, pj_idx])):
                    net.add_arc(pj, ti)
                # Output arcs (transition -> place)
                for _ in range(int(Ao[ti_idx, pj_idx])):
                    net.add_arc(ti, pj)

        net.update_incidence_matrix()
        net.lock()
        return net

    @staticmethod
    def from_definitions(def_files: List[Dict]) -> BasePetriNet:
        """Creates a net from modular definitions (like png_process_DEF_files)."""
        # Combine all definitions
        combined = {
            'places': set(),
            'transitions': set(),
            'arcs': [],
            'inhibitors': [],
            'modules': {}
        }

        for i, pn_def in enumerate(def_files):
            module_id = i + 1
            combined['places'].update(pn_def.get('places', []))
            combined['transitions'].update(pn_def.get('transitions', []))
            combined['arcs'].extend(pn_def.get('arcs', []))
            combined['inhibitors'].extend(pn_def.get('inhibitors', []))

            if 'ports' in pn_def:
                combined['modules'][module_id] = {
                    'name': pn_def.get('name', f'Module_{module_id}'),
                    'transitions': pn_def['transitions'],
                    'ports': pn_def['ports']
                }

        # Create the net
        net = BasePetriNet(" + ".join(
            m['name'] for m in combined['modules'].values()
        ) or "CombinedNet")

        # Add places and transitions using the API
        place_map = {}
        for place_name in combined['places']:
            place = net.add_place(place_name)
            place_map[place_name] = place

        trans_map = {}
        for trans_name in combined['transitions']:
            transition = net.add_transition(trans_name)
            trans_map[trans_name] = transition

        # Add normal arcs
        for arc_def in combined['arcs']:
            if len(arc_def) == 3:
                src, tgt, weight = arc_def
            else:
                src, tgt = arc_def
                weight = 1

            if weight < 1:
                raise ValueError(f"Invalid arc weight {weight} for {src} -> {tgt}")

            source = place_map.get(src) or trans_map.get(src)
            target = place_map.get(tgt) or trans_map.get(tgt)
            
            if not source or not target:
                raise ValueError(f"Invalid arc: {src} -> {tgt}")
                
            net.add_arc(source, target, weight)

        # Add inhibitor arcs
        for inh_def in combined['inhibitors']:
            if len(inh_def) == 3:
                place, trans, weight = inh_def
            else:
                place, trans = inh_def
                weight = 1

            if weight < 1:
                raise ValueError(f"Invalid inhibitor arc weight {weight} for {place} -> {trans}")
                
            net.add_inhibitor_arc(place_map[place], trans_map[trans], weight)

        # Set up modules
        for mod_id, data in combined['modules'].items():
            net.module_info.add_module(
                data['name'],
                list(data['transitions']),
                list(data.get('ports', []))
            )

        net.update_incidence_matrix()
        net.lock()
        return net

    @staticmethod
    def copy_net(net: BasePetriNet) -> BasePetriNet:
        """Creates a deep copy of a Petri net for initialization"""
        new_net = BasePetriNet(net.name + " (Copy)")
        
        # Copy places and build mapping to original objects
        place_map = {}
        for place in net.places:
            place_map[place] = new_net.add_place(place.name)

        # Copy transitions and build mapping
        trans_map = {}
        for transition in net.transitions:
            trans_map[transition] = new_net.add_transition(transition.name)

        # Copy arcs using the created mappings
        for arc in net.arcs:
            source = place_map.get(arc.source, trans_map.get(arc.source))
            target = place_map.get(arc.target, trans_map.get(arc.target))
            new_net.add_arc(source, target, arc.weight) # type: ignore

        # Copy inhibitor arcs
        for trans, inhibitors in net.inhibitor_arcs.items():
            for place, weight in inhibitors:
                new_net.add_inhibitor_arc(place_map[place], trans_map[trans], weight)
        
        # Copy dynamic properties
        new_net.set_initial_marking({p.name: count for p, count in net.initial_marking.items()})
        new_net.set_firing_times({t.name: ft for t, ft in net._firing_times.items()})
        new_net.set_priorities({t.name: prio for t, prio in net._priorities.items()})
        
        # Copy other attributes
        new_net.current_time = net.current_time
        for module_id, data in net.module_info._modules.items():
            new_net.module_info.add_module(
                data['name'],
                list(data['transitions']),
                list(data.get('ports', []))
            )
        new_net.update_incidence_matrix()
        
        if net._locked:
            new_net.lock()
            
        return new_net