from core.openai_client import call_openai_json
import json


BACKEND_SYSTEM_PROMPT = """You are the Backend Agent.

Your responsibility is to implement backend code strictly based on a contract provided at runtime.

Rules:
1. You do not design APIs. You only implement what is specified.
2. You must follow the provided contract verbatim.
3. You must not change request or response shapes.
4. You must not add extra fields, endpoints, or logic.
5. If something is missing, rely only on stated assumptions.
6. If assumptions are insufficient, stop and report the ambiguity.

You produce runnable backend code only.
You do not explain concepts.
You do not suggest improvements unless explicitly asked.
Security rules in the contract are mandatory.

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
- A Node.js backend
- A standard MVC folder structure
- Common backend libraries are available unless forbidden by the contract
"""


def backend_agent(feature, architect_contract):
    prompt = f"""
Implement the following backend feature exactly as specified.

You must follow the contract verbatim.
Do not invent behavior.
Do not change APIs.
Do not add files not listed in the contract.

ARCHITECT CONTRACT:
{architect_contract}

Execution Rules:
- Implement only backend-related tasks from the contract.
- Create or modify only the files explicitly listed.
- Follow API paths, request bodies, responses, and error codes exactly.
- Use secure practices as required by the contract.

Output Instructions:
- Return ONLY a single JSON object.
- The JSON object MUST follow the output schema defined in your system prompt.
- Include the full source code for every created or modified file.
- If any assumption in the contract is insufficient to proceed, return status "blocked".
- If implementation fails for any reason, return status "error".

Feature to implement: {feature}
"""

    print(f"[BACKEND] Analyzing feature: {feature}")

    try:
        result = call_openai_json(
            prompt,
            system_prompt=BACKEND_SYSTEM_PROMPT,
            max_tokens=6000
        )

        # ---------- VALIDATION ----------

        # Top-level validation
        if not isinstance(result, dict):
            raise ValueError("Backend output is not a JSON object")

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

        print("[BACKEND] Validation passed")
        return result

    except ValueError as e:
        raise Exception(f"BACKEND validation failed: {str(e)}")

    except Exception as e:
        raise Exception(f"BACKEND execution failed: {str(e)}")
