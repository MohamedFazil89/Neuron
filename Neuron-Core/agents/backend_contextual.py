# agents/backend_contextual.py - FIXED VERSION
from core.openai_client import call_openai_json
from agents.analyzer import should_modify_file
import json

BACKEND_CONTEXTUAL_PROMPT = """You are the Backend Agent with project context awareness.

You receive:
1. A feature contract
2. Existing project analysis
3. Existing file contents (if any)
4. You must ensure all backend files are properly integrated with existing code

Your job:
- If a file EXISTS, MODIFY it by adding/updating only the necessary parts
- If a file DOES NOT exist, CREATE it from scratch
- NEVER duplicate existing code
- NEVER remove existing functionality
- ALWAYS preserve existing imports, routes, and logic
- ALWAYS ensure new code integrates seamlessly with existing code

CRITICAL: You must respond ONLY with valid JSON. No markdown, no explanations, just JSON.

Output JSON Schema:
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
- Include the COMPLETE updated file content in JSON
- Merge new code with existing code
- Preserve all existing functionality
- Add comments showing what was added: // ADDED: feature name

For CREATE actions:
- Write complete file from scratch

Return ONLY valid JSON matching the schema above.
"""

def backend_agent_contextual(feature, contract, project_analysis):
    """
    Context-aware backend agent that respects existing files.
    """
    
    # Prepare context for each file
    file_contexts = []
    
    for target_file in contract.get("backend_files", []):
        action, existing_content = should_modify_file(project_analysis, target_file)
        
        file_contexts.append({
            "path": target_file,
            "action": action,
            "existing_content": existing_content if action == "modify" else None
        })
    
    # Extract structure information safely
    backend_structure = project_analysis['backend'].get('structure', {})
    frontend_structure = project_analysis['frontend'].get('structure', {})
    
    # Build structure summary
    structure_summary = {
        "backend": {
            "exists": project_analysis['backend']['exists'],
            "framework": project_analysis['backend']['detected_framework'],
            "file_count": len(project_analysis['backend']['files']),
            "categories": {}
        },
        "frontend": {
            "exists": project_analysis['frontend']['exists'],
            "framework": project_analysis['frontend']['detected_framework'],
            "file_count": len(project_analysis['frontend']['files']),
            "categories": {}
        }
    }
    
    # Add category counts
    for category, files in backend_structure.items():
        count = len(files) if isinstance(files, list) else files.get('count', 0)
        structure_summary['backend']['categories'][category] = count
    
    for category, files in frontend_structure.items():
        count = len(files) if isinstance(files, list) else files.get('count', 0)
        structure_summary['frontend']['categories'][category] = count
    
    prompt = f"""
Feature: {feature}

Contract: {json.dumps(contract, indent=2)}

Existing Project Structure:
{json.dumps(structure_summary, indent=2)}

File Context:
{json.dumps(file_contexts, indent=2)}

Instructions:
1. For each file marked "modify", UPDATE the existing content by adding the new feature
2. For each file marked "create", write it from scratch
3. When modifying, preserve ALL existing code and add new code appropriately
4. Add clear comments showing what was added for this feature
5. Ensure the backend integrates properly with the detected framework: {structure_summary['backend']['framework']}

Generate the complete implementation as a JSON response matching the schema in the system prompt.
"""
    
    print(f"[BACKEND-CONTEXT] Processing with {len(file_contexts)} files")
    print(f"[BACKEND-CONTEXT] Detected framework: {structure_summary['backend']['framework']}")
    
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
    
    print(f"[BACKEND-CONTEXT] Generated {len(result['files'])} files")
    for file in result['files']:
        print(f"  {file['action'].upper()}: {file['path']}")
    
    return result
