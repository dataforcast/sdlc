"""Unit tests for the mock AI classification/drafting module."""

import pytest

from app.mock_ai import classify_and_draft
from app.models import Category, Priority


def test_billing_keyword_classifies_as_billing() -> None:
    result = classify_and_draft("I was charged twice on my last invoice")
    assert result.category == Category.BILLING


def test_technical_keyword_classifies_as_technical() -> None:
    result = classify_and_draft("The app crashes with an error every time")
    assert result.category == Category.TECHNICAL


def test_unmatched_text_classifies_as_other() -> None:
    result = classify_and_draft("I have a general comment about your service")
    assert result.category == Category.OTHER


def test_urgent_keyword_yields_high_priority() -> None:
    result = classify_and_draft("This is urgent, my account is down")
    assert result.priority == Priority.HIGH


def test_low_urgency_keyword_yields_low_priority() -> None:
    result = classify_and_draft("Just wondering, no rush, about pricing")
    assert result.priority == Priority.LOW


def test_default_priority_is_medium() -> None:
    result = classify_and_draft("I would like to update my mailing address on file")
    assert result.priority == Priority.MEDIUM


def test_blank_text_raises() -> None:
    with pytest.raises(ValueError):
        classify_and_draft("   ")


def test_draft_text_is_non_empty() -> None:
    result = classify_and_draft("My invoice amount looks wrong")
    assert result.draft_text.strip() != ""
