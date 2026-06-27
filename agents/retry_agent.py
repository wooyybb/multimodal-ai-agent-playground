class RetryAgent:
    def __init__(self, threshold=0.75):
        self.threshold = threshold

    def should_retry(self, score: float) -> bool:
        if score < self.threshold:
            print("[RetryAgent] Score below threshold. Retry needed.")
            return True

        print("[RetryAgent] Score meets threshold. No retry.")
        return False
