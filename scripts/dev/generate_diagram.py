#!/usr/bin/env python3
"""
Generate Mermaid ER diagram from SQLAlchemy models.

This is a prototype implementation to test the design approach documented in
docs/plans/2025-12-31-data-model-diagram-generation-design.md
"""

from collections import defaultdict
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.orm import RelationshipProperty

# Import all models to register them with Base
from mnemosys_core.db.base import Base
from mnemosys_core.db.models import (  # noqa: F401 - imports needed for SQLAlchemy model registration
    Exercise,
    ExerciseInstance,
    ExerciseLog,
    ExerciseState,
    Instrument,
    KeyboardInstrument,
    OverloadDimension,
    PercussionInstrument,
    Practice,
    PracticeBlock,
    PracticeBlockLog,
    StringedInstrument,
    Technique,
    Tuning,
    WindInstrument,
)


def extract_model_info():
    """Extract entity and relationship information from SQLAlchemy models."""
    entities = []
    inheritance_relationships = []
    composition_relationships = []
    association_relationships = []

    # Track association tables (to omit from diagram)
    association_tables = set()
    for table in Base.metadata.tables.values():
        # Association tables have only 2 foreign key columns and no other columns
        fk_columns = [col for col in table.columns if col.foreign_keys]
        if len(table.columns) == len(fk_columns) == 2:
            association_tables.add(table.name)

    # Extract entities and relationships
    for mapper in Base.registry.mappers:
        model_class = mapper.class_

        # Handle polymorphic inheritance (mapped_table might be a Join)
        if hasattr(mapper.mapped_table, 'name'):
            table_name = mapper.mapped_table.name
        else:
            # For polymorphic subclasses, use the local_table
            table_name = mapper.local_table.name if mapper.local_table is not None else None

        # Skip association tables
        if table_name and table_name in association_tables:
            continue

        entities.append({
            'class_name': model_class.__name__,
            'table_name': table_name,
        })

        # Check for inheritance
        if len(model_class.__mro__) > 2:  # More than just (Class, Base, object)
            for base in model_class.__bases__:
                if base != Base and hasattr(base, '__tablename__'):
                    inheritance_relationships.append({
                        'parent': base.__name__,
                        'child': model_class.__name__,
                    })

        # Extract relationships
        for prop in mapper.iterate_properties:
            if isinstance(prop, RelationshipProperty):
                target_class = prop.mapper.class_.__name__

                # Determine relationship type
                if prop.secondary is not None:
                    # Many-to-many (has association table)
                    association_relationships.append({
                        'from': model_class.__name__,
                        'to': target_class,
                        'association_table': prop.secondary.name,
                    })
                elif prop.uselist:
                    # One-to-many
                    composition_relationships.append({
                        'from': model_class.__name__,
                        'to': target_class,
                        'cardinality': '1:many',
                    })
                else:
                    # One-to-one or many-to-one
                    # Check if it's a back_populates to avoid duplicates
                    if prop.back_populates:
                        # Only add from the "owning" side (the one with the foreign key)
                        inspector = inspect(model_class)
                        table = inspector.mapped_table
                        has_fk_to_target = any(
                            fk.column.table.name == prop.mapper.mapped_table.name
                            for col in table.columns
                            for fk in col.foreign_keys
                        )
                        if has_fk_to_target:
                            composition_relationships.append({
                                'from': model_class.__name__,
                                'to': target_class,
                                'cardinality': '1:1',
                            })

    return {
        'entities': entities,
        'inheritance': inheritance_relationships,
        'composition': composition_relationships,
        'association': association_relationships,
    }


def infer_groups(entities):
    """Infer entity groups based on namespace prefixes."""
    groups = defaultdict(list)

    for entity in entities:
        class_name = entity['class_name']

        # Find common prefixes
        if class_name.startswith('Exercise'):
            groups['Exercise'].append(class_name)
        elif class_name.startswith('Practice'):
            groups['Practice'].append(class_name)
        elif class_name.startswith('Instrument') or class_name.endswith('Instrument'):
            groups['Instrument'].append(class_name)
        elif class_name.startswith('Tuning') or class_name.endswith('Tuning'):
            groups['Tuning'].append(class_name)
        else:
            # Standalone entities
            groups['Other'].append(class_name)

    return dict(groups)


def generate_mermaid(model_info):
    """Generate Mermaid class diagram syntax."""
    entities = model_info['entities']
    inheritance = model_info['inheritance']
    composition = model_info['composition']
    association = model_info['association']

    groups = infer_groups(entities)

    lines = []
    lines.append('```mermaid')
    lines.append('classDiagram')
    lines.append('')

    # Generate entity declarations grouped by conceptual area
    # Note: Mermaid doesn't support visual grouping, so we use comments
    # and spatial organization (entities declared together may render near each other)
    for group_name in sorted(groups.keys()):
        if group_name == 'Other':
            continue  # Handle ungrouped entities separately

        lines.append(f'    %% === {group_name} Group ===')
        for entity_name in sorted(groups[group_name]):
            lines.append(f'    class {entity_name}')
        lines.append('')

    # Handle ungrouped entities
    if 'Other' in groups:
        lines.append('    %% === Connector Entities ===')
        for entity_name in sorted(groups['Other']):
            lines.append(f'    class {entity_name}')
        lines.append('')

    # Generate inheritance relationships
    if inheritance:
        lines.append('    %% Inheritance relationships')
        for rel in sorted(inheritance, key=lambda x: (x['parent'], x['child'])):
            lines.append(f"    {rel['parent']} <|-- {rel['child']}")
        lines.append('')

    # Generate composition relationships (1:1, 1:many)
    if composition:
        lines.append('    %% Composition relationships')
        for rel in sorted(composition, key=lambda x: (x['from'], x['to'])):
            # Use class diagram syntax with cardinality labels
            if rel['cardinality'] == '1:1':
                lines.append(f"    {rel['from']} \"1\" --> \"1\" {rel['to']}")
            else:  # 1:many
                lines.append(f"    {rel['from']} \"1\" --> \"*\" {rel['to']}")
        lines.append('')

    # Generate association relationships (many:many)
    if association:
        lines.append('    %% Association relationships (many-to-many)')
        # Deduplicate bidirectional associations
        seen = set()
        for rel in sorted(association, key=lambda x: (x['from'], x['to'])):
            pair = tuple(sorted([rel['from'], rel['to']]))
            if pair not in seen:
                seen.add(pair)
                lines.append(f"    {rel['from']} \"*\" --> \"*\" {rel['to']}")
        lines.append('')

    lines.append('```')

    return '\n'.join(lines)


def main():
    """Generate and save Mermaid diagram."""
    print("Extracting model information...")
    model_info = extract_model_info()

    print(f"Found {len(model_info['entities'])} entities")
    print(f"Found {len(model_info['inheritance'])} inheritance relationships")
    print(f"Found {len(model_info['composition'])} composition relationships")
    print(f"Found {len(model_info['association'])} association relationships")

    print("\nGenerating Mermaid diagram...")
    mermaid_code = generate_mermaid(model_info)

    # Save to file
    output_path = Path(__file__).parent.parent.parent / 'docs' / 'diagrams' / 'data-model.md'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open('w') as f:
        f.write('# MNEMOSYS Data Model\n\n')
        f.write('Auto-generated diagram showing entity relationships.\n\n')
        f.write(mermaid_code)

    print(f"\nDiagram saved to: {output_path}")
    print("\nPreview:")
    print(mermaid_code)


if __name__ == '__main__':
    main()
