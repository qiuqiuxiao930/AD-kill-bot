"""Tests for the AI classifier module."""

import pytest

from detection.ai_classifier import AIClassifier, _SKLEARN_AVAILABLE


@pytest.mark.skipif(not _SKLEARN_AVAILABLE, reason="scikit-learn not installed")
class TestAIClassifier:
    def setup_method(self):
        self.clf = AIClassifier(confidence_threshold=0.5)

    def test_available(self):
        assert self.clf.available is True

    def test_scam_detected(self):
        result = self.clf.predict("加我微信稳赚不赔日收益300%")
        assert result is not None
        assert result["confidence"] > 0.5

    def test_normal_not_flagged(self):
        result = self.clf.predict("今天天气不错，大家周末愉快")
        assert result is None

    def test_empty_text(self):
        result = self.clf.predict("")
        assert result is None

    def test_high_threshold_filters(self):
        strict = AIClassifier(confidence_threshold=0.99)
        result = strict.predict("投资理财")
        # With very high threshold most borderline texts should pass through
        # This is a sanity check - the classifier may or may not flag it
        assert result is None or result["confidence"] >= 0.99
