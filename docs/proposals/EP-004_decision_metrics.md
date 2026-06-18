# EP-004: Decision Metrics for the `combine()` Operator

**Status:** Implemented  
**Author:** Antigravity  
**Created:** 2026-06-17

## Abstract

This proposal introduces the **Decision Metrics** feature via the `combine_with_metrics()` operator in the
`mappingtools.operators` module. By passing a list of metrics/callables to the `decision_metrics` parameter, users can
generate one or more
metadata companion trees (e.g., provenance trees, conflict audits, change logs) in a single recursive traversal. The
decision metric trees share the exact structure (shape) of the combined output tree, with their leaves mapped by
user-provided or built-in callback functions.

## Motivation

In nested data integration, workflow orchestration, and config merging, combining two trees is often only half of the
problem. Developers frequently need to extract side-channel metadata about **how** the combination occurred:

- **Provenance**: Which source (`tree1` or `tree2`) contributed each resolved value?
- **Auditing**: Where did collisions occur, what were the conflicting values, and how did the resolver reconcile them?
- **Change Tracking (Diffing)**: Which values were added, updated, or left unchanged relative to the original tree?

Currently, mapping tools do not support extracting this side-channel metadata in a single pass. Developers must resort
to running post-combination comparison passes, which duplicate traversal overhead, double CPU cycles, and are prone to
logic mismatches.

By introducing **Decision Metrics**, we expose a generalized, high-performance side-channel builder directly inside the
recursive combination loop. Furthermore, by supporting a dictionary mapping of metrics, we can generate multiple
metadata trees simultaneously in a single traversal, returning a stable structure.

## Proposed Design

### 1. API Signature

