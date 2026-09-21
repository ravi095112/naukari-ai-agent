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
)
from skills_updater import (
    apply_replacement,
)
from audit_log import (
    write_audit_event,
)


def run_agent():

    print(
        "\n"
        "============================================\n"
        "        Naukri AI Profile Agent\n"
        "============================================\n"
    )

    # ---------------------------------------------------------
    # 1. READ CURRENT PROFILE
    # ---------------------------------------------------------

    print(
        "\n[1/7] Reading current profile..."
    )

    profile = read_profile()

    print(
        f"Current Key Skills: "
        f"{len(profile['key_skills'])}"
    )

    # ---------------------------------------------------------
    # 2. ANALYZE PROFILE
    # ---------------------------------------------------------

    print(
        "\n[2/7] Analyzing profile..."
    )

    analysis = analyze_profile(
        profile
    )

    print(
        "Missing target skills:"
    )

    for skill in analysis[
        "missing_target_skills"
    ]:

        print(
            f"  - {skill}"
        )

    # ---------------------------------------------------------
    # 3. CHECK EVIDENCE
    # ---------------------------------------------------------

    print(
        "\n[3/7] Checking evidence..."
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
            "No evidence-supported "
            "profile improvement found."
        )

        write_audit_event(
            {
                "event_type": (
                    "NO_EVIDENCE_SUPPORTED_CHANGE"
                ),
            }
        )

        return

    print(
        "Verified additions:"
    )

    for skill in (
        verified_add_candidates
    ):

        print(
            f"  - {skill}"
        )

    # ---------------------------------------------------------
    # 4. BUILD CONTROLLED CANDIDATES
    # ---------------------------------------------------------

    print(
        "\n[4/7] Building controlled replacements..."
    )

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

        write_audit_event(
            {
                "event_type": (
                    "NO_REPLACEMENT_PAIRS"
                ),
            }
        )

        return

    print(
        f"Controlled pairs: "
        f"{len(replacement_pairs)}"
    )

    # ---------------------------------------------------------
    # 5. GEMINI
    # ---------------------------------------------------------

    print(
        "\n[5/7] Asking Gemini for ONE proposal..."
    )

    try:

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

    except RuntimeError as exc:

        write_audit_event(
            {
                "event_type": (
                    "GEMINI_PROPOSAL_FAILED"
                ),
                "error": str(exc),
                "profile_skill_count": (
                    len(
                        profile["key_skills"]
                    )
                ),
            }
        )

        print(
            f"\nGemini step failed safely:"
        )

        print(
            f"{exc}"
        )

        print(
            "\nNo Naukri profile changes were made."
        )

        return

    proposal = result.get(
        "proposal"
    )

    if not proposal:

        write_audit_event(
            {
                "event_type": (
                    "GEMINI_EMPTY_PROPOSAL"
                ),
                "gemini_result": result,
            }
        )

        print(
            "\nGemini returned no proposal."
        )

        print(
            "No Naukri profile changes were made."
        )

        return

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
    # 6. POLICY GATE
    # ---------------------------------------------------------

    print(
        "\n[6/7] Running policy gate..."
    )

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

    print(
        f"Policy decision: "
        f"{policy_result['decision']}"
    )

    if policy_result[
        "decision"
    ] != "PASS":

        write_audit_event(
            {
                "event_type": (
                    "PROFILE_UPDATE_REJECTED"
                ),
                "proposal": proposal,
                "policy_result": policy_result,
            }
        )

        print(
            "\nProposal rejected."
        )

        for error in (
            policy_result["errors"]
        ):

            print(
                f"- {error}"
            )

        print(
            "\nNo Naukri profile changes were made."
        )

        return

    # ---------------------------------------------------------
    # 7. APPLY EXACT APPROVED CHANGE
    # ---------------------------------------------------------

    print(
        "\n[7/7] Applying approved replacement..."
    )

    remove_skill = policy_result[
        "remove_skill"
    ]

    add_skill = policy_result[
        "add_skill"
    ]

    playwright = None
    context = None
    page = None

    try:

        from naukri_profile import (
            open_profile,
        )

        playwright, context, page = (
            open_profile()
        )

        saved_skills = (
            apply_replacement(
                page=page,
                remove_skill_name=(
                    remove_skill
                ),
                add_skill=add_skill,
            )
        )

        write_audit_event(
            {
                "event_type": (
                    "PROFILE_UPDATE_SUCCESS"
                ),
                "remove_skill": (
                    remove_skill
                ),
                "add_skill": (
                    add_skill
                ),
                "reason": (
                    proposal["reason"]
                ),
                "policy_decision": (
                    policy_result[
                        "decision"
                    ]
                ),
                "verified_skills": (
                    verified_add_candidates
                ),
                "final_skills": (
                    saved_skills
                ),
            }
        )

        print(
            "\n"
            "============================================"
        )

        print(
            "\nPROFILE UPDATE SUCCESSFUL"
        )

        print(
            f"Removed : {remove_skill}"
        )

        print(
            f"Added   : {add_skill}"
        )

        print(
            "Verified: persisted after reload"
        )

        print(
            "============================================\n"
        )

    except Exception as exc:

        write_audit_event(
            {
                "event_type": (
                    "PROFILE_UPDATE_FAILED"
                ),
                "remove_skill": (
                    remove_skill
                ),
                "add_skill": (
                    add_skill
                ),
                "error": str(exc),
            }
        )

        print(
            "\nPROFILE UPDATE FAILED"
        )

        print(
            f"Error: {exc}"
        )

        print(
            "\nThe failure was recorded in the audit log."
        )

        raise

    finally:

        if context is not None:

            context.close()

        if playwright is not None:

            playwright.stop()


if __name__ == "__main__":

    run_agent()