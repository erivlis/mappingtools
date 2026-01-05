# Algebraic Structures in MappingTools

This document provides a theoretical overview of the algebraic structures used in `mappingtools.algebra`. Understanding these concepts helps clarify why certain operations are grouped together and how they generalize across different domains (graphs, logic, probability).

## Hierarchy of Structures (Ordered by Complexity)

### 1. Monoid $(M, \cdot)$
A set $M$ with a single binary operation $\cdot$ that satisfies:
*   **Closure**: If $a, b \in M$, then $a \cdot b \in M$.
*   **Associativity**: $(a \cdot b) \cdot c = a \cdot (b \cdot c)$.
*   **Identity**: There exists $e \in M$ such that $a \cdot e = e \cdot a = a$.

**Example**:
*   Natural numbers under addition $(\mathbb{N}, +)$. Identity is 0.
*   Strings under concatenation. Identity is `""`.

### 2. Group $(G, \cdot)$
A Monoid where every element has an **Inverse**.
*   **Inverse**: For every $a \in G$, there exists $a^{-1}$ such that $a \cdot a^{-1} = e$.

**Example in Library**:
*   **Permutations** (`algebra.group`): The set of bijective mappings forms a group under composition.
    *   Operation: `compose(f, g)`
    *   Inverse: `invert(f)`
    *   Identity: `{k: k}`

### 3. Abelian Group
A Group where the operation is also **Commutative**:
*   $a \cdot b = b \cdot a$.

**Example**: Integers under addition $(\mathbb{Z}, +)$.

### 4. Semiring $(S, \oplus, \otimes)$
A set $S$ with two operations, Addition ($\oplus$) and Multiplication ($\otimes$), satisfying:
*   $(S, \oplus)$ is a Commutative Monoid (Identity $\mathbf{0}$).
*   $(S, \otimes)$ is a Monoid (Identity $\mathbf{1}$).
*   **Distributivity**: Multiplication distributes over Addition.
*   **Annihilation**: $a \otimes \mathbf{0} = \mathbf{0}$.

**Crucially**: Semirings do **not** require additive inverses (subtraction) or multiplicative inverses (division).

**Examples in Library** (`algebra.semiring`):
*   **Standard**: $(\mathbb{R}, +, \times)$. Standard Matrix Multiplication.
*   **Tropical**: $(\mathbb{R} \cup \{\infty\}, \min, +)$. Shortest Path algorithms.
*   **Boolean**: $(\{T, F\}, \lor, \land)$. Reachability / Transitive Closure.
*   **Viterbi**: $([0, 1], \max, \times)$. Most likely path in HMMs.

### 5. Ring $(R, +, \cdot)$
A Semiring that **has additive inverses**.
*   $(R, +)$ is an Abelian Group (Subtraction is defined).

**Example**: Integers $\mathbb{Z}$, Square Matrices $M_n(\mathbb{R})$.

### 6. Field $(F, +, \cdot)$
A Ring where **multiplication has inverses** (for non-zero elements).
*   $(F \setminus \{0\}, \cdot)$ is an Abelian Group (Division is defined).

**Example**: Real Numbers $\mathbb{R}$, Complex Numbers $\mathbb{C}$.

### 7. Algebra (over a Field)
A Vector Space equipped with a bilinear product.
*   Elements can be added and scaled (Vector Space).
*   Elements can be multiplied (Ring-like).

**Example**: The set of $N \times N$ matrices forms an Algebra.

### 8. Ideal
A subset $I$ of a Ring $R$ that absorbs multiplication.
*   If $x \in I$ and $r \in R$, then $r \cdot x \in I$.
*   Used to define Quotient Rings (e.g., Modular Arithmetic).

### 9. Clifford Algebra (Geometric Algebra)
An associative algebra equipped with a quadratic form, unifying scalars, vectors, and higher-order blades (bivectors, trivectors).
*   **Geometric Product**: $ab = a \cdot b + a \wedge b$.
*   Generalizes Complex Numbers and Quaternions.
*   Used for rotations and physics in any dimension.

---

## Discrete Exterior Calculus (DEC)

The `algebra.analysis` module implements concepts from DEC on graphs.

| Concept | Mathematical Object | Library Type | Example |
| :--- | :--- | :--- | :--- |
| **0-form** | Scalar Field (on nodes) | `SparseVector` | Temperature at each city |
| **1-form** | Vector Field (on edges) | `SparseMatrix` | Traffic flow between cities |
| **Gradient ($d_0$)** | $d: \Omega^0 \to \Omega^1$ | `gradient()` | Difference in temp between cities |
| **Divergence ($d_0^*$)** | $d^*: \Omega^1 \to \Omega^0$ | `divergence()` | Net traffic flow out of a city |
| **Laplacian ($\Delta$)** | $\Delta = d^* d$ | `laplacian()` | Heat diffusion rate |

**Note on Curl**:
The Curl operator ($d_1$) maps 1-forms (edges) to 2-forms (faces). Since `mappingtools` operates on Graphs (nodes and edges only), there are no 2-forms (triangles/faces), so **Curl is undefined** (or trivially zero). To support Curl, the library would need to support Simplicial Complexes.

---

## Why Semirings?

`mappingtools` focuses heavily on **Semirings** because many discrete structures (graphs, automata, logic) do not support subtraction or division.

*   **Shortest Path**: You cannot "un-take" a minimum. $a \oplus b = \min(a, b)$. If $a=5, b=3$, result is 3. You cannot recover 5 from 3.
*   **Reachability**: $T \lor F = T$. You cannot subtract $F$ to get $T$.

By abstracting matrix multiplication to use Semiring operations, we allow the same `matrix.dot` and `matrix.power` functions to solve:
1.  **Physics**: Quantum Mechanics (Standard Algebra).
2.  **Optimization**: Shortest Path (Tropical Algebra).
3.  **Logic**: Connectivity (Boolean Algebra).
4.  **Inference**: Viterbi Decoding (Max-Product Algebra).
5.  **Linguistics**: Regular Expressions (String Algebra).

## Why Not Clifford Algebra?

While Clifford Algebra is powerful for geometry (rotations, physics), it is **not implemented** in `mappingtools` because:
1.  **Density**: Geometric products often mix all components (e.g., rotating a vector usually makes it dense). This conflicts with the library's sparse-first philosophy.
2.  **Complexity**: Implementing a full multivector system requires significant machinery (grade tracking, metric tensors) that is out of scope for a general-purpose mapping library.
3.  **Alternatives**: Specialized libraries like `clifford` or `sympy.diffgeom` handle this domain better.
