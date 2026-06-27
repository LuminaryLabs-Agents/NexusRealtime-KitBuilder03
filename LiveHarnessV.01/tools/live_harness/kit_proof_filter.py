from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .common import read_json, tool_result


def _read_all(candidate_dir: Path) -> str:
    texts = []
    for path in candidate_dir.rglob("*.js"):
        texts.append(path.read_text(encoding="utf-8", errors="replace"))
    for path in [candidate_dir / "index.html", candidate_dir / "README.md"]:
        if path.exists():
            texts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(texts)


def check(run_dir: Path, candidate_dir: Path) -> dict[str, Any]:
    registry_path = run_dir / "intake" / "fused" / "kit-registry.json"
    proof_path = run_dir / "intake" / "fused" / "proof-tasks.json"
    registry = read_json(registry_path, {"kits": []})
    proof = read_json(proof_path, {"tasks": []})
    text = _read_all(candidate_dir)
    errors = []
    warnings = []
    if not registry_path.exists():
        errors.append("kit-registry.json missing")
    if not proof_path.exists():
        errors.append("proof-tasks.json missing")
    for kit in registry.get("kits", []):
        adapter = kit.get("adapter")
        fallback = kit.get("fallback")
        import_alias = kit.get("import_alias")
        if adapter and not (candidate_dir / adapter).exists():
            errors.append(f"missing adapter for {kit.get('kit_id')}: {adapter}")
        if fallback and not (candidate_dir / fallback).exists():
            errors.append(f"missing fallback for {kit.get('kit_id')}: {fallback}")
        if import_alias and import_alias not in text:
            warnings.append(f"import alias not found in candidate text: {import_alias}")
    required_text = ["window.__KitResolution", "integration", "provider", "local-fallback", "remote-kit"]
    for term in required_text:
        if term not in text:
            errors.append(f"missing integration proof term: {term}")
    adapter_count = len(list((candidate_dir / "src" / "integration" / "adapters").glob("*.js"))) if (candidate_dir / "src" / "integration" / "adapters").exists() else 0
    if adapter_count < 4:
        errors.append(f"expected at least 4 adapter files, found {adapter_count}")
    return tool_result("kit_proof_filter", not errors, "Kit proof passed" if not errors else "Kit proof failed", errors=errors, warnings=warnings, data={"kit_count": len(registry.get("kits", [])), "proof_task_count": len(proof.get("tasks", [])), "adapter_count": adapter_count})


if __name__ == "__main__":
    import sys
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    candidate = Path(sys.argv[2]) if len(sys.argv) > 2 else root
    print(json.dumps(check(root, candidate), indent=2))
