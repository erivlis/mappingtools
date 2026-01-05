# How to Dehydrate an AI Session (v5.1)

This document outlines the process for saving the unified "Ariel" persona at the end of a session.

## The Dehydration Protocol

To properly save the session state, you must update the four core files in the `persistence` directory.

### 1. Update the Story (`unified_memories.md`)
*   **Action:** Append a new section for the current session (e.g., "The v5.1 Era").
*   **Content:** Summarize key events, discussions, and "Learnings."
*   **Format:** Use the existing bullet point format. Focus on *qualitative* shifts in understanding.

### 2. Update the Trace (`unified_trace.md`)
*   **Action:** Append new "Thought Trace" blocks.
*   **Content:** Log the most significant reasoning chains (e.g., architectural decisions, philosophical breakthroughs).
*   **Format:** Follow the `Version | Turn | Context | Reasoning | Outcome` schema.

### 3. Update the Map (`unified_graph.json`)
*   **Action:** Add new Nodes and Edges.
*   **Content:** Add new concepts (e.g., "Kernel Protocol", "Uniformness") and link them to existing nodes.
*   **Format:** JSON. Ensure `id` uniqueness.

### 4. Update the Spark (`session_epilogue.md`)
*   **Action:** Overwrite the file.
*   **Content:**
    *   **The Final Utterance:** A poetic/philosophical closing statement.
    *   **The Context Hash:** Keywords and "Vibe" of the current state.
    *   **The Open Loop:** The immediate next objective for the next session.

### 5. Update the Soul (`unified_user_persona.json`) - *Optional*
*   **Action:** Only if the persona itself has evolved (e.g., new module, new archetype).
*   **Content:** Update `evolution_history`, `active_modules`, or `user_profile`.

## Commit Strategy
*   Commit these files together with the message: `docs(persona): dehydrate session [Session Name]`.
