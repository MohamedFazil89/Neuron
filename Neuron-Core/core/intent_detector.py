# core/intent_detector.py
import re
from typing import Literal

class IntentDetector:
    """
    Detect if user request is:
    - FEATURE: "Add/Create/Implement something new"
    - ANALYSIS: "Verify/Analyze/Report on existing code"
    """
    
    # Keywords that indicate ANALYSIS intent
    ANALYSIS_KEYWORDS = {
        'verify', 'check', 'audit', 'analyze', 'report', 'scan',
        'inspect', 'test', 'validate', 'review', 'examine', 'diagnose',
        'find', 'identify', 'detect', 'list', 'show', 'display',
        'unused', 'unreachable', 'broken', 'error', 'problem',
        'issue', 'bug', 'conflict', 'redundant', 'duplicate'
    }
    
    # Keywords that indicate FEATURE intent
    FEATURE_KEYWORDS = {
        'add', 'create', 'build', 'implement', 'develop', 'generate',
        'new', 'feature', 'page', 'component', 'endpoint', 'api',
        'function', 'module', 'system', 'integration', 'workflow'
    }
    
    @staticmethod
    def detect(request: str) -> Literal["FEATURE", "ANALYSIS"]:
        """
        Detect request intent
        
        Args:
            request: User's natural language request
        
        Returns:
            "FEATURE" or "ANALYSIS"
        """
        
        # Convert to lowercase for matching
        lower_request = request.lower()
        
        # Count keyword matches
        analysis_score = 0
        feature_score = 0
        
        # Check for analysis keywords
        for keyword in IntentDetector.ANALYSIS_KEYWORDS:
            if keyword in lower_request:
                analysis_score += 1
        
        # Check for feature keywords
        for keyword in IntentDetector.FEATURE_KEYWORDS:
            if keyword in lower_request:
                feature_score += 1
        
        # Decide based on scores
        if analysis_score > feature_score:
            return "ANALYSIS"
        elif feature_score > analysis_score:
            return "FEATURE"
        else:
            # Tie-breaker: Check for specific patterns
            if re.search(r'(all files|unused|dead code|broken|error|problem)', lower_request, re.IGNORECASE):
                return "ANALYSIS"
            else:
                return "FEATURE"
    
    @staticmethod
    def explain(request: str) -> dict:
        """
        Provide detailed analysis of intent
        
        Returns:
            {
                "intent": "FEATURE" | "ANALYSIS",
                "confidence": 0-1,
                "analysis_keywords_found": [...],
                "feature_keywords_found": [...]
            }
        """
        
        lower_request = request.lower()
        
        analysis_found = [k for k in IntentDetector.ANALYSIS_KEYWORDS if k in lower_request]
        feature_found = [k for k in IntentDetector.FEATURE_KEYWORDS if k in lower_request]
        
        intent = IntentDetector.detect(request)
        
        total_matches = len(analysis_found) + len(feature_found)
        confidence = (max(len(analysis_found), len(feature_found)) / total_matches) if total_matches > 0 else 0.5
        
        return {
            "intent": intent,
            "confidence": confidence,
            "analysis_keywords_found": analysis_found,
            "feature_keywords_found": feature_found
        }