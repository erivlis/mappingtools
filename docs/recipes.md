---
icon: lucide/chef-hat
---

# Recipes

The `mappingtools` primitives (Operators, Collectors, Lenses, Transformers) are designed to be highly composable.

Below are real-world recipes demonstrating how to combine these mathematical engines to solve complex IT, data, and
architectural problems.

You can find the executable code for all of these recipes in the
[`recipes/`](https://github.com/erivlis/mappingtools/tree/main/recipes) folder on GitHub.

!!! note "Organization"

    Recipes are grouped by domain to help you find solutions relevant to your work. Within each domain, the recipes are ordered progressively—starting from foundational concepts and building up to more advanced architectural patterns.

---

### Data Engineering & ETL

- **[Reshaping Tabular Data - Recipe #2](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_02_etl_reshape.py):**

  Convert a flat stream of dicts (like a CSV or DB cursor) into a nested dictionary using `reshape` and `Aggregation`.

- **[Quick Serialization - Recipe #6](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_06_serialization_pipeline.py):**

  Convert `dataclasses`, `datetime` objects, and custom Python structures directly into JSON-serializable dictionaries
  using `strictify`.

- **[Dynamic Object Minification - Recipe #14](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_14_auto_minification.py):**

  Combine `AutoMapper` and `strictify` to recursively rewrite verbose JSON string keys into sequentially generated,
  ultra-compact shortcodes to save network bandwidth.

- **[Pivot Tensors - Recipe #15](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_15_data_pivot_tensor.py):**

  Combine `reshape` and `Aggregation.ALL` to group a flat stream of transactional records into an N-dimensional
  analytical tensor without losing any underlying individual records.

### Configuration & State Management

- **[Configuration Management - Recipe #3](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_03_config_management.py):**

  Load multiple configuration layers and fold them into a single state using `functools.reduce` and `merge`.

- **[The Inverted Configuration Index - Recipe #8](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_08_inverted_config_index.py):**

  Combine `flatten` and `MappingCollector` (with `Aggregation.ALL`) to instantly find duplicated values (like IPs or
  secrets) scattered across deeply nested configuration files.

- **[Cartesian Grid Search - Recipe #9](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_09_hyperparameter_grid_search.py):**

  Combine `itertools.product` and `merge` to instantly generate an N-dimensional matrix of fully-formed configurations
  for hyperparameter tuning or parameterized testing.

- **[Feature Flag Rollout State - Recipe #19](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_19_feature_flag_rollout.py):**

  Combine native Python comprehensions and `distinct` to isolate feature flags across an N-tier configuration cascade (
  Global -> Region -> User) and detect conflicting state overrides.

### Security, Auditing & Governance

- **[Deep JSON Diffing - Recipe #4](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_04_deep_json_diffing.py):**

  Find additions, removals, and changes between two complex JSON payloads by collapsing them with `flatten`.

- **[Cryptographic Redaction - Recipe #10](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_10_cryptographic_redaction.py):**

  Combine `flatten`, `hashlib`, and `Lens` optics to locate and cryptographically mask sensitive secrets (PII, Tokens)
  deep within an N-dimensional JSON payload before logging.

- **[Data Governance & RBAC - Recipe #17](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_17_data_governance_masking.py):**

  Combine native dictionary comprehensions, `rename`, and `Lens` optics to strip internal metadata, reshape schemas, and
  cryptographically mask sensitive fields before sending a database record to an external API client.

### Architecture & Microservices

- **[Deep JSON Patching - Recipe #1](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_01_deep_json_patching.py):**

  Immutably update deep nested sections of a JSON payload using `Lens` and `merge`.

- **[Microservice Dependency Graph - Recipe #11](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_11_microservice_dependency_graph.py):**

  Combine the `inverse` operator with the `AutoMapper` collector to compute the blast radius of an infrastructure outage
  and generate a minified Mermaid.js node visualization.

- **[Schema-Guided Payload Correction - Recipe #12](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_12_schema_guided_correction.py):**

  Combine `flatten`, `Lens`, and `merge` to build an auto-correction pipeline that casts types, migrates deprecated
  keys, and applies structural defaults to incoming JSON payloads.

- **[Broadcasting Method Calls - Recipe #13](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_13_dictifier_broadcasting.py):**

  Use the `Dictifier` wrapper to instantly proxy method calls and attribute accesses across a vast fleet of identically
  typed objects simultaneously.

- **[Bi-directional State Sync - Recipe #18](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_18_bidirectional_state_sync.py):**

  Use `inverse` and `rekey` to instantly build a two-way synchronization bridge (snake_case <-> camelCase) between a
  Python backend and a React/Vue frontend payload.

- **[JSON Schema Derivation - Recipe #26](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_26_json_schema_derivation.py):**

  Combine `flatten`, `Lens`, `patch`, and `merge` to derive a public API contract from a canonical internal JSON Schema
  by pruning internal/read-only fields and overlaying partner-specific constraints.

- **[JSON Schema Review Envelopes - Recipe #27](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_27_json_schema_review_envelopes.py):**

  Combine `flatten`, `Lens`, `patch`, and `merge` to preserve a JSON Schema's object shape while replacing each
  primitive field, scalar array item, direct `$ref`, and direct union/composition schema (`oneOf`, `anyOf`, `allOf`)
  with a `oneOf` wrapper representing either an override value or an approval decision. If the root schema has a `$id`,
  the recipe also appends a suffix so the derived schema gets a distinct identity.

- **[Conflict Resolution Strategies - Recipe #28](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_28_conflict_resolution.py):**

  Use the `lift` operator alongside the `Resolver` and `NumericResolver` enums (or a custom callable)
  to deeply merge two trees while precisely controlling how collisions at the leaf level are resolved (e.g., `FAIL`, `FIRST`, `SUM`).

### Telemetry & Analytics

- **[Profiling Config Access - Recipe #5](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_05_slow_config_profiling.py):**

  Wrap generic configurations in `MeteredDict` to track "hot" read/write paths and identify dead code.

- **[Multi-Dimensional Counting - Recipe #7](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_07_filesystem_categorization.py):**

  Traverse a filesystem and simultaneously categorize files by extension, size bucket, and hidden status using a single
  `CategoryCounter`.

- **[Time-Series Smoothing - Recipe #16](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_16_time_series_ema.py):**

  Use `MappingCollector` and `Aggregation.EMA` to automatically calculate an Exponential Moving Average across a noisy
  stream of live data ticks grouped by their sensor source.

- **[Telemetry Aggregation - Recipe #20](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_20_telemetry_aggregation.py):**

  Combine `MeteredDict`, `Dictifier`, and `reduce(merge, ...)` to effortlessly broadcast metric collection across a
  distributed fleet of isolated workers and instantly fold their results into a single global telemetry map.

- **[Real-Time Anomaly Detection - Recipe #24](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_24_anomaly_detection.py):**

  Use `MappingCollector` with `Aggregation.EMA` to maintain a memory-efficient baseline of a noisy time-series and
  instantly flag incoming data points that deviate beyond a set threshold.

### Algorithmic Explorations

- **[Algorithmic Music Transposition - Recipe #21](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_21_algorithmic_music_transposition.py):**

  Combine `reshape` and `Lens` optics to convert a flat stream of MIDI events into a nested musical score, and immutably
  transpose a specific instrument track without mutating the original composition.

- **[Image Bounding Box Filter - Recipe #22](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_22_image_bounding_box_filter.py):**

  Combine `reshape` and `Lens` optics to convert a flat 1D stream of RGB pixels into a 2D spatial tensor (Row -> Col ->
  RGB) and apply a Grayscale filter specifically to a central bounding box.

- **[Graph Theory Connectivity - Recipe #23](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_23_graph_theory_connectivity.py):**

  Use `flatten` to expand a nested graph traversal and extract all unique nodes reachable within a specific sub-graph generated from an Adjacency List.

- **[Markov Chain Text Generation - Recipe #25](https://github.com/erivlis/mappingtools/blob/main/recipes/recipe_25_markov_chain_text_generator.py):**

  Combine `MappingCollector` and `Aggregation.COUNT` to instantly build a Markov Transition Matrix (Word -> Counter(Next
  Words)) from a training corpus, and use it to hallucinate new sentences.