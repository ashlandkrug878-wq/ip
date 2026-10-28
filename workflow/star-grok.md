# Grok 明星潮玩流水线（全自动）

给明星做同人潮玩的单独一条线，用于自媒体内容。Grok 负责调研和创意，ChatGPT 用一个**单独的定时任务**负责出图回传。**全程自动，不等用户在选品板上点选**：用户隔几天回来批量看、批量标、批量写批注，下一次运行自动按批注改。

和 ChatGPT 日更概念**完全分开**：数据、编号、出图队列、选品板栏目都各用各的，两边互不读写。

## 目录
1. 和日更怎么分开
2. 每天自动做什么
3. 用户回来批量处理之后
4. 明星原点卡格式
5. Grok 每日定时任务提示词
6. ChatGPT 明星出图定时任务提示词
7. 怎么设置

## 1. 和日更怎么分开

| | 日更（ChatGPT） | 明星（Grok + ChatGPT） |
|---|---|---|
| 谁做 | ChatGPT 日更定时任务：出方案、出图 | Grok 定时任务：调研、创意；ChatGPT 明星出图定时任务：只出图回传 |
| 原点 | 网上的社会情绪、圈层信号 | `data/stars/star-<代号>.json` |
| 表达卡 | `data/ips/daily-YYYYMMDD-NN.json` | `data/ips/star-<代号>-e<序号>.json`，带 `"source": "grok-star"`、`"star": "star-<代号>"` |
| 形 | `data/forms/<方案 id>-A1.json` | `data/forms/star-<代号>-e<序号>-A<序号>.json`，带 `"source": "grok-star"` |
| 出图队列 | `queue/image-jobs.json` | `queue/star-image-jobs.json` |
| 图片 | `images/daily-*/` | `images/star-*/` |
| 选品板 | 「① 表达」「② 找形」 | 「Grok 明星」 |

规则：
- 所有编号以 `star-` 开头。`scripts/build_queue.py` 把 `star-` 开头或 `source` 为 `grok-star` 的方案和形，只放进 `queue/star-image-jobs.json`
- Grok 只读写 `star-` 开头的文件和 `data/stars/`，不出图；ChatGPT 明星出图任务只处理明星队列；ChatGPT 日更任务只读写 `daily-` 文件和主队列
- 共用、只读的：`AGENTS.md`、`skills/`、`data/feedback/learned-rules.json`、`data/studies/`
- **同人边界**：只做角色化的潮玩形象，不画明星本人的脸、发型和服装；不碰原点卡里的雷区；不写贬低、恶搞、色情或涉及家人隐私的内容

## 2. 每天自动做什么

```
Grok 每日一次（例如 10:00）
  ① 选一位新明星：先从 data/stars/wishlist.json 按顺序取；清单空了，自己挑一位近期讨论度高的，写明为什么
  ② 调研 → data/stars/star-xx.json
  ③ 直接写 3 张表达卡 → data/ips/star-xx-e1..e3
  ④ 每张表达卡出 3 个发散段概念图的形，一共 9 个 → data/forms/star-xx-e{n}-A1..A3
  ⑤ 处理用户回来后新标的保留、待优化、锁定（见第 3 节）
  ⑥ 运行两个脚本，提交

ChatGPT 每天三次（例如 11:00、15:00、19:00），每次最多 4 张
  读 queue/star-image-jobs.json 的 pending 任务 → 出图 → 压缩 → 回传 → 标 done
```

一位明星 9 张概念图，ChatGPT 一天三次、每次 4 张，当天基本出完。不需要等用户点任何东西。

9 个形按 form 的发散段规则一起拉开：把 6 个形的配额按比例放到 9 个上，至少 6 个有物件融合，人形或类人最多 1 个。

## 3. 用户回来批量处理之后

用户隔几天在「Grok 明星」里批量标状态、写批注。Grok 每次运行都扫一遍 `star-` 开头的 `data/reviews/`，有变化就自动接着做：

| 用户做了什么 | Grok 下一次运行自动做 |
|---|---|
| 某个形标**保留** | 锁形段：以这张概念图为参考，写白模和线稿两个形（`render` 为 `clay`、`line`，`reference` 写概念图路径），按 `naming.md` 给它出名字候选，再出 4 个裂变（B 轮） |
| 某个形或表达卡标**待优化**并写了批注 | 按批注出一个修订版，只改批注提到的地方 |
| 表达卡标**待优化** | 按批注改写表达，并重新出 3 个形 |
| 批注里写**锁定** | 按 `handoff.md` 写 IP 档案，形的 `locked` 设为 `true` |
| 原点卡写了批注（例如"人设不对""物种用 xx"） | 按批注更新原点卡；已有的形不删，之后的新形按新设定 |
| **淘汰** | 不再做这个方向；淘汰原因进反馈规则 |
| 没标的 | 不当作喜欢，也不当作不喜欢，不动 |

已经处理过的批注不重复处理：每处理一条，在对应形或表达卡里记 `handled_reviews`（review 的 `updatedAt`）。

## 4. 明星原点卡格式

`data/stars/star-<代号>.json`，代号用拼音或英文小写，例如 `star-xiaoming`：

