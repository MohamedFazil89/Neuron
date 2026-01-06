# agents/architect.py - IMPROVED VERSION
from core.openai_client import call_openai_json
import json

ARCHITECT_SYSTEM_PROMPT = """You are the Architect agent. Your job is to decide WHAT will be built, not HOW.

Your output is a CONTRACT that other agents must follow exactly.

CRITICAL NEW REQUIREMENT:
You must EXPLICITLY state which domain (frontend/backend/both) this feature requires.

Rules:
1. Output ONLY valid JSON. No markdown. No explanations.
2. Be annoyingly specific. "Implement login" is not specific enough.
3. Freeze the API contract if backend is involved.
4. Declare assumptions explicitly.
5. Do NOT write code. Do NOT suggest libraries.
6. Do NOT say "optionally", "could be", "might". Ambiguity is poison.
7. CLEARLY indicate if this is frontend-only, backend-only, or full-stack.

Your output schema:
{
  "feature": "string - exact feature description",
  "domain": "frontend" | "backend" | "fullstack",
  "requires_api": true | false,
  "api": {
    "method": "POST|GET|PUT|DELETE",
    "path": "/api/...",
    "request": { "field": "type" },
    "response": { "field": "type" },
    "errors": [
      { "status": 400, "reason": "..." }
    ]
  } | null,
  "backend_tasks": ["specific step 1", "specific step 2"],
  "frontend_tasks": ["specific step 1", "specific step 2"],
  "backend_files": ["path/to/file.js"],
  "frontend_files": ["path/to/file.jsx"],
  "integration_points": {
    "frontend_entry": "App.jsx" | "routes.jsx" | null,
    "backend_entry": "server.js" | "app.py" | null
  },
  "assumptions": ["what must be true when code runs"]
}

DOMAIN DETECTION RULES:
- If user mentions "UI", "page", "component", "design", "frontend", "interface" → domain: "frontend"
- If user mentions "API", "endpoint", "database", "server", "backend" → domain: "backend"
- If user mentions "feature" with both UI and server logic → domain: "fullstack"
- If domain is "frontend", then requires_api: false and api: null
- If domain is "backend", then frontend_files: [] and frontend_tasks: []

Return ONLY this JSON. Nothing else."""

def architect_agent(feature):
    """
    Architect breaks down feature into a frozen contract.
    
    NEW: Now explicitly states which domain (frontend/backend/both) is required.
    """
    
    prompt = f"""
Feature request: {feature}

Create a complete contract that defines EXACTLY what will be built.

CRITICAL: Determine if this feature is:
- Frontend only (UI, components, pages, design)
- Backend only (API, database, server logic)
- Full-stack (requires both frontend and backend)

Be specific:
- What domain does this belong to?
- What are the exact endpoints (if backend)?
- What are the exact request/response schemas (if API)?
- What are the exact tasks?
- What files need to be created/modified?
- What are the integration points?
- What assumptions must be true?

Examples:
- "Create a landing page" → domain: "frontend", requires_api: false
- "Add login UI with email and password" → domain: "frontend", requires_api: false
- "Create /api/users endpoint" → domain: "backend"
- "Implement user authentication" → domain: "fullstack", requires_api: true

Analyze the request carefully and be precise.

Return the JSON contract exactly as specified in the system prompt.
"""
    
    print(f"[ARCHITECT] Analyzing: {feature}")
    
    try:
        result = call_openai_json(prompt, max_tokens=2000, system_prompt=ARCHITECT_SYSTEM_PROMPT)
        
        # Validate output has required fields
        required_fields = ["feature", "domain", "requires_api", "backend_tasks", 
                          "frontend_tasks", "backend_files", "frontend_files", 
                          "integration_points", "assumptions"]
        missing = [f for f in required_fields if f not in result]
        
        if missing:
            raise ValueError(f"Architect missing fields: {missing}")
        
        # Validate domain
        if result["domain"] not in ["frontend", "backend", "fullstack"]:
            raise ValueError(f"Invalid domain: {result['domain']}")
        
        # Validate consistency
        if result["domain"] == "frontend":
            if result["requires_api"]:
                raise ValueError("Frontend-only features cannot require API")
            if result["api"] is not None:
                raise ValueError("Frontend-only features should have api: null")
            if len(result["backend_files"]) > 0:
                raise ValueError("Frontend-only features should have no backend files")
        
        if result["domain"] == "backend":
            if len(result["frontend_files"]) > 0:
                raise ValueError("Backend-only features should have no frontend files")
            if len(result["frontend_tasks"]) > 0:
                raise ValueError("Backend-only features should have no frontend tasks")
        
        # Validate API contract if required
        if result["requires_api"] and result["api"]:
            api = result["api"]
            api_required = ["method", "path", "request", "response", "errors"]
            api_missing = [f for f in api_required if f not in api]
            
            if api_missing:
                raise ValueError(f"API contract incomplete: {api_missing}")
        
        print(f"[ARCHITECT] Contract locked successfully")
        print(f"  Domain: {result['domain']}")
        print(f"  Requires API: {result['requires_api']}")
        if result.get("api"):
            print(f"  API: {result['api']['method']} {result['api']['path']}")
        print(f"  Backend tasks: {len(result['backend_tasks'])}")
        print(f"  Frontend tasks: {len(result['frontend_tasks'])}")
        print(f"  Backend files: {len(result['backend_files'])}")
        print(f"  Frontend files: {len(result['frontend_files'])}")
        
        return result
    
    except ValueError as e:
        raise Exception(f"Architect validation failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Architect failed: {str(e)}")