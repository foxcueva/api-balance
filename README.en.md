# api-balance

English | [中文](README.md)

A command-line tool for checking your LLM API balance: hand it a key, and it tells you how much is left on that key.

Built on the Python standard library only — no dependencies, runs on Python 3.6+.

> Unofficial tool, not affiliated with any provider mentioned below. It only calls the read-only endpoints each provider documents publicly. Read the [disclaimer](#disclaimer) before using it.

## Why this exists

Checking a balance normally means opening a browser, logging in, and finding the right page — different for every provider, and something an agent can't do for you. This script moves it to the command line: one command in your terminal, or one sentence to your agent.

## Supported providers

| Provider | Balance | Endpoint |
| --- | --- | --- |
| DeepSeek | Yes | `GET /user/balance` |
| Kimi (Moonshot) | Yes | `GET /v1/users/me/balance` |
| SiliconFlow | Yes | `GET /v1/user/info` |
| OpenRouter | Yes | `GET /api/v1/key` (shows used / limit) |
| OpenAI | No | No public balance API — check platform.openai.com |
| Anthropic | No | No public balance API — check console.anthropic.com |
| Zhipu GLM | No | No public per-account balance API — check open.bigmodel.cn |
| Google AI Studio | N/A | Free-tier credits, no balance concept |

For providers without a public API, the script won't guess blindly — it tells you where to look instead.

## Three ways to use it

### 1. Install as an OpenClaw skill

```bash
git clone https://github.com/foxcueva/api-balance.git ~/.openclaw/skills/api-balance
```

Then just ask Claw: "check my API balance". Where the skills directory lives depends on your OpenClaw version — see its docs.

### 2. Grab a single-file script

Each provider has one standalone file under `providers/` — zero dependencies, copy it and run it. If you only ever use one provider, this is the better option: no probing, it talks to that one provider only.

| File | Environment variable | Get a key at |
| --- | --- | --- |
| `deepseek_balance.py` | `DEEPSEEK_API_KEY` | platform.deepseek.com |
| `moonshot_balance.py` | `MOONSHOT_API_KEY` | platform.moonshot.cn |
| `siliconflow_balance.py` | `SILICONFLOW_API_KEY` | cloud.siliconflow.cn |
| `openrouter_balance.py` | `OPENROUTER_API_KEY` | openrouter.ai/keys |

DeepSeek example:

```bash
export DEEPSEEK_API_KEY=sk-xxxx
python3 deepseek_balance.py

# or skip the environment variable and pass the key directly
python3 deepseek_balance.py --key sk-xxxx
```

On Windows:

```powershell
$env:DEEPSEEK_API_KEY="sk-xxxx"   # PowerShell
set DEEPSEEK_API_KEY=sk-xxxx      # CMD
python deepseek_balance.py
```

### 3. Run the smart script directly

```bash
python3 check_balance.py              # finds your key, detects the provider
python3 check_balance.py --list       # supported providers
python3 check_balance.py --dry-run    # show the detection plan only, no requests
python3 check_balance.py --provider moonshot    # pin a provider
```

Key lookup order: `--key` argument > environment variables (`BALANCE_API_KEY` or provider-specific ones) > local `~/.openclaw/openclaw.json`.

#### How provider detection works

| Key looks like | Verdict |
| --- | --- |
| starts with `sk-or-` | OpenRouter |
| starts with `sk-ant-` | Anthropic (reports "not supported") |
| starts with `AIza` | Google (reports "no balance concept") |
| `id.xxx.xxx` pattern | Zhipu (reports "not supported") |
| other `sk-` prefix | probes in order: DeepSeek → Kimi → SiliconFlow |
| anything else | asks you to use `--provider` |

OpenAI, DeepSeek and Kimi all use the `sk-` prefix, so the prefix alone isn't enough — that's why probing exists. Probing sends your key to the candidate providers' APIs (the key is never logged). If that bothers you, use `--provider` to skip it. Once a key has been identified, the result is cached in `~/.cache/balance-check.json` (SHA256 fingerprint only, never the key itself), so the next run is instant.

## Sample output

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

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `HTTP 401` | Key invalid, or belongs to a different provider (probing moves on automatically) |
| `Network error` | Check your network and proxy settings |
| `Environment variable not set` | Set it as shown above; note it only applies to the current terminal session |

## Disclaimer

Read this section before running anything. It restates, more concretely, the terms in the [LICENSE](./LICENSE) (MIT).

**1. Not an official tool.** A personal learning project. Not affiliated with, endorsed, or authorized by DeepSeek, Moonshot (Kimi), SiliconFlow, OpenRouter, OpenAI, Anthropic, Zhipu, or Google. Provider names and trademarks only identify which service the script talks to; they belong to their respective owners.

**2. No warranty.** Provided "as is", without warranty of any kind, to the extent permitted by law. Balances shown are for reference only — the provider's own console is always authoritative. APIs may change or disappear at any time; no promise of continued maintenance. The author is not liable for any direct or indirect loss arising from the use of this tool (including key leaks or account losses).

**3. Your key stays yours.** The script collects nothing, uploads nothing, no telemetry. Your key only exists on your machine: environment variables, command-line arguments, or the local `~/.openclaw/openclaw.json` file (read only to locate the key; it never leaves your device). The detection cache stores a SHA256 fingerprint only, never the key itself — delete the file if you don't want it. One thing to be clear about: **the smart script's probing sends your key to DeepSeek, Kimi, and SiliconFlow in sequence.** If you'd rather it didn't, use `--provider`, preview the plan with `--dry-run`, or just use a single-file script, which talks to one provider only. Finally: treat your key like a password. Don't share it, don't commit it, don't hardcode it. If it leaks, revoke and reissue it immediately — the consequences of a leaked key are on its owner.

**4. Stay within the rules.** The script only calls documented read-only endpoints, but you are responsible for making sure your use complies with each provider's terms of service. Use your own key, for your own account. Sharing, reselling, or using someone else's key is a violation, and any resulting trouble has nothing to do with this project.

**5. Nature of the project.** A personal code record, shared for learning. Not a commercial service, not consulting.

## License

[MIT](./LICENSE)
