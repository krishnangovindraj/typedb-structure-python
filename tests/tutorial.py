from typing import List, Tuple
from typedb.driver import Concept, TransactionType, Credentials, DriverOptions, TypeDB, QueryOptions, ConceptRow
from typedb.common.enums import ConstraintExactness
from typedb.analyze import Pipeline, Constraint, ConstraintVertex

DB_ADDRESS = "127.0.0.1:1729"
DB_CREDENTIALS = Credentials("admin", "password")
DRIVER_OPTIONS = DriverOptions(is_tls_enabled=False)
QUERY_OPTIONS = QueryOptions()
QUERY_OPTIONS.include_query_structure = True
DB_NAME = "typedb-graph-tutorial-py"

SCHEMA = """
    define
      attribute name, value string;
      attribute age, value integer;
      entity person, owns name, owns age;
    """

DATA = """
    insert
      $john isa person, has name "John", has age 20;
      $jane isa person, has name "Jane", has age 30;
    """
QUERY = """
    match
     $x isa person;
     { $x has name $a; } or { $x has age $a; };
    """


def setup(driver, schema, data):
    if next(db for db in driver.databases.all() if db.name == DB_NAME):
        driver.databases.get(DB_NAME).delete()
    driver.databases.create(DB_NAME)
    with driver.transaction(DB_NAME, TransactionType.SCHEMA) as tx:
        tx.query(schema).resolve()
        tx.commit()
    with driver.transaction(DB_NAME, TransactionType.WRITE) as tx:
        rows = list(tx.query(data).resolve())
        assert 1 == len(rows)
        tx.commit()


def part1(driver):
    def involved_constraints(row: ConceptRow) -> List[List[Constraint]]:
        conjunctions = [row.query_structure().conjunction(c) for c in row.involved_conjunctions()]
        return [list(conjunction.constraints()) for conjunction in conjunctions]

    with driver.transaction(DB_NAME, TransactionType.READ) as tx:
        answers = list(tx.query(QUERY, QUERY_OPTIONS).resolve())

    for (i, row) in enumerate(answers):
        constraints = involved_constraints(row)
        print(f"answers[{i}]: {constraints}")  # e.g.: [ Isa($p, person), [ Has($p, $a); Isa($a, name); ] ]


def part2(driver):
    # Updates it to filter out or/not/try and flattens the lists
    import networkx
    import matplotlib.pyplot as pyplot
    def involved_constraints(row: ConceptRow) -> List[List[Constraint]]:
        def _is_subpattern(constraint: Constraint) -> bool:
            return constraint.is_or() or constraint.is_not() or constraint.is_try()

        conjunctions = [row.query_structure().conjunction(c) for c in row.involved_conjunctions()]
        return [
            constraint
            for conjunction in conjunctions for constraint in conjunction.constraints()
            if not _is_subpattern(constraint)
        ]

    def to_edge(pipeline: Pipeline, constraint: Constraint, concept_row: ConceptRow) -> Tuple[Concept, str, Concept]:
        """ Returns an edge as (from, label, to)"""
        def _substitute(vertex: ConstraintVertex) -> Concept:
            if vertex.is_label():
                return vertex.as_label()
            elif vertex.is_variable():
                var_name = pipeline.get_variable_name(vertex.as_variable())
                return concept_row.get(var_name) if var_name else None
            else:
                raise NotImplementedError("Not implemented in tutorial. See resolve_constraint_vertex")

        if constraint.is_isa():
            isa = constraint.as_isa()
            return (_substitute(isa.instance()), "isa", _substitute(isa.type()))
        elif constraint.is_has():
            has = constraint.as_has()
            return (_substitute(has.owner()), "has", _substitute(has.attribute()))
        else:
            raise NotImplementedError("Not implemented in tutorial. See DataConstraint.of")

    def draw(edges: List[Tuple[Concept, str, Concept]]):
        def _node_label(node: Concept) -> str:
            return node.get_label() + f":{node.get_value()}" if node.is_attribute() else ""

        graph = networkx.DiGraph()
        graph.add_edges_from((u, v, {"label": label}) for (u, label, v) in edges)
        pos = networkx.planar_layout(graph)
        node_labels = {n: _node_label(n) for n in graph.nodes}
        node_colors = ["b" if n.is_type() else "c" for n in graph.nodes]
        networkx.draw(graph, pos, labels=node_labels, node_color=node_colors)
        edge_labels = {(u, v): graph.get_edge_data(u, v)["label"] for (u, v) in graph.edges()}
        networkx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
        pyplot.show()

    with driver.transaction(DB_NAME, TransactionType.READ) as tx:
        answers = list(tx.query(QUERY, QUERY_OPTIONS).resolve())

    assert 4 == len(answers), "TypeDB answer count mismatch"
    # Collect edges in a set to de-duplicate
    edges = set()
    for (i, row) in enumerate(answers):
        flattened_constraints = involved_constraints(row)
        edges_in_answer = [to_edge(row.query_structure(), constraint, row) for constraint in flattened_constraints]
        # e.g.: [(Entity(person: 0x1e00000000000000000000), 'has', Attribute(age: 20)), ...]
        print(f"answers[{i}]: {edges_in_answer}")
        edges.update(edges_in_answer)
    draw(edges)


if __name__ == "__main__":
    driver = TypeDB.driver(DB_ADDRESS, DB_CREDENTIALS, DRIVER_OPTIONS)
    print("\n--- Setting up ---")
    setup(driver, SCHEMA, DATA)
    print("\n--- Starting part 1 ---")
    part1(driver)
    print("\n--- Starting part 2 ---")
    part2(driver)
