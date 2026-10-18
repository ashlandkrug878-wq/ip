# 潮玩 IP 工作区

把潮玩 IP 从原点到量产的整套工作流放在一个仓库里，让 Claude、出图工具和其他 AI 共用同一份规则和数据。

## 怎么流转

```
Claude 第一步（每周）          你                     出图工具                 Claude 第二步 / 其他 AI
抓原点、生成方案      →   选品板上选择和批注   →   按队列出基础形象图   →   诊断、配色选材、插画、表情包…
写入 data/ 和队列         同步回 data/reviews        写入 images/              写入 ip-archives/ 和新的出图任务
```

1. **第一步**：Claude 每周按 `skills/chaowan-ip-lab` 生成一期方案，写进选品板，同步到 `data/`，并把每个方案的基础形象提示词加进 `queue/image-jobs.json`
2. **你选择**：在选品板上标保留、待优化、淘汰，写批注，存素材池。Claude 同步时把这些写回 `data/reviews/` 和 `data/pools/`
3. **出图**：`.github/workflows/generate-images.yml` 读取队列里待出图的任务，调用你配置的出图接口，图存进 `images/`
4. **第二步**：Claude 或其他 AI 按 `skills/chaowan-ip-studio` 读 IP 档案和图片，继续做配色选材、插画、表情包等，需要出图的再加进队列

给 AI 看的详细说明在 `AGENTS.md`。

## 目录

| 位置 | 内容 |
|---|---|
| `AGENTS.md` | 给所有 AI 的说明和规则 |
| `workflow/` | 工作流文档 |
| `skills/` | 两个 skill：第一步 chaowan-ip-lab，第二步 chaowan-ip-studio |
| `data/` | 选品板数据：每期内容、方案、你的选择、你的素材池 |
| `ip-archives/` | 选中 IP 的档案 |
| `queue/` | 出图任务队列 |
| `images/` | 生成的图 |
| `scripts/` | 生成队列和调用出图接口的脚本 |
| `.github/workflows/` | 自动出图的 GitHub Action |

## 配置自动出图

出图脚本默认按 OpenAI 兼容的图片生成接口调用，任何提供兼容接口的服务都可以用。在仓库的 Settings → Secrets and variables → Actions 里添加：

| 名称 | 类型 | 说明 |
|---|---|---|
| `IMAGE_API_KEY` | Secret | 出图服务的 API 密钥 |
| `IMAGE_API_URL` | Variable | 图片生成接口地址，例如 `https://api.openai.com/v1/images/generations` |
| `IMAGE_MODEL` | Variable | 模型名，以 OpenAI 文档为准（例如 `gpt-image-2`，上线前在 OpenAI 的模型列表里确认） |

配置好以后，队列有新任务被推送时会自动出图，也可以在 Actions 页面手动运行。没有配置密钥时，Action 会跳过出图，不会报错。

不支持 API 的工具（例如一些只有网页界面的出图工具），可以手动打开 `queue/image-jobs.json`，复制 `prompt_en` 或 `prompt_zh` 去出图，再把图放进对应的 `output` 路径，把状态改成 `done`。
