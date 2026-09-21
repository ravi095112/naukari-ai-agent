from policy_gate import (
    validate_all,
    print_policy_results,
)


supported_skills = {
    "REST API": [
        "Developed Java-based RESTful APIs enabling seamless integration across 15+ microservices.",
        "Built Java RESTful services with Spring Boot.",
    ],

    "Docker": [
        "Docker is explicitly listed under Cloud & DevOps technical skills.",
    ],

    "GenAI": [
        "Engineered an AI-driven chatbot utilizing Langchain and Spring AI.",
        "Implemented Retrieval-Augmented Generation (RAG).",
    ],
}


proposals = [
    {
        "skill": "REST API",
        "proposed_skill_text": "REST API",
        "reason": "Developed Java-based RESTful APIs and microservices with Spring Boot.",
        "action": "PROPOSE",
    },

    {
        "skill": "Docker",
        "proposed_skill_text": "Docker",
        "reason": "Listed under Cloud and DevOps technical skills.",
        "action": "PROPOSE",
    },

    {
        "skill": "GenAI",
        "proposed_skill_text": "Generative AI",
        "reason": "Engineered an AI-driven chatbot using LangChain and Spring AI with RAG.",
        "action": "PROPOSE",
    },

    # Intentionally malicious/unsupported proposal
    {
        "skill": "Kubernetes",
        "proposed_skill_text": "Kubernetes",
        "reason": "Modern cloud technology.",
        "action": "PROPOSE",
    },
]


results = validate_all(
    proposals,
    supported_skills,
)

print_policy_results(results)