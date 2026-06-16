# Governed Agentic Analytics Platform

A connector-based data-integration platform that ingests Australian open-government and
market data, models it in a serverless warehouse, and exposes it through a **governed,
evaluated GenAI analytics layer** — natural-language questions answered with *validated*
SQL, grounded answers, and a measured quality harness.

> Solo portfolio project demonstrating production **data engineering** + applied **AI/ML engineering** + **software engineering**.

## Why this exists
Most "chat with your data" demos cannot prove they are correct. This project pairs a real
ELT backbone with a **first-class evaluation harness** that measures answer accuracy,
grounding/faithfulness, latency, and cost per query — the difference between a demo and a
system you can trust.

## Architecture
```
Public APIs (AEMO energy, air quality)  ─┐
Batch files (CSV / Excel / XML, GCS+S3) ─┼─► Connectors ─► GCS raw (bronze) ─► BigQuery raw
                                          │
                          dbt: staging (silver) ─► marts + metrics (gold)
                                          │
                          Semantic layer (YAML)  ◄──┘
                                          │
  Next.js app ◄──► FastAPI Agent: NL ─► schema-constrained SQL ─► validate
  (chat + dashboard)                  ─► BigQuery dry-run cost guard ─► execute
                                      ─► grounded answer + citations   (traced in Langfuse)
                                          ▲
              Eval harness (gold Qs → metrics) ── runs in CI as a quality gate
```

## Stack
| Layer | Tech |
|---|---|
| Warehouse | BigQuery (serverless) |
| Lake / landing | Google Cloud Storage |
| Ingestion | Python connector framework (API + file) |
| Orchestration | Dagster |
| Transformation | dbt-core |
| Semantic layer | YAML (descriptions, metrics, joins) |
| Agent / API | FastAPI on Cloud Run |
| LLM | OpenAI |
| LLM observability | Langfuse |
| Evaluation | Custom harness (CI gate) |
| Frontend | Next.js + Tailwind + shadcn/ui (Vercel) |
| IaC / CI | Terraform · GitHub Actions |

## Repository layout
```
infra/         Terraform (GCS, BigQuery, IAM, Artifact Registry)
ingestion/     connector framework + source connectors
orchestration/ Dagster assets + schedules
transform/     dbt project (raw -> staging -> marts)
semantic/      YAML semantic models
agent/         FastAPI agent (NL->SQL, guardrails, enrichment)
eval/          evaluation harness + gold sets
web/           Next.js app (chat + dashboard)
docs/          architecture, diagrams, ADRs
```

## Status
- [x] **Phase 0** — Foundations (Terraform infra, repo, CI)
- [ ] **Phase 1** — Ingestion + orchestration
- [ ] **Phase 2** — Modelling + genericity (2 domains + file ingestion)
- [ ] **Phase 3** — Agentic core (NL->SQL, guardrails, grounding)
- [ ] **Phase 4** — Evaluation harness (CI gate)
- [ ] **Phase 5** — Web app (Next.js on Vercel)
- [ ] **Phase 6** — Polish, docs, case study

## Local development
```bash
uv sync                 # base + dev dependencies
uv run pytest           # tests
uv run ruff check .     # lint
terraform -chdir=infra init && terraform -chdir=infra plan
```

## License
MIT — see [LICENSE](LICENSE).
