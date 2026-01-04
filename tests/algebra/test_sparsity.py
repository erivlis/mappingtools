from mappingtools.algebra.sparsity import density, is_sparse, sparsity


def test_density_vector():
    # 2 items, capacity 10 -> 0.2
    obj = {1: 1, 5: 1}
    assert density(obj, capacity=10) == 0.2

    # Capacity None -> 1.0 (if not empty)
    assert density(obj) == 1.0
    assert density({}) == 0.0


def test_density_matrix():
    # 2x2 matrix with 2 elements
    # {0: {0: 1}, 1: {1: 1}}
    # Total elements = 2. Capacity = 4. Density = 0.5.
    # Old behavior (len) would be 2/4 = 0.5 (coincidentally correct).
    # Let's try 2x2 with 3 elements.
    # {0: {0: 1, 1: 1}, 1: {0: 1}}
    # Total = 3. Capacity = 4. Density = 0.75.
    # Old behavior: len=2. 2/4 = 0.5. Incorrect.

    obj = {0: {0: 1, 1: 1}, 1: {0: 1}}
    assert density(obj, capacity=4) == 0.75


def test_sparsity():
    # 2 items, capacity 10 -> density 0.2 -> sparsity 0.8
    obj = {1: 1, 5: 1}
    assert sparsity(obj, capacity=10) == 0.8


def test_is_sparse():
    # 2/10 = 0.2 density -> 0.8 sparsity. > 0.5 -> True
    obj = {1: 1, 5: 1}
    assert is_sparse(obj, capacity=10) is True

    # 8/10 = 0.8 density -> 0.2 sparsity. < 0.5 -> False
    # Dense vector
    dense_obj = dict.fromkeys(range(8), 1)
    assert is_sparse(dense_obj, capacity=10) is False
