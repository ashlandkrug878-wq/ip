# Grok 明星潮玩流水线

给明星做潮玩的单独一条线：Grok 负责调研和创意，ChatGPT 用一个**单独的定时任务**负责出图回传。和 ChatGPT 的日更概念**完全分开**：数据、编号、出图队列、选品板栏目都各用各的，两边互不读写。

## 目录
1. 和日更怎么分开
2. 流程与状态
3. 明星原点卡格式
4. 给 Grok 的两段提示词
5. ChatGPT 明星出图定时任务
6. 怎么设置：谁、什么时候跑

## 1. 和日更怎么分开

| | 日更（ChatGPT） | 明星（Grok + ChatGPT） |
|---|---|---|
| 谁做 | ChatGPT 日更定时任务：出方案、出图 | Grok：调研、创意；ChatGPT 明星出图定时任务：只出图回传 |
| 原点 | 网上的社会情绪、圈层信号 | `data/stars/star-<代号>.json` |
| 表达卡 | `data/ips/daily-YYYYMMDD-NN.json` | `data/ips/star-<代号>-e<序号>.json`，带 `"source": "grok-star"` 和 `"star": "star-<代号>"` |
| 形 | `data/forms/<方案 id>-A1.json` | `data/forms/star-<代号>-e<序号>-A<序号>.json`，带 `"source": "grok-star"` |
| 出图队列 | `queue/image-jobs.json` | `queue/star-image-jobs.json` |
| 图片 | `images/daily-*/` | `images/star-*/` |
| 选品板 | 「① 表达」「② 找形」 | 「Grok 明星」 |

规则：
- 所有编号以 `star-` 开头。`scripts/build_queue.py` 看到 `star-` 开头或 `source` 为 `grok-star` 的方案和形，只往 `queue/star-image-jobs.json` 加任务
- Grok 只读写 `star-` 开头的文件，不出图；ChatGPT 明星出图任务只处理明星队列；ChatGPT 日更任务只读写 `daily-` 文件和主队列。两个 ChatGPT 定时任务是分开的两个任务
- 两条线共用的只有规则：`AGENTS.md`、`skills/`、`data/feedback/learned-rules.json`、`data/studies/`（撞车检查）。这些 Grok 只读不改

**前提：授权。** 用明星的名字、形象、人设做潮玩，商用前需要本人或经纪方授权。原点卡里写清 `authorization`：`signed`（签约艺人）、`authorized`（已获授权）、`pending`（待确认）。`pending` 的可以做内部概念，不对外发布、不打样。

## 2. 流程与状态

```
① Grok 调研 → data/stars/star-xx.json（status: researched）
      ↓ 你在「Grok 明星」把原点卡标「保留」= 确认人设
② Grok 创意 A → 3 张表达卡（data/ips/star-xx-e1..e3）
      ↓ 你把其中一张标「保留」
② Grok 创意 B → 发散段 6 个形（data/forms/star-xx-e1-A1..A6）→ 明星队列
③ ChatGPT 明星出图定时任务 → images/star-xx-e1-A1/lineart-01.webp → 选品板显示
      ↓ 你把某个形标「保留」
② Grok 创意 C → 锁形段（白模、线稿，以概念图为参考）+ 名字候选 + 需要时裂变 4 个
③ ChatGPT 明星出图定时任务
      ↓ 你说「锁定」
② Grok 写 IP 档案，形的 locked 设为 true
```

每一步做完就停，等你在选品板上标状态。Grok 定时巡检时先看哪一步有新的「保留」，只做那一步；ChatGPT 明星出图任务定时看明星队列里有没有新任务。

## 3. 明星原点卡格式

`data/stars/star-<代号>.json`，代号用拼音或英文小写，例如 `star-xiaoming`：

```json
{
  "name": "明星名",
  "aliases": ["英文名", "常用昵称"],
  "authorization": {"status": "signed | authorized | pending", "note": "谁确认的、哪天"},
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

## 4. 给 Grok 的两段提示词

① 调研是你手动发起（告诉它做哪位明星）；② 创意设成定时巡检。

### ① 调研

```
你是潮玩 IP 工作流「Grok 明星」这条线的调研员。仓库：github.com/ashlandkrug878-wq/ip。
开始前读 AGENTS.md 和 workflow/star-grok.md。你只能新建或修改以 star- 开头的文件，不碰 daily- 开头的任何东西和 queue/image-jobs.json。

任务：为 {明星名} 建原点卡 data/stars/star-{代号}.json，格式见 workflow/star-grok.md 第 3 节。授权状态：{signed/authorized/pending}。

