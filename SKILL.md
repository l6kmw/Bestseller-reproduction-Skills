---
name: ecommerce-viral-remix-workflow
description: |
  电商爆款内容再创作工作流。用于从社交媒体爆款短视频/文章/广告中提取可复制结构，清洗原内容，结合自家产品卖点，生成原创宣传脚本、短视频分镜、视频生成提示词、素材补拍清单和QA检查表。内置多平台下载脚本、Gemini 视频/图文分析脚本、完整方案生成脚本。适用于跨境电商、独立站、亚马逊、TikTok Shop、抖音、小红书等产品宣传内容生产。用户提到“爆款拆解”“竞品视频改写”“广告分镜”“产品宣传视频”“短视频工作流”“种草脚本”“素材再创作”“电商视频提示词”“DemoBrand/割草机宣传”时使用。
---

# 电商爆款内容再创作工作流

把「看到一个爆款，凭感觉模仿」变成「下载/读取素材 → AI结构化拆解 → 合规清洗 → 自家产品重组 → 生成脚本/分镜/视频提示词」。

> `SKILL_DIR` 指本 Skill 目录。Clone 后可运行：`export SKILL_DIR="$PWD"`

## 目录结构

```text
SKILL.md
README.md                 # 公开说明页：定位、快速开始、失败模式、验证方式
test-prompts.json         # 典型触发语和期望输出
install.sh
scripts/
  download_media.py       # 用 yt-dlp 下载多平台爆款视频
  llm_client.py           # OpenAI-compatible 自定义接口客户端
  analyze_video.py        # 用 Gemini 原生视频或自定义接口关键帧分析视频
  analyze_text.py         # 用 Gemini 或自定义接口分析文章/Markdown/网页文本
  generate_package.py     # 基于分析结果和产品brief生成完整方案
  run_workflow.py         # 一键串联下载/分析/生成
  validate_package.py     # 检查输出包章节、DemoBrand证明链和合规关键词
references/
  analysis-framework.md   # 爆款内容分析框架
  viral-formulas.md       # 通用公式和 DemoBrand 割草机公式
  platform-notes.md       # 平台适配规则
templates/
  product-brief-template.yaml
  example-product-brief.yaml
  output-package-template.md
examples/
  example-output-sample.md # 可截图传播的示例输出
```

## 环境要求

- `uv`
- `yt-dlp`
- 默认 Gemini：`GEMINI_API_KEY` 或 `GOOGLE_API_KEY`
- 自定义 OpenAI-compatible 接口：`--provider custom --base-url ... --api-key ... --model-id ...`
- 视频走自定义接口时需要 `ffmpeg` 抽关键帧
- Chrome 已登录目标平台时，可用 `--cookies-browser chrome` 读取 cookies

检查环境：

```bash
bash $SKILL_DIR/install.sh
```

## 快速开始

### 1. 用本地文章生成完整方案

```bash
uv run $SKILL_DIR/scripts/run_workflow.py \
  --texts "/path/to/article.md" \
  --product $SKILL_DIR/templates/example-product-brief.yaml \
  --workdir _temp/example-case \
  --duration 30 \
  --platform "TikTok/Reels/Shorts/独立站"
```

### 2. 用社媒链接生成完整方案

```bash
uv run $SKILL_DIR/scripts/run_workflow.py \
  --urls "https://www.tiktok.com/@example/video/123" \
  --product $SKILL_DIR/templates/example-product-brief.yaml \
  --workdir _temp/example-case
```

### 3. 只生成 prompt，不调用 Gemini

```bash
uv run $SKILL_DIR/scripts/run_workflow.py \
  --texts "/path/to/article.md" \
  --product $SKILL_DIR/templates/example-product-brief.yaml \
  --workdir _temp/example-case \
  --prompt-only
```


### 4. 使用自定义 OpenAI-compatible 接口

不要把 API key 写进 skill 文件，推荐用环境变量：

```bash
export CUSTOM_BASE_URL="https://api.example.com/v1"
export CUSTOM_API_KEY="sk-..."
export CUSTOM_MODEL="gemini-3-flash-preview"
```

然后运行：

```bash
uv run $SKILL_DIR/scripts/run_workflow.py \
  --provider custom \
  --texts "/path/to/article.md" \
  --product $SKILL_DIR/templates/example-product-brief.yaml \
  --workdir _temp/example-case
```

也可以一次性传参：

```bash
uv run $SKILL_DIR/scripts/run_workflow.py \
  --provider custom \
  --base-url "https://api.example.com/v1" \
  --api-key "$CUSTOM_API_KEY" \
  --model-id "gemini-3-flash-preview" \
  --texts "/path/to/article.md" \
  --product $SKILL_DIR/templates/example-product-brief.yaml \
  --workdir _temp/example-case
```

