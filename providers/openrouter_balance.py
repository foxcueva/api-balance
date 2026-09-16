#!/usr/bin/env python3
# openrouter_balance.py — 查询 OpenRouter 账户额度（只读）
# 作者：foxcueva, 2026-09 | License: MIT
# 仅供学习与个人使用，无任何担保；免责声明与风险提示见仓库 README
"""查询 OpenRouter 账户额度/用量。零依赖，单文件即用。

用法：
    export OPENROUTER_API_KEY=sk-or-xxxx    # macOS / Linux
    python3 openrouter_balance.py
或：
    python3 openrouter_balance.py --key sk-or-xxxx

Windows CMD          : set OPENROUTER_API_KEY=sk-or-xxxx
Windows PowerShell   : $env:OPENROUTER_API_KEY="sk-or-xxxx"

注意：OpenRouter 的接口返回的是「已用金额 / 消费上限」，不是充值余额；
充值余额可看 https://openrouter.ai/credits

key 申请：https://openrouter.ai/keys
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://openrouter.ai/api/v1/key"
ENV_NAME = "OPENROUTER_API_KEY"


def main():
    parser = argparse.ArgumentParser(description="查询 OpenRouter 账户额度（只读）")
    parser.add_argument("--key", help=f"API key；不传则读环境变量 {ENV_NAME}")
    args = parser.parse_args()

    key = args.key or os.environ.get(ENV_NAME)
    if not key:
        sys.stderr.write(
            f"错误: 未设置 {ENV_NAME}。两种方式任选:\n"
            f"  export {ENV_NAME}=sk-or-xxxx\n"
            "  或 python3 openrouter_balance.py --key sk-or-xxxx\n"
        )
        return 1

    req = urllib.request.Request(API_URL, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        hint = "(key 无效, 请检查)" if e.code == 401 else ""
        sys.stderr.write(f"错误: 接口返回 HTTP {e.code} {hint}\n")
        return 1
    except urllib.error.URLError as e:
        sys.stderr.write(f"错误: 网络请求失败({e.reason})\n")
        return 1
    except TimeoutError:
        sys.stderr.write("错误: 请求超时\n")
        return 1
    except json.JSONDecodeError:
        sys.stderr.write("错误: 返回内容不是有效 JSON\n")
        return 1

    d = data.get("data")
    if isinstance(d, dict) and d.get("usage") is not None:
        limit = d.get("limit")
        limit_txt = "未设置" if limit is None else f"${limit}"
        print(f"已用: ${d['usage']} / 上限: {limit_txt}")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
