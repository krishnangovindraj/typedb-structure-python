from abc import ABC

import networkx as nx
import matplotlib.pyplot as plt
from .data_constraint import (
    DataVertex, ConceptVertex, FunctionCallVertex, ExpressionVertex, NamedRoleVertex
)
from typedb.driver import (Concept, Relation, Entity, Attribute)


class MatplotlibVisualizer(ABC):  # Keep it static
    NODE_ATTRIBUTES = None  # Late initialized

    def draw(graph: nx.MultiDiGraph):
        node_attributes = {node: MatplotlibVisualizer._get_attributes(node) for node in graph.nodes}
        node_colours = [node_attributes[node][0] for node in graph.nodes]
        node_labels = {node: node_attributes[node][1](node) for node in graph.nodes}
        nx.draw(graph, node_color=node_colours, labels=node_labels)
        plt.show()

    def _entity_relation_label(vertex: ConceptVertex):
        concept = vertex.concept
        return f"{concept.get_type().get_label()}({concept.get_iid()[-4:]})"

    def _attribute_value_as_label(vertex: ConceptVertex):
        concept = vertex.concept
        return f"{concept.get_type().get_label()}({concept.get_value()})"

    def _get_attributes(node: DataVertex):
        what = node.concept if isinstance(node, ConceptVertex) else node
        found = [c for c in MatplotlibVisualizer.NODE_ATTRIBUTES.keys() if c and isinstance(what, c)]
        key = found[0] if len(found) > 0 else None
        return MatplotlibVisualizer.NODE_ATTRIBUTES[key]

    # start


MatplotlibVisualizer.NODE_ATTRIBUTES = {
    Relation: ("b", MatplotlibVisualizer._entity_relation_label),
    Entity: ("r", MatplotlibVisualizer._entity_relation_label),
    Attribute: ("g", MatplotlibVisualizer._attribute_value_as_label),
    None: ("c", str),  # DEFAULT
}
