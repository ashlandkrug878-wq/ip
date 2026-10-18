"""Write data/index.json listing every doc id in data/batches, ips, reviews and
pools. The website reads this file because a static site cannot list folders.
Run after adding or removing files in data/. Safe to run repeatedly."""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
COLS = ["batches", "ips", "reviews", "pools"]

def main():
    idx = {c: sorted(p.stem for p in (DATA / c).glob("*.json")) for c in COLS}
    path = DATA / "index.json"
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if all(old.get(c) == idx[c] for c in COLS):
        print("index unchanged")
        return
    idx["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(idx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("index written:", {c: len(idx[c]) for c in COLS})

if __name__ == "__main__":
    main()
