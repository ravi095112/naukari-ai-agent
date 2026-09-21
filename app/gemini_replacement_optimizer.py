import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors

from profile_reader import read_profile
from profile_analyzer import analyze_profile
from evidence_checker import load_evidence
from replacement_engine import (
    get_verified_add_candidates,
    build_replacement_pairs,
)


load_dotenv()

MODEL_NAME = "gemini-3.5-flash"


def get_client():

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured in .env"
        )

    return genai.Client(
        api_key=api_key
    )


def choose_replacement(
    client,
    profile: dict,
    analysis: dict,
    verified_add_candidates: dict,
    replacement_pairs: list[dict],
):

    prompt = f"""
You are a professional career-profile optimization assistant.

Your task is to select EXACTLY ONE genuine Naukri Key Skills
replacement from a controlled list.

IMPORTANT RULES:

1. You may ONLY use the supplied replacement pairs.
2. Do NOT invent a skill.
3. Do NOT invent experience.
4. Do NOT select Kubernetes or Kafka because they are not
   evidence-verified.
5. The ADD skill must have verified evidence.
6. The REMOVE skill must come from the supplied replacement
   candidate list.
7. Prefer removing redundant framework variants before removing
   supporting or testing skills.
8. Prefer preserving JUnit and Mockito when another valid
   replacement exists.
9. Prefer a target skill that strengthens the user's target roles.
10. Select EXACTLY ONE replacement.
11. action must always be "PROPOSE".
12. Do not return confidence scores.
13. Do not return rankings.
14. Do not return alternative proposals.
15. Do not return evidence outside the supplied evidence.
16. This is a DRY RUN from the decision perspective. The caller
    will decide whether to apply the proposal.

CURRENT PROFILE:

Resume headline:
{profile["resume_headline"]}

Current Key Skills:
{json.dumps(profile["key_skills"], indent=2)}

Target roles:
{json.dumps(analysis["target_roles"], indent=2)}

Verified add candidates:
{json.dumps(verified_add_candidates, indent=2)}

Controlled replacement pairs:
{json.dumps(replacement_pairs, indent=2)}

Return JSON in EXACTLY this structure:

{{
  "proposal": {{
    "remove_skill": "Spring Application Framework",
    "add_skill": "GenAI",
    "reason": "Short evidence-based explanation.",
    "action": "PROPOSE"
  }}
}}
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "proposal": {
                            "type": "object",
                            "properties": {
                                "remove_skill": {
                                    "type": "string"
                                },
                                "add_skill": {
                                    "type": "string"
                                },
                                "reason": {
                                    "type": "string"
                                },
                                "action": {
                                    "type": "string",
                                    "enum": [
                                        "PROPOSE"
                                    ]
                                },
                            },
                            "required": [
                                "remove_skill",
                                "add_skill",
                                "reason",
                                "action",
                            ],
                        }
                    },
                    "required": [
                        "proposal"
                    ],
                },
            ),
        )

    except errors.ServerError as exc:

        raise RuntimeError(
            "Gemini server error while generating "
            "replacement proposal. "
            "No profile changes were made."
        ) from exc

    except errors.APIError as exc:

        raise RuntimeError(
            f"Gemini API error: {exc}. "
            "No profile changes were made."
        ) from exc

    except Exception as exc:

        raise RuntimeError(
            f"Unexpected Gemini error: {exc}. "
            "No profile changes were made."
        ) from exc

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty response. "
            "No profile changes were made."
        )

    try:

        return json.loads(
            response.text
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Gemini returned invalid JSON. "
            "No profile changes were made."
        ) from exc


def print_proposal(
    result: dict,
    verified_add_candidates: dict,
):

    proposal = result.get(
        "proposal"
    )

    if not proposal:

        raise RuntimeError(
            "Gemini response does not contain "
            "a proposal."
        )

    print(
        "\n========== Gemini Replacement Proposal ==========\n"
    )

    print(
        f"REMOVE : "
        f"{proposal.get('remove_skill')}"
    )

    print(
        f"ADD    : "
        f"{proposal.get('add_skill')}"
    )

    print(
        f"REASON : "
        f"{proposal.get('reason')}"
    )

    print(
        f"ACTION : "
        f"{proposal.get('action')}"
    )

    print(
        "\nEvidence for ADD skill:"
    )

    evidence = verified_add_candidates.get(
        proposal.get("add_skill"),
        [],
    )

    for item in evidence:

        print(
            f"- {item}"
        )


def main():

    print(
        "\n========== Gemini Replacement Optimizer ==========\n"
    )

    profile = read_profile()

    analysis = analyze_profile(
        profile
    )

    evidence_data = load_evidence()

    verified_add_candidates = (
        get_verified_add_candidates(
            analysis,
            evidence_data,
        )
    )

    if not verified_add_candidates:

        print(
            "No evidence-supported target skills found."
        )

        return

    replacement_pairs = (
        build_replacement_pairs(
            verified_add_candidates,
            analysis[
                "replacement_candidates"
            ],
        )
    )

    if not replacement_pairs:

        print(
            "No valid replacement pairs found."
        )

        return

    print(
        "Verified target skills:"
    )

    for skill in verified_add_candidates:

        print(
            f"- {skill}"
        )

    print(
        f"\nControlled replacement pairs: "
        f"{len(replacement_pairs)}"
    )

    client = get_client()

    result = choose_replacement(
        client=client,
        profile=profile,
        analysis=analysis,
        verified_add_candidates=(
            verified_add_candidates
        ),
        replacement_pairs=replacement_pairs,
    )

    print_proposal(
        result,
        verified_add_candidates,
    )


if __name__ == "__main__":

    main()