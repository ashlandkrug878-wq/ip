# 对标卡：研究的标准输出

每次研究，不管哪一档，都要交一张对标卡：`data/studies/<subject-id>.json`。它是研究和创作之间的接口，选品板「研究库」栏目、lab、form、studio 都读它。分类字段的取值见 `vocab.md`。

## 目录
1. 字段
2. 用户理论检查
3. 怎么交给其他 skill
4. 更新规则

## 1. 字段

```json
{
  "id": "the-monsters",
  "name": "THE MONSTERS",
  "aliases": ["精灵天团", "LABUBU"],
  "tier": "quick | standard | deep",
  "status": "partial | complete",
  "cutoff_date": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD",
  "summary": "一句话：它为什么值得研究、最关键的机制是什么",

  "owner": {"creator": "", "operator": "", "relation": "授权、自有或未知", "since": "YYYY", "sources": ["s1"]},
  "origin": {"path": ["绘本出版"], "year": "YYYY", "story": "最早的形象在哪里、为谁出现", "sources": []},
  "timeline": [{"date": "YYYY 或 YYYY-MM", "event": "", "type": "fact", "sources": []}],

  "expression": {"line": "一句话表达", "sentence_type": "反差", "basis": "official | inferred", "sources": []},
  "core": {"personality": "三个词以内", "emotion": "内收", "action": "它在做什么", "basis": "official | inferred"},
  "insight": {"scene": "", "behavior": "", "state": "", "conflict": "", "unsaid": "", "basis": "inferred"},
  "circle": {"who": "", "where": "", "buy": "", "signs": "", "share": "", "breakout": ""},
  "pendulum": {"position": "丑萌怪趣", "against": "它是对哪种主流的反动"},

  "form": {"archetype": "怪兽精灵", "silhouette": "大头小身", "mark_position": ["五官", "头顶"], "mark": "", "face": "", "emotion": "反差", "odd": "", "density": "中等", "naming": "叠音", "group": "角色群"},
  "collide_combo": "最好不要撞上的识别组合，一句话",
  "color": {"mode": "多色系列", "main": "", "signature": "", "notes": "官方还是估计"},
  "materials": "主要材质和工艺",
  "carrier": {"primary": "实物潮玩", "secondary": "短视频"},
  "product": {"first_category": "盲盒手办", "hit_category": "搪胶毛绒", "hit_product": "", "price_band": "", "sources": []},

  "numbers": [{"metric": "IP 收入", "value": 0, "unit": "亿元", "period": "2025 全年", "type": "fact", "sources": []}],
  "mechanisms": [{"claim": "", "type": "inference", "evidence": "", "boundary": "什么条件下不成立", "sources": []}],
  "counterexamples": "相似却没火的对象、失败款、争议，没找到写没找到",

  "theory": {
    "shell": "外壳：样子靠什么成立",
    "core": "内核：表达、性格、情绪",
    "shadow": "外壳有没有大量公共元素、内核是否独特",
    "two_layers": {"surface": "路人为什么喜欢", "deep": "圈层彩蛋是什么"},
    "validation": "付费、粉丝增长、点赞分别有什么证据"
  },

  "for_skills": {
    "lab": "给表达和洞察的启发，一两句",
    "form": "给找形的启发：可以借的机制、不能借的组合",
    "studio": "给配色、材质、内容、系列、产品的启发"
  },

  "gaps": ["没查到或有冲突的地方"],
  "sources": [{"id": "s1", "title": "", "url": "", "publisher": "", "published": "YYYY-MM-DD", "observed": "YYYY-MM-DD", "access": "full"}],
  "archive": "research/<id>/<date>/report.md，标准档以上才有"
}
```

规则：
- 每个有 `sources` 的地方都要能在 `sources` 列表里找到；`numbers` 和 `mechanisms` 必须有来源
- 找不到写 `null` 或空字符串，并在 `gaps` 里说明；不填 0，不编
- `basis: inferred` 表示这是研究者的归纳，不是官方说法
- 数字写清口径：期间、单位、主体（公司收入不等于 IP 收入）

## 2. 用户理论检查

`theory` 一节用用户自己的框架看这个 IP：
- **外壳与内核**：外壳是样子，内核是表达、性格、情绪、背景。分别写它靠什么成立
- **有没有别人的影子**：外壳是否主要由公共元素构成（雀斑、腮红、大眼睛、双马尾、嘟嘴、眼镜等）；如果是，内核靠什么拉开
- **两层用户**：表层给路人的普适情绪；深层给圈层的彩蛋
- **相信腿不相信嘴**：按"付费 > 粉丝增长 > 点赞和评论"的顺序找证据。只有点赞、没有付费证据的，写清楚

## 3. 怎么交给其他 skill

| 读的 skill | 读哪些字段 | 用来做什么 |
|---|---|---|
| lab | `expression`、`core`、`insight`、`circle`、`pendulum`、`mechanisms`、`for_skills.lab` | 句式和钟摆站位的参照；判断某类表达是否已经饱和 |
| form | `form`、`collide_combo`、`theory.shell`、`for_skills.form` | 撞车检查（替代或补充 `benchmarks.md`）；看哪种轮廓、记忆点位置已经很拥挤 |
| studio | `color`、`materials`、`carrier`、`product`、`numbers`、`for_skills.studio` | 配色和材质的参照；系列和品类节奏；投产门槛的参照 |

`for_skills` 写的是"有边界的候选启发"，不是规则，也不能替用户改任何已锁定的角色。

## 4. 更新规则

- 同一个 IP 再研究时，更新同一张卡：改 `updated`，旧数字不删，在 `timeline` 或 `numbers` 里按期间并存
- 速查档升级到标准档、深挖档时，`tier` 改掉，`archive` 指向完整档案
- 研究结论和 `skills/chaowan-ip-form/references/benchmarks.md` 冲突时，不直接改 benchmarks，在交付时列出"对标库修正建议"，用户同意后再改
