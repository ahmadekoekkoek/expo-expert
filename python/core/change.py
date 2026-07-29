"""XOS Change Management — isolate proposals from the main graph, OpenSpec-style."""

import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from typing import Optional

class ChangeStatus(str, Enum):
    PROPOSED = "proposed"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    ARCHIVED = "archived"
    REJECTED = "rejected"

@dataclass
class Change:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    status: ChangeStatus = ChangeStatus.PROPOSED
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    spec_files: list[str] = field(default_factory=list)
    affected_nodes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "description": self.description, "status": self.status.value, "created_at": self.created_at, "completed_at": self.completed_at, "spec_files": self.spec_files, "affected_nodes": self.affected_nodes}

class ChangeManager:
    def __init__(self, workspace_dir: str = "workspace"):
        self.changes_dir = Path(workspace_dir) / "changes"
        self.archive_dir = Path(workspace_dir) / "archive"
        self.changes_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def propose(self, title: str, description: str = "") -> Change:
        c = Change(title=title, description=description)
        (self.changes_dir / c.id).mkdir(parents=True, exist_ok=True)
        (self.changes_dir / c.id / "proposal.json").write_text(json.dumps(c.to_dict(), indent=2))
        return c

    def list_active(self) -> list[dict]:
        result = []
        for d in self.changes_dir.iterdir():
            if d.is_dir():
                pf = d / "proposal.json"
                if pf.exists():
                    result.append(json.loads(pf.read_text()))
        return result

    def apply(self, change_id: str) -> bool:
        pf = self.changes_dir / change_id / "proposal.json"
        if not pf.exists():
            return False
        data = json.loads(pf.read_text())
        data["status"] = ChangeStatus.IMPLEMENTED.value
        data["completed_at"] = datetime.now(timezone.utc).isoformat()
        pf.write_text(json.dumps(data, indent=2))
        return True

    def archive(self, change_id: str) -> bool:
        src = self.changes_dir / change_id
        dst = self.archive_dir / change_id
        if not src.exists():
            return False
        src.rename(dst)
        return True

def cmd_change(args):
    mgr = ChangeManager()
    if args.subcommand == "list":
        changes = mgr.list_active()
        if not changes:
            print("No active changes.")
            return
        for c in changes:
            print(f"  [{c['id']}] {c['title']} ({c['status']})")
    elif args.subcommand == "propose":
        c = mgr.propose(args.title, args.description or "")
        print(f"Change proposed: {c.id}")
    elif args.subcommand == "apply":
        ok = mgr.apply(args.id)
        print(f"Change {args.id} {'applied' if ok else 'not found'}")
    elif args.subcommand == "archive":
        ok = mgr.archive(args.id)
        print(f"Change {args.id} {'archived' if ok else 'not found'}")
