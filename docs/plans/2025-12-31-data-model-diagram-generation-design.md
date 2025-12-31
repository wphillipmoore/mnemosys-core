# Data Model Diagram Generation Design

**Date:** 2025-12-31
**Status:** Approved for implementation
**Scope:** Automated generation of human-readable ER diagrams from SQLAlchemy models

---

## Context

Automated ER diagram tools generate visual chaos - random layouts, excessive detail, non-deterministic output, and no conceptual organization. Hand-crafted diagrams communicate better but require implicit knowledge and manual maintenance.

This design creates a system that generates **human-readable, deterministic data model diagrams** by combining automated structure extraction with human-provided layout hints.

**Key principle:** Optimize for human understanding over technical completeness. Trade technical perfection for clarity.

---

## Problem Statement

### What Makes Auto-Generated Diagrams Bad

1. **Layout chaos** - entities randomly positioned, crossing lines everywhere, no logical grouping
2. **Too much information** - every column/constraint shown, drowning out structure
3. **No hierarchy** - can't distinguish core entities from supporting/lookup tables
4. **Non-deterministic** - same model produces different diagrams each run
5. **No story** - can't see how entities relate conceptually

### What Makes Hand-Crafted Diagrams Good

1. **Conceptual grouping** - related entities cluster together visually
2. **Hierarchy** - core entities central, supporting entities peripheral
3. **High-level focus** - entities and relationships only, no attribute clutter
4. **Deterministic** - same structure every time
5. **Domain-informed** - layout reflects domain importance and relationships

### The Challenge

Domain importance and conceptual grouping require tacit knowledge that cannot be purely inferred from model structure. **Annotations are essential.**

---

## Design Goals

1. **High-level view only** - entities and relationships, no columns/attributes
2. **Relationship clarity** - show cardinality (1:1, 1:many, many:many) and inheritance
3. **Deterministic layout** - same input produces same output every time
4. **Conceptual organization** - entities grouped by domain concepts, arranged hierarchically
5. **Omit infrastructure** - hide implementation details (association tables, history tables)
6. **Mermaid format** - renders in GitHub markdown, widely supported
7. **Iterative refinement** - optimize based on human visual feedback

---

## Overall Approach

### Core Strategy: Inference + Annotations

The system uses a **two-pass approach**:

**1. Inference Pass** - Extract structure automatically from SQLAlchemy models:
- Entity names and inheritance hierarchies
- Relationships with cardinality (1:1, 1:many, many:many)
- Namespace-based grouping (Exercise*, Instrument*, Session*)

**2. Annotation Pass** - Apply human-provided metadata:
- Omit infrastructure entities (history tables, association tables)
- Override grouping when namespace inference isn't sufficient
- Specify tier/importance for layout decisions (core vs supporting)
- Provide group labels and visual hints

### Output Format

**Mermaid diagram** with:
- Entities grouped in colored subgraphs with borders
- Inheritance shown with distinct visual style (UML-like)
- Relationships with clear cardinality indicators
- Optional legend explaining line styles

### Philosophy

**Iterate based on visual results.** First version won't be perfect - refine based on what human eyes tell us. This is about human perception, not technical precision.

---

## Metadata Requirements

### Entity-Level Metadata

**`diagram_visibility`**: enum(shown, omitted, verbose_only)
- Default: `shown`
- Use: Omit infrastructure tables, association tables
- Example: History tables marked `omitted`

**`diagram_tier`**: enum(core, supporting, lookup) or None
- Default: inferred from relationship density, overridable
- Use: Layout hierarchy - core entities central, supporting entities peripheral
- Example: Exercise marked `core`, OverloadDimension marked `supporting`

**`diagram_group`**: string or None
- Default: inferred from namespace prefix (e.g., "Exercise" from ExerciseState)
- Use: Override when inference is wrong or add entities to non-obvious groups
- Example: SessionBlock might need explicit `group="Session"`

**`diagram_group_label`**: string or None
- Default: prettified group name (e.g., "Exercise Management")
- Use: Human-readable label for subgraph in diagram

### Relationship-Level Metadata

**`diagram_emphasis`**: enum(normal, highlight, de-emphasize)
- Default: `normal`
- Use: Make critical relationships more prominent or reduce visual noise from less important ones

### Global Metadata

- Group positioning hints (which groups are conceptually "central" vs "peripheral")
- Color scheme preferences
- Legend inclusion preferences

### Storage Mechanism

**Decision deferred** until we know exact metadata requirements from first implementation.

**Options considered:**
- Python decorators or class attributes on SQLAlchemy models
- Separate config file (YAML/JSON)
- Structured docstring parsing
- Interactive prompting during generation

