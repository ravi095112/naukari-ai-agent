import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from profile_reader import read_profile
from profile_analyzer import analyze_profile
from evidence_checker import load_evidence, check_skill_evidence
from policy_gate import validate_all, print_policy_results
from audit_log import log_proposal, print_audit_location


load_dotenv()

MODEL_NAME = "gemini-2.5-flash"


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured in .env"
        )

    return genai.Client(api_key=api_key)


def generate_ai_proposals(
    client,
    profile,
    supported_skills,
):
    prompt = f"""
You are a professional career-profile optimization assistant.

Create truthful Naukri Key Skills proposals.

RULES:
- Use ONLY the supplied evidence.
- Never invent experience or technology.
- Do not exaggerate.
- Return exactly one proposal for each supplied skill.
- proposed_skill_text must be concise.
- action must always be PROPOSE.
- Do not return evidence_used.
- Do not return confidence.

Current Naukri skills:
{json.dumps(profile["key_skills"])}

Skills that passed deterministic evidence validation:

{json.dumps(supported_skills, indent=2)}

Return JSON in exactly this format:

{{
  "proposals": [
    {{
      "skill": "REST API",
      "proposed_skill_text": "REST API",
      "reason": "Short evidence-based reason",
      "action": "PROPOSE"
    }}
  ]
}}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "proposals": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "skill": {
                                    "type": "string"
                                },
                                "proposed_skill_text": {
                                    "type": "string"
                                },
                                "reason": {
                                    "type": "string"
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["PROPOSE"]
                                }
                            },
                            "required": [
                                "skill",
                                "proposed_skill_text",
                                "reason",
                                "action"
                            ]
                        }
                    }
                },
                "required": ["proposals"]
            }
        )
    )

    return json.loads(response.text)


def main():

    # --------------------------------------------------
    # 1. Read current Naukri profile
    # --------------------------------------------------

    profile = read_profile()

    # --------------------------------------------------
    # 2. Analyze profile
    # --------------------------------------------------

    analysis = analyze_profile(profile)

    # --------------------------------------------------
    # 3. Load evidence
    # --------------------------------------------------

    evidence_data = load_evidence()

    supported_skills = {}

    for skill, status in analysis["skill_visibility"].items():

        if status != "NOT_CURRENTLY_VISIBLE":
            continue

        evidence_result = check_skill_evidence(
            skill,
            evidence_data,
        )

        if evidence_result["decision"] != "PROPOSE":
            continue

        supported_skills[skill] = (
            evidence_result["evidence"]
        )

    print(
        "\n========== Gemini Profile Proposals ==========\n"
    )

    if not supported_skills:
        print(
            "No evidence-supported changes found."
        )
        return

    print(
        "Skills passed deterministic evidence check:"
    )

    for skill in supported_skills:
        print(f"  - {skill}")

    print()

    # --------------------------------------------------
    # 4. Generate Gemini proposals
    # --------------------------------------------------

    client = get_client()

    result = generate_ai_proposals(
        client,
        profile,
        supported_skills,
    )

    proposals = result.get(
        "proposals",
        [],
    )

    # --------------------------------------------------
    # 5. Display Gemini proposals
    # --------------------------------------------------

    for proposal in proposals:

        print(
            json.dumps(
                proposal,
                indent=2,
                ensure_ascii=False,
            )
        )

        print()

    # --------------------------------------------------
    # 6. Policy Gate
    # --------------------------------------------------

    policy_results = validate_all(
        proposals,
        supported_skills,
    )

    print_policy_results(
        policy_results
    )

    # --------------------------------------------------
    # 7. Audit Log
    # --------------------------------------------------

    for proposal, policy_result in zip(
        proposals,
        policy_results,
    ):

        skill = proposal.get(
            "skill"
        )

        evidence = supported_skills.get(
            skill,
            [],
        )

        log_proposal(
            proposal=proposal,
            policy_result=policy_result,
            evidence=evidence,
        )

    print_audit_location()


if __name__ == "__main__":
    main()