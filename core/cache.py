import json
from pathlib import Path
from typing import Any, Optional

class JsonCache:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        path = self.root / f"{key}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set(self, key: str, value: Any) -> None:
        path = self.root / f"{key}.json"
        path.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")