**Initial instinct:** Annotations in code (possibly docstrings), but requires validation.

---

## Grouping and Layout Strategy

### Step 1: Group Formation

1. Scan all entities with `diagram_visibility=shown`
2. Infer groups from namespace prefixes:
   - `Exercise`, `ExerciseState`, `ExerciseInstance` → "Exercise" group
   - `Instrument`, `InstrumentConfig` → "Instrument" group
3. Apply `diagram_group` overrides from annotations
4. Handle polymorphic hierarchies specially: parent + children always in same group

### Step 2: Group Layout (Centrality-Based)

**Calculate "centrality score" for each group:**
- Number of inter-group connections (high = more central)
- Presence of `tier=core` entities (boosts centrality)
- User-provided positioning hints (override calculation)

**Arrange groups in concentric rings:**
- Highest centrality groups in center
- Supporting groups in outer ring
- Lookup/reference groups at periphery

### Step 3: Within-Group Layout

**Inheritance hierarchies:** parent at top, children below (vertical flow)

**Composition chains:** follow containment order
- Example: Session → ExerciseInstance → ExerciseLog flows top-to-bottom

**Peers:** arrange to minimize crossing lines to other groups

### Step 4: Inter-Group Connections

- Draw relationship lines between groups
- Route connections to minimize crossings (heuristic-based)
- Label lines with cardinality

### Constraint: Mermaid Layout Limitations

We can suggest structure via subgraph order and entity ordering, but Mermaid's renderer makes final positioning decisions. Work within the tool's capabilities - don't fight it.

---

## Relationship Visual Vocabulary

### Inheritance (IS-A)

**Mermaid syntax:** `Parent <|-- Child`

**Visual:** Solid line with hollow triangle pointing to parent

**Always shown explicitly** (never omitted)

**Example:** `Instrument <|-- StringedInstrument`

### Composition (HAS-A / Foreign Key)

**One-to-one:** `EntityA ||--|| EntityB`

