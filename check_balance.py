#!/usr/bin/env python3
# check_balance.py — 自动识别厂商并查询 LLM API 账户余额（只读）
# 作者：foxcueva, 2026-09 | License: MIT
# 仅供学习与个人使用，无任何担保；免责声明与风险提示见仓库 README
"""自动识别 API key 属于哪家服务商，并查询账户余额。零依赖（纯 Python 标准库）。

key 的查找顺序：
  1. 命令行参数 --key
  2. 环境变量 BALANCE_API_KEY / DEEPSEEK_API_KEY / MOONSHOT_API_KEY 等
  3. 本机 OpenClaw 配置（~/.openclaw/openclaw.json 或 /root/.openclaw/openclaw.json）

自动识别规则：
  sk-or-  开头  -> OpenRouter
  sk-ant- 开头  -> Anthropic（官方无余额接口，会给出指引）
  AIza    开头  -> Google AI Studio（免费额度，无余额概念）
  id.x.y  格式  -> 智谱 GLM（官方无个人余额接口，会给出指引）
  其余 sk- 开头 -> 按 DeepSeek -> Kimi -> SiliconFlow 顺序探测
  首次识别成功会缓存（只存 key 的 SHA256 指纹，不存 key 本身），下次秒识别

常用命令：
  python3 check_balance.py --list       # 查看支持的厂商
  python3 check_balance.py --dry-run    # 只看识别结果，不发真实请求
  python3 check_balance.py --provider moonshot   # 明确指定厂商，跳过探测

只要某一家的极简版？看 providers/ 目录：单文件、零依赖、拷走就能用。
"""
import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


# ---------------------------------------------------------------------------
# 余额摘要：从各家返回的 JSON 提取一行人话（取不到就返回 None，只打印原始 JSON）
# ---------------------------------------------------------------------------
def _dig(data, *path):
    cur = data
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def _sum_deepseek(d):
    infos = _dig(d, "balance_infos") or []
    if infos and isinstance(infos[0], dict):
        return f"总额 {infos[0].get('total_balance', '?')} {infos[0].get('currency', '')}".strip()
    return None


def _sum_moonshot(d):
    data = _dig(d, "data")
    if isinstance(data, dict):
        total = data.get("total_balance") or data.get("balance")
        if total is not None:
            return f"总额 {total} {data.get('currency', '')}".strip()
    return None


def _sum_siliconflow(d):
    bal = _dig(d, "data", "balance")
    return f"总额 {bal} CNY" if bal is not None else None


def _sum_openrouter(d):
    data = _dig(d, "data")
    if isinstance(data, dict) and data.get("usage") is not None:
        limit = data.get("limit")
        limit_txt = "未设置" if limit is None else f"${limit}"
        return f"已用 ${data['usage']} / 上限 {limit_txt}"
    return None


# ---------------------------------------------------------------------------
# 厂商注册表：endpoint 全部来自官方文档公开的只读接口
# ---------------------------------------------------------------------------
PROVIDERS = {
    "deepseek": {
        "label": "DeepSeek（深度求索）",
        "endpoint": "https://api.deepseek.com/user/balance",
        "summarize": _sum_deepseek,
    },
    "moonshot": {
        "label": "Kimi（月之暗面 Moonshot）",
        "endpoint": "https://api.moonshot.cn/v1/users/me/balance",
        "summarize": _sum_moonshot,
    },
    "siliconflow": {
        "label": "SiliconFlow（硅基流动）",
        "endpoint": "https://api.siliconflow.cn/v1/user/info",
        "summarize": _sum_siliconflow,
    },
    "openrouter": {
        "label": "OpenRouter",
        "endpoint": "https://openrouter.ai/api/v1/key",
        "summarize": _sum_openrouter,
    },
}

