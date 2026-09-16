# api-balance

查询 LLM API 账户余额的命令行工具集。零依赖（纯 Python 标准库），Python 3.6+ 开箱即用。

两种用法，按需选择：

1. **装成 OpenClaw skill** —— 整个仓库克隆到 skills 目录，之后直接问一句「查下我的 API 余额」，自动识别你的 key 属于哪家厂商并查询。
2. **只用你那一家的单文件脚本** —— 去 `providers/` 目录挑一个，下载就能跑，不用装整仓。
3. **不装 skill，直接跑智能版** —— `python3 check_balance.py`，自动识别厂商。

> 非官方工具，与各厂商无关联，仅调用官方文档公开的只读接口。
> 仅供学习与个人使用；使用前请阅读下方的[免责声明与风险提示](#免责声明与风险提示)。
> Unofficial personal project, provided "AS IS", without warranty of any kind.

## 厂商支持情况

| 厂商 | 余额查询 | 说明 |
| --- | --- | --- |
| DeepSeek | 支持 | `GET /user/balance` |
| Kimi（月之暗面 Moonshot） | 支持 | `GET /v1/users/me/balance` |
| SiliconFlow（硅基流动） | 支持 | `GET /v1/user/info` |
| OpenRouter | 支持 | `GET /api/v1/key`（显示已用/上限） |
| OpenAI（GPT） | 不支持 | 官方未公开余额接口，请到 platform.openai.com 后台查看 |
| Anthropic（Claude） | 不支持 | 官方未公开余额接口，请到 console.anthropic.com 查看 |
| 智谱 GLM | 不支持 | 个人余额无公开接口，请到 open.bigmodel.cn 查看 |
| Google AI Studio | 无余额概念 | 免费额度制 |

对不支持的厂商，脚本不会乱试，而是明确告诉你去哪里查。

## 用法一：装成 OpenClaw skill

```bash
git clone https://github.com/foxcueva/api-balance.git ~/.openclaw/skills/api-balance
```

然后直接对 Claw 说「查一下我的 API 余额」即可。
（skills 目录位置以你所用 OpenClaw 版本的官方文档为准。）

## 用法二：只拿单文件脚本

`providers/` 目录下每家一个独立脚本，单文件、零依赖、拷走就能用：

| 文件 | 环境变量 | key 申请地址 |
| --- | --- | --- |
| `deepseek_balance.py` | `DEEPSEEK_API_KEY` | platform.deepseek.com |
| `moonshot_balance.py` | `MOONSHOT_API_KEY` | platform.moonshot.cn |
| `siliconflow_balance.py` | `SILICONFLOW_API_KEY` | cloud.siliconflow.cn |
| `openrouter_balance.py` | `OPENROUTER_API_KEY` | openrouter.ai/keys |

只查一家的话，单文件是最省心、也最隐私友好的选择：不做探测、只与这一家通信，也最适合直接单独喂给你的 agent。

以 DeepSeek 为例：

```bash
export DEEPSEEK_API_KEY=sk-xxxx
python3 deepseek_balance.py
# 或者不设环境变量，直接传参：
python3 deepseek_balance.py --key sk-xxxx
```

Windows：

```powershell
$env:DEEPSEEK_API_KEY="sk-xxxx"   # PowerShell
set DEEPSEEK_API_KEY=sk-xxxx      # CMD
python deepseek_balance.py
```

## 用法三：不装 skill，直接跑智能版

```bash
python3 check_balance.py              # 自动找 key、自动识别厂商
python3 check_balance.py --list       # 查看支持的厂商
python3 check_balance.py --dry-run    # 只看识别结果，不发请求
python3 check_balance.py --provider moonshot    # 指定厂商
```

key 的查找顺序：`--key` 参数 > 环境变量（`BALANCE_API_KEY` 或各家专属变量）> 本机 `~/.openclaw/openclaw.json`。

### 自动识别规则

| key 长相 | 判定 |
| --- | --- |
| `sk-or-` 开头 | OpenRouter |
| `sk-ant-` 开头 | Anthropic（提示不支持） |
| `AIza` 开头 | Google（提示无余额概念） |
| `id.xxx.xxx` 格式 | 智谱（提示不支持） |
| 其他 `sk-` 开头 | 按 DeepSeek -> Kimi -> SiliconFlow 顺序探测 |
| 其他 | 提示用 `--provider` 指定 |

说明：

- `sk-` 前缀 OpenAI、DeepSeek、Kimi 都在用，光看前缀分不出来，所以才需要探测。探测会把 key 发给候选厂商的接口（key 不会被记录，但介意的话请用 `--provider` 一键跳过）。
- 首次识别成功后，结果缓存到 `~/.cache/balance-check.json`（只存 key 的 SHA256 指纹，**不存 key 本身**），之后再跑秒识别。

## 输出示例

```json
{
  "is_available": true,
  "balance_infos": [
    {
      "currency": "CNY",
      "total_balance": "110.00",
      "granted_balance": "10.00",
      "topped_up_balance": "100.00"
    }
  ]
}
```

## 常见问题

| 现象 | 原因与处理 |
| --- | --- |
| `HTTP 401` | key 无效，或不属于当前探测的厂商（探测模式会自动换下一家） |
| `网络请求失败` | 检查网络、代理设置 |
| `未设置环境变量` | 按上面的命令设置；注意环境变量只对当前终端窗口有效 |

## 免责声明与风险提示

> 下载、克隆或运行本项目代码，即表示你已阅读并理解本节内容。本节与 [LICENSE](./LICENSE)（MIT）中的免责条款一致，并作更具体的补充。

### 1. 非官方项目，与任何厂商无关联

- 本项目是个人学习用的小工具，**与 DeepSeek、Moonshot（Kimi）、SiliconFlow、OpenRouter、OpenAI、Anthropic、智谱、Google 等服务商均无关联，未获任何授权或背书**。
- 文中出现的厂商名称与商标仅用于说明脚本所对接的服务，归各自权利人所有。

### 2. 无担保，责任自负

- 本项目按「现状」提供，在法律允许的最大范围内，**不附带任何明示或默示的担保**（包括但不限于可用性、准确性、适用性）。
- 本工具输出的余额信息**仅供参考**，一切以各厂商官方后台/账单为准，不构成任何财务依据。
- 各厂商接口可能随时变更或下线，作者不承诺持续维护、更新。
- 对使用本工具导致的任何直接或间接损失（包括但不限于 key 泄露、账户损失、费用损失、功能失效），作者在法律允许范围内不承担责任。

### 3. 隐私与 API key 安全

- 本工具**不收集、不上传、不存储**任何用户数据，无遥测、无统计。
- 你的 key 只存在于你自己的设备上（环境变量、命令行参数或本机 OpenClaw 配置文件）。脚本读取本机 `~/.openclaw/openclaw.json` 仅为自动寻找 key，该文件不会离开你的设备。
- 识别缓存（`~/.cache/balance-check.json`）只保存 key 的 **SHA256 指纹**（不保存 key 本身），用于跳过重复探测；不想要缓存可直接删除该文件。
- **探测模式会依次把你的 key 发送给多家候选厂商的接口**（DeepSeek -> Kimi -> SiliconFlow）。介意的话，请用 `--provider` 指定厂商，或先用 `--dry-run` 查看识别计划（不发请求）；更推荐直接使用 `providers/` 下对应厂商的**单文件脚本**——只与一家通信，不做探测。
- key 等同于账户密码：不要发给任何人、不要提交到 git、不要写死在代码里。key 一旦泄露，请立即到对应平台删除并重建；**key 保管不善造成的后果由 key 的持有者自行承担**。

### 4. 合规使用第三方服务

- 本工具只调用各厂商官方公开文档中的**只读**查询接口。你需要自行确保持有、使用 key 的方式符合对应厂商的服务条款。
- 请使用自己的 key、为自己的账号充值。**共享、转售或使用他人 key 均属违规**，由此产生的一切问题与本项目无关。
- 请勿将本工具用于任何违反适用法律法规或厂商条款的用途。

### 5. 项目性质

- 本项目以**技术学习与个人使用**为目的分享，属于个人代码记录，不构成商业服务或技术咨询。
- 余额查询本身是免费只读请求；你的 key 在其他场景下产生的调用费用，是你与厂商之间的事，与本项目无关。

## License

[MIT](./LICENSE)
