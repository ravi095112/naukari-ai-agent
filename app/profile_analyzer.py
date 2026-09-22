from profile_reader import read_profile

TARGET_ROLES = [
    "Senior Java Developer",
    "Senior Backend Developer",
    "Java Microservices Developer",
    "Java + GenAI Developer",
    "AI/LLM Application Developer",
]

TARGET_SKILLS = [
    "Java",
    "Spring Boot",
    "Spring Security",
    "Microservices",
    "Rest API Development",
    "Docker",
    "Kubernetes",
    "Kafka",
    "AWS",
    "Python",
    "Fast API",
    "Spring AI",
    "Langchain",
    "Retrieval Augmented Generation",
    "Generative Ai",
]

MAX_KEY_SKILLS = 23


def normalize(value: str) -> str:
    return " ".join(
        value.lower().strip().split()
    )


SKILL_ALIASES = {
    "Fast API": ["fastapi", "fast api"],
    "Rest API Development": ["rest api development"],
    "Langchain": ["langchain"],
    "Retrieval Augmented Generation": [
        "retrieval augmented generation",
        "rag",
    ],
    "Generative Ai": ["generative ai", "genai"],
}


REMOVAL_CANDIDATES = {
    "Spring Application Framework": {
        "priority": 1,
        "category": "REDUNDANT_VARIANT",
        "reason": (
            "Overlaps with Spring Boot and other Spring framework "
            "entries already present."
        ),
    },
    "Spring Boot Framework": {
        "priority": 2,
        "category": "REDUNDANT_VARIANT",
        "reason": (
            "Overlaps with the primary Spring Boot skill already present."
        ),
    },
    "Java Spring Boot": {
        "priority": 3,
        "category": "REDUNDANT_VARIANT",
        "reason": (
            "Overlaps with Java and Spring Boot already present."
        ),
    },
    "Spring Data": {
        "priority": 4,
        "category": "SUPPORTING_SKILL",
        "reason": (
            "Useful backend skill, but less directly aligned with "
            "the missing target skills."
        ),
    },
    "Spring Integration": {
        "priority": 5,
        "category": "SUPPORTING_SKILL",
        "reason": (
            "Useful integration skill, but not one of the current "
            "highest-priority target skills."
        ),
    },
    "JUnit": {
        "priority": 6,
        "category": "TESTING_SKILL",
        "reason": (
            "Useful testing skill that should generally be preserved "
            "unless a stronger profile improvement is justified."
        ),
    },
    "Mockito": {
        "priority": 7,
        "category": "TESTING_SKILL",
        "reason": (
            "Useful testing skill that should generally be preserved "
            "unless a stronger profile improvement is justified."
        ),
    },
}


def skill_is_present(skill: str, skills: list[str], headline: str) -> str:
    normalized_skills = {
        normalize(skill_value)
        for skill_value in skills
    }

    normalized_headline = normalize(headline)

    aliases = SKILL_ALIASES.get(skill, [skill])

    for alias in aliases:
        alias_normalized = normalize(alias)

        if alias_normalized in normalized_skills:
            return "PRESENT_IN_SKILLS"

        if alias_normalized in normalized_headline:
            return "PRESENT_IN_HEADLINE"

    return "NOT_CURRENTLY_VISIBLE"


def find_missing_target_skills(
    skill_visibility: dict[str, str],
) -> list[str]:
    return [
        skill
        for skill, status in skill_visibility.items()
        if status == "NOT_CURRENTLY_VISIBLE"
    ]


def find_replacement_candidates(
    skills: list[str],
) -> list[dict]:
    normalized_existing = {
        normalize(skill): skill
        for skill in skills
    }

    candidates = []

    for candidate_name, metadata in REMOVAL_CANDIDATES.items():
        normalized_candidate = normalize(candidate_name)

        if normalized_candidate in normalized_existing:
            candidates.append(
                {
                    "skill": normalized_existing[normalized_candidate],
                    "priority": metadata["priority"],
                    "category": metadata["category"],
                    "reason": metadata["reason"],
                }
            )

    candidates.sort(
        key=lambda item: item["priority"]
    )

    return candidates


def analyze_profile(profile: dict) -> dict:
    headline = profile["resume_headline"]
    skills = profile["key_skills"]

    visibility = {}

    for skill in TARGET_SKILLS:
        visibility[skill] = skill_is_present(
            skill,
            skills,
            headline,
        )

    skill_count = len(skills)

    if skill_count >= MAX_KEY_SKILLS:
        capacity_status = "FULL"
    else:
        capacity_status = "AVAILABLE"

    missing_target_skills = find_missing_target_skills(
        visibility
    )

    replacement_candidates = find_replacement_candidates(
        skills
    )

    return {
        "target_roles": TARGET_ROLES,
        "target_skills": TARGET_SKILLS,
        "skill_visibility": visibility,
        "key_skill_count": skill_count,
        "max_key_skills": MAX_KEY_SKILLS,
        "capacity_status": capacity_status,
        "missing_target_skills": missing_target_skills,
        "replacement_candidates": replacement_candidates,
        "current_key_skills": skills,
    }


def print_analysis(analysis: dict):
    print(
        "\n========== Profile Analysis ==========\n"
    )

    print("Target roles:")

    for role in analysis["target_roles"]:
        print(f"- {role}")

    print("\nKey Skills capacity:")

    print(
        f"{analysis['key_skill_count']}/"
        f"{analysis['max_key_skills']} "
        f"({analysis['capacity_status']})"
    )

    print("\nSkill visibility:")

    for skill, status in analysis["skill_visibility"].items():
        print(
            f"{skill:<35} -> {status}"
        )

    print("\nMissing target skills:")

    if analysis["missing_target_skills"]:
        for skill in analysis["missing_target_skills"]:
            print(f"- {skill}")
    else:
        print("- None")

    print("\nReplacement candidates:")

    if analysis["replacement_candidates"]:
        for candidate in analysis["replacement_candidates"]:
            print(f"- {candidate['skill']}")
            print(f"  Priority : {candidate['priority']}")
            print(f"  Category : {candidate['category']}")
            print(f"  Reason   : {candidate['reason']}")
    else:
        print("- None")


if __name__ == "__main__":
    profile = read_profile()

    analysis = analyze_profile(profile)

    print_analysis(analysis)
