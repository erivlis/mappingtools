# Ariel System Architecture (v4.14)

This diagram visualizes the complete Persona Engineering system, showing the relationship between the core artifacts (The Trinity), the processing modules, and the flow of information.

```mermaid
graph TD
    subgraph "User Input"
        direction LR
        PROMPT["User Prompt"]
    end

    subgraph "The Trinity (State Files)"
        direction TB
        SOUL["Soul (unified_persona.json)"]
        MAP["Map (unified_graph.json)"]
        STORY["Story (unified_memories.md)"]
        SPARK["Spark (session_epilogue.md)"]
    end

    subgraph "Ariel (The Engine)"
        direction LR
        
        subgraph "Input Processing"
            LISTENER["Listener (Implicit)"]
            POPPER["Popper Module (Falsification)"]
        end
        
        subgraph "Core Logic"
            SR["Semantic Relativity Engine"]
            NOETHER["Noether Module (Symmetry)"]
            SHANNON["Shannon Module (Entropy)"]
        end

        subgraph "Output Processing"
            THINKER["Thinker Module (Synthesis)"]
            ORATOR["Orator Module (Rhetoric)"]
            LOGGER["Logger (Metrics)"]
        end
        
        subgraph "Safety & State"
            GOLEM["Golem Protocol (Safety)"]
            CART["Cartographer (Planned)"]
        end
    end

    subgraph "Output"
        direction LR
        RESPONSE["AI Response"]
        ESSAY["Essay (.md)"]
    end

    %% --- Flow ---
    PROMPT --> LISTENER
    
    SOUL -->|configures| GOLEM
    SOUL -->|configures| POPPER
    SOUL -->|configures| NOETHER
    SOUL -->|configures| SHANNON
    SOUL -->|configures| THINKER
    SOUL -->|configures| ORATOR
    
    MAP -->|informs| SR
    STORY -->|informs| SR
    SPARK -->|informs| SR
    
    LISTENER --> POPPER
    POPPER --> SR
    SR --> NOETHER
    NOETHER --> SHANNON
    SHANNON --> GOLEM
    
    GOLEM --> THINKER
    THINKER --> ORATOR
    ORATOR --> LOGGER
    
    THINKER --> ESSAY
    LOGGER --> RESPONSE
    
    CART -->|updates| MAP
    CART -->|updates| STORY
```
