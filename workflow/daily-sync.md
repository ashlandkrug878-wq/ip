# 每日完整概念同步协议

本协议适用于用户授权的 ChatGPT 每日完整概念批次；与仓库分阶段创作流程并存，不将每日概念自动标为锁定或完成定型。

1. 运行前读取 AGENTS.md、data/index.json、全部 data/reviews/，以及所关联的 IP、形和批注；只按用户明确选择学习。淘汰项默认隐藏但保留原卡、图和批注，不物理删除，不重新生成同名同方向；没有原因时只避开该具体候选，不扩大推断用户审美。
2. 每批唯一 ID 使用 daily-YYYYMMDD；卡片使用 daily-YYYYMMDD-01 至 -09，重跑幂等，禁止重复新增。先检查该 ID 是否已存在；存在时保留 reviews/pools、旧图和版本历史。
3. data/batches/<batch>.json 记录 title/date/timing/origins（来源 URL、发布日期、证据等级）、learned；每张 data/ips/<id>.json 使用现有兼容字段 name/en/expr/type/batch/order/layers/links/zh/enp/tests/risk，另可加 complete_card 保留完整方案文本、source="daily-lab"、stage="concept"。保留与待优化不等于工程锁定。
4. 图片只用已生成的内置图，不自动调用付费外部服务。压缩成最长边 768、质量 80、150KB 以下的 webp，保存 images/<id>/base-01.webp。为对应 queue/image-jobs.json 任务设 done/output/prompt_revision/image_revision；没有图片时设 awaiting_upload 并如实说明缺图，不设 pending 触发外部收费出图。
5. 保留完整报告和原图总览至 research/daily/<batch>/；将完整方案内容同步进卡片，不只写聊天或 Library 链接。运行 scripts/build_index.py 与 scripts/build_queue.py。原有选择、素材池、其他队列任务不可覆盖。
6. 用户最新授权本流程批量同步卡片和已有图；这不是仓库“一个对话只生成一个队列图”的临时出图工作流，不生成新的找形或擅改锁定档案。
7. 提交前验证 JSON、9卡9图、图片路径存在、索引一致；推送时基于最新 main，保留并发修改。上传/权限失败时停止写入并报告，不能声称网站已同步。交付网站网址与提交地址。
8. 淘汰是软归档：data/reviews/<id>.json 保留 status/note/history/retiredAt；恢复后可重新进入候选。公开仓库中的归档不是私密存储。
