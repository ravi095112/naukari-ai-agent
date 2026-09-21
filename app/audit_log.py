import json
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
AUDIT_FILE = LOG_DIR / "profile_audit.jsonl"


def write_audit_event(event: dict):
    """
    Append one audit event as a JSON line.
    """

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    event_with_timestamp = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        **event,
    }

    with AUDIT_FILE.open(
        "a",
        encoding="utf-8",
    ) as f:

        f.write(
            json.dumps(
                event_with_timestamp,
                ensure_ascii=False,
            )
            + "\n"
        )


def log_proposal(
    proposal: dict,
    policy_result: dict,
    evidence: list[str],
):
    event = {
        "event_type": "PROFILE_UPDATE_PROPOSAL",

        "skill": proposal.get(
            "skill"
        ),

        "proposed_skill_text": proposal.get(
            "proposed_skill_text"
        ),

        "reason": proposal.get(
            "reason"
        ),

        "action": proposal.get(
            "action"
        ),

        "policy_decision": policy_result.get(
            "decision"
        ),

        "policy_errors": policy_result.get(
            "errors",
            [],
        ),

        "evidence": evidence,
    }

    write_audit_event(event)


def print_audit_location():
    print(
        f"\nAudit log:"
        f"\n{AUDIT_FILE}"
    )

