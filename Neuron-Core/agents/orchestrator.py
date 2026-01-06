# agents/orchestrator.py
"""
The Orchestrator Agent is the ONLY agent that decides:
1. Which agents to run
2. In what order
3. With what exact parameters

It enforces role boundaries and prevents unauthorized agent execution.
"""

from core.openai_client import call_openai_json
import json


ORCHESTRATOR_SYSTEM_PROMPT = """You are the Orchestrator Agent.

Your ONLY job is to decide which agents execute and in what order.

You receive:
- User's feature request
- Architect's contract (what to build)
- Project analysis (existing code)

You must output an EXECUTION PLAN.

RULES:
1. If the request is FRONTEND-ONLY (UI, design, components, pages):
   - Execute ONLY Frontend Agent
   - Backend Agent is FORBIDDEN

2. If the request is BACKEND-ONLY (API, database, server logic):
   - Execute ONLY Backend Agent
   - Frontend Agent is FORBIDDEN

3. If the request requires BOTH:
   - Execute Backend Agent first
   - Then Frontend Agent

4. You must EXPLICITLY state which agents run

5. Output ONLY valid JSON. No explanations.

Output Schema:
{
  "execution_plan": [
    {
      "agent": "frontend" | "backend",
      "reason": "why this agent is needed",
      "order": 1
    }
  ],
  "integration_required": true | false,
  "integration_targets": ["App.jsx", "routes.js"],
  "verification_needed": true | false
}

CRITICAL:
- If user asks for "landing page", "login UI", "dashboard design" → FRONTEND ONLY
- If user asks for "API endpoint", "database model", "authentication logic" → BACKEND ONLY
- Default to MINIMUM agents needed

Return ONLY JSON."""


def orchestrator_agent(feature, architect_contract, project_analysis):
    """
    Orchestrator decides which agents to execute.
    
    Args:
        feature: User's feature request
        architect_contract: Architect's plan
        project_analysis: Existing project structure
    
    Returns:
        {
            "execution_plan": [...],
            "integration_required": bool,
            "integration_targets": [...]
        }
    """
    
    # Extract key signals from contract
    backend_files = architect_contract.get("backend_files", [])
    frontend_files = architect_contract.get("frontend_files", [])
    backend_tasks = architect_contract.get("backend_tasks", [])
    frontend_tasks = architect_contract.get("frontend_tasks", [])
    
    # Prepare context for orchestrator
    context = {
        "feature_request": feature,
        "contract": {
            "has_backend_files": len(backend_files) > 0,
            "has_frontend_files": len(frontend_files) > 0,
            "backend_task_count": len(backend_tasks),
            "frontend_task_count": len(frontend_tasks),
            "backend_files": backend_files,
            "frontend_files": frontend_files
        },
        "project": {
            "has_backend": project_analysis["backend"]["exists"],
            "has_frontend": project_analysis["frontend"]["exists"],
            "backend_framework": project_analysis["backend"]["detected_framework"],
            "frontend_framework": project_analysis["frontend"]["detected_framework"]
        }
    }
    
    prompt = f"""
Analyze this feature request and decide which agents to execute.

User Request: {feature}

Contract Analysis:
{json.dumps(context, indent=2)}

Decision Rules:
1. If contract has ONLY frontend files/tasks → Frontend Agent ONLY
2. If contract has ONLY backend files/tasks → Backend Agent ONLY
3. If contract has BOTH → Backend first, then Frontend
4. If user explicitly says "frontend only", "UI only", "design" → Frontend ONLY

Determine:
- Which agents run
- In what order
- Whether integration verification is needed
- Which files need to be checked for proper wiring

Return ONLY the JSON execution plan.
"""
    
    print(f"[ORCHESTRATOR] Analyzing execution requirements...")
    
    result = call_openai_json(
        prompt,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        max_tokens=1000
    )
    
    # Validate output
    if "execution_plan" not in result:
        raise ValueError("Orchestrator must return 'execution_plan'")
    
    execution_plan = result["execution_plan"]
    
    print(f"[ORCHESTRATOR] Execution plan created successfully")
    print(f"  Agents to run: {len(execution_plan)}")
    for step in execution_plan:
        print(f"    {step['order']}. {step['agent'].upper()} - {step['reason']}")
    
    if result.get("integration_required"):
        print(f"  Integration check: REQUIRED")
        print(f"  Targets: {result.get('integration_targets', [])}")
    
    return result