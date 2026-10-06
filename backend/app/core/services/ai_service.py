"""
AI service - handles AI-powered ticket triage and response generation.

This service provides:
- Ticket classification (category and priority)
- AI-generated suggested responses

Note: This is a mock implementation. In production, this would integrate
with an actual AI/ML service or LLM API.
"""

import random
from typing import Dict, Optional

from backend.app.core.models.ticket import Category, Priority


# Keyword mappings for mock classification
CATEGORY_KEYWORDS: Dict[Category, list] = {
    Category.BILLING: ['bill', 'payment', 'invoice', 'charge', 'billing', 'fee', 'price', 'cost'],
    Category.TECHNICAL: ['bug', 'error', 'crash', 'technical', 'issue', 'problem', 'not working', 'broken'],
    Category.ACCOUNT: ['account', 'login', 'password', 'user', 'profile', 'register', 'sign up', 'credentials'],
    Category.OTHER: [],
}


class AIService:
    """
    Service for AI-powered ticket processing.
    
    Provides classification and response generation capabilities.
    """

    def triage(self, ticket_text: str) -> dict:
        """
        Classify a ticket and generate a suggested answer.
        
        Args:
            ticket_text: The text content of the ticket to process
            
        Returns:
            Dictionary containing:
            - category: Classified category (Category enum value)
            - priority: Classified priority (Priority enum value)
            - suggested_answer: AI-generated response suggestion
            
        Raises:
            ValueError: If ticket_text is empty or None
        """
        if not ticket_text or not ticket_text.strip():
            raise ValueError("Ticket text cannot be empty")
        
        text_lower = ticket_text.lower()
        
        # Determine category based on keywords
        category = self._classify_category(text_lower)
        
        # Determine priority (mock - in production could use text analysis)
        priority = self._classify_priority(text_lower)
        
        # Generate suggested answer
        suggested_answer = self._generate_suggestion(ticket_text, category)
        
        return {
            "category": category.value,
            "priority": priority.value,
            "suggested_answer": suggested_answer
        }

    def _classify_category(self, text: str) -> Category:
        """
        Classify ticket text into a category based on keywords.
        
        Args:
            text: Lowercase ticket text
            
        Returns:
            Category enum value
        """
        for category, keywords in CATEGORY_KEYWORDS.items():
            if category == Category.OTHER:
                continue
            if any(keyword in text for keyword in keywords):
                return category
        return Category.OTHER

    def _classify_priority(self, text: str) -> Priority:
        """
        Classify ticket priority based on text content.
        
        This is a mock implementation. In production, this could use:
        - Sentiment analysis
        - Keyword detection (urgent, critical, etc.)
        - ML classification
        
        Args:
            text: Lowercase ticket text
            
        Returns:
            Priority enum value
        """
        # Check for urgent indicators
        urgent_keywords = ['urgent', 'critical', 'emergency', 'immediately', 'asap', 'down']
        if any(keyword in text for keyword in urgent_keywords):
            return Priority.HIGH
        
        # Check for high priority indicators
        high_keywords = ['error', 'not working', 'broken', 'problem', 'issue', 'bug']
        if any(keyword in text for keyword in high_keywords):
            return Priority.HIGH
        
        # Default to random for mock
        return random.choice([Priority.LOW, Priority.MEDIUM, Priority.HIGH])

    def _generate_suggestion(self, ticket_text: str, category: Category) -> str:
        """
        Generate a mock AI suggestion based on ticket text and category.
        
        Args:
            ticket_text: Original ticket text
            category: Detected category
            
        Returns:
            Suggested response text
        """
        # Truncate text for suggestion
        text_preview = ticket_text[:100] + "..." if len(ticket_text) > 100 else ticket_text
        
        templates = {
            Category.BILLING: (
                "Thank you for reaching out regarding your billing concern. "
                "We've reviewed your account and can see the issue. "
                "Our billing team will process this within 24-48 hours. "
                "In the meantime, your current services will remain active."
            ),
            Category.TECHNICAL: (
                "We apologize for the technical issue you're experiencing. "
                "Our engineering team has been notified and is investigating. "
                "We'll provide an update within 4 hours. "
                "If this is urgent, please call our support line."
            ),
            Category.ACCOUNT: (
                "Thank you for contacting us about your account. "
                "We can help you resolve this quickly. "
                "Please verify your identity by replying with your account email. "
                "We'll then assist you with the next steps."
            ),
            Category.OTHER: (
                "Thank you for your message. "
                "We've received your request and will review it shortly. "
                "A support agent will respond within 24 hours. "
                "For faster service, please provide any additional details."
            ),
        }
        
        # Get base template for category
        suggestion = templates.get(category, templates[Category.OTHER])
        
        # Add ticket-specific context
        suggestion = f"Based on your request: '{text_preview}'\n\n{suggestion}"
        
        return suggestion
