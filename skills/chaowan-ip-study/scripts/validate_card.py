#!/usr/bin/env python3
"""Check a study card (data/studies/<id>.json) against references/card.md and
references/vocab.md: required fields, controlled vocabulary, source links.
It checks structure only, not whether the facts are true.

Usage: python validate_card.py data/studies/<id>.json [more.json ...]
"""
import json
import re
import sys
from pathlib import Path

VOCAB = {
    ("origin", "path"): {"绘本出版", "网络插画", "表情包传播", "短视频", "动画影视", "游戏", "艺术家潮玩", "产品先行", "社群二创", "渠道孵化", "名人流量", "其他"},
    ("carrier", "primary"): {"实物潮玩", "表情包", "短视频", "动画", "绘本漫画", "游戏", "授权图案", "线下人偶", "其他"},
    ("carrier", "secondary"): {"实物潮玩", "表情包", "短视频", "动画", "绘本漫画", "游戏", "授权图案", "线下人偶", "其他"},
    ("product", "first_category"): {"盲盒手办", "搪胶毛绒", "毛绒", "大娃", "挂件", "授权周边", "出版物", "其他"},
    ("product", "hit_category"): {"盲盒手办", "搪胶毛绒", "毛绒", "大娃", "挂件", "授权周边", "出版物", "其他"},
    ("expression", "sentence_type"): {"允许", "反差", "陪伴", "留白", "自嘲", "其他"},
    ("core", "emotion"): {"外放", "内收", "反差", "面无表情"},
    ("pendulum", "position"): {"甜美治愈", "暗黑酷", "丑萌怪趣", "软萌治愈", "荒诞抽象", "其他"},
    ("form", "archetype"): {"人", "类人", "动物", "动物类人", "怪兽精灵", "物件", "食物植物天气", "抽象形"},
    ("form", "silhouette"): {"团子", "长条", "几何块", "大头小身", "头身一体", "拼接组合"},
    ("form", "mark_position"): {"头顶", "头型", "五官", "手臂", "尾巴", "肚子", "脚", "姿态", "功能结构", "随身道具", "整体轮廓"},
    ("form", "emotion"): {"外放", "内收", "反差", "面无表情"},
    ("form", "density"): {"极简", "中等", "繁复"},
    ("form", "naming"): {"叠音", "描述", "人名", "其他"},
    ("form", "group"): {"单角色", "角色群"},
    ("color", "mode"): {"白底加签名色", "单色识别", "多色系列", "暗黑加亮色", "马卡龙", "低饱和", "其他"},
}
MULTI = {("origin", "path"), ("form", "mark_position")}
TYPES = {"fact", "self_report", "inference", "hypothesis"}
ACCESS = {"full", "partial", "snippet_only", "blocked"}
REQUIRED = ["id", "name", "tier", "status", "cutoff_date", "summary", "owner", "origin", "expression", "core",
            "circle", "pendulum", "form", "collide_combo", "color", "carrier", "product", "numbers",
            "mechanisms", "theory", "for_skills", "gaps", "sources"]


def check(path):
    errors = []
    card = json.loads(Path(path).read_text(encoding="utf-8"))
    for k in REQUIRED:
        if k not in card:
            errors.append(f"missing {k}")
    if card.get("id") != Path(path).stem:
        errors.append("id must match file name")
    if card.get("tier") not in {"quick", "standard", "deep"}:
        errors.append("tier must be quick, standard or deep")
    if card.get("status") not in {"partial", "complete"}:
        errors.append("status must be partial or complete")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(card.get("cutoff_date", ""))):
        errors.append("cutoff_date must be YYYY-MM-DD")

    for (sec, key), allowed in VOCAB.items():
        val = (card.get(sec) or {}).get(key)
        if val is None:
            continue
        vals = val if isinstance(val, list) else [val]
        if (sec, key) in MULTI and not isinstance(val, list):
            errors.append(f"{sec}.{key} must be a list")
        if (sec, key) not in MULTI and isinstance(val, list):
            errors.append(f"{sec}.{key} must be a single value")
        for v in vals:
            if v not in allowed:
                errors.append(f"{sec}.{key}: '{v}' not in vocab.md")
    if len((card.get("form") or {}).get("mark_position") or []) > 2:
        errors.append("form.mark_position: at most 2")

    src_ids = []
    for s in card.get("sources", []):
        src_ids.append(s.get("id"))
        if not s.get("url", "").startswith(("http://", "https://")):
            errors.append(f"source {s.get('id')}: url must be http(s)")
        if s.get("access") not in ACCESS:
            errors.append(f"source {s.get('id')}: access must be one of {sorted(ACCESS)}")
    if None in src_ids or len(src_ids) != len(set(src_ids)):
        errors.append("sources: missing or duplicate id")
    known = set(src_ids)

    def walk(node, where):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "sources" and where != "":
                    for sid in v or []:
                        if sid not in known:
                            errors.append(f"{where}: unknown source {sid}")
                else:
                    walk(v, f"{where}.{k}" if where else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{where}[{i}]")
    walk({k: v for k, v in card.items() if k != "sources"}, "")

    for name in ("numbers", "mechanisms", "timeline"):
        for i, row in enumerate(card.get(name) or []):
            if row.get("type") is not None and row.get("type") not in TYPES:
                errors.append(f"{name}[{i}].type must be one of {sorted(TYPES)}")
            if name != "timeline" and not row.get("sources"):
                errors.append(f"{name}[{i}]: needs sources")
            if name == "numbers" and row.get("value") == 0:
                errors.append(f"numbers[{i}]: value 0 — use null when unknown")
    for k in ("lab", "form", "studio"):
        if not (card.get("for_skills") or {}).get(k):
            errors.append(f"for_skills.{k} is empty")
    return errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    bad = 0
    for p in sys.argv[1:]:
        try:
            errs = check(p)
        except (OSError, ValueError) as e:
            errs = [str(e)]
        if errs:
            bad += 1
            print(f"FAIL {p}")
            for e in errs:
                print("  - " + e)
        else:
            print(f"PASS {p} (structure and vocab only; facts need review)")
    sys.exit(1 if bad else 0)
