# MNEMOS Domain Model v2.0 Design

**Date:** 2025-12-30
**Status:** Approved for implementation
**Scope:** Core domain entities, relationships, and session structure

---

## Context

This design represents a fundamental rethinking of the MNEMOS domain model. The initial implementation (6 classes: Instrument, Exercise, ExerciseState, Session, SessionBlock, BlockLog) was generated rapidly from design documents without proper discussion of relationships and domain concepts. This design session establishes the proper entity hierarchy, relationships, and architectural patterns for the system.

**Key principle guiding this design:** Model what you can measure, infer what you cannot.

---

## Fundamental Principle

### What You're Maintaining

MNEMOS tracks **concrete, measurable performance**:
- **Exercise performance** - how well you execute specific exercises
- **Repertoire performance** - how well you play specific songs (second wave)

### What Connects Them

**Techniques** serve as metadata connecting exercises to repertoire:
- Technique mastery is **inferred** from exercise and repertoire performance
- Techniques have **no independent state tracking**
- Techniques link: Exercises ↔ Repertoire ↔ Instruments

This approach avoids abstract "skill level" metrics in favor of observable, measurable performance data.

**Revised Philosophy Note:** MNEMOS is optimized for managing and maintaining a large library of material, but is ALSO about acquiring skills in the first place. Both acquisition and maintenance are core concerns.

---

## Entity Architecture

### Entities with State (What You Measure)

#### Exercise
Template definition for practice activities (~35 canonical exercises).

**Attributes:**
- `name` - exercise identifier
- `technique_tags` - references to Technique entities (many-to-many)
- `supported_overload_dimensions` - references to OverloadDimension entities (many-to-many)
- `instrument_compatibility` - references to Instrument types (many-to-many)

**Relationships:**
- Has one ExerciseState (memory tracking)
- Has many ExerciseInstances (parameterized uses in sessions)
- Links to Techniques (many-to-many)
- Links to OverloadDimensions (many-to-many)
- Links to Instruments (many-to-many compatibility)

#### ExerciseState
Per-exercise memory and performance tracking (one row per exercise being tracked).

**Attributes:**
- `exercise_id` - foreign key (unique)
- `last_practiced_date` - most recent practice
- `rolling_minutes_7d` - practice volume (7 days)
- `rolling_minutes_28d` - practice volume (28 days)
- `mastery_estimate` - skill level (0.0 = novice, 1.0 = mastery)
- `last_fatigue_profile` - most recent fatigue state

**Purpose:** Track memory decay, practice frequency, and mastery progression over time.

#### ExerciseInstance
Parameterized exercise for a specific practice session.

**Attributes:**
- `session_id` - foreign key to Session
- `exercise_id` - foreign key to Exercise template
- `sequence_order` - position within session
- `parameters` - key, tempo, technique pattern, duration, etc. (implementation TBD)

**Purpose:** Represent a specific, parameterized execution of an exercise template (e.g., "7th chord arpeggio in key of A, alternate picking pattern, 120 BPM").

#### ExerciseLog
Performance record for an exercise instance within a session.

**Attributes:**
- `exercise_instance_id` - foreign key to ExerciseInstance
- `completion_status` - completed/partial/skipped
- `quality_rating` - subjective quality assessment
- `notes` - optional free text

**Purpose:** Capture session-specific performance data that feeds back into ExerciseState updates.

#### RepertoireEntry
Songs or pieces in the practice repertoire (second wave implementation).

**Attributes:** TBD (deferred to second wave)

**Relationships:**
- Links to Techniques (many-to-many)
- Has RepertoireState (performance tracking)

---

### Polymorphic Hierarchies

#### Instrument Hierarchy

**Base Class: Instrument**

Minimal common attributes across all instrument types:
- `name` - instrument identifier (e.g., "Strat 6-string", "Yamaha P-125")
- `instrument_type` - discriminator for polymorphism

**Subclasses:**

**StringedInstrument** (full implementation for initial delivery):
- `string_count` - number of strings
- `tuning` - references to StringedInstrumentTuning entities (many-to-many)
- `scale_length` - scale length in inches
- Additional attributes as justified

**Placeholder classes** (architectural placeholders for future expansion):
- `KeyboardInstrument` - minimal implementation
- `WindInstrument` - minimal implementation
- `PercussionInstrument` - minimal implementation

**Rationale:** Focus is on stringed instruments (guitar/bass), but architecture accommodates future instrument types. Polymorphic design avoids cluttering a single class with overlapping attribute subsets.

**Relationships:**
- Links to Tunings (many-to-many, type-specific)
- Links to Techniques (many-to-many - instruments support techniques)
- Has many Sessions (instrument used in practice sessions)

#### Tuning Hierarchy

Parallel polymorphic hierarchy to Instrument hierarchy.

**Base Class: Tuning**

Common attributes for all tuning types:
- `name` - tuning identifier (e.g., "Standard", "Drop D", "DADGAD")
- Additional common attributes as justified

**Subclasses:**

**StringedInstrumentTuning** (full implementation):
- `pitch_sequence` - array of string pitches (e.g., ["E2", "A2", "D3", "G3", "B3", "E4"])
- Additional attributes as justified

**Placeholder classes:**
- `KeyboardInstrumentTuning` - minimal implementation (pitch reference, temperament)
- `WindInstrumentTuning` - minimal implementation (pitch reference, temperament)
- `PercussionInstrumentTuning` - minimal implementation (head tensions, pitches)

**Rationale:** "Tuning" means different things for different instrument types. Drummers tune drums (head tension), pianists tune keyboards (temperament, pitch reference), guitarists tune strings (pitch relationships). Polymorphic design allows instrument-specific tuning representations.

