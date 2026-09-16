# api-balance

[English](README.en.md) | 中文

命令行查 LLM API 余额的工具：给它一个 key，它告诉你这个 key 还剩多少钱。

纯 Python 标准库实现，没有依赖，Python 3.10+ 直接跑。

> 非官方工具，和下面提到的厂商都没有关联，只调用它们文档里公开的只读接口。动手前先看[免责声明](#免责声明)。

## 为什么有这个

查余额得开浏览器、登后台、找对页面，一家一个地方，agent 也没法帮你查。这个脚本把这件事搬到命令行——终端敲一行命令，或者对 agent 说一句话。

## 支持哪些厂商

| 厂商 | 能查余额吗 | 接口 |
| --- | --- | --- |
| DeepSeek | 能 | `GET /user/balance` |
| Kimi（月之暗面） | 能 | `GET /v1/users/me/balance` |
| SiliconFlow（硅基流动） | 能 | `GET /v1/user/info` |
| OpenRouter | 能 | `GET /api/v1/key`，显示已用/上限 |
| OpenAI | 不能 | 官方没公开余额接口，去 platform.openai.com 看 |
| Anthropic | 不能 | 同样没公开，去 console.anthropic.com |
| 智谱 GLM | 不能 | 个人余额没有公开接口，去 open.bigmodel.cn |
| Google AI Studio | 不适用 | 免费额度制，没有余额概念 |

OpenAI 和 Anthropic 这类没公开接口的，脚本不会硬试，会直接告诉你去哪查。

## 三种用法

### 1. 装成 OpenClaw skill

```bash
git clone https://github.com/foxcueva/api-balance.git ~/.openclaw/skills/api-balance
```

然后对 Claw 说「查一下我的 API 余额」就行。skills 目录的位置以你那版 OpenClaw 的文档为准。

### 2. 只拿单文件脚本

`providers/` 下每家一个文件，单文件、零依赖，拷走就能跑。只查一家的话，这个最合适：它不探测，只和这一家通信。

| 文件 | 环境变量 | key 在哪申请 |
| --- | --- | --- |
| `deepseek_balance.py` | `DEEPSEEK_API_KEY` | platform.deepseek.com |
| `moonshot_balance.py` | `MOONSHOT_API_KEY` | platform.moonshot.cn |
| `siliconflow_balance.py` | `SILICONFLOW_API_KEY` | cloud.siliconflow.cn |
| `openrouter_balance.py` | `OPENROUTER_API_KEY` | openrouter.ai/keys |

以 DeepSeek 为例：

```bash
export DEEPSEEK_API_KEY=sk-xxxx
python3 deepseek_balance.py

# 或者不设环境变量，直接传参
python3 deepseek_balance.py --key sk-xxxx
```

Windows 下：

```powershell
$env:DEEPSEEK_API_KEY="sk-xxxx"   # PowerShell
set DEEPSEEK_API_KEY=sk-xxxx      # CMD
python deepseek_balance.py
```

### 3. 不装 skill，直接跑智能版

```bash
python3 check_balance.py              # 自动找 key、自动认厂商
python3 check_balance.py --list       # 看支持哪些厂商
python3 check_balance.py --dry-run    # 只看识别结果，不发请求
python3 check_balance.py --provider moonshot    # 手动指定厂商
```

key 的查找顺序：`--key` 参数 > 环境变量（`BALANCE_API_KEY` 或各家专属变量）> 本机 `~/.openclaw/openclaw.json`。

#### 智能版怎么认厂商

| key 长相 | 判定 |
| --- | --- |
| `sk-or-` 开头 | OpenRouter |
| `sk-ant-` 开头 | Anthropic（提示不支持） |
| `AIza` 开头 | Google（提示没有余额概念） |
| `id.xxx.xxx` 格式 | 智谱（提示不支持） |
| 其他 `sk-` 开头 | 按 DeepSeek → Kimi → SiliconFlow 顺序探测 |
| 都不是 | 提示用 `--provider` 指定 |

`sk-` 这个前缀 OpenAI、DeepSeek、Kimi 都在用，光看前缀分不出来，所以才需要探测。探测会把 key 发给候选厂商的接口——key 不会被记录，但介意的话用 `--provider` 跳过就行。识别成功一次后，结果会缓存到 `~/.cache/balance-check.json`（只存 key 的 SHA256 指纹，不存 key 本身），之后再跑就秒认了。

## 输出长什么样

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

## 遇到问题

| 现象 | 怎么办 |
| --- | --- |
| `HTTP 401` | key 无效，或者 key 不是当前探测的这家（探测模式会自动换下一家） |
| `网络请求失败` | 检查网络和代理设置 |
| `未设置环境变量` | 按上面的命令设置；环境变量只对当前终端窗口有效 |

## 免责声明

往下跑代码之前把这节看完。这里和 [LICENSE](./LICENSE)（MIT）的免责条款是一回事，写得具体一点。

**1. 这不是官方工具。** 个人学习用的小项目，和 DeepSeek、Moonshot（Kimi）、SiliconFlow、OpenRouter、OpenAI、Anthropic、智谱、Google 都没有关联，也没拿到任何授权或背书。厂商名字和商标只是用来说明脚本对接的是谁，归各自权利人所有。

**2. 没有任何担保。** 代码按「现状」提供，法律允许范围内不附带任何明示或默示的担保。输出的余额仅供参考，一切以各厂商官方后台为准。接口哪天改了、下线了，不承诺跟进。用这个工具导致的任何直接或间接损失（包括 key 泄露、账户损失），作者不承担责任。

**3. 你的 key 在你手里。** 脚本不收集、不上传、不存储任何数据，没有遥测。key 只存在你自己的设备上：环境变量、命令行参数，或者本机 `~/.openclaw/openclaw.json`（读它只是为了自动找 key，这个文件不会离开你的设备）。识别缓存只存 key 的 SHA256 指纹，不存 key 本身，不想要就删掉那个文件。有一点要明确：**智能版探测会依次把 key 发给 DeepSeek、Kimi、SiliconFlow 三家的接口**。介意的话用 `--provider` 指定厂商、用 `--dry-run` 先看识别计划，或者干脆用单文件脚本——只和一家通信。最后，key 等于密码：别发给别人，别提交进 git，别写死在代码里。万一泄露，立刻去对应平台删掉重建，后果由 key 的持有者承担。

**4. 别拿去干违规的事。** 脚本只调官方文档里的只读接口，但你需要自己确认这种用法符合对应厂商的服务条款。用自己的 key、查自己的账。共享、转售、用别人的 key 都属于违规，由此产生的问题和本项目无关。

**5. 项目性质。** 个人代码记录，学习交流用，不构成商业服务，也不是技术咨询。

## License

[MIT](./LICENSE)
