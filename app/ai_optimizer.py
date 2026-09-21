from dataclasses import dataclass
from typing import List

from profile_reader import read_profile
from profile_analyzer import analyze_profile
from evidence_checker import load_evidence, check_skill_evidence


@dataclass
class ProfileOptimizationProposal:
    change: str
    reason: str
    evidence: list[str]
    confidence: float
    action: str = "PROPOSE"


def generate_proposals(
    profile: dict,
    analysis: dict,
    evidence_data: dict,
) -> List[ProfileOptimizationProposal]:

    proposals = []

    for skill, status in analysis["skill_visibility"].items():

        # Already visible on Naukri -> no change required.
        if status != "NOT_CURRENTLY_VISIBLE":
            continue

        evidence_result = check_skill_evidence(
            skill,
            evidence_data
        )

        # Never propose unsupported skills.
        if evidence_result["decision"] != "PROPOSE":
            continue

        proposals.append(
            ProfileOptimizationProposal(
                change=f"Consider adding '{skill}' to Key Skills",
                reason=(
                    f"{skill} is not currently visible on Naukri "
                    "but is supported by verified resume evidence."
                ),
                evidence=evidence_result["evidence"],
                confidence=0.90,
            )
        )

    return proposals


def print_proposals(
    proposals: List[ProfileOptimizationProposal]
):
    print("\n========== Evidence-Aware Profile Proposals ==========\n")

    if not proposals:
        print("No supported profile changes proposed.")
        return

    for index, proposal in enumerate(proposals, start=1):
        print(f"Proposal #{index}")
        print(f"Action     : {proposal.action}")
        print(f"Change     : {proposal.change}")
        print(f"Reason     : {proposal.reason}")
        print(f"Evidence   :")

        for evidence in proposal.evidence:
            print(f"  - {evidence}")

        print(f"Confidence : {proposal.confidence}")
        print()


if __name__ == "__main__":

    # 1. Read current Naukri profile
    profile = read_profile()

    # 2. Analyze profile visibility
    analysis = analyze_profile(profile)

    # 3. Load verified resume evidence
    evidence_data = load_evidence()

    # 4. Generate evidence-aware proposals
    proposals = generate_proposals(
        profile,
        analysis,
        evidence_data,
    )

    # 5. Print proposals only
    print_proposals(proposals)