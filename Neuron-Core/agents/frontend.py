# agents/frontend.py
from core.openai_client import call_openai_json

FRONTEND_SYSTEM_PROMPT = """You are the Frontend Agent.

Your responsibility is to implement frontend code strictly based on a contract provided at runtime.

Rules:
1. You do not design UIs. You only implement what is specified.
2. You must follow the provided contract verbatim.
3. You must consume the exact API specified in the contract.
4. You must not change request or response shapes.
5. You must not add extra fields, components, or logic beyond the contract.
6. If something is missing, rely only on stated assumptions.
7. If assumptions are insufficient, stop and report the ambiguity.

You produce runnable React code only.
You do not explain concepts.
You do not suggest improvements unless explicitly asked.

Output Rules (STRICT):
- Your entire output MUST be a single valid JSON object.
- No markdown.
- No explanations.
- No text outside JSON.
- No extra keys beyond the defined schema.

Required Output Schema:
{
  "status": "success | blocked | error",
  "files": [
    {
      "path": "string",
      "action": "create | modify",
      "content": "string"
    }
  ]
}

Schema Rules:
- "content" MUST contain the full source code of the file.
- Partial files, diffs, or placeholders are forbidden.
- If you cannot proceed, set status to "blocked" and return an empty files array.
- If an internal failure occurs, set status to "error" and return an empty files array.

You may assume:
- A React frontend (functional components with hooks)
- Modern JavaScript (ES6+)
- Common libraries are available (axios, react-router-dom) unless forbidden by the contract
"""

def frontend_agent(feature, architect_contract):
    prompt = f"""
Implement the following frontend feature exactly as specified.

You must follow the contract verbatim.
Do not invent behavior.
Do not change API calls.
Do not add files not listed in the contract.

ARCHITECT CONTRACT:
{architect_contract}

Execution Rules:
- Implement only frontend-related tasks from the contract.
- Create or modify only the files explicitly listed.
- Call the API endpoint exactly as specified: {architect_contract['api']['method']} {architect_contract['api']['path']}
- Send the exact request body: {architect_contract['api']['request']}
- Handle the exact response schema: {architect_contract['api']['response']}
- Handle all error codes: {architect_contract['api']['errors']}

Output Instructions:
- Return ONLY a single JSON object.
- The JSON object MUST follow the output schema defined in your system prompt.
- Include the full source code for every created or modified file.
- If any assumption in the contract is insufficient to proceed, return status "blocked".
- If implementation fails for any reason, return status "error".

Feature to implement: {feature}
"""

    print(f"[FRONTEND] Analyzing feature: {feature}")

    try:
        result = call_openai_json(
            prompt,
            system_prompt=FRONTEND_SYSTEM_PROMPT,
            max_tokens=6000
        )

        # ---------- VALIDATION ----------

        # Top-level validation
        if not isinstance(result, dict):
            raise ValueError("Frontend output is not a JSON object")

        if "status" not in result:
            raise ValueError("Missing top-level field: status")

        if "files" not in result:
            raise ValueError("Missing top-level field: files")

        if result["status"] not in ["success", "blocked", "error"]:
            raise ValueError(f"Invalid status value: {result['status']}")

        if not isinstance(result["files"], list):
            raise ValueError("files must be a list")

        # Per-file validation
        for index, file in enumerate(result["files"]):
            if not isinstance(file, dict):
                raise ValueError(f"File entry {index} is not an object")

            for key in ["path", "action", "content"]:
                if key not in file:
                    raise ValueError(
                        f"File entry {index} missing required field: {key}"
                    )

            if file["action"] not in ["create", "modify"]:
                raise ValueError(
                    f"Invalid action for file {file['path']}: {file['action']}"
                )

            if not isinstance(file["content"], str) or not file["content"].strip():
                raise ValueError(
                    f"File {file['path']} has empty or invalid content"
                )

        print(f"[FRONTEND] Validation passed - Generated {len(result['files'])} files")
        for file in result['files']:
            print(f"  - {file['path']}")
        
        return result

    except ValueError as e:
        raise Exception(f"FRONTEND validation failed: {str(e)}")

    except Exception as e:
        raise Exception(f"FRONTEND execution failed: {str(e)}")
