import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
EVIDENCE_FILE = BASE_DIR / "data" / "profile_evidence.json"


def load_evidence() -> dict:
    if not EVIDENCE_FILE.exists():
        raise FileNotFoundError(
            f"Evidence file not found: {EVIDENCE_FILE}"
        )

    with EVIDENCE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_skill_evidence(skill: str, evidence_data: dict) -> dict:
    skill_data = evidence_data.get("skills", {}).get(skill)

    if not skill_data:
        return {
            "skill": skill,
            "verified": False,
            "evidence": [],
            "decision": "DO_NOT_PROPOSE",
            "reason": "No evidence record exists.",
        }

    evidence = skill_data.get("evidence", [])
    verified = skill_data.get("verified", False)

    if verified and evidence:
        return {
            "skill": skill,
            "verified": True,
            "evidence": evidence,
            "decision": "PROPOSE",
            "reason": "Verified evidence is available.",
        }

    return {
        "skill": skill,
        "verified": False,
        "evidence": evidence,
        "decision": "DO_NOT_PROPOSE",
        "reason": "Evidence is missing or not verified.",
    }


def print_results(results: list[dict]):
    print("\n========== Evidence Check ==========\n")

    for result in results:
        print(f"Skill      : {result['skill']}")
        print(f"Decision   : {result['decision']}")
        print(f"Verified   : {result['verified']}")
        print(f"Evidence   : {result['evidence']}")
        print(f"Reason     : {result['reason']}")
        print()


if __name__ == "__main__":
    evidence_data = load_evidence()

    skills_to_check = [
        "REST API",
        "Docker",
        "Kubernetes",
        "Kafka",
        "GenAI",
    ]

    results = [
        check_skill_evidence(skill, evidence_data)
        for skill in skills_to_check
    ]

    print_results(results)