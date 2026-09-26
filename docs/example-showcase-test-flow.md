# DemoBrand Showcase Test Flow

这份流程用来展示 `ecommerce-viral-remix-workflow` 如何把一个机器人割草机爆款结构，改造成原创短视频生产包。`DemoBrand` 是虚构示例品牌。

## 目标用户

- 内容团队：想把竞品爆款结构改成自家可拍摄脚本。
- 代理商/剪辑师：需要从参考视频快速拿到脚本、分镜、补拍清单。
- AI 视频生成操作者：需要稳定的视频生成 prompt 和 QA 检查表。

## 测试材料

| 材料 | 文件 | 作用 |
|---|---|---|
| 爆款结构参考 | `examples/example-viral-reference-notes.md` | 模拟公开视频拆解结果，避免 demo 依赖平台登录 |
| DemoBrand 产品 brief | `templates/example-product-brief.yaml` | 提供品牌、产品细节、卖点、禁区 |
| 期望输出样例 | `examples/example-output-sample.md` | 给用户看最终生产包长什么样 |
| 结构验证器 | `scripts/validate_package.py` | 检查章节、DemoBrand 术语和安全边界 |

## 公开视频抓取流程

真实使用时，优先从公开平台抓取参考视频：

```bash
uv run scripts/run_workflow.py \
  --urls "https://www.tiktok.com/@example/video/123" \
  --product templates/example-product-brief.yaml \
  --workdir _temp/example-url-case \
  --duration 30 \
  --platform "TikTok/Reels/Shorts"
```

如果 TikTok/YouTube/Instagram 触发登录、反爬或版权限制，不要卡住。把公开视频人工观察结果整理成 `examples/example-viral-reference-notes.md` 这种结构化 notes，然后走稳定的本地文本流程。

## 稳定可复现流程

第一步：生成最终生产包提示词，不调用模型。

```bash
python3 scripts/run_workflow.py \
  --texts examples/example-viral-reference-notes.md \
  --product templates/example-product-brief.yaml \
  --workdir _temp/example-showcase \
  --duration 30 \
  --platform "TikTok/Reels/Shorts/独立站" \
  --prompt-only
```

产物位置：

```text
_temp/example-showcase/final/ecommerce-viral-remix-package.md
```

注意：`--prompt-only` 产出的是“最终生成提示词”，适合复制到模型里继续生成完整方案；配置模型 API 后，去掉 `--prompt-only` 就会生成完整生产包。

第二步：用内置样例验证最终包结构。

```bash
python3 scripts/validate_package.py \
  examples/example-output-sample.md \
  --brand-terms \
  --require-safety
```

期望结果：

```text
PASS required_sections
PASS brand_terms
PASS safety_terms
PASS package is structurally complete
```

## 用户能看到什么

最终生产包应该包含 8 个章节：

1. 原爆款内容拆解摘要
2. 可复用爆款公式
3. 自家产品卖点映射表
4. 原创宣传脚本
5. 短视频分镜表
6. 视频生成提示词
7. 素材补拍清单
8. QA检查表

## DemoBrand 必须出现的证明链

- 白色机身、DEMO BRAND Logo、红色 STOP 键、黑色 PUSH 旋钮、大轮胎。
- 充电座离座、App/扫码连接、自动割草、割前/割后、自动回充。
- 情绪收束：`DEMO BRAND - Let weekends be weekends`。

## QA 验收标准

- 是否只借爆款结构，不复用原素材？
- 是否把竞品元素替换成 DemoBrand 自有产品证明？
- 前 3 秒是否同时有痛点和视觉反差？
- 是否能交给拍摄、剪辑或 AI 视频生成工具执行？
- 是否没有承诺 ROAS、绝对性能或无法证明的数据？