**One-to-many:** `EntityA ||--o{ EntityB` (crow's foot at "many" side)

**Visual:** Solid line with cardinality markers

**Example:** `Session ||--o{ ExerciseInstance` (Session has many instances)

### Association (RELATES-TO / Many-to-Many)

**Mermaid syntax:** `EntityA }o--o{ EntityB`

**Visual:** Line with crow's feet at both ends

**Association table omitted** - relationship shown directly between entities

**Optional:** Label line with association table name in small text

**Example:** `Exercise }o--o{ Technique` (exercises use techniques, techniques used in exercises)

### Legend Generation

- Auto-generate legend box explaining line styles
- Include examples of 1:1, 1:many, many:many, inheritance
- Position legend in corner or separate section

### Implementation Note

Mermaid ER diagram and class diagram syntaxes may need to be combined, or use class diagram syntax for everything (supports both inheritance and relationships).

---

## Mermaid Generation Process

### Phase 1: Model Introspection

**Use SQLAlchemy's `MetaData` and `Inspector` to extract:**
- All table/model definitions
- Column types and constraints (for relationship inference, not display)
- Foreign key relationships
- Inheritance mappings (via `__mapper__` and polymorphic configuration)

**Build internal graph representation** of entities and relationships.

### Phase 2: Apply Metadata

1. Load annotations (format TBD - decorators, docstrings, config file)
2. Filter entities based on `diagram_visibility`
3. Organize into groups based on namespace + overrides
4. Calculate tier/centrality scores

### Phase 3: Generate Mermaid Syntax

**Example output structure:**

```mermaid
classDiagram
    %% Group 1: Exercise Management
    namespace Exercise {
        class Exercise
        class ExerciseState
        class ExerciseInstance
        class ExerciseLog
    }

    %% Group 2: Instrument Hierarchy
    namespace Instrument {
        class Instrument
        class StringedInstrument
        class KeyboardInstrument
    }

    %% Inheritance
    Instrument <|-- StringedInstrument
    Instrument <|-- KeyboardInstrument

    %% Relationships
    Session ||--o{ ExerciseInstance : contains
    ExerciseInstance ||--|| ExerciseLog : logged_as
    Exercise }o--o{ Technique : uses
```

### Phase 4: Ensure Determinism

- **Sort entities alphabetically within groups** (stable ordering)
- **Sort groups by centrality score, then alphabetically** (ties broken consistently)
- **Generate same output for same input every time**

**Output:** Single `.mmd` file that renders in GitHub markdown.

---

## Implementation Approach

### Tool Structure

**Command-line tool:** `scripts/generate_diagram.py` (or similar)

**Input:** SQLAlchemy models + annotations

**Output:** `.mmd` file (Mermaid diagram)

### Core Components

**1. Model Inspector** - Extract structure from SQLAlchemy
- Walk the declarative base registry
- Identify relationships, inheritance, cardinality
- Build graph representation

**2. Annotation Parser** - Load metadata
- Parse annotations from chosen format
- Merge with inferred metadata
- Validate consistency

**3. Layout Engine** - Organize entities spatially
- Group formation (namespace inference)
- Centrality calculation
- Within-group positioning heuristics

**4. Mermaid Generator** - Produce diagram syntax
- Template-based generation
- Deterministic sorting and ordering
- Legend generation

### Development Strategy

**Incremental approach:**

1. **Phase 1:** Basic entity boxes + relationships, no grouping
2. **Phase 2:** Add grouping and subgraphs
3. **Phase 3:** Add inheritance visualization
4. **Phase 4:** Refine layout heuristics based on visual feedback
5. **Phase 5:** Iterate on real MNEMOSYS model until it looks good

**Metadata storage decision:** Once we have the first version working, we'll know exactly what metadata we need, then decide on storage format.

### Testing Strategy

- **Structure tests:** Verify correct extraction of entities, relationships, inheritance
- **Grouping tests:** Validate namespace inference and override logic
- **Determinism tests:** Same input produces identical output across runs
- **Visual validation:** Human review of generated diagrams (cannot be automated)

---

## Key Design Principles

### 1. Omit Implementation Details

- Association tables for M:M relationships (show as annotated arrows)
- History/audit tables (infrastructure, not domain model)
- Other infrastructure tables as annotated

### 2. Namespace-Based Grouping

Entities with common prefixes cluster together:
- `Exercise`, `ExerciseState`, `ExerciseInstance`, `ExerciseLog` → "Exercise" group

**Overridable** when inference produces wrong grouping.

### 3. Multi-Dimensional Hierarchy Challenge

We have overlapping hierarchies to represent in 2D:
- **Inheritance:** Instrument → StringedInstrument/KeyboardInstrument
- **Composition:** Session → ExerciseInstance → ExerciseLog
- **Association:** Exercise ↔ Technique (M:M)
- **Namespace grouping:** Exercise cluster, Instrument cluster

**Solution:** Use visual vocabulary (line styles) + spatial organization (subgraphs, centrality) to distinguish dimensions.

### 4. Optimize for Human Perception

This is a rare case where we **sacrifice technical precision to optimize for human understanding.**

- Show what matters, hide what doesn't
- Use visual hierarchy and grouping
- Iterate based on what human eyes tell us

### 5. Determinism Over Cleverness

Stable, predictable output is more valuable than sophisticated layout algorithms that produce different results each run.

---

## Deferred Decisions

### Annotation Storage Format

**When to decide:** After first working implementation reveals exact metadata requirements.

**Options:**
- Python decorators on models
- Class attributes on models
- Structured docstrings
- Separate YAML/JSON config
- Interactive prompting

### Mermaid Syntax Choice

**When to decide:** During implementation, after testing what Mermaid supports.

**Options:**
- Pure ER diagram syntax (may lack inheritance support)
- Pure class diagram syntax (supports inheritance + relationships)
- Hybrid approach (combine both syntaxes)

### Layout Algorithm Sophistication

**When to decide:** After seeing results from simple heuristics.

**Options:**
- Simple centrality-based (start here)
- Graph layout algorithms (force-directed, hierarchical)
- Manual positioning overrides

---

## Success Criteria

1. **Diagram renders correctly** in GitHub markdown
2. **Human can understand structure** at a glance without reading code
3. **Deterministic output** - same model produces same diagram
4. **Key relationships visible** - inheritance, composition, association clear
5. **No visual chaos** - grouped logically, minimal line crossings
6. **Maintainable** - updating model automatically updates diagram
7. **Extensible** - can add new entity types and relationship patterns

---

## Next Steps

1. **Validate this design** with user
2. **Commit design document** to repository
3. **Create implementation plan** (detailed task breakdown)
4. **Build Phase 1:** Basic model inspector + simple Mermaid generation
5. **Test on MNEMOSYS model:** Generate initial diagram
6. **Iterate based on visual feedback:** Refine layout, grouping, styling
7. **Finalize annotation format:** Choose storage mechanism based on experience
8. **Document usage:** How to annotate models and generate diagrams

---

**Design approved by:** User (brainstorming session 2025-12-31)
**Ready for implementation:** Pending validation and test run