Instead of modifying the legacy `combine()` operator, we implement a dedicated `combine_with_metrics()` function
in [operators.py](file:///C:/dev/erivlis/mappingtools/src/mappingtools/operators.py):

```python
def combine_with_metrics(
        tree1: Tree[T] | Missing = MISSING,
        tree2: Tree[T] | Missing = MISSING,
        op: Combine | ResolverType = Resolver.LAST,
        decision_metrics: list[DecisionMetric | Callable[[Any, Any, Any], Any]] | None,
) -> tuple[Tree[T] | Any, dict[str, Tree[Any] | Any]]:
```

- **`decision_metrics`**: A list of `DecisionMetric` enums or custom callable metrics (or `None`).
- **Return Value**: A 2-tuple containing `(combined_tree, metrics_dict)`, where `metrics_dict` maps the string name of
  each decision metric (e.g., `DecisionMetric.PROVENANCE.name` which is `"PROVENANCE"`, or the name of a custom
  callable) to its corresponding metric tree.

### 2. The Decision Metric Callback Interface

A decision metric is defined by a simple callback function that evaluates conflict and single-sided resolution leaves:

```python
def metric_callback(t1: Any, t2: Any, resolved: Any) -> Any:
    ...
```

- `t1`: The value from `tree1` at the current leaf path (or `MISSING`).
- `t2`: The value from `tree2` at the current leaf path (or `MISSING`).
- `resolved`: The resolved value returned by the conflict operator `op(t1, t2)`.

### 3. Built-in Decision Metric Strategies

We encapsulate common strategies inside a new `DecisionMetric` Enum:

```python
class DecisionMetric(Enum):
    PROVENANCE = member(_provenance_metric)
    AUDIT = member(_audit_metric)
    CHANGELOG = member(_change_metric)
```

#### A. `DecisionMetric.PROVENANCE`

Shorthand for tracking which input source selected each leaf:

- If `t1 is MISSING` $\rightarrow$ `1` (sourced from `t2`)
- If `t2 is MISSING` $\rightarrow$ `0` (sourced from `t1`)
- If `resolved is t1` or `resolved == t1` $\rightarrow$ `0`
- If `resolved is t2` or `resolved == t2` $\rightarrow$ `1`
- Otherwise $\rightarrow$ `None` (non-selective/aggregative combination like `SUM`)

*Behavior with Special Resolvers*:

* `Resolver.VOID` (returns `MISSING`): The key is dropped from both the combined tree and the metric tree (since it's
  omitted).
* `Resolver.NULL` (returns `None`): Resolves to `None` provenance (or `0`/`1` if one of the inputs was already `None`).

#### B. `DecisionMetric.AUDIT`

Generates a detailed conflict log mapping:

- If `t1 is MISSING` or `t2 is MISSING` $\rightarrow$ `"clean"`
- Otherwise $\rightarrow$ `f"conflict: {t1} vs {t2} -> {resolved}"`

#### C. `DecisionMetric.CHANGELOG`

Tracks mutation status relative to the base tree (`tree1`):

- If `t1 is MISSING` $\rightarrow$ `"added"`
- If `t2 is MISSING` $\rightarrow$ `"unchanged"`
- Otherwise $\rightarrow$ `"updated"` if `resolved != t1` else `"unchanged"`

---

## Detailed Walk-Through / Multi-Metric Output

Given:

```python
tree1 = {"a": 10, "b": 100}
tree2 = {"a": 20, "c": 200}
```

Calling:

```python
combined, metrics = combine_with_metrics(
    tree1, tree2, NumericResolver.SUM,
    [DecisionMetric.PROVENANCE, DecisionMetric.AUDIT]
)
```

Yields:

* `combined`: `{"a": 30, "b": 100, "c": 200}`
* `metrics["PROVENANCE"]`: `{"a": None, "b": 0, "c": 1}`
* `metrics["AUDIT"]`: `{"a": "conflict: 10 vs 20 -> 30", "b": "clean", "c": "clean"}`

---

## Application-Level Use Cases (Chaining and Vectorization) (Post-Implementation)

> [!NOTE]
> This section outlines advanced use cases (including multi-tree reductions, sequential history logs, and vectorized
> operations). These are downstream application-level recipes to be built *after* the core binary decision metrics API
> is
> implemented in the library.

In large-scale operations (such as folding/reducing a sequence of $N$ trees), users can chain binary combines to
construct complex multi-source decision metric outputs.

### 1. Multi-Tree Source Index Tracking (Provenance)

If we have $N$ trees and want to map each leaf to its originating tree index ($0$ to $N-1$), we can perform a standard
`reduce` pass. At each step $i$, we use the binary decision metric output to blend the previous accumulator's metadata
with the new source index $i$:

```python
def blend_reducer(acc_prov_val: Any, binary_prov_val: Any) -> Any:
    if binary_prov_val == 0:
        return acc_prov_val  # Sourced from accumulator
    if binary_prov_val == 1:
        return i  # Sourced from the new tree_i
    return None  # Composite/aggregative conflict
```

By combining the accumulator's provenance tree with the step's binary provenance tree using this blend resolver, the
source indices correctly bubble up through the fold.

### 2. Multi-Tree Audit Trail Concatenation (Audit Log)

When auditing a pipeline of combinations, conflicts can occur at multiple stages for a single leaf. We can use the
reduction loop to accumulate a comprehensive, step-by-step history log:

```python
def audit_blend_resolver(acc_audit: str, binary_audit: str) -> str:
    if binary_audit == "clean":
        return acc_audit
    if acc_audit == "clean":
        return binary_audit
    return f"{acc_audit} -> {binary_audit}"
```

Using this resolver to combine the accumulator's audit tree with the new step's binary audit tree yields a final audit
tree containing the complete history of conflicts for each path (e.g.,
`"conflict: 10 vs 20 -> 30 -> conflict: 30 vs 35 -> 35"`).

### 3. Multi-Tree Net Mutation Tracking (Changelog)

When folding a sequence of trees, we can determine the net change of the final tree relative to the very first tree (
`tree_0`) by blending mutation state transitions as a finite state machine:

| Accumulated State (`acc`) | Step State (`step`) | Net State   |
|:--------------------------|:--------------------|:------------|
| `added`                   | `updated`           | `added`     |
| `added`                   | `unchanged`         | `added`     |
| `updated`                 | `updated`           | `updated`   |
| `updated`                 | `unchanged`         | `updated`   |
| `unchanged`               | `updated`           | `updated`   |
| `unchanged`               | `unchanged`         | `unchanged` |

The blend resolver encodes this transition matrix:

```python
def changelog_blend_resolver(acc: str, step: str) -> str:
    if acc == "added":
        return "added"  # Net addition relative to tree_0 remains added
    if step == "updated":
        return "updated"
    return acc
```

This guarantees that the final changelog tree reports correct mutation status relative to the root base tree (`tree_0`),
regardless of intermediate modifications.

### 4. Flat Vectorization Optimization (e.g., via NumPy)

For massive tree structures, recursively traversing the tree shape to blend metadata at every reduce step is
computationally expensive. Because decision metric trees match the structure of the combined output tree, we can
optimize the reduction by flattening the trees into 1D vectors and using vectorized hardware instructions:

1. **Flattening**: Flatten the structures to flat dictionaries of `{path_tuple: value}` using `flatten()`.
2. **Alignment**: Align the paths to form a single coordinate index.
3. **Vectorized Blend**: Represent the metadata as 1D arrays of floats (using `np.nan` for missing/composite entries).
   We can execute the blend operation in $O(P)$ time (where $P$ is the number of leaves) using a conditional
   multiplexer (`np.where`):

   $$\mathbf{p}'_{acc} = \text{select}(\mathbf{p}_{binary} == 0, \mathbf{p}_{acc}, \text{select}(\mathbf{p}_{binary} == 1, i, \text{nan}))$$

   In Python:
   ```python
   P_acc_new = np.where(P_binary == 0.0, P_acc, np.where(P_binary == 1.0, float(i), np.nan))
   ```

#### Why `np.where` instead of Algebraic Hadamard Products?

In pure algebraic formulation, one might attempt to express this update as a Hadamard product:
$$\mathbf{p}'_{acc} = (\mathbf{1} - \mathbf{p}_{binary}) \odot \mathbf{p}_{acc} + i \cdot \mathbf{p}_{binary}$$
However, in standard IEEE 754 float arithmetic, if a leaf was previously
aggregative ($\mathbf{p}_{acc}[k] = \text{nan}$) but is overwritten by tree $i$ ($\mathbf{p}_{binary}[k] = 1$), the
algebraic product evaluates:
$$(1-1) \cdot \text{nan} + i = 0 \cdot \text{nan} + i = \text{nan} + i = \text{nan}$$
The conditional `np.where` multiplexer bypasses this IEEE 754 propagation rule, ensuring that overwrites correctly
restore the source index `i` even when overwriting a previously composite (`nan`) value.

---

## Backwards Compatibility

Because we implemented a dedicated `combine_with_metrics` function, the existing `combine` operator remains completely
untouched, ensuring zero regressions.

---

## Testing Strategy

Minimum test matrix:

1. **Single Metric**: Verify `combine_with_metrics(t1, t2, op, DecisionMetric.PROVENANCE)` returns
   `(combined, {"PROVENANCE": provenance_tree})`.
2. **Multiple Metrics**: Verify passing multiple metrics as a list
   `combine_with_metrics(t1, t2, op, [DecisionMetric.PROVENANCE, DecisionMetric.AUDIT])` returns
   `(combined, {"PROVENANCE": ..., "AUDIT": ...})`.
3. **Custom Callback**: Verify passing a lambda function creates the correct metric tree under the `"<lambda>"` key.
4. **Structural Preservation**: Verify that single-sided missing structures (nested dicts, lists) correctly replicate
   shapes and invoke the callbacks.
5. **Special Cases**:
    - `Resolver.VOID`: Keys are dropped consistently from the output and all metric trees.
    - `Resolver.NULL`: Yields appropriate results through callbacks.

---

## Security and Reliability Considerations

* **Traversals and Allocation**: Evaluating multiple metrics in a single pass minimizes traversal CPU overhead. Memory
  usage is proportional to the number of requested metric trees.
* **Side-Effects**: Callback functions must be pure and free of side-effects.

---

## Naming Alternatives Considered

While this proposal uses the term **Decision Metrics**, several alternative metaphors have been explored for naming the
parameter and its output trees:

| Metaphor / Term                         | Pros                                                                                                                                                                              | Cons                                                                                                             |
|:----------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------|
| **`decision_metrics`**                  | Focuses precisely on tracking the conflict resolution decisions made at each leaf path. Prevents any ambiguity.                                                                   | Slightly longer name.                                                                                            |
| **`sidecar`** (`sidecar=...`)           | Familiar software pattern; describes an attached helper component running alongside the main process.                                                                             | Highly associated with container/systems engineering; might feel slightly mechanical for a pure data library.    |
| **`prism`** (`prism=...`)               | Beautiful optical metaphor. A prism refracts a single combined merge operation into multiple spectral bands of metadata (provenance, audit, diff). Fits the multi-pass perfectly. | Slightly less self-evident for developers seeking standard/simple provenance tracking.                           |
| **`companion`** (`companion=...`)       | Friendly, natural-language term describing a tree walking hand-in-hand with the main output.                                                                                      | Does not explicitly convey its role as a metadata generator.                                                     |
| **`probe`** / **`telemetry`**           | Highly descriptive of the observability and logging aspect of the feature.                                                                                                        | Implies passive reading/logging, whereas these are active structures mirroring the shape of the resolved object. |
| **`echo`** (`echo=...`)                 | Acoustic metaphor representing reflection; mirrors the structural shape of the combined tree while carrying a modified signal.                                                    | None significant.                                                                                                |
| **`witness`** (`witness=...`)           | Derived from logic and type theory, where a "witness" holds proof values of computation paths. Highly precise.                                                                    | Requires familiarity with formal logic/theory concepts.                                                          |
| **`gloss`** (`gloss=...`)               | From linguistics and ancient manuscripts; a margin notation explaining origin/annotations of a text at exact coordinates. Highly poetic and visually accurate.                    | Unorthodox; may feel unfamiliar to mainstream software developers.                                               |
| **`overlay`** (`overlay=...`)           | From cartography/GIS; transparent sheets overlaid onto a map to show metadata layers without changing the base topology.                                                          | Typically implies visual representation rather than a data object.                                               |
| **`receipt`** (`receipt=...`)           | Clear transactional metaphor, showing what was "paid" (or which value won) at each position.                                                                                      | Focuses on value exchange; less fitting for audit or change-log tracking.                                        |
| **`genealogy`** / **`lineage`**         | Focuses directly on the ancestry and source parentage of each leaf.                                                                                                               | Specific to provenance; does not naturally extend to audit logging or change tracking.                           |
| **`trace`** / **`track`** / **`trail`** | Directly indicates path-marking of conflict resolutions.                                                                                                                          | Often implies a flat sequence or timeline log rather than a mirror tree.                                         |
| **`chronicle`** (`chronicle=...`)       | Archival metaphor representing an ordered history of steps and resolutions.                                                                                                       | Implies chronological ordering, which is less relevant for commutative/associative binary combines.              |

---

## Rejected Alternatives

1. **Explicit wrapper metadata (`{"__value__": X, "__source__": Y}`)**:
    - Rejected because it changes the data types of the output tree nodes, breaking downstream consumers that expect the
      unmodified schema.
2. **Explicit resolver inspection**:
    - Rather than checking whether the resolver is `Resolver.FIRST` or `Resolver.LAST` statically, the dynamic
      identity/equality check was chosen. This allows seamless out-of-the-box support for any custom callables (e.g.,
      lambda functions) without requiring changes to the library's registry.
3. **Integrating Decision Metrics with the `visitors` Namespace**:
    - *Alternative considered*: Integrating metric generation into the visitor classes (`RecursiveDoubleTreeVisitor` and
      `IterativeDoubleTreeVisitor`) to ensure safe recursive fallback and traversal mode registries.
    - *Reason for rejection*: The `mappingtools.visitors` namespace is currently designated as **experimental** and
      subject to change. The primary combination operators in `operators.py` must remain lightweight, fast,
      self-contained, and production-grade. Decoupling decision metrics from the visitors namespace ensures that
      production-ready features do not inherit experimental dependencies.

---

## Divergences from Proposal

During implementation, the design was refined to solve specific type safety, API symmetry, and framework parity issues:

1. **API Signature (`list` parameter vs. Varargs `*args`)**:
    - *Proposal*: Accept positional varargs `*decision_metrics`.
    - *Implementation*: Accept a list `decision_metrics: list[DecisionMetric | Callable] | None = None`. This avoids
      signature ambiguity, enforces consistent signature patterns in the library, and prevents type mismatches when
      additional options might be appended in the future.
2. **List Sentinel (`MISSING`) Parity**:
    - *Proposal*: Filter/prune or rewrite `MISSING` sentinels inside lists when `Resolver.VOID` removes elements.
    - *Implementation*: Keep `MISSING` inside list outputs to match the behavior of standard `combine()`. This preserves
      exact index offsets across accumulator, binary, and target output trees, allowing consistent traversal and
      reduction.
3. **No Traversal Registry Integration**:
    - As proposed and confirmed, `combine` operates on dictionaries and lists natively without utilizing
      `TraversalModeRegistry` to preserve performance and avoid experimental dependencies.
4. **API Unification (`combine_with_metrics` merged into `combine`)**:
    - *Proposal*: Introduce a separate function `combine_with_metrics`.
    - *Implementation*: Merged `combine_with_metrics` directly into the standard `combine` operator to avoid duplicate traversal engines and prevent code/implementation drift. By default, `combine` returns only the resolved tree. If `decision_metrics` (a list of metrics) is passed, Python `@overload` signatures ensure type-safety, and `combine` returns a 2-tuple of `(combined_tree, metrics_dict)`.
