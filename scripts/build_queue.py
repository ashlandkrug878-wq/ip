"""Add missing image jobs to queue/image-jobs.json. Safe to run repeatedly.

- data/ips/<id>.json with a base prompt (`enp` or `zh`) and no base job:
  add a `base` job, unless the user marked the IP 淘汰. Expression cards from
  lab v2.0 carry no prompt and get no job.
- data/forms/<id>.json with no lineart job: add a `lineart` job, unless the
  user marked the form 淘汰.

New jobs start as `pending`. scripts/generate_images.py only runs when an
image API key is configured; otherwise the user generates the image in a chat
tool and uploads it on the board website, which marks the job done.
"""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "queue" / "image-jobs.json"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def main():
    jobs = load(QUEUE) if QUEUE.exists() else []
    have = {(j.get("ip"), j.get("kind")) for j in jobs}
    reviews = {p.stem: load(p) for p in (ROOT / "data" / "reviews").glob("*.json")}
    today = datetime.date.today().isoformat()
    added = 0

    def dropped(i):
        return reviews.get(i, {}).get("status") == "淘汰"

    for p in sorted((ROOT / "data" / "ips").glob("*.json")):
        ip, iid = load(p), p.stem
        if (iid, "base") in have or dropped(iid) or not (ip.get("enp") or ip.get("zh")):
            continue
        jobs.append({
            "id": f"{iid}-base-01", "ip": iid, "name": ip.get("name", ""), "kind": "base",
            "prompt_en": ip.get("enp", ""), "prompt_zh": ip.get("zh", ""), "size": "1024x1024",
            "status": "pending", "output": f"images/{iid}/base-01.png", "created": today, "note": "",
        })
        added += 1

    forms_dir = ROOT / "data" / "forms"
    for p in sorted(forms_dir.glob("*.json")) if forms_dir.exists() else []:
        f, fid = load(p), p.stem
        if (fid, "lineart") in have or dropped(fid):
            continue
        jobs.append({
            "id": f"{fid}-lineart-01", "ip": fid, "parent_ip": f.get("ip", ""),
            "name": f.get("title", ""), "kind": "lineart",
            "prompt_en": f.get("enp", ""), "prompt_zh": f.get("zh", ""), "size": "1024x1024",
            "status": "pending", "output": f"images/{fid}/lineart-01.png", "created": today, "note": "",
        })
        added += 1

    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"added {added} job(s); {len(jobs)} total")

if __name__ == "__main__":
    main()
