# MappingTools Recipes

This directory contains examples and recipes demonstrating how to combine `mappingtools` primitives (Operators, Lenses,
Collectors) with built-in Python features and third-party libraries (like `pandas`, `requests`, or `json`).

## The Philosophy

In accordance with **The Council Framework** (Symmetry, Clarity, Functional Primitives):

1. **Build the engine, then build the car:** `mappingtools` provides the raw mathematical engines (Monoids, Optics,
   Reshaping). These recipes build the "cars" (data pipelines, deep JSON patching, ETL flows).
2. **No Magic:** Recipes should be explicit and composable, preferring pure functions and standard Python `functools`
   over bloated manager classes.

## Available Recipes

* [01. Deep JSON Patching](01_deep_json_patching.py):
  Immutably update deep nested sections of a JSON payload using `Lens` and `merge`.
* [02. Reshaping Tabular Data](02_etl_reshape.py):
  Convert a flat stream of dicts (like a CSV or DB cursor) into a nested dictionary using `reshape` and `Aggregation`.
* [03. Configuration Management](03_config_management.py):
  Load multiple configuration layers and fold them into a single state using `functools.reduce` and `merge`.
* [04. Deep JSON Diffing](recipe_04_deep_json_diffing.py):
  Find additions, removals, and changes between two complex JSON payloads by collapsing them with `flatten`.
* [05. Profiling Config Access](recipe_05_slow_config_profiling.py):
  Wrap generic configurations in `MeteredDict` to track "hot" read/write paths and identify dead code.
* [06. Quick Serialization](recipe_06_serialization_pipeline.py):
  Convert `dataclasses`, `datetime` objects, and custom Python structures directly into JSON-serializable dictionaries
  using `strictify`.
* [07. Multi-Dimensional Counting](recipe_07_filesystem_categorization.py):
  Traverse a filesystem and simultaneously categorize files by extension, size bucket, and hidden status using a single
  `CategoryCounter`.
* [08. The Inverted Configuration Index](recipe_08_inverted_config_index.py):
  Combine `flatten` and `MappingCollector` with `Aggregation.ALL` to instantly find duplicated values (like IPs or secrets) scattered across deeply nested configuration files.
* [09. Cartesian Grid Search](recipe_09_hyperparameter_grid_search.py):
  Combine `itertools.product` and `merge` to instantly generate an N-dimensional matrix of fully-formed configurations for hyperparameter tuning or parameterized testing.
* [10. Cryptographic Redaction](recipe_10_cryptographic_redaction.py):
  Combine `flatten`, `hashlib`, and `Lens` optics to locate and cryptographically mask sensitive secrets (PII, Tokens) deep within an N-dimensional JSON payload before logging.
* [11. Microservice Dependency Graph](recipe_11_microservice_dependency_graph.py):
  Combine the `inverse` operator with the `AutoMapper` collector to compute the blast radius of an infrastructure outage and generate a minified Mermaid.js node visualization.
* [12. Schema-Guided Payload Correction](recipe_12_schema_guided_correction.py):
  Combine `flatten`, `Lens`, and `merge` to build an auto-correction pipeline that casts types, migrates deprecated keys, and applies structural defaults to incoming JSON payloads.
* [13. Broadcasting Method Calls](recipe_13_dictifier_broadcasting.py):
  Use the `Dictifier` wrapper to instantly proxy method calls and attribute accesses across a vast fleet of identically typed objects simultaneously.
* [14. Dynamic Object Minification](recipe_14_auto_minification.py):
  Combine `AutoMapper` and `strictify(key_converter=...)` to recursively rewrite verbose JSON string keys into sequentially generated, ultra-compact shortcodes to save network bandwidth.
* [15. Pivot Tensors](recipe_15_data_pivot_tensor.py):
  Combine `reshape` and `Aggregation.ALL` to group a flat stream of transactional records into an N-dimensional analytical tensor without losing any underlying individual records.
* [16. Time-Series Smoothing](recipe_16_time_series_ema.py):
  Use `MappingCollector` and `Aggregation.EMA` to automatically calculate an Exponential Moving Average across a noisy stream of live data ticks grouped by their sensor source.
* [17. Data Governance & RBAC](recipe_17_data_governance_masking.py):
  Combine Python's native dictionary comprehensions, `rename`, and `Lens` optics to strip internal metadata, reshape schemas, and cryptographically mask sensitive fields before sending a database record to an external API client.
* [18. Bi-directional State Sync](recipe_18_bidirectional_state_sync.py):
  Use `inverse` and `rekey` to instantly build a two-way synchronization bridge (snake_case <-> camelCase) between a Python backend and a React/Vue frontend payload.
* [19. Feature Flag Rollout State](recipe_19_feature_flag_rollout.py):
  Combine native Python comprehensions and `distinct` to isolate feature flags across an N-tier configuration cascade (Global -> Region -> User) and detect conflicting state overrides.
* [20. Telemetry Aggregation](recipe_20_telemetry_aggregation.py):
  Combine `MeteredDict`, `Dictifier`, and `reduce(merge, ...)` to effortlessly broadcast metric collection across a distributed fleet of isolated workers and instantly fold their results into a single global telemetry map.
* [21. Algorithmic Music Transposition](recipe_21_algorithmic_music_transposition.py):
  Combine `reshape` and `Lens` optics to convert a flat stream of MIDI events into a nested musical score, and immutably transpose a specific instrument track without mutating the original composition.
* [22. Image Bounding Box Filter](recipe_22_image_bounding_box_filter.py):
  Combine `reshape` and `Lens` optics to convert a flat 1D stream of RGB pixels into a 2D spatial tensor (Row -> Col -> RGB) and apply a Grayscale filter specifically to a central bounding box.
* [23. Graph Theory Connectivity](recipe_23_graph_theory_connectivity.py):
  Combine `flatten` and `distinct` to extract all unique nodes reachable within a specific sub-graph generated from an Adjacency List.
* [24. Real-Time Anomaly Detection](recipe_24_anomaly_detection.py):
  Use `MappingCollector` with `Aggregation.EMA` to maintain a memory-efficient baseline of a noisy time-series and instantly flag incoming data points that deviate beyond a set threshold.
* [25. Markov Chain Text Generation](recipe_25_markov_chain_text_generator.py):
  Combine `MappingCollector` and `Aggregation.COUNT` to instantly build a Markov Transition Matrix (Word -> Counter(Next Words)) from a training corpus, and use it to hallucinate new sentences.
* [26. JSON Schema Derivation](recipe_26_json_schema_derivation.py):
  Combine `flatten`, `Lens`, `patch`, and `merge` to derive a public API contract from a canonical internal JSON Schema by pruning internal/read-only fields and overlaying partner-specific constraints.
* [27. JSON Schema Review Envelopes](recipe_27_json_schema_review_envelopes.py):
  Combine `flatten`, `Lens`, `patch`, and `merge` to preserve a JSON Schema's object shape while replacing each primitive field, scalar array item, direct `$ref`, and direct union/composition schema (`oneOf`, `anyOf`, `allOf`) with a `oneOf` wrapper representing either an override value or an approval decision. If the root schema has a `$id`, the recipe appends a suffix so the derived schema gets a distinct identity.
