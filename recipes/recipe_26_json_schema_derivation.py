"""
Recipe 26: JSON Schema Derivation (flatten + Lens + patch + merge)

Canonical JSON Schemas often contain internal-only fields, server-managed
fields, or environment-specific constraints. This recipe demonstrates how to
derive a public contract from the canonical internal schema without mutating
the source.

- `flatten` discovers which schema nodes are tagged as `readOnly` or
  `x-internal`.
- `Lens` immutably rewrites only the affected `properties` / `required`
  branches.
- `patch` updates targeted schema paths in one step.
- `merge` overlays environment-specific defaults and descriptions.
"""

import json
from collections import defaultdict
from functools import reduce

from mappingtools.operators import flatten, merge
from mappingtools.optics import Lens, patch

MARKERS = {'readOnly', 'x-internal'}


def find_properties_to_drop(schema):
    """
    Group removable property names by the path to their parent `properties`
    mapping.

    Example:
        ('properties', 'profile', 'properties') -> {'internal_notes'}
    """
    grouped = defaultdict(set)

    for path, value in flatten(schema).items():
        if not (
                value is True
                and len(path) >= 3
                and path[-1] in MARKERS
                and path[-3] == 'properties'
        ):
            continue

        parent_properties_path = path[:-2]
        property_name = path[-2]
        grouped[parent_properties_path].add(property_name)

    return sorted(grouped.items(), key=lambda item: len(item[0]), reverse=True)


def prune_properties(schema, properties_path, property_names):
    """Immutably remove properties and keep the sibling `required` list honest."""
    properties_lens = Lens.path(*properties_path)
    current_properties = properties_lens.get(schema)

    filtered_properties = {
        name: definition
        for name, definition in current_properties.items()
        if name not in property_names
    }
    next_schema = properties_lens.set(schema, filtered_properties)

    required_path = (*properties_path[:-1], 'required')
    required_lens = Lens.path(*required_path)

    try:
        current_required = required_lens.get(next_schema)
    except KeyError:
        return next_schema

    filtered_required = [name for name in current_required if name in filtered_properties]
    return required_lens.set(next_schema, filtered_required)


def derive_public_schema(canonical_schema):
    removal_plan = find_properties_to_drop(canonical_schema)

    sanitized_schema = reduce(
        lambda state, item: prune_properties(state, item[0], item[1]),
        removal_plan,
        canonical_schema,
    )

    public_schema = patch(
        sanitized_schema,
        {
            'title': 'PartnerUserCreateRequest',
            'description': 'Public contract exposed to third-party integrators.',
            Lens.path('properties', 'role', 'enum'): ['member', 'viewer'],
            Lens.path('properties', 'role', 'default'): 'viewer',
            Lens.path('properties', 'role', 'description'): 'Partners cannot create admin users.',
        },
    )

    partner_defaults = {
        'properties': {
            'email': {
                'description': 'Primary login identifier.',
            },
            'profile': {
                'properties': {
                    'timezone': {
                        'default': 'UTC',
                        'description': 'Defaults to Coordinated Universal Time.',
                    }
                }
            },
        }
    }

    return merge(public_schema, partner_defaults)


def main():
    canonical_schema = {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'title': 'InternalUserRecord',
        'description': 'Canonical persistence schema used inside the service boundary.',
        'type': 'object',
        'additionalProperties': False,
        'required': ['id', 'email', 'given_name', 'family_name', 'role', 'created_at', 'profile', 'audit'],
        'properties': {
            'id': {'type': 'string', 'format': 'uuid', 'readOnly': True},
            'email': {'type': 'string', 'format': 'email'},
            'given_name': {'type': 'string', 'minLength': 1},
            'family_name': {'type': 'string', 'minLength': 1},
            'role': {'type': 'string', 'enum': ['admin', 'member', 'viewer'], 'default': 'member'},
            'created_at': {'type': 'string', 'format': 'date-time', 'readOnly': True},
            'profile': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['timezone', 'internal_notes'],
                'properties': {
                    'timezone': {'type': 'string'},
                    'locale': {'type': 'string', 'default': 'en-US'},
                    'internal_notes': {'type': 'string', 'x-internal': True},
                },
            },
            'audit': {
                'type': 'object',
                'x-internal': True,
                'properties': {
                    'created_by': {'type': 'string'},
                    'updated_by': {'type': 'string'},
                },
            },
        },
    }

    removal_plan = find_properties_to_drop(canonical_schema)
    public_schema = derive_public_schema(canonical_schema)

    print('--- 1. Canonical Internal Schema ---')
    print(json.dumps(canonical_schema, indent=2))

    print('\n--- 2. Removal Plan Discovered via flatten() ---')
    for properties_path, property_names in removal_plan:
        object_path = '.'.join(map(str, properties_path[:-1])) or '<root>'
        print(f'{object_path}: {sorted(property_names)}')

    print('\n--- 3. Derived Public Schema ---')
    print(json.dumps(public_schema, indent=2))

def test_main():
    main()

if __name__ == '__main__':
    main()
