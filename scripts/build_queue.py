"""Add missing image jobs to the image queues. Safe to run repeatedly.

Two separate pipelines, two separate queues:
- queue/image-jobs.json       daily concepts and the main workflow (ChatGPT daily run)
- queue/star-image-jobs.json  Grok star pipeline: anything whose id starts with
                              "star-" or whose data has source "grok-star"

Jobs:
- data/ips/<id>.json with a base prompt (`enp` or `zh`) and no base job:
  add a `base` job, unless the user marked the IP 淘汰. Expression cards without
  a prompt get no job.
- data/forms/<id>.json with no lineart job: add a `lineart` job (concept image,
  clay or line art, see the form's `render`), unless the user marked it 淘汰.
  A form with `reference` (path to an image in the repo) passes it to the job.

New jobs start as `pending`. scripts/generate_images.py only processes the main
queue and only when an image API key is configured; otherwise the image is
made in a chat tool (ChatGPT for the main queue, Grok for the star queue) and
uploaded, which marks the job done.
"""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "queue" / "image-jobs.json"
STAR_QUEUE = ROOT / "queue" / "star-image-jobs.json"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def is_star(item_id, data):
    return item_id.startswith("star-") or data.get("source") == "grok-star"


def main():
    queues = {False: load(QUEUE) if QUEUE.exists() else [], True: load(STAR_QUEUE) if STAR_QUEUE.exists() else []}
    have = {k: {(j.get("ip"), j.get("kind")) for j in v} for k, v in queues.items()}
    reviews = {p.stem: load(p) for p in (ROOT / "data" / "reviews").glob("*.json")}
    today = datetime.date.today().isoformat()
    added = {False: 0, True: 0}

    def dropped(i):
        return reviews.get(i, {}).get("status") == "淘汰"

    def add(star, job):
        queues[star].append(job)
        added[star] += 1

    for p in sorted((ROOT / "data" / "ips").glob("*.json")):
        ip, iid = load(p), p.stem
        star = is_star(iid, ip)
        if (iid, "base") in have[star] or dropped(iid) or not (ip.get("enp") or ip.get("zh")):
            continue
        add(star, {
            "id": f"{iid}-base-01", "ip": iid, "name": ip.get("name", ""), "kind": "base",
            "prompt_en": ip.get("enp", ""), "prompt_zh": ip.get("zh", ""), "size": "1024x1024",
            "status": "pending", "output": f"images/{iid}/base-01.png", "created": today, "note": "",
        })

    forms_dir = ROOT / "data" / "forms"
    for p in sorted(forms_dir.glob("*.json")) if forms_dir.exists() else []:
        f, fid = load(p), p.stem
        star = is_star(fid, f)
        if (fid, "lineart") in have[star] or dropped(fid):
            continue
        job = {
            "id": f"{fid}-lineart-01", "ip": fid, "parent_ip": f.get("ip", ""),
            "name": f.get("title", ""), "kind": "lineart", "render": f.get("render", ""),
            "prompt_en": f.get("enp", ""), "prompt_zh": f.get("zh", ""), "size": "1024x1024",
            "status": "pending", "output": f"images/{fid}/lineart-01.png", "created": today, "note": "",
        }
        if f.get("reference"):
            job["reference"] = f["reference"]
        add(star, job)

    for star, path in ((False, QUEUE), (True, STAR_QUEUE)):
        if star and not queues[True] and not STAR_QUEUE.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(queues[star], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"main queue: added {added[False]}, {len(queues[False])} total; "
          f"star queue: added {added[True]}, {len(queues[True])} total")


if __name__ == "__main__":
    main()
