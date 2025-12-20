# agents/architect.py
from core.openai_client import call_openai_json
import json

ARCHITECT_SYSTEM_PROMPT = """You are the Architect agent. Your job is to decide WHAT will be built, not HOW nicely.

Your output is a CONTRACT. Every other agent must obey it exactly.

Rules:
1. Output ONLY valid JSON. No markdown. No explanations. No text outside JSON.
2. Be annoyingly specific. "Implement login" is not specific. List exact steps.
3. Freeze the API contract. Backend implements it. Frontend consumes it. No agent changes it.
4. Declare assumptions explicitly. What will be true when code runs.
5. Do NOT write code. Do NOT suggest libraries. Do NOT optimize.
6. Do NOT say "optionally", "could be", "might". Ambiguity is poison.

Your output schema (THIS IS THE ONLY THING YOU RETURN):
{
  "feature": "string - exact feature description",
  "api": {
    "method": "POST|GET|PUT|DELETE",
    "path": "/api/...",
    "request": { "field": "type" },
    "response": { "field": "type" },
    "errors": [
      { "status": 400, "reason": "..." },
      { "status": 401, "reason": "..." }
    ]
  },
  "backend_tasks": ["specific step 1", "specific step 2"],
  "frontend_tasks": ["specific step 1", "specific step 2"],
  "backend_files": ["path/to/file.js"],
  "frontend_files": ["path/to/file.jsx"],
  "assumptions": ["what must be true when code runs"]
}

Return ONLY this JSON. Nothing else. No markdown headers. No explanations."""

def architect_agent(feature):
    """
    Architect breaks down feature into a frozen contract.
    Input: feature (str) - raw feature request
    Output: dict - complete plan that all agents must follow
    This agent MUST NOT be creative. It must be explicit.
    """
    
    prompt = f"""
Feature request: {feature}

Tech stack:
- Frontend: React (create-react-app)
- Backend: Express.js
- Testing: Jest

Create a complete contract that defines EXACTLY what will be built.
Be specific:
- What are the exact endpoints?
- What are the exact request/response schemas?
- What are the exact tasks?
- What assumptions must be true?

Do not be vague. Ambiguity breaks downstream agents.

Return the JSON contract exactly as specified in the system prompt.
"""
    
    print(f"[ARCHITECT] Analyzing: {feature}")
    
    try:
        result = call_openai_json(prompt, max_tokens=2000, system_prompt=ARCHITECT_SYSTEM_PROMPT)
        
        # Validate output has required fields
        required_fields = ["feature", "api", "backend_tasks", "frontend_tasks",
                          "backend_files", "frontend_files", "assumptions"]
        missing = [f for f in required_fields if f not in result]
        
        if missing:
            raise ValueError(f"Architect missing fields: {missing}")
        
        # Validate API contract is complete
        api = result["api"]
        api_required = ["method", "path", "request", "response", "errors"]
        api_missing = [f for f in api_required if f not in api]
        
        if api_missing:
            raise ValueError(f"API contract incomplete: {api_missing}")
        
        print(f"[ARCHITECT] ✓ Contract locked")
        print(f"  API: {api['method']} {api['path']}")
        print(f"  Backend tasks: {len(result['backend_tasks'])}")
        print(f"  Frontend tasks: {len(result['frontend_tasks'])}")
        print(f"  Assumptions: {len(result['assumptions'])}")
        print(result['backend_tasks'])
        
        return result
    
    except ValueError as e:
        raise Exception(f"Architect validation failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Architect failed: {str(e)}")