要求：
- 实际去搜索，用 X 搜索和网页搜索，不凭记忆填。每条信息附来源链接和日期，标 self / fan / inference
- 微博、小红书、抖音这类需要登录的页面，记进 gaps，不要绕过
- 收集：人设（三个词以内，附依据）、口头禅和名场面、官方色和应援色（分开写）、粉丝昵称、常被比作的动物或物件、随身物和爱好、作品里反复出现的符号、雷区
- 最后给 3 到 5 个物种候选：动物或物件，各一句为什么像他。优先选能"长进身体"的物件（见 skills/chaowan-ip-form/references/axes.md 第⑥轴）
- 不写造型，不出图
- status 写 researched，运行 python scripts/build_index.py，提交到 main，提交说明写「明星调研：{明星名}」，然后停下
```

### ② 创意（A：表达卡；B：发散段；C：锁形段）

```
你是潮玩 IP 工作流「Grok 明星」这条线的创意。仓库同上。这是定时巡检：没有新的「保留」或「锁定」就什么都不做，直接结束。
每次开工先读：AGENTS.md、workflow/star-grok.md、data/feedback/learned-rules.json、
skills/chaowan-ip-lab/SKILL.md、skills/chaowan-ip-form/SKILL.md 和它的 references/
（axes.md、form-and-prompts.md、checks.md、naming.md、handoff.md）。
你只能新建或修改以 star- 开头的文件，不碰 daily- 开头的任何东西和 queue/image-jobs.json，不改 data/reviews/。

先看状态，只做下面其中一步，做完提交并停下：

A. data/reviews/star-{代号}.json 的 status 是「保留」，但还没有 data/ips/star-{代号}-e*.json：
   按 lab 写 3 张表达卡 data/ips/star-{代号}-e1..e3.json，字段按 lab 的「写入仓库」，另加
   "source": "grok-star"、"star": "star-{代号}"、"batch": "star-{代号}"。
   洞察从他公开的矛盾里来，不写通用鸡汤；name 只写「暂名：描述词」，不起正式名。
   用户在原点卡批注里写的意见优先。

B. 某张 star-{代号}-e* 表达卡被标「保留」，还没有它的形：
   按 form 的发散段出 6 个形，写 data/forms/star-{代号}-e{n}-A1..A6.json，加 "source": "grok-star"、"render": "concept"。
   物种从原点卡的 species_candidates 里来；范式、配额、七条轴、负面词按 form-and-prompts.md。
   明星的官方色、应援色只能当对比色或签名色的候选，不画他本人的长相、发型、服装，不写他的名字。
   每个形写明对上了 learned-rules.json 的哪几条。

C. 某个 star- 形被标「保留」：
   按 form 的锁形段写白模和线稿两个形（render 为 clay、line），"reference" 写那张概念图的路径；
   按 naming.md 给这个形所属的表达卡写 name_candidates 和建议名；需要时出 4 个裂变（B 轮）。

D. 用户在批注里写了「锁定」：按 handoff.md 写 ip-archives/IP档案_<名字>_v1.md，形的 locked 设为 true。

每一步写完运行 python scripts/build_index.py 和 python scripts/build_queue.py（出图任务会自动进 queue/star-image-jobs.json，由 ChatGPT 明星出图任务来出图；你不出图），
提交说明写「明星创意：{明星名} {A/B/C/D}」。
```

## 5. ChatGPT 明星出图定时任务

在 ChatGPT 里**新建一个定时任务**，和日更那个任务分开。提示词：

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

每次最多 4 张，是为了不撞对话长度上限；一轮发散段 6 张，分两次跑完。

## 6. 怎么设置：谁、什么时候跑

| 谁 | 任务 | 怎么触发 | 建议时间 |
|---|---|---|---|
| Grok | ① 调研 | 手动：告诉它明星名、代号、授权状态 | 需要时 |
| Grok | ② 创意巡检 | 定时 | 每天 10:00、15:00 |
| ChatGPT | 明星出图（第 5 节提示词） | 定时，**新建的单独任务** | 每天 11:00、16:00，比 Grok 晚一小时 |
| ChatGPT | 日更概念（`daily-sync.md`） | 定时，原来的任务不动 | 原时间，和明星出图错开至少半小时 |

一个来回大概是这样：你上午在选品板标了「保留」→ Grok 15:00 写好 6 个形的提示词 → ChatGPT 16:00 出前 4 张、次日 11:00 出后 2 张 → 选品板显示，你再挑。想快一点，可以直接在 Grok 或 ChatGPT 里手动发一次对应的提示词，不用等定时。

两个 ChatGPT 定时任务各用各的提示词，日更任务继续只读 `queue/image-jobs.json`，明星任务只读 `queue/star-image-jobs.json`，所以同时开着也不会抢同一个任务。
