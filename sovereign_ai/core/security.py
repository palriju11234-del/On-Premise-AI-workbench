class SecurityEngine:

    def classify(self, filename: str, text: str):

        sensitive_keywords = [
            "confidential",
            "internal",
            "inspection",
            "maintenance",
            "equipment",
            "vendor",
            "plant",
            "refinery"
        ]

        score = 0

        text_lower = text.lower()

        for keyword in sensitive_keywords:
            if keyword in text_lower:
                score += 1

        if score >= 2:
            classification = "CONFIDENTIAL"
        elif score == 1:
            classification = "INTERNAL"
        else:
            classification = "GENERAL"

        return {
            "classification": classification,
            "score": score,
            "policy": self.get_policy(classification)
        }

    def get_policy(self, classification):

        policies = {
            "GENERAL": {
                "allow_local_processing": True,
                "external_api": False,
                "human_review": False
            },

            "INTERNAL": {
                "allow_local_processing": True,
                "external_api": False,
                "human_review": False
            },

            "CONFIDENTIAL": {
                "allow_local_processing": True,
                "external_api": False,
                "human_review": True
            }
        }

        return policies[classification]