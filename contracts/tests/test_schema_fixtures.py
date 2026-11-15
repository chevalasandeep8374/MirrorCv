"""Tests validating sample fixtures against JSON Schema specifications and Pydantic v2 models."""

import json
from pathlib import Path
import pytest
import jsonschema
from pydantic import ValidationError

from contracts.models import (
    ResumeContent,
    StyleTokens,
    TemplateProfile,
    TailoredContent,
    CompositionResult,
)

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = BASE_DIR / "schemas"
FIXTURES_DIR = BASE_DIR / "fixtures"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestContractSchemasAndFixtures:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.resume_schema = load_json(SCHEMAS_DIR / "resume_content.schema.json")
        self.style_schema = load_json(SCHEMAS_DIR / "style_tokens.schema.json")
        self.template_schema = load_json(SCHEMAS_DIR / "template_profile.schema.json")
        self.tailored_schema = load_json(SCHEMAS_DIR / "tailored_content.schema.json")
        self.composition_schema = load_json(SCHEMAS_DIR / "composition_result.schema.json")

    def test_resume_content_fixture(self):
        fixture = load_json(FIXTURES_DIR / "resume_content.fixture.json")
        # Validate against raw JSON Schema
        jsonschema.validate(instance=fixture, schema=self.resume_schema)

        # Validate against generated Pydantic v2 model
        model = ResumeContent.model_validate(fixture)
        assert model.schema_version.value == "1.0.0"
        assert model.header.name == "Alex Mercer"
        assert len(model.sections) == 3
        assert model.sections[1].type.value == "experience"
        assert len(model.sections[1].items[0].bullets) == 2

    def test_style_tokens_fixture(self):
        fixture = load_json(FIXTURES_DIR / "style_tokens.fixture.json")
        jsonschema.validate(instance=fixture, schema=self.style_schema)

        model = StyleTokens.model_validate(fixture)
        assert model.schema_version.value == "1.0.0"
        assert model.pageSize.value == "A4"
        assert model.margins.unit.value == "pt"
        assert model.typography.fontSizes.name == 22

    def test_template_profile_fixture(self):
        fixture = load_json(FIXTURES_DIR / "template_profile.fixture.json")
        jsonschema.validate(instance=fixture, schema=self.template_schema)

        model = TemplateProfile.model_validate(fixture)
        assert model.schema_version.value == "1.0.0"
        assert len(model.slots) == 3
        assert model.slots[0].role.value == "name"
        assert model.fidelity_score == 98.5

    def test_tailored_content_fixture(self):
        fixture = load_json(FIXTURES_DIR / "tailored_content.fixture.json")
        jsonschema.validate(instance=fixture, schema=self.tailored_schema)

        model = TailoredContent.model_validate(fixture)
        assert model.schema_version.value == "1.0.0"
        assert model.rules.no_new_facts_allowed.value is True
        assert len(model.changes) == 1
        assert model.changes[0].source_reference.is_grounded is True
        assert model.score_after > model.score_before

    def test_tailored_content_1_1_0_fixture(self):
        fixture = load_json(FIXTURES_DIR / "tailored_content_1_1_0.fixture.json")
        jsonschema.validate(instance=fixture, schema=self.tailored_schema)

        model = TailoredContent.model_validate(fixture)
        assert model.schema_version.value == "1.1.0"
        assert model.mode == "full"
        assert model.score_breakdown is not None
        assert model.score_breakdown.required_skill_coverage == 32.0
        assert model.generator.model == "gpt-4o"
        assert len(model.changes) == 1
        assert model.changes[0].target_content_id == "b-exp-1"
        assert len(model.suggestions) == 1
        assert model.suggestions[0].canonical_name == "Kubernetes"


    def test_composition_result_fixture(self):
        fixture = load_json(FIXTURES_DIR / "composition_result.fixture.json")
        jsonschema.validate(instance=fixture, schema=self.composition_schema)

        model = CompositionResult.model_validate(fixture)
        assert model.schema_version.value == "1.0.0"
        assert len(model.output_files) == 2
        assert model.overflow_report.has_overflow is False
        assert model.fidelity_score == 99.2

    def test_composition_result_1_1_0_fixture(self):
        fixture = load_json(FIXTURES_DIR / "composition_result_1_1_0.fixture.json")
        jsonschema.validate(instance=fixture, schema=self.composition_schema)

        model = CompositionResult.model_validate(fixture)
        assert model.schema_version.value == "1.1.0"
        assert model.status.value == "ready"
        assert model.integrity_report is not None
        assert model.integrity_report.passed is True
        assert len(model.integrity_report.invariants_checked) == 8
        assert model.page_count_preserved is True
        assert model.fit_loop.rounds_executed == 0

    def test_invalid_tailored_content_rejects_hallucinations(self):
        fixture = load_json(FIXTURES_DIR / "tailored_content.fixture.json")
        # Attempt to bypass anti-hallucination rule
        fixture["rules"]["no_new_facts_allowed"] = False
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=fixture, schema=self.tailored_schema)

    def test_invalid_resume_missing_section_id(self):
        fixture = load_json(FIXTURES_DIR / "resume_content.fixture.json")
        del fixture["sections"][0]["id"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=fixture, schema=self.resume_schema)
