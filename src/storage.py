
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data/interviews")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_interview(responses, transcript, summary):
    path = DATA_DIR / f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "project": "Agentic AI Exit Interview Voice",
                "llm_provider": "Groq"
            },
            "responses": responses,
            "transcript": transcript,
            "ai_summary": summary
        }, f, indent=4, ensure_ascii=False)
    return str(path)
