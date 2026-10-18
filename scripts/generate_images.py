"""Process pending jobs in queue/image-jobs.json with an OpenAI-compatible
image generation endpoint. Configure with environment variables:

  IMAGE_API_KEY  required; without it the script exits without doing anything
  IMAGE_API_URL  default https://api.openai.com/v1/images/generations
  IMAGE_MODEL    model name from your provider's docs
  MAX_JOBS       optional cap per run (default 6)

Each finished image is written to the job's `output` path and the job is marked
done; failures are marked failed with the reason in `note`.
"""
import base64, json, os, pathlib, sys, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "queue" / "image-jobs.json"

def call(url, key, model, prompt, size):
    body = {"prompt": prompt, "size": size, "n": 1}
    if model:
        body["model"] = model
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read().decode("utf-8"))
    item = (data.get("data") or [{}])[0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    if item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=300) as r:
            return r.read()
    raise RuntimeError("response had no image: " + json.dumps(data)[:300])

def main():
    key = os.environ.get("IMAGE_API_KEY", "").strip()
    if not key:
        print("IMAGE_API_KEY is not set; skipping image generation")
        return 0
    url = os.environ.get("IMAGE_API_URL", "").strip() or "https://api.openai.com/v1/images/generations"
    model = os.environ.get("IMAGE_MODEL", "").strip()
    cap = int(os.environ.get("MAX_JOBS", "6") or 6)
    jobs = json.loads(QUEUE.read_text(encoding="utf-8")) if QUEUE.exists() else []
    done = 0
    for j in jobs:
        if j.get("status") != "pending" or done >= cap:
            continue
        prompt = j.get("prompt_en") or j.get("prompt_zh")
        if not prompt:
            j["status"], j["note"] = "failed", "no prompt"
            continue
        try:
            img = call(url, key, model, prompt, j.get("size", "1024x1024"))
            out = ROOT / j["output"]
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(img)
            j["status"], j["note"] = "done", ""
            print("done", j["id"])
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError, OSError) as e:
            detail = e.read().decode("utf-8", "replace")[:300] if isinstance(e, urllib.error.HTTPError) else str(e)
            j["status"], j["note"] = "failed", detail
            print("failed", j["id"], detail, file=sys.stderr)
        done += 1
    QUEUE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    sys.exit(main())
