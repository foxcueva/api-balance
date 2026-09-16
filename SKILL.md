---
name: api-balance
description: 查询 LLM API 服务商（DeepSeek / Kimi(Moonshot) / SiliconFlow / OpenRouter）的账户余额。当用户问「API 还剩多少余额/额度」「查一下 XX 的账户余额」「我的 key 还有钱吗」等问题时使用。自动识别 key 属于哪家厂商；OpenAI、Anthropic、智谱、Google 等未公开余额接口的厂商会明确告知并指引到网页后台。
---

# api-balance — LLM API 余额查询

## 何时使用

用户想查 API 账户余额、剩余额度、key 里还有多少钱时。

## 怎么做

首选（自动识别厂商，key 会自动从环境变量或 OpenClaw 配置里找）：

```bash
python3 check_balance.py
```

key 的查找顺序：`--key` 参数 > 环境变量（`DEEPSEEK_API_KEY` / `MOONSHOT_API_KEY` / `SILICONFLOW_API_KEY` / `OPENROUTER_API_KEY` / `BALANCE_API_KEY`）> 本机 `~/.openclaw/openclaw.json`。

用户明确说了厂商时，也可以直接跑对应的单文件版（更直接）：

```bash
python3 providers/deepseek_balance.py      # DEEPSEEK_API_KEY
python3 providers/moonshot_balance.py      # MOONSHOT_API_KEY（Kimi）
python3 providers/siliconflow_balance.py   # SILICONFLOW_API_KEY
python3 providers/openrouter_balance.py    # OPENROUTER_API_KEY
```

单文件版优先读对应环境变量，也接受 `--key sk-xxx` 传参。

不确定能识别时，先跑 `python3 check_balance.py --dry-run` 看识别计划（不发请求）。

## 注意

- 全部是只读 GET 请求，不会产生费用或写操作。
- 绝对不要把用户的 key 明文回显在对话或日志里（脚本自身只输出打码后的 key）。
- 遇到「未公开余额接口」的提示是正常结果（OpenAI / Anthropic / 智谱 / Google），如实转述给用户即可，不要反复重试。
- 查询失败时把脚本的错误信息原样告诉用户，帮助其排查（key 错、网络问题等）。
- 用户只查某一家时，优先用 providers/ 下对应的单文件脚本：不探测、只与一家通信，更省事也更保护隐私。
- 顺带提醒用户：key 等同账户密码，别发给任何人；探测模式会把 key 发给多家厂商接口，介意请用 --provider 指定。
- 本项目是个人学习性质的非官方工具，与各厂商无关联；不要以任何「官方」口吻转述结果或做出担保。
