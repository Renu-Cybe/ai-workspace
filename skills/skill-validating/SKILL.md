---
name: skill-validating
description: |
  Validate Claude Code Skills for compliance with official specifications.
  Checks SKILL.md format, YAML frontmatter, directory structure, and script quality.
  Provides scoring and suggestions for improvement.

tools: [Read, Bash, Glob]
context: fork
---

# Skill Validating

## Purpose

Validate Skills against Claude Code official specifications to ensure compliance and quality.

## Usage Scenarios

- Validate a newly created Skill before deployment
- Batch validate all Skills in the directory
- Check specific file for syntax issues
- Quality gate before activation

## Usage

### 1. Validate Single Skill
```
User: "Validate skill-generating"
User: "Check if my-skill is compliant"
User: "Validate ~/.claude/skills/my-skill"
```

### 2. Validate All Skills
```
User: "Validate all skills"
User: "Check all skills for compliance"
```

### 3. Detailed Report
```
User: "Show detailed validation report"
User: "Check skill with full details"
```

## Workflow

1. **Receive Target**
   - Parse skill name or path from user input
   - Resolve full path

2. **Execute Validation**
   - Call `scripts/validator.py`
   - Check SKILL.md format
   - Validate YAML frontmatter
   - Verify directory structure
   - Score script quality

3. **Output Results**
   - Display validation score
   - List errors and warnings
   - Provide suggestions

## Validation Rules

| Rule | Description | Severity |
|------|-------------|----------|
| SKILL.md exists | Must have SKILL.md | Error |
| YAML frontmatter | Valid YAML with required fields | Error |
| Name format | Lowercase with hyphens | Warning |
| Scripts directory | Proper structure if scripts exist | Warning |
| Script quality | JSON I/O compliance | Info |

## Required Fields

SKILL.md must have:
- `name`: lowercase-hyphenated
- `description`: max 1024 chars, includes usage scenarios
- `tools`: list of available tools

## Output Format

```json
{
  "status": "ok|error",
  "score": 85,
  "skill_name": "my-skill",
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

## Example

**User**: "Validate skill-generating"

**Claude**: Running validation...
- Score: 95/100
- Status: Compliant
- 1 warning: description could be more detailed
