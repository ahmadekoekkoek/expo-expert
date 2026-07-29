"""XOS Clarify Engine — interactive spec refinement before compilation."""

import json
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ClarifyQuestion:
    id: str
    question: str
    context: str = ""
    options: list[str] = field(default_factory=list)
    answer: str = ""

class ClarifyEngine:
    def __init__(self):
        self.questions: list[ClarifyQuestion] = []

    def scan_spec(self, spec_path: str) -> list[ClarifyQuestion]:
        spec = Path(spec_path)
        if not spec.exists():
            return []
        data = json.loads(spec.read_text()) if spec.suffix == ".json" else {}
        qs = []
        if not data.get("name"):
            qs.append(ClarifyQuestion(id="name", question="What is the feature/screen name?", context="spec root"))
        if not data.get("screens"):
            qs.append(ClarifyQuestion(id="screens", question="How many screens does this feature require?", options=["1", "2", "3", "4+"]))
        if not data.get("user_stories"):
            qs.append(ClarifyQuestion(id="user_stories", question="What are the primary user stories?", context="Describe the core flows."))
        self.questions = qs
        return qs

    def set_answer(self, qid: str, answer: str):
        for q in self.questions:
            if q.id == qid:
                q.answer = answer

    def unresolved(self) -> list[ClarifyQuestion]:
        return [q for q in self.questions if not q.answer]

def cmd_clarify(args):
    engine = ClarifyEngine()
    qs = engine.scan_spec(args.spec) if hasattr(args, 'spec') else []
    if not qs:
        print("No clarification needed.")
        return
    for i, q in enumerate(qs, 1):
        opts = f" [{', '.join(q.options)}]" if q.options else ""
        print(f"{i}. {q.question}{opts}")
