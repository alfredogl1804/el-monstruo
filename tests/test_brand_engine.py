"""
El Monstruo — Brand Engine Tests (Sprint 52)
==============================================
Tests for brand_dna.py and validator.py.
Includes Cowork's 23 parametric cases for validate_output_name.
"""

import pytest

from kernel.brand.brand_dna import (
    BRAND_DNA,
    _tokenize_identifier,
    get_error_message,
    get_forbidden_matches,
    is_generic_error,
    validate_output_name,
)
from kernel.brand.validator import BrandAuditReport, BrandValidationResult, BrandValidator


# ═══════════════════════════════════════════════════════════════════════
# BRAND DNA — Structure Tests
# ═══════════════════════════════════════════════════════════════════════


class TestBrandDNAStructure:
    """Verify BRAND_DNA dict has all required keys and values."""

    def test_has_mission(self):
        assert "mission" in BRAND_DNA
        assert len(BRAND_DNA["mission"]) > 20

    def test_has_vision(self):
        assert "vision" in BRAND_DNA
        assert len(BRAND_DNA["vision"]) > 20

    def test_has_archetype(self):
        assert BRAND_DNA["archetype"] == "creator_mage"

    def test_has_personality_traits(self):
        traits = BRAND_DNA["personality"]
        assert len(traits) == 4
        assert "implacable" in traits
        assert "preciso" in traits
        assert "soberano" in traits

    def test_has_tone_do_and_dont(self):
        assert "do" in BRAND_DNA["tone"]
        assert "dont" in BRAND_DNA["tone"]
        assert len(BRAND_DNA["tone"]["do"]) >= 4
        assert len(BRAND_DNA["tone"]["dont"]) >= 4

    def test_has_naming_rules(self):
        naming = BRAND_DNA["naming"]
        assert "modules" in naming
        assert "error_format" in naming
        assert "never" in naming
        assert len(naming["never"]) >= 6

    def test_has_visual_palette(self):
        visual = BRAND_DNA["visual"]
        assert visual["primary"] == "#F97316"
        assert visual["background"] == "#1C1917"
        assert visual["accent"] == "#A8A29E"

    def test_has_anti_patterns(self):
        assert len(BRAND_DNA["anti_patterns"]) >= 5


# ═══════════════════════════════════════════════════════════════════════
# BRAND DNA — _tokenize_identifier (Cowork patch)
# ═══════════════════════════════════════════════════════════════════════


class TestTokenizeIdentifier:
    """Test the tokenizer that underpins all naming validation."""

    def test_snake_case(self):
        assert _tokenize_identifier("data_handler") == ["data", "handler"]

    def test_camel_case(self):
        assert _tokenize_identifier("MyHelper") == ["my", "helper"]

    def test_upper_acronym(self):
        assert _tokenize_identifier("URLParser") == ["url", "parser"]

    def test_simple_word(self):
        assert _tokenize_identifier("forja") == ["forja"]

    def test_kebab_case(self):
        assert _tokenize_identifier("embrion-loop") == ["embrion", "loop"]

    def test_dot_notation(self):
        assert _tokenize_identifier("api.utils.helper") == ["api", "utils", "helper"]

    def test_empty_string(self):
        assert _tokenize_identifier("") == []

    def test_none(self):
        assert _tokenize_identifier(None) == []

    def test_mixed_separators(self):
        tokens = _tokenize_identifier("my_great-module.v2")
        assert "my" in tokens
        assert "great" in tokens
        assert "module" in tokens


# ═══════════════════════════════════════════════════════════════════════
# BRAND DNA — validate_output_name (Cowork's 23 parametric cases)
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("name,expected_compliant", [
    # Compliant
    ("forja", True),
    ("embrion_loop", True),
    ("forja_dashboard", True),
    ("MagnaClassifier", True),
    ("multi_agent", True),
    ("tool_broker", True),
    # Non-compliant — directo
    ("handler", False),
    ("service", False),
    ("manager", False),
    # Non-compliant — snake_case (bug histórico)
    ("data_handler", False),
    ("user_service", False),
    ("dispatch_handler", False),
    ("utils_helper", False),
    ("service_module", False),
    # Non-compliant — camelCase
    ("MyHelper", False),
    ("messageManager", False),
    ("URLHelper", False),
    # Non-compliant — kebab-case y dot.notation
    ("event-handler", False),
    ("api.utils.helper", False),
    # Edge cases
    ("", False),
    (None, False),
    ("forjA", True),  # case insensitive sí, pero "forja" no es prohibido
])
def test_validate_output_name(name, expected_compliant):
    assert validate_output_name(name) == expected_compliant


