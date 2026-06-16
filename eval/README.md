# Evaluation harness

The headline proof of quality. Runs a gold question set against the agent and measures
execution accuracy, SQL validity, hallucinated-column rate, grounding/faithfulness,
latency (p50/p95), and cost per query. Runs in CI as a quality gate.
