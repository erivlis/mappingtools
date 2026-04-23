"""
Recipe 11: Microservice Dependency Graph (inverse + AutoMapper)

In large-scale Microservice architectures, you often define a "forward"
dependency graph in your infrastructure as code:
"Service A depends on [Service B, Service C]".

However, during an incident (e.g., Service C goes down), you need the
"reverse" graph to determine the blast radius: "Who is impacted by Service C failing?".
Furthermore, when exporting this complex graph to a visualization tool
(like Mermaid.js or Graphviz), long service names create cluttered, unreadable diagrams,
so we need consistent, minified short-codes.

This recipe combines the `inverse` mathematical operator with the stateful
`AutoMapper` collector to instantly resolve reverse dependencies and generate
a minified visualization manifest.
"""

from mappingtools.collectors import AutoMapper
from mappingtools.operators import inverse


def main():
    # 1. The Forward Dependency Graph (Microservice -> {Dependencies})
    # This maps a service to the upstream services it calls.
    forward_graph = {
        "api-gateway": {"auth-service", "product-catalog"},
        "product-catalog": {"inventory-db", "pricing-engine"},
        "auth-service": {"user-db", "redis-cache"},
        "pricing-engine": {"redis-cache", "exchange-rate-api"},
        "inventory-db": set(),
        "user-db": set(),
        "redis-cache": set(),
        "exchange-rate-api": set()
    }

    # 2. Calculate the Reverse Dependency Graph using `inverse`.
    # This mathematical operation swaps keys and values.
    # Since multiple services might depend on the same target (like redis-cache),
    # `inverse` automatically handles collisions by grouping the origins into a `set`.
    reverse_graph = inverse(forward_graph)

    print("--- Incident Response: Blast Radius ---")
    incident_service = "redis-cache"
    impacted = reverse_graph.get(incident_service, set())
    print(f"If '{incident_service}' goes down, these services are immediately impacted:")
    for svc in impacted:
        print(f"  - {svc}")

    # 3. Minify the graph for visualization (Graphviz / Mermaid.js)
    # We use AutoMapper to automatically assign a short-code (A, B, C...) to every service
    # the first time it is accessed.
    short_codes = AutoMapper(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    print("\n--- Minified Diagram Manifest (Mermaid.js Format) ---")
    print("graph TD")
    for service, dependencies in forward_graph.items():
        service_node = short_codes[service]
        for dep in dependencies:
            dep_node = short_codes[dep]
            print(f"    {service_node} --> {dep_node}")

    print("\n--- Node Legend ---")
    # AutoMapper acts like a dictionary containing the mappings it generated
    for full_name, short_code in short_codes.items():
        print(f"    {short_code} = {full_name}")


def test_main():
    main()


if __name__ == "__main__":
    main()