# ═══════════════════════════════════════════════════════════════════════
# BRAND DNA — get_forbidden_matches (Cowork's cases)
# ═══════════════════════════════════════════════════════════════════════


def test_get_forbidden_matches_returns_unique_lowercase():
    assert get_forbidden_matches("user_service") == ["service"]
    assert get_forbidden_matches("HandlerHelper") == ["handler", "helper"]
    assert get_forbidden_matches("forja") == []
    assert get_forbidden_matches("ManagerManager") == ["manager"]  # dedupe


class TestGetForbiddenMatches:
    def test_no_matches(self):
        assert get_forbidden_matches("embrion_loop") == []

    def test_single_match(self):
        matches = get_forbidden_matches("user_service")
        assert "service" in matches

    def test_multiple_matches(self):
        matches = get_forbidden_matches("service_handler_utils")
        assert len(matches) == 3


# ═══════════════════════════════════════════════════════════════════════
# BRAND DNA — get_error_message
# ═══════════════════════════════════════════════════════════════════════


class TestGetErrorMessage:
    def test_basic_error(self):
        err = get_error_message("embrion", "classify", "timeout")
        assert err["error"] == "embrion_classify_timeout"
        assert err["module"] == "embrion"
        assert err["action"] == "classify"
        assert err["failure_type"] == "timeout"

    def test_with_context(self):
        err = get_error_message("magna", "score", "invalid_input", {"input": "x"})
        assert err["context"] == {"input": "x"}

    def test_has_suggestion(self):
        err = get_error_message("guardian", "audit", "not_found")
        assert "guardian" in err["suggestion"]
        assert "not_found" in err["suggestion"]


# ═══════════════════════════════════════════════════════════════════════
# BRAND DNA — is_generic_error
# ═══════════════════════════════════════════════════════════════════════


class TestIsGenericError:
    def test_generic_errors_detected(self):
        assert is_generic_error("internal server error") is True
        assert is_generic_error("something went wrong") is True
        assert is_generic_error("unknown error") is True
        assert is_generic_error("error") is True

    def test_branded_errors_pass(self):
        assert is_generic_error("embrion_classify_timeout") is False
        assert is_generic_error("magna_score_invalid_input") is False

    def test_empty_string(self):
        assert is_generic_error("") is False

    def test_none(self):
        assert is_generic_error(None) is False


# ═══════════════════════════════════════════════════════════════════════
# BRAND VALIDATOR — Output Name
# ═══════════════════════════════════════════════════════════════════════


class TestBrandValidatorOutputName:
    def setup_method(self):
        self.v = BrandValidator(threshold=60)

    def test_valid_name_passes(self):
        result = self.v.validate_output_name("BrandValidator")
        assert result.passes is True
        assert result.score == 100

    def test_forbidden_name_penalized(self):
        result = self.v.validate_output_name("user_service")
        assert result.score <= 75
        assert len(result.issues) > 0
        assert "service" in result.issues[0].lower()

    def test_empty_name_fails(self):
        result = self.v.validate_output_name("")
        assert result.passes is False
        assert result.score == 0


# ═══════════════════════════════════════════════════════════════════════
# BRAND VALIDATOR — Endpoint Name
# ═══════════════════════════════════════════════════════════════════════


class TestBrandValidatorEndpoint:
    def setup_method(self):
        self.v = BrandValidator(threshold=60)

    def test_versioned_endpoint_passes(self):
        result = self.v.validate_endpoint_name("/v1/brand/dna")
        assert result.passes is True
        assert result.score >= 85

    def test_unversioned_penalized(self):
        result = self.v.validate_endpoint_name("/api/users")
        assert result.score < 100
        assert any("versionado" in i for i in result.issues)

    def test_forbidden_term_in_path(self):
        result = self.v.validate_endpoint_name("/v1/service/health")
        assert result.score < 100
        assert any("prohibido" in i.lower() for i in result.issues)

    def test_health_exempt_from_versioning(self):
        result = self.v.validate_endpoint_name("/health")
        assert result.score == 100


# ═══════════════════════════════════════════════════════════════════════
# BRAND VALIDATOR — Tool Spec
# ═══════════════════════════════════════════════════════════════════════


