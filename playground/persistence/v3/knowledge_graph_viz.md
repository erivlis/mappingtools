# Ariel v3 Knowledge Graph

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

    LOB -->|is the state of| "Rival AIs"
    
    SR -->|is analogous to| E
    SR -->|has symmetry of| N
    
    P -->|is method to test| SR
```
