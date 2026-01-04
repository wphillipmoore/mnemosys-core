"""
Render IAM policy and trust templates with account-specific values.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PLACEHOLDER_PATTERN = re.compile(r"__\\S+__")


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Render IAM template files.")
    parser.add_argument("--template-dir", default="infra/iam", dest="template_dir")
    parser.add_argument("--output-dir", required=True, dest="output_dir")
    parser.add_argument("--aws-account-id", required=True, dest="aws_account_id")
    parser.add_argument("--aws-region", required=True, dest="aws_region")
    parser.add_argument("--github-org", required=True, dest="github_org")
    parser.add_argument("--github-repo", required=True, dest="github_repo")
    return parser.parse_args()


def render_template(template_text: str, replacements: dict[str, str]) -> str:
    """Apply placeholder replacements to the template text."""
    rendered_text = template_text
    for placeholder, value in replacements.items():
        if placeholder in rendered_text:
            rendered_text = rendered_text.replace(placeholder, value)

    remaining = sorted(set(PLACEHOLDER_PATTERN.findall(rendered_text)))
    if remaining:
        raise SystemExit(f"Unrendered placeholders remain: {', '.join(remaining)}")
    return rendered_text


def main() -> int:
    """Entry point for template rendering."""
    arguments = parse_arguments()
    template_dir = Path(arguments.template_dir)
    output_dir = Path(arguments.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    replacements = {
        "__AWS_ACCOUNT_ID__": arguments.aws_account_id,
        "__AWS_REGION__": arguments.aws_region,
        "__GITHUB_ORG__": arguments.github_org,
        "__GITHUB_REPO__": arguments.github_repo,
    }

    template_paths = sorted(template_dir.glob("*.json"))
    if not template_paths:
        raise SystemExit(f"No JSON templates found in {template_dir}")

    for template_path in template_paths:
        template_text = template_path.read_text(encoding="utf-8")
        rendered_text = render_template(template_text, replacements)
        try:
            rendered_payload = json.loads(rendered_text)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON after rendering {template_path}: {exc}") from exc

        output_path = output_dir / template_path.name
        output_path.write_text(json.dumps(rendered_payload, indent=2) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
