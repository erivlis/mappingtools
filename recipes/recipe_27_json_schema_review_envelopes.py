"""
Recipe 27: JSON Schema Review Envelopes (flatten + Lens + patch + merge)

Some workflows do not want the raw scalar directly. They want each leaf field
to become a decision envelope:

- an `override` branch carrying a proposed replacement value
- an `approved` branch carrying a boolean/null decision state

This recipe preserves the original object shape and replaces:

- primitive property schemas
- scalar array `items` schemas
- direct `$ref` schemas
- direct `oneOf` schemas
- direct `anyOf` schemas
- direct `allOf` schemas

with a `oneOf` wrapper.
"""

import json

from mappingtools.operators import flatten, merge
from mappingtools.optics import Lens, patch

NON_WRAPPABLE_COMPLEX_KEYS = {'properties', 'items'}
DEFINITION_KEYS = {'$defs', 'definitions'}
ID_SUFFIX = '-review-envelope'


def discover_wrappable_schema_paths(schema):
    """
    Discover wrappable schema paths by flattening the schema tree.

    Example:
        ('properties', 'profile', 'properties', 'timezone')
        ('properties', 'tags', 'items')
    """
    schema_paths = {
        path[:-1]
        for path in flatten(schema)
        if (
                not any(segment in DEFINITION_KEYS for segment in path)
                and (
                        (len(path) >= 3 and path[-3] == 'properties')
                        or (len(path) >= 2 and path[-2] == 'items')
                )
        )
    }
    return sorted(schema_paths, key=len)


def is_wrappable_leaf_schema(schema_node):
    """Return True when the node should be wrapped as an atomic leaf schema."""
    if not isinstance(schema_node, dict):
        return False

    if any(key in schema_node for key in NON_WRAPPABLE_COMPLEX_KEYS):
        return False

    if '$ref' in schema_node or 'oneOf' in schema_node or 'anyOf' in schema_node or 'allOf' in schema_node:
        return True

    schema_type = schema_node.get('type')
    if isinstance(schema_type, list):
        return not any(item in {'object', 'array'} for item in schema_type)

    return schema_type not in {None, 'object', 'array'}


def build_review_envelope(leaf_schema):
    """Wrap a primitive leaf schema in override/approved decision models."""
    base_branch = {
        'type': 'object',
        'additionalProperties': False,
        'required': ['type', 'value'],
        'properties': {
            'type': {'type': 'string'},
            'value': {},
            'details': {'type': 'string'},
        },
    }

    override_branch = merge(
        base_branch,
        {
            'properties': {
                'type': {'const': 'override'},
                'value': leaf_schema,
            }
        },
    )

    approved_branch = merge(
        base_branch,
        {
            'properties': {
                'type': {'const': 'approved'},
                'value': {'type': ['boolean', 'null']},
                'details': {'description': 'Optional rationale for the approval decision.'},
            }
        },
    )

    return {'oneOf': [override_branch, approved_branch]}


def derive_schema_id(schema_id, suffix=ID_SUFFIX):
    """Append a suffix to the root schema id while preserving any fragment."""
    if '#' in schema_id:
        base, fragment = schema_id.split('#', 1)
        return f'{base}{suffix}#{fragment}'
    return f'{schema_id}{suffix}'


def derive_review_schema(canonical_schema):
    schema_paths = discover_wrappable_schema_paths(canonical_schema)

    replacements = {}
    wrapped_paths = []
    for schema_path in schema_paths:
        schema_node = Lens.path(*schema_path).get(canonical_schema)
        if not is_wrappable_leaf_schema(schema_node):
            continue

        replacements[Lens.path(*schema_path)] = build_review_envelope(schema_node)
        wrapped_paths.append(schema_path)

    review_schema = patch(canonical_schema, replacements)
    review_schema = patch(
        review_schema,
        {
            'title': 'UserReviewEnvelopeSchema',
            'description': 'Every primitive field, scalar array item, direct $ref, and direct union/composition '
                           'schema (oneOf/anyOf/allOf) is wrapped in an override-or-approval envelope.',
        },
    )
    if isinstance(canonical_schema.get('$id'), str):
        review_schema = patch(
            review_schema,
            {
                '$id': derive_schema_id(canonical_schema['$id']),
            },
        )
    return review_schema, wrapped_paths


