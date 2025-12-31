# MNEMOSYS Data Model

Auto-generated diagram showing entity relationships.

```mermaid
classDiagram

    %% Group: Exercise
    namespace Exercise {
        class Exercise
        class ExerciseInstance
        class ExerciseLog
        class ExerciseState
    }

    %% Group: Instrument
    namespace Instrument {
        class Instrument
        class KeyboardInstrument
        class PercussionInstrument
        class StringedInstrument
        class WindInstrument
    }

    %% Group: Practice
    namespace Practice {
        class Practice
        class PracticeBlock
        class PracticeBlockLog
    }

    %% Group: Tuning
    namespace Tuning {
        class KeyboardInstrumentTuning
        class PercussionInstrumentTuning
        class StringedInstrumentTuning
        class Tuning
        class WindInstrumentTuning
    }

    %% Ungrouped entities
    class OverloadDimension
    class Technique

    %% Inheritance relationships
    Instrument <|-- KeyboardInstrument
    Instrument <|-- PercussionInstrument
    Instrument <|-- StringedInstrument
    Instrument <|-- WindInstrument
    Tuning <|-- KeyboardInstrumentTuning
    Tuning <|-- PercussionInstrumentTuning
    Tuning <|-- StringedInstrumentTuning
    Tuning <|-- WindInstrumentTuning

    %% Composition relationships
    Exercise ||--o{ ExerciseInstance
    Exercise ||--o{ PracticeBlock
    ExerciseInstance ||--|| Exercise
    ExerciseInstance ||--|| Practice
    ExerciseLog ||--|| ExerciseInstance
    ExerciseState ||--|| Exercise
    Instrument ||--o{ Practice
    KeyboardInstrument ||--o{ Practice
    PercussionInstrument ||--o{ Practice
    Practice ||--o{ ExerciseInstance
    Practice ||--|| Instrument
    Practice ||--o{ PracticeBlock
    PracticeBlock ||--|| Exercise
    PracticeBlock ||--|| Practice
    PracticeBlock ||--o{ PracticeBlockLog
    PracticeBlockLog ||--|| PracticeBlock
    StringedInstrument ||--o{ Practice
    WindInstrument ||--o{ Practice

    %% Association relationships (many-to-many)
    Exercise }o--o{ OverloadDimension
    Exercise }o--o{ Technique
    Instrument }o--o{ Technique
    KeyboardInstrument }o--o{ Technique
    PercussionInstrument }o--o{ Technique
    StringedInstrument }o--o{ StringedInstrumentTuning
    StringedInstrument }o--o{ Technique
    WindInstrument }o--o{ Technique

```