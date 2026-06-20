#!/usr/bin/env bash
# examples/quickstart.sh —— chinese-geo 最快上手：一条命令看到结果（零 key、零网络）。
# 跑的就是你刚 clone 的这份源码（设 PYTHONPATH 到仓库根，免装即跑）。
set -e
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD"
GEO="python3 -m seogeo.cli"

echo "== chinese-geo demo：内置差站 体检 → 修复 → 复检，前后分数对比 =="
$GEO demo

echo
echo "== 想看你自己的站？（联网）=="
echo "   chinese-geo audit 你的域名                    # pip install -e . 后即可用 chinese-geo 命令"
echo "   chinese-geo audit example.com --format json   # 给 agent / CI 用"