def test_deeply_nested_schema_wraps_scalar_properties_and_scalar_items_only():
    canonical_schema = {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'https://schemas.example.com/deep-schema.json',
        'title': 'DeepSchema',
        'type': 'object',
        'properties': {
            'status': {'type': 'string'},
            'tags': {
                'type': 'array',
                'items': {'type': 'string'},
            },
            'profile': {
                'type': 'object',
                'properties': {
                    'age': {'type': 'integer'},
                    'aliases': {
                        'type': 'array',
                        'items': {'type': 'string'},
                    },
                },
            },
            'addresses': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'street': {'type': 'string'},
                        'country_codes': {
                            'type': 'array',
                            'items': {'type': 'string'},
                        },
                    },
                },
            },
            'matrix': {
                'type': 'array',
                'items': {
                    'type': 'array',
                    'items': {'type': 'number'},
                },
            },
        },
    }

    review_schema, wrapped_paths = derive_review_schema(canonical_schema)
    wrapped_paths = {tuple(path) for path in wrapped_paths}

    assert review_schema['$id'] == 'https://schemas.example.com/deep-schema.json-review-envelope'
    assert canonical_schema['$id'] == 'https://schemas.example.com/deep-schema.json'
    assert ('properties', 'status') in wrapped_paths
    assert ('properties', 'tags', 'items') in wrapped_paths
    assert ('properties', 'profile', 'properties', 'age') in wrapped_paths
    assert ('properties', 'profile', 'properties', 'aliases', 'items') in wrapped_paths
    assert ('properties', 'addresses', 'items', 'properties', 'street') in wrapped_paths
    assert ('properties', 'addresses', 'items', 'properties', 'country_codes', 'items') in wrapped_paths
    assert ('properties', 'matrix', 'items', 'items') in wrapped_paths

    assert review_schema['properties']['status']['oneOf'][0]['properties']['value'] == {'type': 'string'}
    assert review_schema['properties']['tags']['type'] == 'array'
    assert review_schema['properties']['tags']['items']['oneOf'][0]['properties']['value'] == {'type': 'string'}

    assert review_schema['properties']['addresses']['type'] == 'array'
    assert review_schema['properties']['addresses']['items']['type'] == 'object'
    assert review_schema['properties']['addresses']['items']['properties']['street']['oneOf'][0]['properties'][
               'value'] == {'type': 'string'}
    assert review_schema['properties']['addresses']['items']['properties']['country_codes']['type'] == 'array'
    assert \
    review_schema['properties']['addresses']['items']['properties']['country_codes']['items']['oneOf'][0]['properties'][
        'value'] == {'type': 'string'}

    assert review_schema['properties']['matrix']['type'] == 'array'
    assert review_schema['properties']['matrix']['items']['type'] == 'array'
    assert review_schema['properties']['matrix']['items']['items']['oneOf'][0]['properties']['value'] == {
        'type': 'number'}


def test_direct_ref_and_union_composition_nodes_are_wrapped_atomically():
    canonical_schema = {
        'type': 'object',
        'properties': {
            'choice': {
                'oneOf': [
                    {'type': 'string'},
                    {'type': 'integer'},
                ]
            },
            'linked': {
                '$ref': '#/$defs/LinkedType',
            },
            'choices': {
                'type': 'array',
                'items': {
                    'oneOf': [
                        {'type': 'string'},
                        {'type': 'integer'},
                    ]
                },
            },
            'linked_items': {
                'type': 'array',
                'items': {
                    '$ref': '#/$defs/LinkedType',
                },
            },
            'maybe': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'},
                ]
            },
            'composed': {
                'allOf': [
                    {'type': 'string'},
                    {'maxLength': 10},
                ]
            },
            'record': {
                'type': 'object',
                'properties': {
                    'kind': {'type': ['string', 'null']},
                },
            },
        },
        '$defs': {
            'LinkedType': {'type': 'string'},
        },
    }

    review_schema, wrapped_paths = derive_review_schema(canonical_schema)
    wrapped_paths = {tuple(path) for path in wrapped_paths}

    assert ('properties', 'record', 'properties', 'kind') in wrapped_paths
    assert ('properties', 'choice') in wrapped_paths
    assert ('properties', 'linked') in wrapped_paths
    assert ('properties', 'choices', 'items') in wrapped_paths
    assert ('properties', 'linked_items', 'items') in wrapped_paths
    assert ('properties', 'maybe') in wrapped_paths
    assert ('properties', 'composed') in wrapped_paths

    assert review_schema['properties']['choice']['oneOf'][0]['properties']['value'] == canonical_schema['properties'][
        'choice']
    assert review_schema['properties']['linked']['oneOf'][0]['properties']['value'] == canonical_schema['properties'][
        'linked']
    assert review_schema['properties']['choices']['items']['oneOf'][0]['properties']['value'] == {
        'oneOf': [
            {'type': 'string'},
            {'type': 'integer'},
        ]
    }
    assert review_schema['properties']['linked_items']['items']['oneOf'][0]['properties']['value'] == {
        '$ref': '#/$defs/LinkedType'}
    assert review_schema['properties']['maybe']['oneOf'][0]['properties']['value'] == canonical_schema['properties'][
        'maybe']
    assert review_schema['properties']['composed']['oneOf'][0]['properties']['value'] == canonical_schema['properties'][
        'composed']
    assert review_schema['$defs'] == canonical_schema['$defs']
    assert review_schema['properties']['record']['properties']['kind']['oneOf'][0]['properties']['value'] == {
        'type': ['string', 'null']}


