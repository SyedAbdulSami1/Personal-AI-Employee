# Professional standard implementation | Global GEMINI.md
"""
AuditLogic — Pattern matching for transaction analysis.
Identifies subscriptions and categorizes expenses for the CEO Briefing.
"""
import logging
from typing import Dict, Optional, List, Any

logger = logging.getLogger(__name__)

# Required SUBSCRIPTION_PATTERNS from teacher-requirement.md
SUBSCRIPTION_PATTERNS = {
    'netflix.com': 'Netflix',
    'spotify.com': 'Spotify',
    'adobe.com': 'Adobe Creative Cloud',
    'notion.so': 'Notion',
    'slack.com': 'Slack',
    'google.com/storage': 'Google One',
    'anthropic.com': 'Claude Pro',
    'openai.com': 'ChatGPT Plus',
    'github.com': 'GitHub Copilot',
    'cursor.com': 'Cursor AI',
    'amazon.com/prime': 'Amazon Prime',
    'linkedin.com/premium': 'LinkedIn Premium'
}

class AuditLogic:
    """Logic for analyzing bank transactions and identified cost optimizations."""

    def __init__(self):
        self.patterns = SUBSCRIPTION_PATTERNS

    def analyze_transaction(self, description: str, amount: float, date: str) -> Optional[Dict[str, Any]]:
        """
        Identify if a transaction is a known subscription.
        
        Args:
            description: Transaction description from bank
            amount: Transaction amount
            date: Transaction date (ISO format)
            
        Returns:
            Subscription info dict or None
        """
        desc_lower = description.lower()
        for pattern, name in self.patterns.items():
            if pattern in desc_lower:
                return {
                    'type': 'subscription',
                    'name': name,
                    'amount': amount,
                    'date': date,
                    'pattern': pattern
                }
        return None

    def find_cost_optimizations(self, transactions: List[Dict[str, Any]], inactive_threshold_days: int = 30) -> List[Dict[str, Any]]:
        """
        Identify potential cost savings (e.g., unused subscriptions).
        
        Note: In a real system, this would check 'last_login' or usage metrics.
        For the hackathon, we simulate identification of 'no activity'.
        """
        optimizations = []
        
        # Example simulation: Notion hasn't been used
        for tx in transactions:
            if tx.get('name') == 'Notion' and tx.get('days_since_active', 0) > inactive_threshold_days:
                optimizations.append({
                    'tool': 'Notion',
                    'cost': tx.get('amount', 15.0),
                    'reason': f"No team activity in {tx.get('days_since_active')} days",
                    'suggestion': "Cancel subscription? Move to /Pending_Approval"
                })
        
        return optimizations

# Global instance
audit_logic = AuditLogic()
