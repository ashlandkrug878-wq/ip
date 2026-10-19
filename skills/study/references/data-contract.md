# 档案数据契约 v1

目录：文件；实体；声明；来源；视觉；状态；检查。

## 文件

`research/<subject-id>/<YYYY-MM-DD>/`：
- report.md：摘要及A–L全文、各表、视觉拆解、提示词、方法卡与缺口；重要结论附声明或证据ID。
- archive.json：下面全部集合；可拆表给网站，但保留ID关系。
- assets/：确实可留存的图，不含无权再分发的拷贝。

网站开发与发布单独授权。不要写入选品板原有data/reviews、data/pools、图片生成队列，不把案例图当原创资产。

## 顶层

schema_version、revision、publications、color_system、form_spec、head_face_profile、narrative_system、action_library、series_matrix、recognition_checks、audience_insights、repo_audit、subject_id、cutoff_date、observed_at、markets、status、entities、claims、evidence、events、products、accounts、content_samples、user_evidence、images、visual_analyses、character_rules、prompt_layers、methods、gaps、coverage。

日期为ISO8601；日期精度只有年份时存YYYY，不补01-01。未知用null，已确认没有该项才用空数组并解释。统计窗口、采集日、事件发生日分开。

## 实体与声明

entities：entity_id、type（character/group/brand/person/company/account）、name、aliases、relationships（关系、目标ID、时间、evidence_ids）。

每条claim：claim_id、subject_id、predicate、value、unit、market、valid_time、observed_at、evidence_ids、information_type（fact/self_report/inference/hypothesis）、confidence（high/medium/low）、limitations。

金额加currency，绝对值保留原单位或明确换算；无法确认口径用limitations。推断与假设也关联证据，可明确其只能支持前提、不能证明机制。

## 来源

evidence：evidence_id、title、publisher、url、published_at、observed_at、source_type、access_status（full/partial/snippet_only/blocked）、origin_family、supports、locator、reliability、limitations。

同源转载使用同一origin_family。事实冲突在gaps中列各版本的evidence_ids，不静默覆盖。报告对原始网页使用真实URL；不要将仅会话有效的搜索引用ID当长期主键。

## 事件、产品与账号

events：event_id、date、date_precision、subject_ids、description、change、evidence_ids、mechanism、alternative_explanations。
products：product_id、subject_id、name、series、released_at、market、category、size、materials、material_basis、price、currency、price_observed_at、channel、usage_scenarios、evidence_ids。
accounts：account_id、subject_id、platform、name、url、ownership_status、followers、observed_at、evidence_ids、limitations。
content_samples：content_id、account_id、url、published_at、format、theme、metrics、observed_at、selection_method、evidence_ids。
user_evidence：user_evidence_id、group、scenario、expression、behavior、need_interpretation、counterexample、source_url、observed_at、sampling_method、directness、evidence_ids、limitations。没有直接样本则不伪造，保留缺口。

## 图片及视觉

images：image_id、subject_id、type、product_ids、event_ids、version、creator_or_brand、source_page_url、original_image_url、observed_at、page_published_at、product_released_at、image_created_at、rights、source_class、selection_reason、save_status、local_path、sha256、evidence_ids。

visual_analyses：analysis_id、image_id、viewed、resolution_limit、observed_features、official_settings、interpretation、material_and_structure、presentation、limitations。
character_rules：identity_invariants、expression_invariants、variables、medium_adaptations、uncertain；每项关联image_ids及证据。
prompt_layers：disclaimer、sample_descriptions（关联图）、mechanisms、original_translation（新brief、fixed、variables、flat_zh/en、product_zh/en、risks）。

prompt_validation：每条可执行提示词的版本、目标对象／范围／载体、完整文本及语言、纯文字或参考图模式、参考图ID、实际输出图路径、tested_at、逐项视觉对照、修订原因、status（draft／testing／revise／blocked／ready）。正式网页提示词只引用ready的已测版本；无法判断关键身份或颜色时不得ready。生成图单列AI测试来源，不混入官方证据图索引。只测一种语言时不宣称双语均通过。修改正式词后重新验证，保存历史版本。
methods：method_id、problem、claim_ids、image_ids、mechanism、conditions、counterexamples、failure_boundary、design_implication、experiment、metric、rejection_condition、evidence_level。

## 状态与覆盖

status：in_progress／partial／complete。
coverage：每模块A–L及visuals/prompts/cross_case对应status、evidence_ids、limitations；未研究不得标complete，单例cross_case标not_applicable。
gaps：gap_id、module、status（unknown/partially_verified/not_found/blocked/conflicting）、question、searched、impact、next_action。

## 完成前检查

运行脚本验证必需集合、声明字段、ID唯一、关联有效、已存图片确实存在与哈希一致。脚本不验证事实真实性或版权，人工检查来源是否支持结论、图片是否真的看过、报告数据是否一致、是否有反证。记录实际检查结果，不把结构校验通过说成研究已完成。

## v0.2新增对象

publications：publication_id、title、subtitle、author_roles、isbn、cip、publisher、producer、retailer、edition、dates（date_type/value/source原值，冲突并存）、binding、volumes、pages、format、price、currency、content_scope、relation_to_early_works、evidence_ids。
color_system：palette_id、scope、role、colors数组；逐色字段遵守color-system.md，取样坐标和方法可复现。无分割不写数值面积。
form_spec、head_face_profile、narrative_system、action_library、series_matrix各条字段必须含basis、image_ids或evidence_ids、limitations。recognition_checks含method、status、performed、sample_ids、finding；未做不填通过。
audience_insights逐层记录场景行为状态矛盾隐含表达，不能把解读伪装用户原话。
repo_audit：repository、commit、read_at、files（路径、SHA256、阅读范围）、mapping、cautions。不内嵌密钥或用户令牌。