def test_root_id_suffix_preserves_fragment():
    canonical_schema = {
        '$id': 'https://schemas.example.com/user.json#/derived/root',
        'type': 'object',
        'properties': {
            'status': {'type': 'string'},
        },
    }

    review_schema, _ = derive_review_schema(canonical_schema)

    assert review_schema['$id'] == 'https://schemas.example.com/user.json-review-envelope#/derived/root'


def test_alternating_array_object_array_object_array_nesting():
    canonical_schema = {
        'type': 'object',
        'properties': {
            'groups': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'group_id': {'type': 'string'},
                        'members': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'labels': {
                                        'type': 'array',
                                        'items': {'type': 'string'},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    }

    review_schema, wrapped_paths = derive_review_schema(canonical_schema)
    wrapped_paths = {tuple(path) for path in wrapped_paths}

    assert ('properties', 'groups', 'items', 'properties', 'group_id') in wrapped_paths
    assert ('properties', 'groups', 'items', 'properties', 'members', 'items', 'properties', 'name') in wrapped_paths
    assert ('properties', 'groups', 'items', 'properties', 'members', 'items', 'properties', 'labels',
            'items') in wrapped_paths

    groups_schema = review_schema['properties']['groups']
    assert groups_schema['type'] == 'array'
    assert groups_schema['items']['type'] == 'object'
    assert groups_schema['items']['properties']['group_id']['oneOf'][0]['properties']['value'] == {'type': 'string'}

    members_schema = groups_schema['items']['properties']['members']
    assert members_schema['type'] == 'array'
    assert members_schema['items']['type'] == 'object'
    assert members_schema['items']['properties']['name']['oneOf'][0]['properties']['value'] == {'type': 'string'}

    labels_schema = members_schema['items']['properties']['labels']
    assert labels_schema['type'] == 'array'
    assert labels_schema['items']['oneOf'][0]['properties']['value'] == {'type': 'string'}


def main():
    canonical_schema = {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'https://schemas.example.com/user.json',
        'title': 'CanonicalUserSchema',
        'type': 'object',
        'additionalProperties': False,
        'required': ['id', 'email', 'active', 'profile'],
        'properties': {
            'id': {'type': 'string', 'format': 'uuid'},
            'email': {'type': 'string', 'format': 'email'},
            'active': {'type': 'boolean'},
            'tags': {
                'type': 'array',
                'items': {'type': 'string'},
            },
            'manager': {
                '$ref': '#/$defs/Manager',
            },
            'login': {
                'oneOf': [
                    {'type': 'string', 'format': 'email'},
                    {'type': 'string', 'pattern': '^svc-'},
                ]
            },
            'nickname': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'},
                ]
            },
            'score': {
                'allOf': [
                    {'type': 'integer'},
                    {'minimum': 0},
                ]
            },
            'profile': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['timezone', 'locale', 'preferences'],
                'properties': {
                    'timezone': {'type': 'string'},
                    'locale': {'type': 'string', 'default': 'en-US'},
                    'preferences': {
                        'type': 'object',
                        'additionalProperties': False,
                        'required': ['marketing_opt_in', 'max_items'],
                        'properties': {
                            'marketing_opt_in': {'type': 'boolean'},
                            'max_items': {'type': 'integer', 'minimum': 1},
                        },
                    },
                },
            },
        },
        '$defs': {
            'Manager': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string', 'format': 'uuid'},
                },
            }
        },
    }

    review_schema, wrapped_paths = derive_review_schema(canonical_schema)

    print('--- 1. Canonical Schema ---')
    print(json.dumps(canonical_schema, indent=2))

    print('\n--- 2. Wrappable Leaf Paths Discovered via flatten() ---')
    for path in wrapped_paths:
        print('.'.join(map(str, path)))

    print('\n--- 3. Sample Wrapped Nodes (id + manager + login + nickname + score + tags.items) ---')
    sample_nodes = {
        'id': review_schema['properties']['id'],
        'manager': review_schema['properties']['manager'],
        'login': review_schema['properties']['login'],
        'nickname': review_schema['properties']['nickname'],
        'score': review_schema['properties']['score'],
        'tags.items': review_schema['properties']['tags']['items'],
    }
    print(json.dumps(sample_nodes, indent=2))

    print('\n--- 4. Derived Review Schema ---')
    print(json.dumps(review_schema, indent=2))

def test_main():
    main()

if __name__ == '__main__':
    main()
