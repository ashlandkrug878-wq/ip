"""Add a base-image job to queue/image-jobs.json for every IP that has no job yet
and that the user has not marked 淘汰. Safe to run repeatedly."""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "queue" / "image-jobs.json"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def main():
    jobs = load(QUEUE) if QUEUE.exists() else []
    have = {j["ip"] for j in jobs if j.get("kind") == "base"}
    reviews = {p.stem: load(p) for p in (ROOT / "data" / "reviews").glob("*.json")}
    today = datetime.date.today().isoformat()
    added = 0
    for p in sorted((ROOT / "data" / "ips").glob("*.json")):
        ip = load(p)
        iid = p.stem
        if iid in have or reviews.get(iid, {}).get("status") == "淘汰":
            continue
        jobs.append({
            "id": f"{iid}-base-01",
            "ip": iid,
            "name": ip.get("name", ""),
            "kind": "base",
            "prompt_en": ip.get("enp", ""),
            "prompt_zh": ip.get("zh", ""),
            "size": "1024x1024",
            "status": "pending",
            "output": f"images/{iid}/base-01.png",
            "created": today,
            "note": "",
        })
        added += 1
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"added {added} job(s); {len(jobs)} total")

if __name__ == "__main__":
    main()
