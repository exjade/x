"""多账号批量注册/兑换示例。

用法: python example_batch.py [count]
读取 config.json（见 config.example.json 的批量字段），按批量调度语义运行，
结束打印 batch_summary JSON。仅供个人学习与研究使用。
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from musepy.runner import BatchRunner


def load_config(path="config.json"):
    if not os.path.exists(path):
        raise SystemExit(f"缺少配置文件 {path}，请从 config.example.json 复制并填写")
    with open(path, encoding="utf-8") as stream:
        return json.load(stream)


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    runner = BatchRunner(load_config())
    try:
        queued = runner.init(count)
    except ValueError as exc:
        raise SystemExit(f"配置不完整: {exc}")
    print(f"[i] queued={queued} workers={runner.workers} "
          f"max_per_ip={runner.max_per_ip}", flush=True)
    runner.run()
    print(json.dumps(runner.summary(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