class TestBrandValidatorToolSpec:
    def setup_method(self):
        self.v = BrandValidator(threshold=60)

    def test_good_spec_passes(self):
        spec = {
            "name": "web_search",
            "description": "Search the web for real-time information",
            "category": "investigación",
        }
        result = self.v.validate_tool_spec(spec)
        assert result.passes is True
        assert result.score >= 80

    def test_missing_name_penalized(self):
        spec = {"description": "Does something", "category": "x"}
        result = self.v.validate_tool_spec(spec)
        assert result.score < 100

    def test_missing_description_penalized(self):
        spec = {"name": "web_search", "category": "x"}
        result = self.v.validate_tool_spec(spec)
        assert result.score < 100

    def test_missing_category_penalized(self):
        spec = {"name": "web_search", "description": "Search the web for info"}
        result = self.v.validate_tool_spec(spec)
        assert result.score < 100

    def test_forbidden_name_in_tool(self):
        spec = {
            "name": "task_manager",
            "description": "Manages tasks",
            "category": "orquestación",
        }
        result = self.v.validate_tool_spec(spec)
        assert any("prohibido" in i.lower() for i in result.issues)


# ═══════════════════════════════════════════════════════════════════════
# BRAND VALIDATOR — Error Message
# ═══════════════════════════════════════════════════════════════════════


class TestBrandValidatorErrorMessage:
    def setup_method(self):
        self.v = BrandValidator(threshold=60)

    def test_branded_error_passes(self):
        result = self.v.validate_error_message("embrion_classify_timeout")
        assert result.passes is True
        assert result.score == 100

    def test_generic_error_penalized(self):
        result = self.v.validate_error_message("something went wrong")
        assert result.score < 100
        assert any("genérico" in i.lower() for i in result.issues)

    def test_empty_error_fails(self):
        result = self.v.validate_error_message("")
        assert result.passes is False


# ═══════════════════════════════════════════════════════════════════════
# BRAND VALIDATOR — Batch Audit
# ═══════════════════════════════════════════════════════════════════════


class TestBrandValidatorAudit:
    def setup_method(self):
        self.v = BrandValidator(threshold=60)

    def test_audit_tool_specs(self):
        specs = [
            {"name": "web_search", "description": "Search the web", "category": "investigación"},
            {"name": "consult_sabios", "description": "Consult AI council", "category": "orquestación"},
            {"name": "task_manager", "description": "Manage tasks", "category": "orquestación"},
        ]
        report = self.v.audit_tool_specs(specs)
        assert report.total == 3
        assert report.passed >= 2  # web_search and consult_sabios should pass
        assert isinstance(report.avg_score, float)

    def test_audit_endpoints(self):
        paths = ["/v1/brand/dna", "/v1/chat", "/api/users", "/health"]
        report = self.v.audit_endpoints(paths)
        assert report.total == 4

    def test_empty_audit(self):
        report = self.v.audit_tool_specs([])
        assert report.total == 0
        assert report.avg_score == 0.0


# ═══════════════════════════════════════════════════════════════════════
# BRAND VALIDATOR — Stats & Config
# ═══════════════════════════════════════════════════════════════════════


class TestBrandValidatorConfig:
    def test_default_threshold(self):
        v = BrandValidator()
        assert v.threshold == 60

    def test_custom_threshold(self):
        v = BrandValidator(threshold=75)
        assert v.threshold == 75

    def test_threshold_clamped(self):
        v = BrandValidator(threshold=150)
        assert v.threshold == 100
        v2 = BrandValidator(threshold=-10)
        assert v2.threshold == 0

    def test_stats(self):
        v = BrandValidator(threshold=60, mode="advisory")
        stats = v.stats
        assert stats["threshold"] == 60
        assert stats["mode"] == "advisory"
        assert stats["validations_total"] == 0

    def test_violations_counter(self):
        v = BrandValidator(threshold=100)  # Very strict — everything fails
        v.validate_output_name("user_service")  # score 75, threshold 100 → violation
        assert v.stats["violations_total"] >= 1


# ═══════════════════════════════════════════════════════════════════════
# RESULT TYPES
# ═══════════════════════════════════════════════════════════════════════


class TestResultTypes:
    def test_validation_result_to_dict(self):
        r = BrandValidationResult(
            target="test",
            target_type="output_name",
            score=85,
            issues=[],
            passes=True,
        )
        d = r.to_dict()
        assert d["target"] == "test"
        assert d["score"] == 85
        assert d["passes"] is True

    def test_audit_report_to_dict(self):
        r = BrandAuditReport(total=5, passed=4, failed=1, avg_score=88.0)
        d = r.to_dict()
        assert d["total"] == 5
        assert d["avg_score"] == 88.0
