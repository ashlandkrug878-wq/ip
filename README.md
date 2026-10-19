# 潮玩 IP 工作区

把潮玩 IP 从原点到量产的整套工作流放在一个仓库里，让 Claude、出图工具和其他 AI 共用同一份规则和数据。

## 怎么流转

工作流分三步，每步之后你在选品板网站上挑选。另有一个第 0 步做研究：

0. **研究**：Claude 或 ChatGPT 按 `skills/chaowan-ip-study` 研究已有 IP，写成对标卡放进 `data/studies/`，网站「研究库」栏目可以横向比较。后面三步都会参照它

1. **第一步 · 表达**：Claude 按 `skills/chaowan-ip-lab` 从原点生成表达卡（洞察、圈层、一句表达、情绪范围），写进 `data/ips/`。你在网站「① 表达」挑保留
2. **第二步 · 找形**：Claude 按 `skills/chaowan-ip-form` 给保留的表达出 6 个黑白线稿方向，写进 `data/forms/`。你在「② 找形」复制提示词去出线稿、上传、挑选；保留的再裂变 4 个，满意后锁定，生成 IP 档案
3. **第三步 · 定型与内容**：Claude 按 `skills/chaowan-ip-studio` 以锁定线稿为参考，从你的素材池配色选材、渲染、出三视图，再做表情包、故事、系列和打样。锁定的 IP 出现在「③ 定型」

流水线：`data/` 或出图队列变动时，`.github/workflows/generate-images.yml` 自动重建网站索引、给新的方案和形加出图任务，配置了出图密钥时自动出图。

给 AI 看的详细说明在 `AGENTS.md`。

## 目录

| 位置 | 内容 |
|---|---|
| `AGENTS.md` | 给所有 AI 的说明和规则 |
| `workflow/` | 工作流文档 |
| `skills/` | 第 0 步 chaowan-ip-study（研究），以及三个创作 skill：第一步 chaowan-ip-lab（表达），第二步 chaowan-ip-form（找形），第三步 chaowan-ip-studio（定型、内容、产品） |
| `index.html` | 选品板网站 |
| `data/` | 选品板数据：每期内容、表达卡、形、你的选择、你的素材池 |
| `ip-archives/` | 选中 IP 的档案 |
| `queue/` | 出图任务队列 |
| `images/` | 生成的图 |
| `scripts/` | 生成队列和调用出图接口的脚本 |
| `.github/workflows/` | 自动出图的 GitHub Action |

## 选品板网站

地址：https://ashlandkrug878-wq.github.io/ip/（GitHub Pages，公开可看）

- 不连接时是只读模式，任何人能看
- 点"连接 GitHub 以保存"，粘贴一个只给 `ip` 仓库、Contents 读写权限的细粒度令牌，之后的选择、批注、素材池会直接提交到仓库
- 令牌只存在你自己浏览器里，不会进仓库。换设备要重新粘贴；不用了可以在 GitHub 设置里删除令牌
- 页面按阶段分栏：研究库、① 表达、② 找形、③ 定型、本期素材、我的素材池
- 页面每两分钟和切回页面时自动刷新；上传的图会显示在卡片上
- 不用 API 出图时：详情里点「复制英文提示词」，去 ChatGPT 出图，下载原图后点上传，网站会压缩并存进 `images/`，同时把队列里的任务标成已完成

开启方法：仓库 Settings → Pages → Source 选 Deploy from a branch，分支 `main`，目录 `/ (root)`。

## 配置自动出图

出图脚本默认按 OpenAI 兼容的图片生成接口调用，任何提供兼容接口的服务都可以用。在仓库的 Settings → Secrets and variables → Actions 里添加：

| 名称 | 类型 | 说明 |
|---|---|---|
| `IMAGE_API_KEY` | Secret | 出图服务的 API 密钥 |
| `IMAGE_API_URL` | Variable | 图片生成接口地址，例如 `https://api.openai.com/v1/images/generations` |
| `IMAGE_MODEL` | Variable | 模型名，以 OpenAI 文档为准（例如 `gpt-image-2`，上线前在 OpenAI 的模型列表里确认） |

配置好以后，队列有新任务被推送时会自动出图，也可以在 Actions 页面手动运行。没有配置密钥时，Action 会跳过出图，不会报错。

不支持 API 的工具（例如一些只有网页界面的出图工具），可以手动打开 `queue/image-jobs.json`，复制 `prompt_en` 或 `prompt_zh` 去出图，再把图放进对应的 `output` 路径，把状态改成 `done`。
