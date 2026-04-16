---
icon: lucide/chef-hat
---

# Recipes

The `mappingtools` primitives (Operators, Collectors, Lenses, Transformers) are designed to be highly composable.
Below are real-world recipes demonstrating how to combine these mathematical engines to solve complex IT, data, and
architectural problems.

You can find the executable code for all of these recipes in the [
`recipes/`](https://github.com/erivlis/mappingtools/tree/main/recipes) folder on GitHub.

---

### Data Engineering & ETL

* **[Reshaping Tabular Data](https://github.com/erivlis/mappingtools/blob/main/recipes/02_etl_reshape.py):**
  Convert a flat stream of dicts (like a CSV or DB cursor) into a nested dictionary using `reshape` and `Aggregation`.
* **[Quick Serialization](https://github.com/erivlis/mappingtools/blob/main/recipes/06_serialization_pipeline.py):**
  Convert `dataclasses`, `datetime` objects, and custom Python structures directly into JSON-serializable dictionaries
  using `strictify`.
* **[Pivot Tensors](https://github.com/erivlis/mappingtools/blob/main/recipes/15_data_pivot_tensor.py):**
  Combine `reshape` and `Aggregation.ALL` to group a flat stream of transactional records into an N-dimensional
  analytical tensor without losing any underlying individual records.
* **[Dynamic Object Minification](https://github.com/erivlis/mappingtools/blob/main/recipes/14_auto_minification.py):**
  Combine `AutoMapper` and `strictify` to recursively rewrite verbose JSON string keys into sequentially generated,
  ultra-compact shortcodes to save network bandwidth.

### Configuration & State Management

* **[Configuration Management](https://github.com/erivlis/mappingtools/blob/main/recipes/03_config_management.py):**
  Load multiple configuration layers and fold them into a single state using `functools.reduce` and `merge`.
* **[The Inverted Configuration Index](https://github.com/erivlis/mappingtools/blob/main/recipes/08_inverted_config_index.py):**
  Combine `flatten` and `MappingCollector` (with `Aggregation.ALL`) to instantly find duplicated values (like IPs or
  secrets) scattered across deeply nested configuration files.
* **[Feature Flag Rollout State](https://github.com/erivlis/mappingtools/blob/main/recipes/19_feature_flag_rollout.py):**
  Combine native Python comprehensions and `distinct` to isolate feature flags across an N-tier configuration cascade (
  Global -> Region -> User) and detect conflicting state overrides.
* **[Cartesian Grid Search](https://github.com/erivlis/mappingtools/blob/main/recipes/09_hyperparameter_grid_search.py):**
  Combine `itertools.product` and `merge` to instantly generate an N-dimensional matrix of fully-formed configurations
  for hyperparameter tuning or parameterized testing.

### Security, Auditing & Governance

* **[Cryptographic Redaction](https://github.com/erivlis/mappingtools/blob/main/recipes/10_cryptographic_redaction.py):**
  Combine `flatten`, `hashlib`, and `Lens` optics to locate and cryptographically mask sensitive secrets (PII, Tokens)
  deep within an N-dimensional JSON payload before logging.
* **[Deep JSON Diffing](https://github.com/erivlis/mappingtools/blob/main/recipes/04_deep_json_diffing.py):**
  Find additions, removals, and changes between two complex JSON payloads by collapsing them with `flatten`.
* **[Data Governance & RBAC](https://github.com/erivlis/mappingtools/blob/main/recipes/17_data_governance_masking.py):**
  Combine native dictionary comprehensions, `rename`, and `Lens` optics to strip internal metadata, reshape schemas, and
  cryptographically mask sensitive fields before sending a database record to an external API client.

### Architecture & Microservices

* **[Deep JSON Patching](https://github.com/erivlis/mappingtools/blob/main/recipes/01_deep_json_patching.py):**
  Immutably update deep nested sections of a JSON payload using `Lens` and `merge`.
* **[Schema-Guided Payload Correction](https://github.com/erivlis/mappingtools/blob/main/recipes/12_schema_guided_correction.py):**
  Combine `flatten`, `Lens`, and `merge` to build an auto-correction pipeline that casts types, migrates deprecated
  keys, and applies structural defaults to incoming JSON payloads.
* **[JSON Schema Derivation](https://github.com/erivlis/mappingtools/blob/main/recipes/26_json_schema_derivation.py):**
  Combine `flatten`, `Lens`, `patch`, and `merge` to derive a public API contract from a canonical internal JSON Schema
  by pruning internal/read-only fields and overlaying partner-specific constraints.
* **[JSON Schema Review Envelopes](https://github.com/erivlis/mappingtools/blob/main/recipes/27_json_schema_review_envelopes.py):**
  Combine `flatten`, `Lens`, `patch`, and `merge` to preserve a JSON Schema's object shape while replacing each
  primitive field, scalar array item, direct `$ref`, and direct union/composition schema (`oneOf`, `anyOf`, `allOf`)
  with a `oneOf` wrapper representing either an override value or an approval decision. If the root schema has a `$id`,
  the recipe also appends a suffix so the derived schema gets a distinct identity.
* **[Bi-directional State Sync](https://github.com/erivlis/mappingtools/blob/main/recipes/18_bidirectional_state_sync.py):**
  Use `inverse` and `rekey` to instantly build a two-way synchronization bridge (snake_case <-> camelCase) between a
  Python backend and a React/Vue frontend payload.
* **[Microservice Dependency Graph](https://github.com/erivlis/mappingtools/blob/main/recipes/11_microservice_dependency_graph.py):**
  Combine the `inverse` operator with the `AutoMapper` collector to compute the blast radius of an infrastructure outage
  and generate a minified Mermaid.js node visualization.
* **[Broadcasting Method Calls](https://github.com/erivlis/mappingtools/blob/main/recipes/13_dictifier_broadcasting.py):**
  Use the `Dictifier` wrapper to instantly proxy method calls and attribute accesses across a vast fleet of identically
  typed objects simultaneously.

### Telemetry & Analytics

* **[Profiling Config Access](https://github.com/erivlis/mappingtools/blob/main/recipes/05_slow_config_profiling.py):**
  Wrap generic configurations in `MeteredDict` to track "hot" read/write paths and identify dead code.
* **[Telemetry Aggregation](https://github.com/erivlis/mappingtools/blob/main/recipes/20_telemetry_aggregation.py):**
  Combine `MeteredDict`, `Dictifier`, and `reduce(merge, ...)` to effortlessly broadcast metric collection across a
  distributed fleet of isolated workers and instantly fold their results into a single global telemetry map.
* **[Real-Time Anomaly Detection](https://github.com/erivlis/mappingtools/blob/main/recipes/24_anomaly_detection.py):**
  Use `MappingCollector` with `Aggregation.EMA` to maintain a memory-efficient baseline of a noisy time-series and
  instantly flag incoming data points that deviate beyond a set threshold.
* **[Time-Series Smoothing](https://github.com/erivlis/mappingtools/blob/main/recipes/16_time_series_ema.py):**
  Use `MappingCollector` and `Aggregation.EMA` to automatically calculate an Exponential Moving Average across a noisy
  stream of live data ticks grouped by their sensor source.
* **[Multi-Dimensional Counting](https://github.com/erivlis/mappingtools/blob/main/recipes/07_filesystem_categorization.py):**
  Traverse a filesystem and simultaneously categorize files by extension, size bucket, and hidden status using a single
  `CategoryCounter`.

### Algorithmic Explorations

* **[Markov Chain Text Generation](https://github.com/erivlis/mappingtools/blob/main/recipes/25_markov_chain_text_generator.py):**
  Combine `MappingCollector` and `Aggregation.COUNT` to instantly build a Markov Transition Matrix (Word -> Counter(Next
  Words)) from a training corpus, and use it to hallucinate new sentences.
* **[Graph Theory Connectivity](https://github.com/erivlis/mappingtools/blob/main/recipes/23_graph_theory_connectivity.py):**
  Combine `flatten` and `distinct` to extract all unique nodes reachable within a specific sub-graph generated from an
  Adjacency List.
* **[Algorithmic Music Transposition](https://github.com/erivlis/mappingtools/blob/main/recipes/21_algorithmic_music_transposition.py):**
  Combine `reshape` and `Lens` optics to convert a flat stream of MIDI events into a nested musical score, and immutably
  transpose a specific instrument track without mutating the original composition.
* **[Image Bounding Box Filter](https://github.com/erivlis/mappingtools/blob/main/recipes/22_image_bounding_box_filter.py):**
  Combine `reshape` and `Lens` optics to convert a flat 1D stream of RGB pixels into a 2D spatial tensor (Row -> Col ->
  RGB) and apply a Grayscale filter specifically to a central bounding box.
