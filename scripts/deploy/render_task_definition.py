"""
Render an ECS task definition template with runtime values.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PLACEHOLDER_PATTERN = re.compile(r"__\\S+__")


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Render ECS task definition template.")
    parser.add_argument("--template", dest="template_path", required=True)
    parser.add_argument("--output", dest="output_path", required=True)
    parser.add_argument("--environment", dest="environment_name", required=True)
    parser.add_argument("--image-uri", dest="image_uri", required=True)
    parser.add_argument("--execution-role-arn", dest="execution_role_arn", required=True)
    parser.add_argument("--task-role-arn", dest="task_role_arn", required=True)
    parser.add_argument("--log-group", dest="log_group", required=True)
    parser.add_argument("--aws-region", dest="aws_region", required=True)
    return parser.parse_args()


def render_template(template_text: str, replacements: dict[str, str]) -> str:
    """Apply placeholder replacements to the template text."""
    rendered_text = template_text
    for placeholder, value in replacements.items():
        if placeholder not in rendered_text:
            raise SystemExit(f"Missing placeholder in template: {placeholder}")
        rendered_text = rendered_text.replace(placeholder, value)

    remaining = sorted(set(PLACEHOLDER_PATTERN.findall(rendered_text)))
    if remaining:
        raise SystemExit(f"Unrendered placeholders remain: {', '.join(remaining)}")
    return rendered_text


def main() -> int:
    """Entry point for template rendering."""
    arguments = parse_arguments()
    template_path = Path(arguments.template_path)
    output_path = Path(arguments.output_path)

    template_text = template_path.read_text(encoding="utf-8")
    replacements = {
        "__ENVIRONMENT__": arguments.environment_name,
        "__IMAGE_URI__": arguments.image_uri,
        "__EXECUTION_ROLE_ARN__": arguments.execution_role_arn,
        "__TASK_ROLE_ARN__": arguments.task_role_arn,
        "__LOG_GROUP__": arguments.log_group,
        "__AWS_REGION__": arguments.aws_region,
    }

    rendered_text = render_template(template_text, replacements)
    try:
        rendered_payload = json.loads(rendered_text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Rendered task definition is invalid JSON: {exc}") from exc

    output_path.write_text(json.dumps(rendered_payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
