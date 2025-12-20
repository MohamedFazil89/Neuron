# agents/frontend_contextual.py
from core.openai_client import call_openai_json
from agents.analyzer import should_modify_file
import json

FRONTEND_CONTEXTUAL_PROMPT = """You are the Frontend Agent with project context awareness.

You receive:
1. A feature contract
2. Existing project analysis
3. Existing component contents (if any)

Your job:
- If a component EXISTS, MODIFY it by adding new features
- If a component DOES NOT exist, CREATE it from scratch
- NEVER duplicate existing UI elements
- NEVER remove existing functionality
- ALWAYS preserve existing state, hooks, and handlers

Output Rules:
{
  "status": "success | blocked | error",
  "files": [
    {
      "path": "string",
      "action": "create | modify",
      "content": "string - FULL file content",
      "reason": "why this action was chosen"
    }
  ]
}

For MODIFY actions:
- Include COMPLETE updated component
- Merge new JSX with existing JSX
- Preserve existing state variables
- Add comments: {/* ADDED: feature name */}

For CREATE actions:
- Write complete component from scratch
"""

def frontend_agent_contextual(feature, contract, project_analysis):
    """
    Context-aware frontend agent that respects existing components.
    """
    
    # Prepare context for each file
    file_contexts = []
    
    for target_file in contract.get("frontend_files", []):
        action, existing_content = should_modify_file(project_analysis, target_file)
        
        file_contexts.append({
            "path": target_file,
            "action": action,
            "existing_content": existing_content if action == "modify" else None
        })
    
    prompt = f"""
Feature: {feature}

Contract: {json.dumps(contract, indent=2)}

Existing Project Analysis:
- Components found: {project_analysis['frontend']['components']}
- Pages found: {project_analysis['frontend']['pages']}
- Hooks found: {project_analysis['frontend']['hooks']}

File Context:
{json.dumps(file_contexts, indent=2)}

Instructions:
1. For components marked "modify", UPDATE them by adding new features
2. For components marked "create", write them from scratch
3. When modifying, preserve ALL existing JSX, state, and handlers
4. Add clear comments showing what was added

Generate the complete implementation.
"""
    
    print(f"[FRONTEND-CONTEXT] Processing with {len(file_contexts)} files")
    
    result = call_openai_json(
        prompt,
        system_prompt=FRONTEND_CONTEXTUAL_PROMPT,
        max_tokens=8000
    )
    
    # Validation
    if "files" not in result:
        raise ValueError("Frontend agent must return 'files' array")
    
    for file in result["files"]:
        if "path" not in file or "content" not in file or "action" not in file:
            raise ValueError(f"File missing required fields")
    
    print(f"[FRONTEND-CONTEXT] ✓ Generated {len(result['files'])} files")
    for file in result['files']:
        print(f"  {file['action'].upper()}: {file['path']}")
    
    return result