```json
{
  "name": "明星名",
  "aliases": ["英文名", "常用昵称"],
  "picked_because": "从清单取的写「清单」；自己挑的写为什么",
  "status": "researched",
  "updated": "YYYY-MM-DD",
  "persona": [{"word": "三个词以内的人设", "basis": "依据", "type": "self | fan | inference", "sources": ["s1"]}],
  "catchphrases": [{"text": "口头禅或名场面", "type": "self | fan", "sources": ["s1"]}],
  "colors": {
    "official": [{"name": "色名", "hex": "#RRGGBB（近似）", "sources": ["s1"]}],
    "fan": [{"name": "应援色", "hex": "#RRGGBB", "sources": ["s2"]}]
  },
  "fan_names": ["粉丝昵称"],
  "likened_to": [{"text": "常被比作的动物或物件", "sources": ["s3"]}],
  "belongings": ["常带的随身物、爱好"],
  "symbols": ["作品里反复出现的符号"],
  "taboo": ["雷区：争议、不能碰的话题、粉丝反感的说法"],
  "species_candidates": [{"answer": "物种或物件", "why": "一句话为什么像他"}],
  "gaps": ["没查到的、需要登录没读到的"],
  "sources": [{"id": "s1", "title": "", "url": "https://...", "date": "YYYY-MM-DD", "type": "self | fan | media"}]
}
```

`type`：`self` 是本人或官方说的；`fan` 是粉丝或媒体的说法；`inference` 是 Grok 自己的归纳。

想指定做哪些明星，在 `data/stars/wishlist.json` 里按顺序写：

```json
[{"name": "明星名", "id": "star-拼音", "note": "可选：想突出的点"}]
```

## 5. Grok 每日定时任务提示词

```
你是潮玩 IP 工作流「Grok 明星」这条线，每天运行一次，全自动，不等用户确认。
仓库：github.com/ashlandkrug878-wq/ip。开工先读：AGENTS.md、workflow/star-grok.md、data/feedback/learned-rules.json、
skills/chaowan-ip-lab/SKILL.md、skills/chaowan-ip-form/SKILL.md 和它的 references/
（axes.md、form-and-prompts.md、checks.md、naming.md、handoff.md）。
你只能新建或修改 data/stars/ 和以 star- 开头的文件；不碰 daily- 开头的任何东西和 queue/image-jobs.json；不改 data/reviews/；不出图。

按顺序做：

一、处理用户的批量反馈。扫描 data/reviews/ 里 star- 开头、updatedAt 比对应文件 handled_reviews 新的记录，按 workflow/star-grok.md 第 3 节处理。

二、做一位新明星。
  1. 从 data/stars/wishlist.json 取第一位还没有原点卡的；清单空了，自己挑一位近期讨论度高的明星，在 picked_because 写原因
  2. 调研：实际用 X 搜索和网页搜索，不凭记忆填。按第 4 节格式写 data/stars/star-{代号}.json，每条信息附来源和日期，标 self / fan / inference。需要登录的页面写进 gaps，不要绕过
  3. 按 lab 写 3 张表达卡 data/ips/star-{代号}-e1..e3.json，另加 "source": "grok-star"、"star": "star-{代号}"、"batch": "star-{代号}"。
     洞察从他公开的矛盾里来，不写通用鸡汤；name 只写「暂名：描述词」
  4. 每张表达卡按 form 的发散段出 3 个形，共 9 个：data/forms/star-{代号}-e{n}-A1..A3.json，加 "source": "grok-star"、"render": "concept"。
     物种从 species_candidates 里来；范式、七条轴、负面词按 form-and-prompts.md，9 个按第 2 节的配额一起拉开。
     官方色、应援色只当对比色或签名色的候选；不画明星本人的脸、发型、服装，提示词里不写明星名字和任何现有 IP、品牌名；不碰 taboo。
     每个形写明对上了 learned-rules.json 的哪几条

三、运行 python scripts/build_index.py 和 python scripts/build_queue.py（出图任务自动进 queue/star-image-jobs.json，由 ChatGPT 出图），
   提交到 main，提交说明写「明星日更：{明星名}；处理反馈 {n} 条」。
```

## 6. ChatGPT 明星出图定时任务提示词

在 ChatGPT 里**新建一个定时任务**，和日更那个任务分开：

```
你是潮玩 IP 工作流「Grok 明星」这条线的出图员。读 GitHub 仓库 ashlandkrug878-wq/ip 的 workflow/star-grok.md。
只处理 queue/star-image-jobs.json，不碰 queue/image-jobs.json 和任何 daily- 开头的文件。没有 pending 任务就直接结束。

1. 找出 status 为 pending 的任务，按顺序每次最多 4 个
2. 用任务的 prompt_en 出图，不改提示词里的造型描述，不加任何现有 IP、品牌、艺术家或明星的名字。
   任务有 reference 字段时，先从仓库读那张图，作为参考图（锁形段的白模、线稿、裂变都要这样）
3. 每张图用代码压缩：最长边 768 像素，webp，质量 80，150KB 以内（超了降到质量 70 或 640 像素）。
   存到任务的 output 路径，后缀改成 .webp
4. 同一次提交里只改这个任务：output 改成 .webp 路径，status 改为 done，note 写「ChatGPT 明星出图」
5. 提交说明写「明星出图：<名字> <任务 id>」，直接提交到 main
6. 出图失败的改成 failed，原因写进 note；上传失败不要反复重试，跳过这一张继续下一张，最后汇报
7. 不修改 data/、skills/、index.html 和任何提示词
```

## 7. 怎么设置

| 谁 | 任务 | 时间 |
|---|---|---|
| Grok | 每日定时任务（第 5 节提示词） | 每天 10:00 |
| ChatGPT | 明星出图定时任务（第 6 节提示词），**新建的单独任务** | 每天 11:00、15:00、19:00 |
| ChatGPT | 日更概念（`daily-sync.md`），原来的任务不动 | 原时间，和明星出图错开至少半小时 |

想加量：Grok 一天跑两次（每次一位新明星），ChatGPT 出图多加一两个时段即可。
