# Free Multi-Agent Demo

这是一个免费版多 agent 样机：

- Planner：规划最小任务
- Worker：执行单个任务
- Reviewer：审查结果

## 本地运行

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=你的key
python agents/run_cycle.py
```

## GitHub Actions

- 手动触发：Actions -> Free Multi-Agent Loop -> Run workflow
- 定时触发：每 15 分钟一次
