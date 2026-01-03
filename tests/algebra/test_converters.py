from mappingtools.algebra.converters import (
    dense_to_sparse_matrix,
    dense_to_sparse_vector,
    sparse_to_dense_matrix,
    sparse_to_dense_vector,
)


def test_dense_to_sparse_vector():
    dense = [0, 1, 0, 2]
    sparse = dense_to_sparse_vector(dense)
    assert sparse == {1: 1, 3: 2}


def test_sparse_to_dense_vector():
    sparse = {1: 1, 3: 2}
    dense = sparse_to_dense_vector(sparse, size=4)
    assert dense == [0, 1, 0, 2]


def test_sparse_to_dense_vector_inferred_size():
    sparse = {1: 1, 3: 2}
    dense = sparse_to_dense_vector(sparse)
    assert dense == [0, 1, 0, 2]


def test_dense_to_sparse_matrix():
    dense = [[0, 1], [2, 0]]
    sparse = dense_to_sparse_matrix(dense)
    assert sparse == {0: {1: 1}, 1: {0: 2}}


def test_dense_to_sparse_matrix_all_defaults():
    # Row 1 is all zeros -> should be skipped in sparse result
    dense = [[0, 1], [0, 0]]
    sparse = dense_to_sparse_matrix(dense)
    assert sparse == {0: {1: 1}}


def test_sparse_to_dense_matrix():
    sparse = {0: {1: 1}, 1: {0: 2}}
    dense = sparse_to_dense_matrix(sparse, shape=(2, 2))
    assert dense == [[0, 1], [2, 0]]


def test_sparse_to_dense_matrix_inferred_shape():
    sparse = {0: {1: 1}, 1: {0: 2}}
    dense = sparse_to_dense_matrix(sparse)
    assert dense == [[0, 1], [2, 0]]


def test_converters_empty():
    assert dense_to_sparse_vector([]) == {}
    assert sparse_to_dense_vector({}) == []
    assert dense_to_sparse_matrix([]) == {}
    assert sparse_to_dense_matrix({}) == []


def test_sparse_to_dense_vector_out_of_bounds():
    # Key 5 is outside size 4 -> Ignored
    sparse = {1: 1, 5: 5}
    dense = sparse_to_dense_vector(sparse, size=4)
    assert dense == [0, 1, 0, 0]


def test_sparse_to_dense_matrix_empty_with_shape():
    # Empty matrix but explicit shape -> Returns zero matrix
    dense = sparse_to_dense_matrix({}, shape=(2, 2))
    assert dense == [[0, 0], [0, 0]]


def test_sparse_to_dense_matrix_empty_rows():
    # Matrix has rows, but some are empty/None
    # {0: {}, 1: {0: 1}}
    sparse = {0: {}, 1: {0: 1}}
    dense = sparse_to_dense_matrix(sparse)
    # Max row 1, max col 0 -> 2x1
    assert dense == [[0], [1]]


def test_sparse_to_dense_matrix_out_of_bounds():
    # Shape 1x1
    # 0: {0: 1} -> In bounds
    # 0: {5: 5} -> Col out of bounds
    # 5: {0: 5} -> Row out of bounds
    sparse = {
        0: {0: 1, 5: 5},
        5: {0: 5}
    }
    dense = sparse_to_dense_matrix(sparse, shape=(1, 1))
    # Only (0,0) fits
    assert dense == [[1]]
