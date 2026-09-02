class Verifier:

    def verify(self, answer, evidence):

        evidence_text = "\n".join(evidence)

        supported = True

        # Basic prototype verification
        if len(answer.strip()) < 50:
            supported = False

        return {
            "status": "PASSED" if supported else "FAILED",
            "evidence_sources": len(evidence),
            "grounded": supported
        }