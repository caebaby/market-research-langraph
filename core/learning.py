from core.config import Config

class SimpleLearning:
    def critique(self, result: str):
        llm = Config.get_llm()
        prompt = f"Score (0-1) and improve: {result}"
        eval = llm.invoke(prompt).content.split('\n')
        score = float(eval[0].split()[0])
        return eval[1] if score < 0.9 else None
