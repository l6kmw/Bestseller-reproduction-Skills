# Ecommerce Viral Remix Workflow

> 把竞品爆款广告拆成原创短视频生产包：脚本、分镜、视频提示词、补拍清单和 QA 一次给齐。

当你看到一个 TikTok/Reels/Shorts/抖音/小红书爆款，不想照搬素材、又想复用它的爆款结构时，用这个 Skill。它会先拆原内容的钩子、节奏、证明链和转化点，再把结构重组到你的产品上。

## 你什么时候需要它？

- 看到竞品爆款视频，想复刻结构但不想侵权搬运。
- 要给拍摄、剪辑或视频生成工具一份可执行任务单。
- 需要把产品卖点变成画面证据，而不是只写抽象文案。
- 要为 TikTok/Reels/Shorts/独立站生成短视频广告方案。

## 它会交付什么？

每次完整运行会生成一份 `ecommerce-viral-remix-package.md`，包含：

1. 原爆款内容拆解摘要
2. 可复用爆款公式
3. 自家产品卖点映射表
4. 原创宣传脚本
5. 短视频分镜表
6. 视频生成提示词
7. 素材补拍清单
8. QA 检查表


## DemoBrand showcase：从爆款结构到原创生产包

这个仓库内置了一个稳定可复现的 showcase 流程。`DemoBrand`（割草机）是**虚构的示例品牌**，产品 brief 和预期输出都按它编好，只为让这条链路开箱可跑通——换成你自己的 brief 即可。

换品牌时需要改的地方：`templates/example-product-brief.yaml` 里的 `brand` / `logo` / `brand_line`，以及 `scripts/validate_package.py` 里的 `BRAND_REQUIRED_TERMS`。

- 参考结构：机器人割草机爆款视频的公开视频观察笔记，见 `examples/example-viral-reference-notes.md`。
- 产品信息：DemoBrand 割草机 brief，见 `templates/example-product-brief.yaml`。
- 测试流程：完整步骤、期望结果和验收标准，见 `docs/example-showcase-test-flow.md`。
- 结果卡：适合放 README/发布页的 showcase 摘要，见 `assets/showcase/example-result-card.md`。

稳定演示命令：

```bash
python3 scripts/run_workflow.py \
  --texts examples/example-viral-reference-notes.md \
  --product templates/example-product-brief.yaml \
  --workdir _temp/example-showcase \
  --duration 30 \
  --platform "TikTok/Reels/Shorts/独立站" \
  --prompt-only
```

`--prompt-only` 会生成一份“最终生产包提示词”，适合复制到模型里继续生成完整方案；配置模型 API 后，去掉 `--prompt-only` 就会生成完整生产包。

一键 smoke test：

```bash
scripts/smoke_test.sh
```

真实抓取公开视频时，可以把 `--texts examples/example-viral-reference-notes.md` 换成 `--urls "公开视频链接"`。如果 TikTok/YouTube/Instagram 触发登录或反爬，就把观察结果整理成结构化 notes，再走本地文本流程，demo 不会被平台状态卡死。

## 快速安装

如果你只是想快速体验 DemoBrand demo：

```bash
git clone <your-repo-url> ecommerce-viral-remix-workflow && cd ecommerce-viral-remix-workflow && bash install.sh && scripts/smoke_test.sh
```

如果你的 Agent runtime 支持 Skills 目录，直接把仓库放进对应的 skills 目录即可：

```bash
git clone <your-repo-url> ~/.config/alma/skills/ecommerce-viral-remix-workflow
```

如果发布到 skills.sh / ClawHub / 类似市场，再把平台给出的安装命令放在这里，例如：

```bash
npx skills add <owner>/ecommerce-viral-remix-workflow
```

> 发布前把 `<your-repo-url>` 和 `<owner>` 替换成真实 GitHub 仓库地址与账号名。

## 快速开始

Clone 后先进入仓库，并设置 `SKILL_DIR`：

```bash
cd /path/to/ecommerce-viral-remix-workflow
export SKILL_DIR="$PWD"
```

检查环境：

```bash
bash $SKILL_DIR/install.sh
```

用本地文章或网页整理稿生成方案：

```bash
uv run $SKILL_DIR/scripts/run_workflow.py \
  --texts "/path/to/article.md" \
  --product $SKILL_DIR/templates/example-product-brief.yaml \
  --workdir _temp/example-case \
  --duration 30 \
  --platform "TikTok/Reels/Shorts/独立站"
```

用社媒链接生成方案：

```bash
uv run $SKILL_DIR/scripts/run_workflow.py \
  --urls "https://www.tiktok.com/@example/video/123" \
  --product $SKILL_DIR/templates/example-product-brief.yaml \
  --workdir _temp/example-case
```

只生成 prompt，不调用模型：

```bash
uv run $SKILL_DIR/scripts/run_workflow.py \
  --texts "/path/to/article.md" \
  --product $SKILL_DIR/templates/example-product-brief.yaml \
  --workdir _temp/example-case \
  --prompt-only
```

## 触发方式

用户这样说时，应该使用这个 Skill：

- “帮我拆这个 TikTok 爆款，改成我们产品的广告。”
- “把这个竞品视频复刻成原创分镜。”
- “给我做一个割草机 30 秒爆款脚本。”
- “这个广告结构不错，帮我洗成我们自己的。”
- “给我短视频分镜、视频生成提示词和补拍清单。”
- “只借爆款结构，不要照搬素材。”
- “我等下给你画板，你来导入。”
- “先 prompt-only，不调用模型。”

## 安全边界

- 只复用爆款结构，不复用原视频素材、原文案、原人物肖像、原品牌资产或原音乐。
- 不生成搬运、洗稿、伪原创指令；必须重组为自家产品的原创证明链。
- 不在输出中展示 API key、cookie、token、私有链接或用户本地隐私路径。
- 不承诺 ROAS、转化率、投放收益；最终产物是创意生产包，不是投放保证。
- 当社媒下载失败、平台登录失效、模型返回空内容、素材证据不足时，先报告失败原因，再给 prompt-only 或人工补料 fallback。

## 失败模式与 fallback

| 失败模式 | 处理方式 |
|---|---|
| TikTok/Instagram 下载失败 | 保留 URL 和错误摘要，要求用户提供本地视频，或改用网页文字/截图分析 |
| 缺少 API key | 运行 `--prompt-only` 生成可复制到模型里的完整提示词，不假装完成分析 |
| 视频分析失败 | 抽关键帧后改走图文分析；仍失败则输出人工拆解模板 |
| 生成结果缺章节 | 重新运行生成，或用 `scripts/validate_package.py` 标出缺失章节 |
| 产品 brief 信息不足 | 先用模板字段补齐问题清单，不直接编造产品能力 |

## 验证

检查输出包结构：

```bash
python3 $SKILL_DIR/scripts/validate_package.py \
  _temp/example-case/final/ecommerce-viral-remix-package.md \
  --brand-terms
```

测试样例在 `test-prompts.json`。示例输出在 `examples/example-output-sample.md`。

## 它和同类有什么不同？

| 类型 | 常见工具 | 这个 Skill 的差异 |
|---|---|---|
| UGC 视频生成器 | 直接生成视频 | 先拆爆款结构，再给可控生产包 |
| 广告 spy 工具 | 找爆款素材 | 把爆款变成脚本、分镜和补拍任务 |
| 脚本文案工具 | 只给 hook/body/CTA | 同时给画面证明、视频提示词和 QA |
| 普通提示词 | 临时生成 | 固化为可复用、可测试、可回放的工作流 |
