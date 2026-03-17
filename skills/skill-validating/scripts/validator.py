#!/usr/bin/env python3
"""
skill-validating script
Official spec: stdin JSON -> stdout JSON, stderr errors
"""

import json
import sys
import io
import re
from pathlib import Path
from datetime import datetime

# Force UTF-8 on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def log_error(message: str):
    """Log error to stderr"""
    print(message, file=sys.stderr)


def validate_yaml_frontmatter(content: str) -> tuple:
    """Validate YAML frontmatter"""
    errors = []
    warnings = []

    # Check for frontmatter
    if not content.startswith('---'):
        errors.append("Missing YAML frontmatter (must start with ---)")
        return errors, warnings, {}

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        errors.append("Invalid YAML frontmatter format")
        return errors, warnings, {}

    yaml_content = match.group(1)

    # Parse simple key-value pairs
    config = {}
    for line in yaml_content.split('\n'):
        if ':' in line and not line.strip().startswith('#'):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if value.startswith('|'):
                # Multi-line value - mark as present but multi-line
                config[key] = "(multi-line)"
                continue
            config[key] = value

    # Validate required fields
    required = ['name', 'description']
    for field in required:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    # Validate name format
    if 'name' in config:
        name = config['name']
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Invalid name format '{name}': use lowercase letters, numbers, and hyphens only")
        if '_' in name:
            warnings.append(f"Name '{name}' contains underscore, consider using hyphen")

    # Validate description length
    if 'description' in config:
        desc = config['description']
        if len(desc) > 1024:
            warnings.append(f"Description is {len(desc)} chars, max 1024 recommended")

    return errors, warnings, config


def validate_structure(skill_path: Path) -> tuple:
    """Validate skill directory structure"""
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return errors, warnings

    # Check content
    try:
        content = skill_md.read_text(encoding='utf-8')
    except Exception as e:
        errors.append(f"Cannot read SKILL.md: {e}")
        return errors, warnings

    # Validate frontmatter
    yaml_errors, yaml_warnings, config = validate_yaml_frontmatter(content)
    errors.extend(yaml_errors)
    warnings.extend(yaml_warnings)

    # Check if scripts exist
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        py_files = list(scripts_dir.glob("*.py"))
        if py_files:
            # Check script quality
            for script in py_files:
                try:
                    script_content = script.read_text(encoding='utf-8')
                    if 'json.load(sys.stdin)' not in script_content:
                        warnings.append(f"Script {script.name} may not read from stdin")
                    if 'json.dumps' not in script_content:
                        warnings.append(f"Script {script.name} may not output JSON")
                except Exception as e:
                    warnings.append(f"Cannot read script {script.name}: {e}")

    return errors, warnings


def validate_skill(config: dict) -> dict:
    """Validate a single skill"""
    skill_name = config.get("skill_name", "")
    skills_dir = Path.home() / ".claude" / "skills"

    result = {
        "status": "ok",
        "score": 100,
        "skill_name": skill_name,
        "errors": [],
        "warnings": [],
        "suggestions": [],
        "timestamp": datetime.now().isoformat()
    }

    if not skill_name:
        result["errors"].append("Missing skill_name in config")
        result["status"] = "error"
        result["score"] = 0
        return result

    skill_path = skills_dir / skill_name
    if not skill_path.exists():
        result["errors"].append(f"Skill not found: {skill_path}")
        result["status"] = "error"
        result["score"] = 0
        return result

    # Validate structure
    errors, warnings = validate_structure(skill_path)
    result["errors"] = errors
    result["warnings"] = warnings

    # Calculate score
    score = 100
    score -= len(errors) * 20
    score -= len(warnings) * 5
    result["score"] = max(0, score)

    if errors:
        result["status"] = "error"

    # Suggestions
    if not (skill_path / "reference").exists():
        result["suggestions"].append("Consider adding reference/ directory for documentation")

    return result


def validate_all_skills() -> dict:
    """Validate all skills in directory"""
    skills_dir = Path.home() / ".claude" / "skills"

    result = {
        "status": "ok",
        "total": 0,
        "passed": 0,
        "failed": 0,
        "details": [],
        "timestamp": datetime.now().isoformat()
    }

    for skill_path in skills_dir.iterdir():
        if not skill_path.is_dir():
            continue
        if skill_path.name.startswith('.'):
            continue

        result["total"] += 1
        skill_result = validate_skill({"skill_name": skill_path.name})

        detail = {
            "name": skill_path.name,
            "score": skill_result["score"],
            "status": skill_result["status"],
            "errors": len(skill_result["errors"]),
            "warnings": len(skill_result["warnings"])
        }
        result["details"].append(detail)

        if skill_result["status"] == "ok":
            result["passed"] += 1
        else:
            result["failed"] += 1

    return result


def main():
    """Main entry: read from stdin, output to stdout"""
    try:
        # Read config
        if sys.stdin.isatty():
            # Interactive mode - validate all
            result = validate_all_skills()
        else:
            config = json.load(sys.stdin)

            if config.get("validate_all"):
                result = validate_all_skills()
            else:
                result = validate_skill(config)

        # Output result
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # Exit code
        sys.exit(0 if result.get("status") == "ok" else 1)

    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON: {e}")
        print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}))
        sys.exit(1)

    except Exception as e:
        log_error(f"Error: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
