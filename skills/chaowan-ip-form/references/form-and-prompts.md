# 造型规格与线稿提示词

## 目录
1. 区分三件事
2. 最小造型规格
3. 线稿提示词模板
4. 从模糊到可画
5. 反例
6. 出图后怎么看
7. 数据字段

## 1. 区分三件事

"创意成立""角色造型成立""渲染好看"是三件事。洞察和情绪解释不能代替造型；材质细节和摄影精度也不能证明造型完成。找形这一步只处理第二件。

## 2. 最小造型规格

每个形写提示词前，先把下面几项写成能画出来的关系。用户锁定的东西优先，不为补规格改身份。

| 项目 | 要写到的程度 | 不够的写法 |
|---|---|---|
| 轮廓 | 横宽还是纵长、顶部和下缘走向、耳朵或突出物和身体的相对位置 | 圆头、可爱 |
| 体块 | 头、身体、手脚的大中小关系，至少一处明显的收放 | 2 头身 |
| 头脸 | 眼型和高度、眼距和头宽的关系、眼皮或视线、嘴型、脸上的留白 | 豆豆眼、微笑 |
| 情绪 | 用眼皮、嘴角、重心、姿态哪几样表现，不要全部叠上 | 生气眉、鼓腮、握拳、跺脚一起上 |
| 记忆点 | 位置、形状、和身体怎么连接；去掉可拆道具后还剩什么 | 头上有个特别的东西 |
| 结构 | 肢体从哪里长出来、接触点、重心、挂点 | 长臂、悬空，接在哪里不清楚 |

相对大小描述就够，不写假装精确的数字。

## 3. 线稿提示词模板

固定格式：白底黑白线稿，主体正面全身居中，右下角放一个同姿态的小黑剪影。按"轮廓与体块 → 头脸 → 情绪与姿态 → 记忆点与结构 → 画面要求 → 避免项"组织，中英文同义。

中文：
> 原创角色造型线稿，[原型]。[轮廓与体块关系]。[头脸几何与留白]。[情绪由哪些五官和姿态表现]。[记忆点的位置、形状和连接]。纯白背景，黑色[线条语言]线稿，主体正面全身居中，只有线条，不上色、不打阴影、不画材质纹理。画面右下角放一个同一角色、同一姿态的纯黑实心剪影，高度约为主体的六分之一。避免[本形最容易画错的两三项]。

English:
> Original character concept line art, [archetype]. [Silhouette and volume hierarchy]. [Face geometry and negative space]. [Expression carried by which features and pose]. [Signature feature: position, shape, connection]. Pure white background, black [line language] line drawing, single character, full body, front view, centered. Line only: no color, no shading, no material texture. In the lower right corner, a small solid black filled silhouette of the same character in the same pose, about one sixth of the main figure's height. Avoid [two or three likely failure modes].

线条语言的写法：
- 圆润均匀中粗线 → `clean rounded lines of even medium weight`
- 硬朗折线 → `crisp angular lines of even weight`
- 手绘抖线 → `slightly wobbly hand-drawn lines`

写提示词时：
- 不写颜色、材质、灯光、"高级""潮玩""收藏级"这类词，它们只会把画面拉回渲染图
- 不写任何现有 IP、品牌或艺术家的名字，也不写"像某某"
- 避免项针对这个形写，例如"不要把手臂接在头顶""不要画出脚"，不写通用的"不要丑"

## 4. 从模糊到可画

模糊：小猫，2 头身，戴墨镜，可爱自信。

可画：横宽的猫头，下颌收成短圆弧；短耳向两侧展开，梨形身体配很小的脚。眼睛区域是一整块边界清楚的平面眼罩形状，扁长眼位于眼罩中下部，眼皮轻压，嘴角微微偏向一侧；脸上不画胡须和瞳孔细节。

重点是把"自信"翻译成可画的几何关系，而不是在原词上加"更潮"。

## 5. 反例

- "高级潮玩，超精细毛发，电影级灯光"：只控制渲染，没有造型
- 每个形都写"豆豆眼 + 腮红 + 微笑"：把不同表达压成同一张默认脸
- "用头顶的定位针体现归属感"：只解释了概念，角色本体还没设计
- 六个形只换了头上的装饰：拉开规则没过

## 6. 出图后怎么看

用户上传线稿后，先查提示词执行，再查造型：
1. 线稿有没有执行到位：是不是变成了上色图、有没有剪影角标、记忆点画没画出来
2. 执行偏差和设计问题分开记：执行偏差就改提示词重出；设计问题按 `checks.md` 处理
3. 五项测试按实际看到的写"通过 / 存疑 / 不通过"，并写依据；没做的变体标"未验证"
4. 是否好看、保留还是淘汰，交给用户

## 7. 数据字段

每个形写一个 `data/forms/<方案 id>-<轮次字母><序号>.json`：

```json
{
  "ip": "2026w42b-1",
  "round": "A",
  "n": 3,
  "parent": "",
  "title": "一句话概括这个形",
  "axes": {
    "archetype": "原型",
    "silhouette": "整体轮廓",
    "mark": "记忆点：位置 · 是什么",
    "face": "五官",
    "emotion": "情绪表达"
  },
  "odd": "反常点，没有写空字符串",
  "line": "这一轮的线条语言",
  "why": "怎么长出表达",
  "spec": {"outline": "", "volume": "", "face": "", "structure": ""},
  "crop": "裁切检验",
  "collide": "撞车检查",
  "tests": [["记忆点", "待出图验证", "风险"], ["剪影", "待出图验证", ""], ["简化", "待出图验证", ""], ["缩小", "待出图验证", ""], ["换皮", "待出图验证", ""]],
  "zh": "中文线稿提示词",
  "enp": "English line-art prompt",
  "diff": "第二轮才写：和母版差在哪",
  "locked": false,
  "created": "YYYY-MM-DD"
}
```

- 第一轮字母 A，第二轮 B，以此类推；`parent` 写母版的形 id（第一轮留空）
- 用户的选择和批注由网站写进 `data/reviews/<形 id>.json`，不要写进形的文件里
