import base64
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

import ollama

from .model_router import ModelRouter
from .verifier import Verifier
from .security import SecurityEngine
from .provenance import Provenance
from sovereign_ai.core.logger import logger, SovereignException
from sovereign_ai.services.rag_service import RAGService
from sovereign_ai.schemas.security import UserRole, DataClassification


class LocalLLM:
    def generate(
        self,
        model: str,
        prompt: str,
        images: Optional[List[str]] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Invokes local Ollama for inference with strict error handling.
        Never fabricates responses or uses mock fallbacks.
        """
        formatted_images: Optional[List[str]] = None
        if images:
            formatted_images = []
            for img in images:
                if not img:
                    continue
                img_path = Path(img)
                if img_path.exists() and img_path.is_file():
                    try:
                        b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")
                        formatted_images.append(b64)
                    except Exception as e:
                        raise SovereignException(
                            f"Failed to read image file '{img}': {str(e)}",
                            status_code=400,
                        )
                else:
                    raw_b64 = img
                    if "," in raw_b64 and "base64" in raw_b64.split(",")[0]:
                        raw_b64 = raw_b64.split(",", 1)[1]
                    try:
                        base64.b64decode(raw_b64)
                        formatted_images.append(raw_b64)
                    except Exception:
                        raise SovereignException(
                            "Invalid image input: expected existing file path or valid base64 string.",
                            status_code=400,
                        )

        message: Dict[str, Any] = {"role": "user", "content": prompt}
        if formatted_images:
            message["images"] = formatted_images

        try:
            response = ollama.chat(
                model=model,
                messages=[message],
                options={"temperature": temperature},
            )
            content = response.get("message", {}).get("content", "")
            return content
        except ollama.ResponseError as e:
            logger.error(f"Ollama ResponseError with model '{model}': {e}")
            if e.status_code == 404 or "not found" in str(e).lower():
                raise SovereignException(
                    f"Model '{model}' is not installed or available in local Ollama.",
                    status_code=404,
                )
            raise SovereignException(
                f"Ollama inference error with model '{model}': {e.error}",
                status_code=500,
            )
        except SovereignException:
            raise
        except Exception as e:
            err_str = str(e).lower()
            logger.error(f"Ollama daemon invocation failed for model '{model}': {e}")
            if "connection" in err_str or "connect" in err_str or "refused" in err_str:
                raise SovereignException(
                    "Local Ollama daemon is unreachable. Please ensure the Ollama service is running.",
                    status_code=503,
                )
            raise SovereignException(
                f"Inference execution failed on model '{model}': {str(e)}",
                status_code=500,
            )


class SovereignAgent:
    def __init__(self, knowledge_store=None):
        self.llm = LocalLLM()
        self.router = ModelRouter()
        self.security = SecurityEngine()
        self.verifier = Verifier()
        self.provenance = Provenance()
        self.knowledge_store = knowledge_store

    def run(
        self,
        task: str,
        document_text: str,
        filename: str = "inspection_report.pdf",
        user_role: UserRole = UserRole.ENGINEER,
        image: Optional[str] = None,
    ) -> Dict[str, Any]:
        events = []

        # 1. Task understanding
        events.append("Understanding task")
        lower_fn = (filename or "").lower()
        lower_task = (task or "").lower()

        if image or lower_fn.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")):
            task_type = "vision"
        elif any(kw in lower_task for kw in ["code", "coding", "python", "debug", "script", "function", "program"]):
            task_type = "coding"
        else:
            task_type = "reasoning"

        # 2. Security classification
        events.append("Classifying information")
        security = self.security.classify(filename, document_text)
        doc_classification = DataClassification(security["classification"])

        # 3. Model routing
        events.append("Selecting local model")
        routing_info = self.router.route(task_type, classification=doc_classification)
        model_name = routing_info["model"]

        # 4. Local knowledge retrieval (RBAC-filtered)
        events.append("Searching local knowledge base")
        rag_response = RAGService.retrieve(query=task, user_role=user_role, top_k=3)
        knowledge_chunks = [item.text for item in rag_response.results]
        context = "\n\n".join(knowledge_chunks) if knowledge_chunks else "No relevant knowledge found."

        # 5. Agent reasoning via real local Ollama inference
        events.append("Executing agent reasoning")
        prompt = f"""You are a controlled enterprise AI assistant.

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
        images_list = [image] if image else None
        answer = self.llm.generate(
            model=model_name,
            prompt=prompt,
            images=images_list,
            temperature=routing_info.get("temperature", 0.7),
        )

        # 6. Verification
        events.append("Verifying output")
        verification = self.verifier.verify(answer, knowledge_chunks)

        # 7. Risk assessment
        events.append("Running risk assessment")
        human_required = (security["classification"] == "CONFIDENTIAL")

        # 8. Provenance & immutable audit logging
        events.append("Writing provenance audit trail")
        input_hash = hashlib.sha256((task + document_text).encode("utf-8")).hexdigest()
        output_hash = hashlib.sha256(answer.encode("utf-8")).hexdigest()

        audit_record = self.provenance.create_record(
            task=task,
            model=model_name,
            verification=verification,
            approval=not human_required,
            input_hash=input_hash,
            output_hash=output_hash,
        )

        return {
            "answer": answer,
            "security": security,
            "model": routing_info,
            "verification": verification,
            "human_required": human_required,
            "events": events,
            "retrieved_sources": len(knowledge_chunks),
            "audit_record": audit_record,
        }