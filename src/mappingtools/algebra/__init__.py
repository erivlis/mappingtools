"""
The `mappingtools.algebra` namespace provides a comprehensive suite of mathematical operations
optimized for sparse, dictionary-based data structures.

It treats Python's native `dict` (and `Mapping`) as a first-class mathematical object,
enabling Linear Algebra, Set Theory, Graph Theory, and Probability operations directly on
sparse data without conversion to dense arrays.

Comparison with Other Libraries
-------------------------------

1. **`scipy.sparse`**:
   - **Domain**: Numerical Linear Algebra.
   - **Pros**: Industry standard, extremely fast (C/Fortran backend).
   - **Cons**: Keys must be integers; requires conversion from dicts; heavy dependency.
   - **Use Case**: Large-scale numerical simulations (e.g., Finite Element Method).

2. **`numpy`**:
   - **Domain**: Dense Numerical Arrays.
   - **Pros**: Universal standard for dense data.
   - **Cons**: Inefficient for sparse data (O(N^2) memory); integer indices only.
   - **Use Case**: Image processing, dense tensors.

3. **`pandas`**:
   - **Domain**: Tabular Data Analysis.
   - **Pros**: Excellent for time-series and labeled data.
   - **Cons**: Not optimized for general mathematical algebra (e.g., matrix multiplication).
   - **Use Case**: Data cleaning, ETL, statistical analysis.

4. **`mappingtools.algebra` (This Library)**:
   - **Domain**: Symbolic/Sparse Algebra on Mappings.
   - **Pros**:
     - **Symbolic Keys**: Works with `str`, `tuple`, or any hashable object (e.g., graphs with string nodes).
     - **Zero-Dependency**: Pure Python.
     - **Functional**: Composable API (`combine`, `compose`).
   - **Cons**: Slower than C-based libraries for massive numerical computations.
   - **Use Case**: NLP (word vectors), Knowledge Graphs, Item-Item similarity, small-to-medium sparse matrices.

Definitions & Criteria
----------------------

*   **Sparse**: Data where the number of non-zero elements ($k$) is significantly smaller than the total capacity ($N$).
    *   *Criterion*: Density ($k/N$) < 0.05 (5%).
*   **Dense**: Data where most elements are non-zero.
    *   *Criterion*: Density > 0.5 (50%).
*   **Lightweight**: Minimal memory overhead and startup time.
    *   *Criterion*: Import time < 10ms; Memory overhead < 1KB per object (beyond data).
*   **Symbolic**: Keys represent semantic entities (e.g., "User_123", "Product_X") rather than contiguous memory
    offsets (0, 1, 2).

Modules
-------

*   **`matrix`**: Linear Algebra (Core & Academic).
*   **`lattice`**: Set/Fuzzy Logic (Union, Intersection).
*   **`analysis`**: Vector Calculus on Graphs (Gradient, Laplacian).
*   **`probability`**: Bayesian/Markov Inference.
*   **`transforms`**: Signal Processing (DFT, Convolution).
*   **`automata`**: Finite State Machines.
*   **`group`**: Permutations.
*   **`sparsity`**: Metrics and checks.
*   **`semiring`**: Generalized algebra (Tropical, Boolean, String).
*   **`typing`**: Type aliases for sparse/dense structures.
"""

from mappingtools.algebra.analysis import (
    divergence,
    gaussian_kernel,
    gradient,
    laplacian,
    ollivier_ricci_curvature,
)
from mappingtools.algebra.automata import (
    dfa_step,
    nfa_step,
    simulate_dfa,
    simulate_nfa,
)
from mappingtools.algebra.converters import (
    dense_to_sparse_matrix,
    dense_to_sparse_vector,
    sparse_to_dense_matrix,
    sparse_to_dense_vector,
)
from mappingtools.algebra.group import compose, invert, signature
from mappingtools.algebra.lattice import (
    average,
    combine,
    difference,
    exclude,
    exclusive,
    geometric_mean,
    harmonic_mean,
    join,
    mask,
    meet,
    product,
    ratio,
    symmetric_difference,
)
from mappingtools.algebra.matrix import (
    add,
    adjoint,
    cofactor,
    determinant,
    dot,
    eigen_centrality,
    inner,
    inverse,
    kronecker_delta,
    mat_vec,
    power,
    trace,
    transpose,
    vec_mat,
)
from mappingtools.algebra.probability import (
    bayes_update,
    cross_entropy,
    entropy,
    kl_divergence,
    marginalize,
    markov_steady_state,
    markov_step,
    mutual_information,
    normalize,
)
from mappingtools.algebra.semiring import (
    BooleanSemiring,
    BottleneckSemiring,
    LogSemiring,
    ReliabilitySemiring,
    Semiring,
    StandardSemiring,
    StringSemiring,
    TropicalSemiring,
    ViterbiSemiring,
)
from mappingtools.algebra.sparsity import (
    balance,
    deepness,
    density,
    is_sparse,
    sparsity,
    wideness,
)
from mappingtools.algebra.transforms import (
    box_counting_dimension,
    convolve,
    dft,
    hilbert,
    idft,
    lorentz_boost,
    z_transform,
)
from mappingtools.algebra.typing import (
    DenseMatrix,
    DenseVector,
    SparseMatrix,
    SparseTensor,
    SparseVector,
)

__all__ = [
    'BooleanSemiring',
    'BottleneckSemiring',
    'DenseMatrix',
    'DenseVector',
    'LogSemiring',
    'ReliabilitySemiring',
    'Semiring',
    'SparseMatrix',
    'SparseTensor',
    'SparseVector',
    'StandardSemiring',
    'StringSemiring',
    'TropicalSemiring',
    'ViterbiSemiring',
    'add',
    'adjoint',
    'average',
    'balance',
    'bayes_update',
    'box_counting_dimension',
    'cofactor',
    'combine',
    'compose',
    'convolve',
    'cross_entropy',
    'deepness',
    'dense_to_sparse_matrix',
    'dense_to_sparse_vector',
    'density',
    'determinant',
    'dfa_step',
    'dft',
    'difference',
    'divergence',
    'dot',
    'eigen_centrality',
    'entropy',
    'exclude',
    'exclusive',
    'gaussian_kernel',
    'geometric_mean',
    'gradient',
    'harmonic_mean',
    'hilbert',
    'idft',
    'inner',
    'inverse',
    'invert',
    'is_sparse',
    'join',
    'kl_divergence',
    'kronecker_delta',
    'laplacian',
    'lorentz_boost',
    'marginalize',
    'markov_steady_state',
    'markov_step',
    'mask',
    'mat_vec',
    'meet',
    'mutual_information',
    'nfa_step',
    'normalize',
    'ollivier_ricci_curvature',
    'power',
    'product',
    'ratio',
    'signature',
    'simulate_dfa',
    'simulate_nfa',
    'sparse_to_dense_matrix',
    'sparse_to_dense_vector',
    'sparsity',
    'symmetric_difference',
    'trace',
    'transpose',
    'vec_mat',
    'wideness',
    'z_transform',
]
