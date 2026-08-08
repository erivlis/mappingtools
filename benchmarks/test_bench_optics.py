"""CodSpeed benchmarks for `mappingtools.optics`."""

from mappingtools.optics import Lens, patch, project

SCHEMA = {
    'first_user': 'users.0.name',
    'first_city': 'users.0.profile.city',
    'last_user': 'users.99.name',
    'last_city': 'users.99.profile.city',
    'namespace': 'meta.schema.namespace',
    'version': 'meta.schema.version',
    'checksum': 'meta.checksum',
}

CHANGES = {
    'users.0.profile.city': 'new_city',
    'users.50.name': 'renamed',
    'meta.schema.version': 4,
    'meta.checksum': 'def456',
}


def test_project(benchmark, document):
    result = benchmark(project, document, SCHEMA)
    assert result


def test_patch(benchmark, document):
    result = benchmark(patch, document, CHANGES)
    assert result


def test_lens_path_get(benchmark, document):
    lenses = [Lens.path('users', i, 'profile', 'city') for i in range(100)]

    def get_all():
        return [lens.get(document) for lens in lenses]

    result = benchmark(get_all)
    assert result


def test_lens_build(benchmark):
    def build():
        return [Lens.path('users', i, 'profile', 'city') for i in range(100)]

    result = benchmark(build)
    assert result


def test_lens_set(benchmark, document):
    lenses = [Lens.path('users', i, 'profile', 'version') for i in range(100)]

    def set_all():
        data = document
        for i, lens in enumerate(lenses):
            data = lens.set(data, i)
        return data

    result = benchmark(set_all)
    assert result


def test_lens_modify(benchmark, document):
    lenses = [Lens.path('users', i, 'profile', 'version') for i in range(100)]

    def modify_all():
        data = document
        for lens in lenses:
            data = lens.modify(data, lambda v: v + 1)
        return data

    result = benchmark(modify_all)
    assert result