## 分步执行

### Step 1：下载爆款视频

```bash
uv run $SKILL_DIR/scripts/download_media.py \
  --urls "URL_OR_SHARE_TEXT" \
  --output-dir _temp/viral-inputs \
  --cookies-browser chrome
```

输出：

- 视频文件
- 缩略图
- info json
- `download-manifest.json`

### Step 2：分析视频

```bash
uv run $SKILL_DIR/scripts/analyze_video.py \
  --video _temp/viral-inputs/video.mp4 \
  --output _temp/analysis/video-analysis.md \
  --model flash \
  --resolution medium
```

### Step 3：分析文章/Markdown

```bash
uv run $SKILL_DIR/scripts/analyze_text.py \
  --input "/path/to/article.md" \
  --output _temp/analysis/text-analysis.md \
  --model flash
```

### Step 4：生成完整再创作方案

```bash
uv run $SKILL_DIR/scripts/generate_package.py \
  --analysis _temp/analysis/video-analysis.md _temp/analysis/text-analysis.md \
  --product $SKILL_DIR/templates/example-product-brief.yaml \
  --output _temp/final/ecommerce-viral-remix-package.md \
  --duration 30 \
  --platform "TikTok/Reels/Shorts/独立站" \
  --model pro
```

## 工作流原则

1. 只借结构，不借素材。
2. 先拆爆款，再融合产品。
3. 每个卖点必须有画面证明。
4. 前3秒必须同时有文案钩子和视觉钩子。
5. 最终输出必须能交给拍摄、剪辑或视频生成工具执行。

## 最终交付格式

每次执行该工作流，最终输出：

```markdown
# 电商爆款内容再创作方案

## 1. 原爆款内容拆解摘要
## 2. 可复用爆款公式
## 3. 自家产品卖点映射表
## 4. 原创宣传脚本
## 5. 短视频分镜表
## 6. 视频生成提示词
## 7. 素材补拍清单
## 8. QA检查表
```

## 安全边界

- 只复用爆款结构，不复用原视频素材、原文案、原人物肖像、原品牌资产或原音乐。
- 不生成搬运、洗稿、伪原创指令；必须重组为自家产品的原创证明链。
- 不在输出中展示 API key、cookie、token、私有链接或用户本地隐私路径。
- 不承诺 ROAS、转化率、投放收益；最终产物是创意生产包，不是投放保证。
- 当社媒下载失败、平台登录失效、模型返回空内容、素材证据不足时，先报告失败原因，再给 prompt-only 或人工补料 fallback。

## 失败模式与 fallback

- TikTok/Instagram 下载失败：保留 URL 和错误摘要，要求用户提供本地视频，或改用网页文字/截图分析。
- 缺少 API key：运行 `--prompt-only` 生成可复制到模型里的完整提示词，不假装已经完成分析。
- 视频分析失败：抽关键帧后改走图文分析；仍失败则输出人工拆解模板。
- 生成结果缺章节：重新运行生成，或用 `scripts/validate_package.py` 标出缺失章节。
- 产品 brief 信息不足：先用模板字段补齐问题清单，不直接编造产品能力。

## 验证方式

检查输出包结构：

```bash
python3 $SKILL_DIR/scripts/validate_package.py \
  _temp/example-case/final/ecommerce-viral-remix-package.md \
  --brand-terms
```

测试样例在 `test-prompts.json`。示例输出在 `examples/example-output-sample.md`。

## DemoBrand/割草机专项要求

必须形成完整证明链：

```text
还在自己割草？ → DemoBrand 从充电座出发 → App/扫码控制 → 自动行驶割草 → 割前/割后对比 → 自动回充 → DEMO BRAND - Let weekends be weekends.
```

必须展示：

- 白色机身和 DEMO BRAND Logo
- 红色 STOP 键
- 黑色 PUSH 高度调节旋钮
- 大轮胎
- 充电座
- 机身二维码/App连接信息
- 自动离座割草
- 草坪割前/割后对比
- 自动回充

## 执行偏好

- 用户给文件时，先读取文件内容再分析。
- 用户给目录时，先列出目录结构，优先读取 `SKILL.md`、`README.md`、`*.md`、脚本和参考资料。
- 用户给社媒链接时，优先运行 `download_media.py`，再运行 `analyze_video.py`。
- 用户给本地视频时，直接运行 `analyze_video.py`。
- 用户给文章/Markdown时，运行 `analyze_text.py`。
- 信息足够时不要过度提问，先产出第一版。
