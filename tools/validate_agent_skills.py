#!/usr/bin/env python3
"""Check repository skill metadata and local guidance links; not prose quality."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]\n]*\]\(([^\s)]+)\)")


def validate(root=ROOT):
    """Return structural errors for a documentation repository."""
    root = Path(root)
    errors = []
    skills_root = root / ".agents" / "skills"
    skill_files = sorted(skills_root.glob("*/SKILL.md"))
    if not skill_files:
        return ["No repository skills found."]

    guidance = [root / "AGENTS.md"]
    for source in skill_files:
        relative = source.relative_to(root)
        text = source.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
        if match is None:
            errors.append(f"{relative}: missing YAML frontmatter")
            continue
        try:
            data = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            errors.append(f"{relative}: invalid YAML: {error}")
            continue
        if not isinstance(data, dict) or set(data) != {"name", "description"}:
            errors.append(f"{relative}: frontmatter requires name and description only")
            continue
        name = data["name"]
        if (
            not isinstance(name, str)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
            or len(name) > 64
            or name != source.parent.name
        ):
            errors.append(f"{relative}: name must match its directory and naming rules")
        if not isinstance(data["description"], str) or not data["description"].strip():
            errors.append(f"{relative}: missing trigger description")

        metadata = source.parent / "agents" / "openai.yaml"
        try:
            ui = yaml.safe_load(metadata.read_text(encoding="utf-8"))["interface"]
            if not isinstance(ui, dict):
                raise ValueError("interface must be a mapping")
            for field in ("display_name", "short_description", "default_prompt"):
                if not isinstance(ui.get(field), str) or not ui[field].strip():
                    raise ValueError(f"missing {field}")
            if not 25 <= len(ui["short_description"]) <= 64:
                raise ValueError("short_description must contain 25–64 characters")
            if f"${name}" not in ui["default_prompt"]:
                raise ValueError("default_prompt must name the skill invocation")
        except (OSError, yaml.YAMLError, KeyError, TypeError, ValueError) as error:
            errors.append(f"{metadata.relative_to(root)}: {error}")
        guidance.extend(source.parent.rglob("*.md"))

    try:
        agent_text = (root / "AGENTS.md").read_text(encoding="utf-8")
        for source in skill_files:
            if source.relative_to(root).as_posix() not in agent_text:
                errors.append(f"AGENTS.md: missing route for {source.parent.name}")
    except OSError as error:
        errors.append(f"AGENTS.md: {error}")

    for source in sorted(set(guidance)):
        if not source.exists():
            continue
        for target in LINK.findall(source.read_text(encoding="utf-8")):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (source.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append(f"{source.relative_to(root)}: missing local link {target}")
    return errors


if __name__ == "__main__":
    findings = validate()
    if findings:
        print("\n".join(findings), file=sys.stderr)
        raise SystemExit(1)
    print("Agent skill metadata and local guidance links passed.")