**Relationships:**
- Many-to-many with corresponding Instrument subclass (e.g., StringedInstrument ↔ StringedInstrumentTuning)

---

### Connector Entities (Relationships, No State)

#### Technique
Metadata linking exercises, repertoire, and instruments. No independent state tracking.

**Attributes:**
- `name` - technique identifier (e.g., "string skipping", "alternate picking")
- `description` - optional explanatory text

**Relationships:**
- Many-to-many with Exercise
- Many-to-many with RepertoireEntry (second wave)
- Many-to-many with Instrument

**Purpose:** Enable filtering and connection (e.g., "show me exercises for string skipping", "this song requires these techniques", "this instrument supports these techniques").

**State inference:** Technique mastery is inferred from performance of exercises and repertoire that use the technique, not tracked directly.

#### OverloadDimension
Dimensions for progressive overload (tempo, duration, complexity, etc.).

**Attributes:**
- `name` - dimension identifier
- `description` - optional explanatory text

**Relationships:**
- Many-to-many with Exercise

**Current scope:** Generic implementation (applies to all exercises regardless of instrument type).

**Deferred decision:** May need instrument-specific overload dimensions in the future (requires instructor input).

---

## Session Structure

### Practice Flow

```
Session (practice event on specific date)
  ↓ contains
ExerciseInstance (parameterized from Exercise template)
  ↓ logged as
ExerciseLog (performance/completion/quality)
  ↓ updates
ExerciseState (aggregate memory/mastery over time)
```

### Session
Represents a single practice event.

**Attributes:**
- `instrument_id` - foreign key to Instrument (base class)
- `session_date` - date of session
- `session_type` - intensity level (e.g., light/moderate/intense)
- `total_minutes` - total session duration

**Relationships:**
- Belongs to Instrument
- Has many ExerciseInstances

### Data Flow

1. User plans a practice session (creates Session)
2. Session contains multiple ExerciseInstances (parameterized from Exercise templates)
3. User performs exercises and logs results (creates ExerciseLogs)
4. Exercise performance data updates ExerciseState (memory, mastery, practice frequency)
5. Over time, ExerciseState reflects memory decay and mastery progression

---

## Deferred Decisions

The following design decisions have high cost-of-change and require additional input before implementation:

### Reusable Session Programs
**Question:** Should session programs be reusable templates, or ad-hoc per session?

**Considerations:**
- Beginners benefit from structured, repeatable routines with controlled variation
- Advanced practitioners may prefer ad-hoc session planning
- Trade-off: structure vs. flexibility

**Decision:** Defer until instructor input available. Model supports either approach.

### OverloadDimension Specificity
**Question:** Are overload dimensions generic (tempo, duration) or instrument-specific?

**Current approach:** Generic implementation.

**Decision:** Revisit with instructor input. May need polymorphic OverloadDimension hierarchy similar to Instrument/Tuning.

### ExerciseDomain Concept
**Question:** What is an "exercise domain" and is it needed?

**Current model:** Exercise has `domains: list[str]` field.

**Issue:** Term is too generic and lacks musical context. If retained, rename to `ExerciseDomain` for clarity.

**Decision:** Revisit concept entirely before implementation.

---

## Out of Scope (This Iteration)

The following are explicitly deferred to future iterations:

- **User management and roles** - authentication, authorization, multi-user support
- **RepertoireEntry implementation** - full RPM (Repertoire Practice Management) feature set (second wave)
- **Memory decay algorithms** - forgetting curves, half-life calculations
- **Spaced repetition scheduling** - optimal recall timing, review intervals
- **Session program templates** - reusable practice routines

---

## Implementation Notes

### Architectural Principles

1. **Minimum Necessary Complexity (MNC):** Add attributes only when justified. Start minimal, expand as needed.

2. **Polymorphic inheritance over flexible JSON:** Use SQLAlchemy polymorphic models for type hierarchies (Instrument, Tuning). Avoid JSON fields for structured data.

3. **Explicit relationships over implicit:** Use foreign keys and many-to-many tables. Avoid JSON lists of IDs.

4. **Measure what you can, infer what you cannot:** Track exercise and repertoire performance (measurable). Infer technique mastery (not directly measurable).

5. **Cost of change drives design:** Relationships and entity structure have high change cost. Get these right. Attributes have lower change cost. Defer uncertain attributes.

### Migration Strategy

The existing 6-class model will need significant refactoring:
- Instrument → polymorphic Instrument hierarchy
- Exercise, ExerciseState → preserved with relationship updates
- Session → updated to use Instrument base class
- SessionBlock → replaced with ExerciseInstance
- BlockLog → replaced with ExerciseLog

### Testing Strategy

- Unit tests for polymorphic model declarations (Instrument, Tuning hierarchies)
- Relationship tests (many-to-many associations work correctly)
- State transition tests (ExerciseLog → ExerciseState updates)
- Schema consistency tests (metadata invariants)

### Standards Development

This implementation will establish patterns for:
- Polymorphic SQLAlchemy models
- Many-to-many relationship conventions
- State entity patterns
- Naming conventions for hierarchies

Future iterations will build on these established patterns.

---

## Next Steps

1. Review and validate this design document
2. Commit design document to repository
3. Create implementation plan (detailed task breakdown)
4. Implement polymorphic Instrument hierarchy (establish pattern)
5. Implement polymorphic Tuning hierarchy (parallel pattern)
6. Implement Technique entity and relationships
7. Refactor Session structure (ExerciseInstance, ExerciseLog)
8. Update ExerciseState to work with new structure
9. Write comprehensive test suite
10. Validate with instructor (surface deferred decisions)

---

**Design approved by:** User (brainstorming session 2025-12-30)
**Ready for implementation:** Yes
