#!/usr/bin/env python3
# deepseek_balance.py — 查询 DeepSeek 账户余额（只读）
# 作者：foxcueva, 2026-09 | License: MIT
# 仅供学习与个人使用，无任何担保；免责声明与风险提示见仓库 README
"""查询 DeepSeek API 账户余额。零依赖，单文件即用。

用法：
    export DEEPSEEK_API_KEY=sk-xxxx    # macOS / Linux
    python3 deepseek_balance.py
或：
    python3 deepseek_balance.py --key sk-xxxx

Windows CMD          : set DEEPSEEK_API_KEY=sk-xxxx
Windows PowerShell   : $env:DEEPSEEK_API_KEY="sk-xxxx"

key 申请：https://platform.deepseek.com  ->  API Keys
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.deepseek.com/user/balance"
ENV_NAME = "DEEPSEEK_API_KEY"


def main():
    parser = argparse.ArgumentParser(description="查询 DeepSeek API 账户余额（只读）")
    parser.add_argument("--key", help=f"API key；不传则读环境变量 {ENV_NAME}")
    args = parser.parse_args()

    key = args.key or os.environ.get(ENV_NAME)
    if not key:
        sys.stderr.write(
            f"错误: 未设置 {ENV_NAME}。两种方式任选:\n"
            f"  export {ENV_NAME}=sk-xxxx\n"
            "  或 python3 deepseek_balance.py --key sk-xxxx\n"
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

    infos = data.get("balance_infos") or []
    if infos and isinstance(infos[0], dict):
        print(f"总额: {infos[0].get('total_balance', '?')} "
              f"{infos[0].get('currency', '')}")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
