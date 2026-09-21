from profile_reader import read_profile
from profile_analyzer import analyze_profile
from evidence_checker import load_evidence, check_skill_evidence


def get_verified_add_candidates(
    analysis: dict,
    evidence_data: dict,
) -> dict[str, list[str]]:

    verified = {}

    for skill in analysis["missing_target_skills"]:

        result = check_skill_evidence(
            skill,
            evidence_data,
        )

        if result["decision"] == "PROPOSE":
            verified[skill] = result["evidence"]

    return verified


def build_replacement_pairs(
    add_candidates: dict[str, list[str]],
    removal_candidates: list[dict],
) -> list[dict]:

    proposals = []

    for add_skill, evidence in add_candidates.items():

        for candidate in removal_candidates:

            proposals.append(
                {
                    "remove_skill": candidate["skill"],
                    "add_skill": add_skill,
                    "remove_priority": candidate["priority"],
                    "remove_category": candidate["category"],
                    "remove_reason": candidate["reason"],
                    "evidence": evidence,
                }
            )

    return proposals


def print_engine_output(
    analysis: dict,
    verified_add_candidates: dict[str, list[str]],
    proposals: list[dict],
):

    print(
        "\n========== Replacement Engine ==========\n"
    )

    print("Current capacity:")

    print(
        f"{analysis['key_skill_count']}/"
        f"{analysis['max_key_skills']} "
        f"({analysis['capacity_status']})"
    )

    print("\nVerified add candidates:")

    if verified_add_candidates:

        for skill, evidence in (
            verified_add_candidates.items()
        ):

            print(
                f"\n{skill} -> VERIFIED"
            )

            for item in evidence:
                print(f"  - {item}")

    else:

        print("- None")

    print("\nReplacement candidates:")

    if analysis["replacement_candidates"]:

        for candidate in (
            analysis["replacement_candidates"]
        ):

            print(
                f"- {candidate['skill']} "
                f"(priority={candidate['priority']}, "
                f"category={candidate['category']})"
            )

    else:

        print("- None")

    print("\nPossible replacement pairs:")

    if proposals:

        for index, proposal in enumerate(
            proposals,
            start=1,
        ):

            print(
                f"\n{index}. "
                f"REMOVE: {proposal['remove_skill']}"
            )

            print(
                f"   ADD   : {proposal['add_skill']}"
            )

            print(
                f"   Category: "
                f"{proposal['remove_category']}"
            )

            print(
                f"   Priority: "
                f"{proposal['remove_priority']}"
            )

    else:

        print("- None")


def main():

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

    proposals = build_replacement_pairs(
        verified_add_candidates,
        analysis["replacement_candidates"],
    )

    print_engine_output(
        analysis,
        verified_add_candidates,
        proposals,
    )


if __name__ == "__main__":

    main()