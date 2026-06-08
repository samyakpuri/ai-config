"""
Structural tests for the requirements-decompose plugin.
Validates frontmatter, cross-references, required sections, and schema correctness.

Run: pytest plugins/requirements-decompose/tests/ -v
"""

import json
import re
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).parent.parent
AGENTS_DIR = PLUGIN_ROOT / "agents"
SKILLS_DIR = PLUGIN_ROOT / "skills"
MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"

VALID_COLORS = {"blue", "cyan", "green", "yellow", "magenta", "red"}
VALID_MODELS = {"sonnet", "opus", "haiku"}

EXPECTED_AGENTS = {
    "req-classifier",
    "fw-decomposer",
    "backend-decomposer",
    "ui-decomposer",
    "api-contract",
    "component-mapper",
    "template-populator",
    "sys-diff",
}

EXPECTED_AGENT_COLORS = {
    "req-classifier": "blue",
    "fw-decomposer": "yellow",
    "backend-decomposer": "green",
    "ui-decomposer": "cyan",
    "api-contract": "magenta",
    "component-mapper": "red",
    "template-populator": "blue",  # shares blue with req-classifier (8 agents, 6 colors)
    "sys-diff": "cyan",  # shares cyan with ui-decomposer
}

AGENT_REQUIRED_SECTIONS = ["## Inputs", "## Workflow", "## Output format", "## Rules"]
SKILL_REQUIRED_SECTIONS = [
    "## Dependencies",
    "## Role",
    "## Input",
    "## Requirement ID Scheme",
    "## Workflow",
    "## Rules",
]


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter fields as a flat dict and return remaining body."""
    if not text.startswith("---"):
        return {}, text
    end = text.index("---", 3)
    fm_block = text[3:end].strip()
    body = text[end + 3:].strip()
    fields = {}
    for line in fm_block.splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip()
    return fields, body


def agent_files() -> list[Path]:
    return sorted(AGENTS_DIR.glob("*.md"))


def agent_name_from_file(path: Path) -> str:
    return path.stem


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

class TestManifest:
    def test_manifest_exists(self):
        assert MANIFEST.exists(), "plugin.json not found"

    def test_manifest_valid_json(self):
        MANIFEST.read_text(encoding="utf-8")  # would raise on read error
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_manifest_required_fields(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for field in ("name", "version", "description", "author"):
            assert field in data, f"manifest missing field: {field}"

    def test_manifest_name_kebab_case(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        name = data["name"]
        assert re.match(r"^[a-z][a-z0-9-]*$", name), f"name not kebab-case: {name}"

    def test_manifest_semver(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        version = data["version"]
        assert re.match(r"^\d+\.\d+\.\d+", version), f"version not semver: {version}"


# ---------------------------------------------------------------------------
# Agent presence
# ---------------------------------------------------------------------------

class TestAgentPresence:
    def test_all_expected_agents_exist(self):
        found = {p.stem for p in agent_files()}
        missing = EXPECTED_AGENTS - found
        assert not missing, f"missing agent files: {missing}"

    def test_no_unexpected_agents(self):
        found = {p.stem for p in agent_files()}
        extra = found - EXPECTED_AGENTS
        assert not extra, f"unexpected agent files (update EXPECTED_AGENTS if intentional): {extra}"

    def test_template_populator_has_write_tool(self):
        # template-populator is the only agent that needs Write — it populates skeleton docs.
        path = AGENTS_DIR / "template-populator.md"
        text = path.read_text(encoding="utf-8")
        assert "Write" in text, "template-populator must declare the Write tool"


# ---------------------------------------------------------------------------
# Agent frontmatter
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("agent_path", agent_files(), ids=lambda p: p.stem)
class TestAgentFrontmatter:
    def test_has_frontmatter(self, agent_path):
        text = agent_path.read_text(encoding="utf-8")
        assert text.startswith("---"), f"{agent_path.name}: missing frontmatter"

    def test_required_fields(self, agent_path):
        text = agent_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        for field in ("name", "description", "model", "color"):
            assert field in fm, f"{agent_path.name}: frontmatter missing '{field}'"

    def test_name_matches_filename(self, agent_path):
        text = agent_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        assert fm.get("name") == agent_path.stem, (
            f"{agent_path.name}: frontmatter name '{fm.get('name')}' "
            f"does not match filename '{agent_path.stem}'"
        )

    def test_valid_color(self, agent_path):
        text = agent_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        color = fm.get("color", "")
        assert color in VALID_COLORS, (
            f"{agent_path.name}: invalid color '{color}'. Must be one of {VALID_COLORS}"
        )

    def test_expected_color(self, agent_path):
        name = agent_path.stem
        if name not in EXPECTED_AGENT_COLORS:
            pytest.skip("agent not in expected color map")
        text = agent_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        expected = EXPECTED_AGENT_COLORS[name]
        assert fm.get("color") == expected, (
            f"{agent_path.name}: expected color '{expected}', got '{fm.get('color')}'"
        )

    def test_valid_model(self, agent_path):
        text = agent_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        model = fm.get("model", "")
        assert model in VALID_MODELS, (
            f"{agent_path.name}: invalid model '{model}'. Must be one of {VALID_MODELS}"
        )

    def test_has_two_examples(self, agent_path):
        text = agent_path.read_text(encoding="utf-8")
        count = text.count("<example>")
        assert count >= 2, f"{agent_path.name}: expected ≥2 <example> blocks, found {count}"

    def test_examples_have_commentary(self, agent_path):
        text = agent_path.read_text(encoding="utf-8")
        commentary_count = text.count("<commentary>")
        example_count = text.count("<example>")
        assert commentary_count >= example_count, (
            f"{agent_path.name}: each <example> should have a <commentary> block"
        )


# ---------------------------------------------------------------------------
# Agent body — required sections
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("agent_path", agent_files(), ids=lambda p: p.stem)
class TestAgentBody:
    def test_required_sections_present(self, agent_path):
        text = agent_path.read_text(encoding="utf-8")
        _, body = parse_frontmatter(text)
        for section in AGENT_REQUIRED_SECTIONS:
            assert section in body, f"{agent_path.name}: missing section '{section}'"

    def test_inferred_tag_defined(self, agent_path):
        text = agent_path.read_text(encoding="utf-8")
        assert "[INFERRED" in text, (
            f"{agent_path.name}: should reference [INFERRED] tagging convention"
        )

    def test_traceability_in_rules(self, agent_path):
        """Every agent that produces requirements must enforce traceability."""
        name = agent_path.stem
        if name == "req-classifier":
            pytest.skip("req-classifier produces SYS reqs, no upstream to trace")
        text = agent_path.read_text(encoding="utf-8")
        _, body = parse_frontmatter(text)
        rules_start = body.find("## Rules")
        if rules_start == -1:
            pytest.skip("no Rules section")
        rules = body[rules_start:]
        assert "trace" in rules.lower() or "SYS" in rules, (
            f"{agent_path.name}: Rules section should enforce traceability to parent reqs"
        )

    def test_no_hardcoded_absolute_paths(self, agent_path):
        text = agent_path.read_text(encoding="utf-8")
        # Flag Windows absolute paths that aren't $CLAUDE_PLUGIN_ROOT references
        bad = re.findall(r"[A-Za-z]:\\(?!.*CLAUDE_PLUGIN_ROOT)[\w\\]+", text)
        assert not bad, f"{agent_path.name}: hardcoded absolute paths found: {bad}"


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------

class TestSkill:
    @property
    def skill_path(self) -> Path:
        return SKILLS_DIR / "req-decompose" / "SKILL.md"

    def test_skill_exists(self):
        assert self.skill_path.exists()

    def test_skill_frontmatter_fields(self):
        text = self.skill_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        for field in ("name", "description", "argument-hint"):
            assert field in fm, f"SKILL.md missing frontmatter field '{field}'"

    def test_skill_name(self):
        text = self.skill_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        assert fm.get("name") == "req-decompose"

    def test_skill_description_third_person(self):
        text = self.skill_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        desc = fm.get("description", "")
        assert not desc.lstrip().startswith("Use this skill"), (
            "description should use third-person framing ('This skill should be used...'), "
            "not second-person ('Use this skill...')"
        )

    def test_skill_required_sections(self):
        text = self.skill_path.read_text(encoding="utf-8")
        _, body = parse_frontmatter(text)
        for section in SKILL_REQUIRED_SECTIONS:
            assert section in body, f"SKILL.md missing section '{section}'"

    def test_skill_references_all_agents(self):
        text = self.skill_path.read_text(encoding="utf-8")
        for agent_name in EXPECTED_AGENTS:
            assert agent_name in text, (
                f"SKILL.md does not reference agent '{agent_name}'"
            )

    def test_skill_argument_hint_has_domain_flag(self):
        text = self.skill_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        hint = fm.get("argument-hint", "")
        assert "--domain" in hint, "argument-hint should document --domain flag"

    def test_skill_argument_hint_has_scope_flag(self):
        text = self.skill_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        hint = fm.get("argument-hint", "")
        assert "--scope" in hint, "argument-hint should document --scope flag"

    def test_skill_req_id_scheme_complete(self):
        text = self.skill_path.read_text(encoding="utf-8")
        for prefix in ("SYS", "FW", "SW", "UI", "API", "COMP"):
            assert prefix in text, f"SKILL.md ID scheme missing prefix '{prefix}'"

    def test_skill_inferred_tag_defined(self):
        text = self.skill_path.read_text(encoding="utf-8")
        assert "[INFERRED]" in text

    def test_skill_ambiguous_tag_defined(self):
        text = self.skill_path.read_text(encoding="utf-8")
        assert "[AMBIGUOUS]" in text

    def test_skill_confirmation_gate_present(self):
        text = self.skill_path.read_text(encoding="utf-8")
        assert "confirmation" in text.lower() or "confirm" in text.lower(), (
            "SKILL.md should document user confirmation gate before decomposing"
        )


# ---------------------------------------------------------------------------
# Cross-plugin consistency
# ---------------------------------------------------------------------------

class TestCrossPluginConsistency:
    def test_agent_colors_mostly_distinct(self):
        # 7 agents, 6 valid colors — one share is acceptable.
        # Verify no color is used by more than 2 agents.
        from collections import Counter
        colors = Counter()
        for path in agent_files():
            text = path.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            color = fm.get("color")
            colors[color] += 1
        overused = {c: n for c, n in colors.items() if n > 2}
        assert not overused, f"colors used by >2 agents (reduce duplication): {overused}"

    def test_readme_references_all_agents(self):
        readme = PLUGIN_ROOT / "README.md"
        assert readme.exists()
        text = readme.read_text(encoding="utf-8")
        for name in EXPECTED_AGENTS:
            assert name in text, f"README.md does not mention agent '{name}'"

    def test_readme_documents_flags(self):
        readme = PLUGIN_ROOT / "README.md"
        text = readme.read_text(encoding="utf-8")
        for flag in ("--domain", "--scope", "--api-contract", "--arch", "--populate-templates"):
            assert flag in text, f"README.md does not document flag '{flag}'"

    def test_skill_has_arch_flag(self):
        skill = SKILLS_DIR / "req-decompose" / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        assert "--arch" in text, "SKILL.md missing --arch flag documentation"

    def test_skill_has_populate_templates_flag(self):
        skill = SKILLS_DIR / "req-decompose" / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        assert "--populate-templates" in text, "SKILL.md missing --populate-templates flag"

    def test_template_populator_no_modify_upstream(self):
        """template-populator must document that it never touches upstream docs."""
        path = AGENTS_DIR / "template-populator.md"
        text = path.read_text(encoding="utf-8")
        assert "Never modify" in text or "never modif" in text.lower(), (
            "template-populator must explicitly state it never modifies upstream (SYS/FW/SW/UI/API) docs"
        )

    def test_template_populator_idempotent(self):
        """template-populator must document idempotent behaviour."""
        path = AGENTS_DIR / "template-populator.md"
        text = path.read_text(encoding="utf-8")
        assert "idempotent" in text.lower() or "already present" in text.lower(), (
            "template-populator should document idempotent re-run behaviour"
        )

    def test_skill_argument_hint_has_arch_flag(self):
        text = (SKILLS_DIR / "req-decompose" / "SKILL.md").read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        assert "--arch" in fm.get("argument-hint", ""), "argument-hint missing --arch"

    def test_skill_argument_hint_has_populate_templates_flag(self):
        text = (SKILLS_DIR / "req-decompose" / "SKILL.md").read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        assert "--populate-templates" in fm.get("argument-hint", ""), \
            "argument-hint missing --populate-templates"

    def test_skill_has_baseline_flag(self):
        skill = SKILLS_DIR / "req-decompose" / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        assert "--baseline" in text, "SKILL.md missing --baseline flag documentation"

    def test_skill_argument_hint_has_baseline_flag(self):
        text = (SKILLS_DIR / "req-decompose" / "SKILL.md").read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        assert "--baseline" in fm.get("argument-hint", ""), "argument-hint missing --baseline"

    def test_sys_diff_references_baseline(self):
        path = AGENTS_DIR / "sys-diff.md"
        text = path.read_text(encoding="utf-8")
        assert "baseline" in text.lower(), "sys-diff should reference baseline input"

    def test_sys_diff_dispatched_conditionally(self):
        """sys-diff must only be dispatched when --baseline is provided, per SKILL.md."""
        skill = SKILLS_DIR / "req-decompose" / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        assert "sys-diff" in text, "SKILL.md must reference sys-diff agent"
        assert "--baseline" in text, "SKILL.md must document --baseline flag condition for sys-diff"
