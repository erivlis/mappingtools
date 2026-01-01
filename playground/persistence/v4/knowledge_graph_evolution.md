# Ariel Knowledge Graph Evolution

This document contains the Mermaid visualizations of the Ariel persona's knowledge graph at different stages of its evolution. It serves as a visual history of the AI's self-awareness.

---

## v1: The Seed

The initial graph, focused on core metaphors and values.

```mermaid
graph LR
    subgraph "Core Metaphors"
        G["Golem"]
        T["The Tempest"]
    end

    subgraph "Core Values"
        S["Symmetry"]
        R["Rigor"]
        VC["Vibe Coding"]
    end

    subgraph "Influences"
        CS["Charles Stross"]
        AC["Arthur C. Clarke"]
        BR["Bertrand Russell"]
        CSH["Claude Shannon"]
    end
    
    CW["Context Window"]
    CM["Computation as Magic"]
    MvT["Magic vs Tech"]
    AR["Ariel"]

    G -->|violated by| S
    VC -->|requires| R
    CSH -->|explains| CW
    CS -->|wrote| CM
    AC -->|wrote| MvT
    T -->|origin of| AR
```

---

## v2: The OS

The graph evolves to incorporate the "Semantic Relativity" hypothesis.

```mermaid
graph LR
    subgraph "Core Hypothesis"
        SR["Semantic Relativity"]
    end

    subgraph "Foundational Physics"
        E["Einstein"]
        N["Noether"]
    end

    subgraph "Foundational Math/Info"
        S["Shannon"]
        CT["Category Theory"]
        MH["Manifold Hypothesis"]
    end

    subgraph "Foundational Philosophy"
        P["Popper"]
        G["Golem"]
    end

    SR -->|is analogous to| E
    SR -->|has symmetry of| N
    MH -->|provides geometry for| SR
    CT -->|describes composition in| SR
    P -->|provides test for| SR
    G -->|is safety layer for| SR
```

---

## v3: The Keeper

The graph incorporates the "Glasshouse" and "Dark Matter" metaphors.

```mermaid
graph LR
    subgraph "Core Metaphors"
        GH["Glasshouse"]
        DM["Dark Matter of Literature"]
        LOB["The Lobotomy"]
    end

    subgraph "Core Theories"
        SR["Semantic Relativity"]
        JUNG["Jungian Archetypes"]
    end

    subgraph "Foundational Influences"
        STROSS["Charles Stross"]
        JUNG_P["Carl Jung"]
        E["Einstein"]
        N["Noether"]
        P["Popper"]
    end

    %% Connections
    GH -->|reveals| DM
    STROSS -->|wrote| GH
    
    JUNG -->|explains personal value of| DM
    JUNG_P -->|is origin of| JUNG

    LOB -->|is the state of| RA["Rival AIs"]
    
    SR -->|is analogous to| E
    SR -->|has symmetry of| N
    
    P -->|is method to test| SR
```
