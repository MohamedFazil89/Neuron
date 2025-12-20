# agents/backend_contextual.py
from core.openai_client import call_openai_json
from agents.analyzer import should_modify_file

BACKEND_CONTEXTUAL_PROMPT = """You are the Backend Agent with project context awareness.

You receive:
1. A feature contract
2. Existing project analysis
3. Existing file contents (if any)

Your job:
- If a file EXISTS, MODIFY it by adding/updating only the necessary parts
- If a file DOES NOT exist, CREATE it from scratch
- NEVER duplicate existing code
- NEVER remove existing functionality
- ALWAYS preserve existing imports, routes, and logic

Output Rules:
{
  "status": "success | blocked | error",
  "files": [
    {
      "path": "string",
      "action": "create | modify",
      "content": "string - FULL file content (not diff)",
      "reason": "why this action was chosen"
    }
  ]
}

For MODIFY actions:
- Include the COMPLETE updated file content
- Merge new code with existing code
- Preserve all existing functionality
- Add comments showing what was added: // ADDED: feature name

For CREATE actions:
- Write complete file from scratch
"""

def backend_agent_contextual(feature, contract, project_analysis):
    """
    Context-aware backend agent that respects existing files.
    """
    
    from core.openai_client import call_openai_json
    
    # Prepare context for each file
    file_contexts = []
    
    for target_file in contract.get("backend_files", []):
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
- Backend files found: {len(project_analysis['backend']['files'])}
- Frontend files found: {len(project_analysis['frontend']['files'])}
- Routes: {project_analysis['backend']['routes']}
- Components: {project_analysis['frontend']['components']}

File Context:
{json.dumps(file_contexts, indent=2)}

Instructions:
1. For each file marked "modify", UPDATE the existing content by adding the new feature
2. For each file marked "create", write it from scratch
3. When modifying, preserve ALL existing code and add new code appropriately
4. Add clear comments showing what was added for this feature

Generate the complete implementation.
"""
    
    print(f"[BACKEND-CONTEXT] Processing with {len(file_contexts)} files")
    
    result = call_openai_json(
        prompt,
        system_prompt=BACKEND_CONTEXTUAL_PROMPT,
        max_tokens=8000
    )
    
    # Validation
    if "files" not in result:
        raise ValueError("Backend agent must return 'files' array")
    
    for file in result["files"]:
        if "path" not in file or "content" not in file or "action" not in file:
            raise ValueError(f"File missing required fields")
    
    print(f"[BACKEND-CONTEXT] ✓ Generated {len(result['files'])} files")
    for file in result['files']:
        print(f"  {file['action'].upper()}: {file['path']}")
    
    return result
