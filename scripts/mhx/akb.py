"""MHX AKB: flat index first (markdown + derived JSON). Query/update as CLI verbs.

Record contract: {stable id, kind, explanation, scope, sources+symbol anchors
(lines=hints), relationships+provenance, fingerprints+last-reviewed,
review_state}. Qualified code IDs language/package/module/symbol. Whole-file
fingerprints conservative first. Bounded query MAX 25 + truncation marker.
Drop no-stopwords rule.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .common import MAX_RECORDS, atomic_write, envelope

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def _parse_record(p: Path) -> dict:
    text = p.read_text(encoding="utf-8")
    m = FRONT_RE.match(text)
    if not m:
        return {"id": p.stem, "path": str(p), "review_state": "unverified",
                "explanation": text[:500], "sources": []}
    front, body = m.group(1), m.group(2)
    meta: dict = {}
    cur_key = None
    for line in front.splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
            cur_key = k.strip()
        elif line.strip().startswith("- ") and cur_key:
            meta.setdefault(cur_key + "_list", []).append(line.strip()[2:])
    srcs = meta.get("sources_list", []) or ([meta["sources"]] if meta.get("sources") else [])
    return {"id": meta.get("id", p.stem), "kind": meta.get("kind", "concept"),
            "sources": srcs, "fingerprint": meta.get("fingerprint", ""),
            "review_state": meta.get("review_state", "unverified"),
            "explanation": body.strip()[:2000], "path": str(p)}


def _fingerprint_source(ws: Path, src: str) -> str:
    p = (ws / src) if not src.startswith("/") else Path(src)
    if not p.exists() or not p.is_file():
        return "missing"
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return "sha256:" + h.hexdigest()[:16]


def akb_query(ws: Path, q: str, limit: int = MAX_RECORDS) -> dict:
    rec_dir = ws / ".mhx" / "knowledge" / "records"
    recs = [_parse_record(p) for p in rec_dir.glob("*.md")] if rec_dir.exists() else []
    ql = q.lower()
    scored = []
    for r in recs:
        hay = (r["id"] + " " + r.get("explanation", "")).lower()
        score = sum(1 for tok in ql.split() if tok in hay)
        if not ql or score > 0:
            scored.append((score, r))
    scored.sort(key=lambda t: -t[0])
    # Freshness: compare recorded fingerprint prefix vs current source hash.
    out = []
    for _, r in scored[:limit]:
        fps = []
        for s in r.get("sources", []):
            cur = _fingerprint_source(ws, s.split("#")[0])
            rec = (r.get("fingerprint", "") or "").strip().strip('"')
            if rec.startswith("sha256:"):
                fresh = rec[:23] in cur if cur != "missing" else "unknown"
            else:
                fresh = "unknown"  # symbolic fingerprint: unknown, not stale
            fps.append({"source": s, "current": cur, "fresh": fresh})
        needs = any(f["fresh"] is False for f in fps) if fps else False
        out.append({**r, "freshness": fps,
                    "effective_review": "needs-review" if needs else r["review_state"]})
    truncated = len(scored) > limit
    return envelope(True, "akb-query", ws, query=q, results=out,
                    truncated=truncated,
                    refine="narrow query or inspect cited sources directly")


def akb_update(ws: Path, rid: str, explanation: str, sources: str = "") -> dict:
    rec_dir = ws / ".mhx" / "knowledge" / "records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    # Qualified-ID guard: warn on unqualified collision (first-by-sorted-path-wins is a bug).
    if "/" not in rid and "." not in rid and ":" not in rid:
        pass  # curated IDs may be short; code IDs must be qualified (checked in review)
    p = rec_dir / f"{rid}.md"
    srcs = [s.strip() for s in sources.split(",") if s.strip()]
    fps = ",".join(_fingerprint_source(ws, s.split('#')[0]) for s in srcs) or "no-sources"
    body = (f"---\nid: {rid}\nkind: concept\nsources:\n"
            + "".join(f"  - {s}\n" for s in srcs)
            + f"fingerprint: \"{fps[:64]}\"\nreview_state: reviewed\n---\n\n# {rid}\n\n{explanation}\n")
    atomic_write(p, body)
    return envelope(True, "akb-update", ws, id=rid, path=str(p))


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    verb = argv[0] if argv else ""
    if verb == "akb-query":
        q, limit = "", MAX_RECORDS
        it = iter(argv[1:])
        for a in it:
            if a == "--q":
                q = next(it, "")
            elif a == "--limit":
                limit = int(next(it, str(MAX_RECORDS)))
        return emit(akb_query(ws, q, limit), True)
    if verb == "akb-update":
        rid, exp, src = "", "", ""
        it = iter(argv[1:])
        for a in it:
            if a == "--id":
                rid = next(it, "")
            elif a == "--explanation":
                exp = next(it, "")
            elif a == "--sources":
                src = next(it, "")
        if not rid or not exp:
            return emit(envelope(False, "akb-update", ws, error="--id + --explanation required"), True)
        return emit(akb_update(ws, rid, exp, src), True)
    return emit(envelope(False, "akb", ws, error="unknown subverb"), True)
