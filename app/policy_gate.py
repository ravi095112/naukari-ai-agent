from typing import Any


ALLOWED_ACTIONS = {"PROPOSE"}

ALLOWED_REMOVE_CATEGORIES = {
    "REDUNDANT_VARIANT",
    "SUPPORTING_SKILL",
    "TESTING_SKILL",
}


def validate_replacement_proposal(
        proposal: dict[str, Any],
        current_skills: list[str],
        verified_add_candidates: dict[str, list[str]],
        removal_candidates: list[dict],
) -> dict[str, Any]:

    errors = []

    remove_skill = proposal.get("remove_skill")
    add_skill = proposal.get("add_skill")
    reason = proposal.get("reason")
    action = proposal.get("action")

    # ---------------------------------------------------------
    # Required fields
    # ---------------------------------------------------------

    if not remove_skill:
        errors.append("Missing remove_skill")

    if not add_skill:
        errors.append("Missing add_skill")

    if not reason:
        errors.append("Missing reason")

    if not action:
        errors.append("Missing action")

    # ---------------------------------------------------------
    # Action validation
    # ---------------------------------------------------------

    if action not in ALLOWED_ACTIONS:
        errors.append(
            f"Unsupported action: {action}"
        )

    # ---------------------------------------------------------
    # Add-skill validation
    # ---------------------------------------------------------

    if add_skill and add_skill not in verified_add_candidates:
        errors.append(
            f"Add skill '{add_skill}' "
            f"was not evidence-verified."
        )

    # ---------------------------------------------------------
    # Remove-skill validation
    # ---------------------------------------------------------

    removal_map = {
        item["skill"]: item
        for item in removal_candidates
    }

    if remove_skill:

        if remove_skill not in current_skills:
            errors.append(
                f"Remove skill '{remove_skill}' "
                f"is not currently present."
            )

        elif remove_skill not in removal_map:
            errors.append(
                f"Remove skill '{remove_skill}' "
                f"is not an approved removal candidate."
            )

        else:

            category = removal_map[
                remove_skill
            ].get("category")

            if category not in ALLOWED_REMOVE_CATEGORIES:
                errors.append(
                    f"Removal category '{category}' "
                    f"is not allowed."
                )

    # ---------------------------------------------------------
    # Prevent duplicate skill
    # ---------------------------------------------------------

    if (
            add_skill
            and remove_skill
            and add_skill == remove_skill
    ):
        errors.append(
            "Cannot remove and add the same skill."
        )

    # ---------------------------------------------------------
    # Text validation
    # ---------------------------------------------------------

    if reason:

        if len(reason) > 500:
            errors.append(
                "Reason is too long."
            )

        if "\n" in reason:
            errors.append(
                "Reason must be a single line."
            )

    # ---------------------------------------------------------
    # Final decision
    # ---------------------------------------------------------

    if errors:

        return {
            "decision": "REJECT",
            "remove_skill": remove_skill,
            "add_skill": add_skill,
            "reason": reason,
            "action": action,
            "errors": errors,
        }

    return {
        "decision": "PASS",
        "remove_skill": remove_skill,
        "add_skill": add_skill,
        "reason": reason,
        "action": action,
        "errors": [],
    }