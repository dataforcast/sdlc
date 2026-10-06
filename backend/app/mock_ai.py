"""Mock AI service simulating ticket classification and answer drafting.

Deliberately offline and deterministic (keyword-based, no randomness) so it
remains reproducible in unit tests. Isolated behind classify_and_draft() so a
real LLM call could later replace the implementation without touching
routers, the FSM, or the ticket store.
"""

from pydantic import BaseModel, ConfigDict

from app.models import Category, Priority

_CATEGORY_KEYWORDS: dict[Category, tuple[str, ...]] = {
    Category.BILLING: ("invoice", "charge", "payment", "refund", "bill", "subscription", "price"),
    Category.TECHNICAL: ("error", "bug", "crash", "not working", "fails", "exception", "login issue", "broken"),
    Category.ACCOUNT: ("password", "account", "profile", "email change", "username", "access"),
}

_URGENT_KEYWORDS: tuple[str, ...] = (
    "urgent",
    "asap",
    "immediately",
    "critical",
    "down",
    "cannot access",
    "can't access",
    "blocked",
)

_LOW_URGENCY_KEYWORDS: tuple[str, ...] = (
    "question",
    "just wondering",
    "no rush",
    "whenever",
    "curious",
)


class MockAIResult(BaseModel):
    """Validated output of the mock AI classification/drafting step."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    category: Category
    priority: Priority
    draft_text: str


def _classify_category(text_lower: str) -> Category:
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return Category.OTHER


def _classify_priority(text_lower: str) -> Priority:
    if any(keyword in text_lower for keyword in _URGENT_KEYWORDS):
        return Priority.HIGH
    if any(keyword in text_lower for keyword in _LOW_URGENCY_KEYWORDS):
        return Priority.LOW
    return Priority.MEDIUM


def classify_and_draft(ticket_text: str) -> MockAIResult:
    """Derive category, priority and a draft answer from raw ticket text."""
    if not ticket_text.strip():
        raise ValueError("ticket_text must not be blank")

    text_lower = ticket_text.lower()
    category = _classify_category(text_lower)
    priority = _classify_priority(text_lower)
    draft_text = (
        f"Hello, thank you for reaching out. We understand your {category.value} "
        f"request and are treating it as {priority.value} priority. "
        "Here is a suggested next step: our team will review the details you "
        "provided and follow up shortly. (AI-drafted suggestion, please review "
        "before sending.)"
    )

    return MockAIResult(category=category, priority=priority, draft_text=draft_text)
