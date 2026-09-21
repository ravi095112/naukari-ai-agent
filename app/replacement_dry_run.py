import json

from profile_reader import read_profile
from profile_analyzer import analyze_profile
from evidence_checker import load_evidence
from replacement_engine import (
    get_verified_add_candidates,
    build_replacement_pairs,
)
from gemini_replacement_optimizer import (
    get_client,
    choose_replacement,
)
from policy_gate import (
    validate_replacement_proposal,
    print_policy_result,
)
from audit_log import (
    write_audit_event,
)


def main():

    print(
        "\n========== REPLACEMENT DRY RUN ==========\n"
    )

    # ---------------------------------------------------------
    # 1. Read current profile
    # ---------------------------------------------------------

    profile = read_profile()

    print(
        f"Current skills: "
        f"{len(profile['key_skills'])}"
    )

    # ---------------------------------------------------------
    # 2. Analyze profile
    # ---------------------------------------------------------

    analysis = analyze_profile(
        profile
    )

    # ---------------------------------------------------------
    # 3. Load evidence
    # ---------------------------------------------------------

    evidence_data = load_evidence()

    verified_add_candidates = (
        get_verified_add_candidates(
            analysis,
            evidence_data,
        )
    )

    if not verified_add_candidates:

        print(
            "No evidence-supported additions found."
        )

        return

    # ---------------------------------------------------------
    # 4. Build controlled candidates
    # ---------------------------------------------------------

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
            "No replacement pairs available."
        )

        return

    # ---------------------------------------------------------
    # 5. Ask Gemini to choose ONE proposal
    # ---------------------------------------------------------

    print(
        f"Controlled pairs: "
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

    proposal = result.get(
        "proposal"
    )

    if not proposal:

        raise RuntimeError(
            "Gemini did not return a proposal."
        )

    print(
        "\n========== Gemini Proposal ==========\n"
    )

    print(
        json.dumps(
            proposal,
            indent=2,
            ensure_ascii=False,
        )
    )

    # ---------------------------------------------------------
    # 6. Policy Gate
    # ---------------------------------------------------------

    policy_result = (
        validate_replacement_proposal(
            proposal=proposal,
            current_skills=(
                profile["key_skills"]
            ),
            verified_add_candidates=(
                verified_add_candidates
            ),
            removal_candidates=(
                analysis[
                    "replacement_candidates"
                ]
            ),
        )
    )

    print_policy_result(
        policy_result
    )

    # ---------------------------------------------------------
    # 7. Audit
    # ---------------------------------------------------------

    write_audit_event(
        {
            "event_type": (
                "REPLACEMENT_DRY_RUN"
            ),
            "proposal": proposal,
            "policy_result": policy_result,
            "verified_add_candidates": (
                verified_add_candidates
            ),
        }
    )

    print(
        "\nAudit event recorded."
    )

    # ---------------------------------------------------------
    # 8. IMPORTANT: no Naukri update
    # ---------------------------------------------------------

    print(
        "\nSTATUS: DRY RUN"
    )

    print(
        "No Naukri profile changes were made."
    )


if __name__ == "__main__":

    main()