# 各家专属环境变量名（也是 key 来源之一，且可作为厂商提示）
ENV_NAMES = {
    "deepseek": "DEEPSEEK_API_KEY",
    "moonshot": "MOONSHOT_API_KEY",
    "siliconflow": "SILICONFLOW_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

# 前缀能明确判定、但没有公开余额接口的厂商：诚实提示，不乱试
UNSUPPORTED = {
    "openai": "OpenAI 未公开余额查询接口，请在 platform.openai.com 后台查看",
    "anthropic": "Anthropic 未公开余额查询接口，请在 console.anthropic.com 查看",
    "zhipu": "智谱 GLM 未公开个人余额查询接口，请在 open.bigmodel.cn 后台查看",
    "google": "Google AI Studio 的 key 是免费额度，没有余额概念",
}

# sk- 模糊前缀的默认探测顺序（探测会把 key 发给对应厂商接口，介意请用 --provider）
PROBE_ORDER = ["deepseek", "moonshot", "siliconflow"]

OPENCLAW_PATHS = [
    Path.home() / ".openclaw" / "openclaw.json",
    Path("/root/.openclaw/openclaw.json"),
]

# 各种已知形态的 API key（在 OpenClaw 配置文本里捞 key 用）
KEY_PATTERN = re.compile(
    r"sk-[A-Za-z0-9_-]{16,}"                  # OpenAI 系（DeepSeek/Kimi/SiliconFlow 等）
    r"|sk-or-[A-Za-z0-9_-]{16,}"              # OpenRouter
    r"|sk-ant-[A-Za-z0-9_-]{16,}"             # Anthropic
    r"|AIza[A-Za-z0-9_-]{20,}"                # Google
    r"|id\.[A-Za-z0-9]{8,}\.[A-Za-z0-9]{8,}"  # 智谱
)


def classify_key(key):
    """按 key 前缀判定厂商。返回 (kind, value)：
    provider / candidates / unsupported / unknown"""
    if key.startswith("sk-or-"):
        return "provider", "openrouter"
    if key.startswith("sk-ant-"):
        return "unsupported", "anthropic"
    if key.startswith("AIza"):
        return "unsupported", "google"
    if re.match(r"^id\.[A-Za-z0-9]{4,}\.[A-Za-z0-9]{4,}$", key):
        return "unsupported", "zhipu"
    if key.startswith("sk-"):
        return "candidates", list(PROBE_ORDER)
    return "unknown", None


def load_openclaw_key():
    """防御式读取 OpenClaw 配置（其结构可能随版本变化，只捞长得像 key 的字符串）。
    返回 (路径, key, 配置原文)；找不到返回 (None, None, None)。"""
    for path in OPENCLAW_PATHS:
        try:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        keys = set(KEY_PATTERN.findall(text))
        if keys:
            if len(keys) > 1:
                print(f"注意: 配置里发现 {len(keys)} 个疑似 key，使用其中一个；"
                      "可用 --key 明确指定。")
            return path, sorted(keys)[0], text
    return None, None, None


def reorder_by_config_hints(candidates, config_text):
    """OpenClaw 配置里如果写明了厂商名（如 deepseek/kimi），把它排到探测队首。"""
    lowered = (config_text or "").lower()
    aliases = {"moonshot": ("moonshot", "kimi")}

    def rank(pid):
        names = aliases.get(pid, (pid,))
        return 0 if any(a in lowered for a in names) else 1

    return sorted(candidates, key=rank)


def mask(key):
    return key[:5] + "..." + key[-4:] if len(key) >= 12 else "***"


def _fingerprint(key):
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


CACHE_FILE = Path.home() / ".cache" / "balance-check.json"


def cache_load():
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def cache_save(fp, pid):
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = cache_load()
        data[fp] = pid
        CACHE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass


def query(pid, key, timeout=20):
    """调厂商余额接口。成功返回 (json, None)，失败返回 (None, 错误描述)。"""
    req = urllib.request.Request(
        PROVIDERS[pid]["endpoint"],
        headers={"Authorization": "Bearer " + key, "User-Agent": "api-balance/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        hint = {
            401: "(key 无效或不属于该厂商)",
            403: "(key 权限不足)",
            429: "(请求太频繁，稍后再试)",
        }.get(e.code, "")
        return None, f"接口返回 HTTP {e.code} {hint}"
    except urllib.error.URLError as e:
        return None, f"网络请求失败({e.reason})"
    except TimeoutError:
        return None, "请求超时"
    except json.JSONDecodeError:
        return None, "接口返回内容不是有效 JSON"


def main():
    parser = argparse.ArgumentParser(
        prog="check_balance",
        description="自动识别厂商并查询 LLM API 账户余额（只读，零依赖）",
        epilog="示例:\n"
               "  python3 check_balance.py\n"
               "  python3 check_balance.py --provider moonshot\n"
               "  python3 check_balance.py --key sk-xxx --dry-run\n"
               "  python3 check_balance.py --list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--key", help="API key；不传则依次找环境变量和 OpenClaw 配置")
    parser.add_argument("--provider", choices=sorted(PROVIDERS),
                        help="明确指定厂商，跳过自动识别")
    parser.add_argument("--list", action="store_true", help="列出支持的厂商后退出")
    parser.add_argument("--dry-run", action="store_true",
                        help="只显示识别结果，不发真实请求")
    args = parser.parse_args()

    if args.list:
        print("支持自动查询余额的厂商:")
        for pid, meta in PROVIDERS.items():
            print(f"  {pid:<12} {meta['label']}")
            print(f"  {'':<12} 接口: {meta['endpoint']}")
        print()
        print("未公开余额接口的厂商(会给出指引, 不会乱试):")
        for pid, note in UNSUPPORTED.items():
            print(f"  {pid:<12} {note}")
        return 0

    # ---- 1. 找 key ----
    key = args.key or os.environ.get("BALANCE_API_KEY")
    key_source = "命令行参数" if args.key else (
        "环境变量 BALANCE_API_KEY" if key else None)
    env_provider = None
    config_text = None
    if not key:
        for pid, env_name in ENV_NAMES.items():
            val = os.environ.get(env_name)
            if val:
                key, key_source, env_provider = val, f"环境变量 {env_name}", pid
                break
    if not key:
        cfg_path, cfg_key, config_text = load_openclaw_key()
        if cfg_key:
            key, key_source = cfg_key, f"OpenClaw 配置({cfg_path})"
    if not key:
        sys.stderr.write(
            "错误: 没有找到 API key。三种方式任选其一:\n"
            "  1. python3 check_balance.py --key sk-xxxx\n"
            "  2. export DEEPSEEK_API_KEY=sk-xxxx  "
            "(或 MOONSHOT_API_KEY / SILICONFLOW_API_KEY / OPENROUTER_API_KEY)\n"
            "  3. 确认本机存在 ~/.openclaw/openclaw.json\n"
        )
        return 1

    # ---- 2. 识别厂商 ----
    if args.provider:
        order = [args.provider]
    else:
        kind, val = classify_key(key)
        if kind == "unsupported":
            print(f"识别结果: {val} -- {UNSUPPORTED[val]}")
            return 0
        if kind == "unknown":
            sys.stderr.write(
                "错误: 认不出这个 key 的格式。"
                "用 --list 查看支持的厂商, 或用 --provider 明确指定。\n"
            )
            return 1
        order = val if kind == "candidates" else [val]
        if kind == "candidates":
            cached = cache_load().get(_fingerprint(key))
            if cached in PROVIDERS:
                order = [cached] + [p for p in order if p != cached]
                print(f"(命中缓存, 优先尝试 {PROVIDERS[cached]['label']}; "
                      "用 --provider 可强制指定)")
            elif env_provider:
                order = [env_provider] + [p for p in order if p != env_provider]
            elif config_text:
                order = reorder_by_config_hints(order, config_text)

    # ---- 3. dry-run：只展示计划 ----
    if args.dry_run:
        print("[dry-run] 识别结果如下(未发任何真实请求):")
        print(f"  key: {mask(key)}  来源: {key_source}")
        if len(order) > 1:
            names = " -> ".join(PROVIDERS[p]["label"] for p in order)
            print(f"  探测顺序: {names}")
        else:
            print(f"  厂商: {PROVIDERS[order[0]]['label']}")
            print(f"  接口: {PROVIDERS[order[0]]['endpoint']}")
        return 0

    # ---- 4. 查询 ----
    if len(order) > 1:
        names = " -> ".join(PROVIDERS[p]["label"] for p in order)
        print(f"提示: key 前缀不够唯一, 将按 {names} 顺序探测;")
        print("      探测会把 key 发给对应厂商的接口。想跳过请用 --provider 明确指定。")

    fp = _fingerprint(key)
    errors = []
    for i, pid in enumerate(order):
        label = PROVIDERS[pid]["label"]
        print(f"正在查询 {label} ...")
        data, err = query(pid, key)
        if err is None:
            cache_save(fp, pid)
            print(f"\n{label} 查询成功 (key {mask(key)}, 来源: {key_source})")
            summary = PROVIDERS[pid]["summarize"](data)
            if summary:
                print(f"  {summary}")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        errors.append(f"{label}: {err}")
        print(f"  失败: {err}")
    print("\n所有候选厂商都查询失败:")
    for e in errors:
        print(f"  - {e}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
