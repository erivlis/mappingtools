"""
Recipe 23: Graph Theory Connectivity (flatten + distinct)

In Graph Theory, determining connectivity components (which nodes can reach which other nodes)
is a classic algorithm. If a graph is represented as a dictionary of Adjacency Lists
(Node -> [Connected Nodes]), we can use `mappingtools` primitives to find all uniquely reachable
nodes within a connected sub-graph.

This recipe uses `flatten` to expand a nested graph traversal and `distinct`
to collect the unique nodes forming the connectivity set.
"""

from collections import defaultdict

from mappingtools.operators import distinct, flatten


def main():
    # 1. A Directed Graph represented as an Adjacency List
    # Node -> [Neighbors]
    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D", "E"],
        "D": ["F"],
        "E": [],
        "F": ["A"], # Circular cycle!
        "G": ["H"], # Disconnected sub-graph
        "H": []
    }

    print("--- 1. The Adjacency List (Graph) ---")
    import json
    print(json.dumps(graph, indent=2))

    # 2. Build an N-Level Reachability Tree via Breadth-First-Search
    # We unroll the graph from a starting node (e.g., 'A') to a specific depth (e.g., 3 hops).
    # This creates a deeply nested dictionary representing all possible paths.
    def unroll_paths(node, max_depth, current_depth=0):
        if current_depth >= max_depth:
            return node # Leaf node
        neighbors = graph.get(node, [])
        if not neighbors:
            return node # Dead end

        # Recursively build the tree
        subtree = {}
        for neighbor in neighbors:
            subtree[neighbor] = unroll_paths(neighbor, max_depth, current_depth + 1)
        return subtree

    # Let's explore everything reachable from 'A' within 3 hops
    reachability_tree = {"A": unroll_paths("A", max_depth=3)}

    print("\n--- 2. Unrolled Reachability Tree (3 Hops from A) ---")
    print(json.dumps(reachability_tree, indent=2))

    # 3. Flatten the tree to find all paths
    flat_paths = flatten(reachability_tree)

    # 4. Extract all uniquely visited nodes using `distinct`
    # Since `flatten` creates paths like `('A', 'C', 'D', 'F')`,
    # the nodes themselves are the elements of the path tuples.
    # We collect them into a set to find the unique connectivity component.
    reachable_nodes = set()
    for path in flat_paths:
        # Every element in the path tuple is a visited node
        reachable_nodes.update(path)

    # We also need to add the leaf values (if they are nodes and not dictionaries)
    for leaf in flat_paths.values():
        if isinstance(leaf, str):
            reachable_nodes.add(leaf)

    print("\n--- 3. Connectivity Component (Nodes reachable from A) ---")
    print(f"Set: {sorted(reachable_nodes)}")
    print("Notice that 'G' and 'H' are mathematically unreachable from 'A'!")


if __name__ == "__main__":
    main()
