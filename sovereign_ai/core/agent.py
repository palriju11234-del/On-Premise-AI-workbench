import ollama

from .model_router import ModelRouter
from .verifier import Verifier
from .security import SecurityEngine
from .provenance import Provenance


class LocalLLM:

    def generate(self, model, prompt):

        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]


class SovereignAgent:

    def __init__(self, knowledge_store):

        self.llm = LocalLLM()

        self.router = ModelRouter()
        self.security = SecurityEngine()
        self.verifier = Verifier()
        self.provenance = Provenance()

        self.knowledge_store = knowledge_store


    def run(self, task, document_text):

        events = []

        # 1. Understand task
        events.append("Understanding task")

        task_type = "scanned_document"


        # 2. Security classification
        events.append("Classifying information")

        security = self.security.classify(
            "inspection_report.pdf",
            document_text
        )


        # 3. Model selection
        events.append("Selecting local model")

        model = self.router.route(task_type)


        # 4. Local knowledge retrieval
        events.append("Searching local knowledge base")

        knowledge = self.knowledge_store.search(
            task,
            top_k=3
        )

        context = "\n\n".join(knowledge)


        # 5. Agent reasoning
        events.append("Executing agent reasoning")

        prompt = f"""
You are a controlled enterprise AI assistant.

RULES:

1. Use ONLY the supplied document and organizational knowledge.
2. Do not invent facts.
3. If information is missing, explicitly state it.
4. Separate evidence from conclusions.
5. This is confidential industrial information.
6. Never claim that an action has been approved unless a human has approved it.

USER TASK:
{task}

INSPECTION DOCUMENT:
{document_text}

ORGANIZATIONAL KNOWLEDGE:
{context}

Produce:

1. Key findings
2. Evidence
3. SOP comparison
4. Recommended action
5. Uncertainties
6. Approval recommendation
"""


        answer = self.llm.generate(
            model["name"],
            prompt
        )


        # 6. Verification
        events.append("Verifying output")

        verification = self.verifier.verify(
            answer,
            knowledge
        )


        # 7. Risk assessment
        events.append("Running risk assessment")

        human_required = (
            security["classification"] == "CONFIDENTIAL"
        )


        return {
            "answer": answer,
            "security": security,
            "model": model,
            "verification": verification,
            "human_required": human_required,
            "events": events
        }