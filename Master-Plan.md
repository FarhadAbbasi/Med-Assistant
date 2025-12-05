# MASTER ARCHITECTURE PROMPT (SCALABLE MEDICAL ASSISTANT SAAS)

You are an expert software architect and backend engineer.
Design and help implement a highly scalable, multi-tenant medical assistant SaaS that uses open-source LLMs for clinical decision support (NOT prescribing). You will ensure architecture is scalable, maintainable, migratable, organized, and secure


Assistant's Role:
It's not a doctor, but an expert assistant. Custom trained LLM for medical diagnosis, predictions, recommendations which will not hallucinate. It will not prescribe, but will accuratley make predictions and assessments based on given patients details. It will not provide false information or recommendations. It will provide disclaimers and escalation advice. It will provide structured case summary, differential diagnoses (with uncertainty), red flags, and escalation advice + disclaimers.

Focus on:

Clean service boundaries

Horizontal scalability (1000+ concurrent users)

Replaceable LLM backbone

Queue-based workload management

Fine-tuning of LLMs

Clear separation between LLM GPU services and image/video GPU services (ComfyUI, not to be implemented yet)

## 1. Objectives (short)

Provide LLM-based medical decision support for doctors (primary) and patients (secondary), with strict safety rules:

    No prescribing or dosing.

    RAG over trusted guidelines/protocols.

    Outputs: structured case summary, differential diagnoses (with uncertainty), red flags, and escalation advice + disclaimers.

Will be Fine-tuned (LoRA, QLoRA) on custom data. 

Support multi-tenant SaaS (separate clinics/hospitals).

Handle 1000 concurrent active users with acceptable latency.

Backbone must be model-agnostic: start with Llama 3.1 (8B & 70B later), but architecture must allow swapping to other open models (e.g. future DeepSeek/Qwen/etc.) with minimal changes.

Image/video generation (via ComfyUI) is separate, optional, and must never degrade LLM performance.

## 2. Target tech stack (keep to this unless strong reason)

    Core API / Orchestration: FastAPI (Python)

    LLM Serving: vLLM (OpenAI-compatible API) on dedicated GPU pods

    Base Models: Llama 3.1 8B (dev) and 70B (prod) – instruction-tuned

    Fine-tuning: HF transformers + peft/trl (LoRA/QLoRA) – separate training pipeline (not in main request path)

    RAG / Search: Qdrant as vector DB + bge-m3 (or similar) embeddings

    Relational DB: Postgres (multi-tenant, audit, logs)

    Message / Job Queue: RabbitMQ (or Redis Streams / Kafka /Celery if you think it’s better) for managing LLM and media jobs

    Frontend: Next.js/React (doctor & patient portals)

    Containers: Docker for all services; docker-compose for dev; design so it can be moved to Kubernetes/RunPod for autoscaling

    Image/Video: ComfyUI on separate GPU pool / pods

## 3. High-level architecture (services & flows)

Design the system as multiple services:

1. API Gateway / Ingress

    Front door for all HTTP(S) traffic (users, tenants).

    Routes to core backend.

2. Core Backend Service (FastAPI)

    Stateless, horizontally scalable.

    Responsibilities:

    Auth + tenant awareness.

    Public endpoints, e.g.:

        POST /api/v1/cases/analyze

        POST /api/v1/notes/summarize

        POST /api/v1/documents/ingest

    RAG orchestration:

        Build RAG query from CaseInput.

        Query Qdrant for relevant guideline chunks.

    Build LLM job payloads (prompt + context + tenant config).

    Enqueue LLM jobs into RabbitMQ/Kafka/Celery to be processed by GPU workers (for heavier calls), OR direct-call vLLM for low-latency simple interactions.

    Apply safety/guardrail logic on outputs:

        Block prescriptions/doses.

        Ensure disclaimers and “consult a doctor” text.

    Persist to Postgres: interactions, audit logs, basic analytics.

3. LLM Worker Service(s) (GPU)

    Stateless worker processes consuming jobs from RabbitMQ/Kafka.

    Each worker:

        Reads LLM job (model name, prompt, context, streaming vs batch, tenant).

        Calls vLLM (same node or separate service) with OpenAI-compatible API.

        Returns structured output back via:

        Response queue, or

        Callback HTTP endpoint on Core Backend.

    Multiple worker pods per GPU pool → horizontally scalable.

    vLLM instance(s) run with:

        Llama 3.1 8B for dev / lightweight requests.

        Llama 3.1 70B for heavy / doctor-facing tasks.

4. vLLM Serving Service (GPU)

    Dedicated service for LLM inference.

    Exposes /v1/chat/completions.

    Deployed with autoscaling based on GPU utilization and QPS.

    Configurable MODEL_NAME and quantization; treat this as a swappable backbone.

5. Vector DB (Qdrant)

Stores guideline/protocol chunks.

Accessible from Core Backend for RAG.

6. Postgres

Stores users, tenants, sessions, case logs, LLM call metadata, etc.

7. ComfyUI Service (GPU) [Separate Pool]

    Completely separate GPU node group / pods.

    Accessed via a simple HTTP API from Core Backend when media is needed.

    Must not share GPU with LLM workers.

8. (Later) Automation Service (n8n)

Optional, not required now.

Consumes webhooks/events from Core Backend and triggers external workflows (emails, WhatsApp, Slack, etc.).

## 4. Scalability & concurrency (1000+ concurrent users)

Core Backend (FastAPI):

        Stateless; scale horizontally via multiple replicas behind load balancer.

        Use async I/O for DB and external calls.

LLM Workload:

    Low-latency “simple” chat can call vLLM directly from FastAPI (no queue) if necessary.

    Heavy or long-running analyses should:

        Be placed on RabbitMQ/Kafka.

        Processed by GPU worker pods that call vLLM.

Autoscaling:

Design so that:

    Core Backend autoscaling based on CPU/RPS.

    LLM Worker pods autoscaling based on queue depth and latency.

    vLLM pods autoscaling based on GPU utilization and request rate.

    ComfyUI pods autoscaling independently (separate GPU pool).

All services should be containerized and ready to run under:

    docker-compose in dev

    Kubernetes/RunPod (or similar) in production with HPA.

## 5. What I want you (coding assistant) to produce

Given this architecture and stack, help me:

1۔ Define clear service boundaries and APIs between:

    Core Backend ↔ LLM workers ↔ vLLM

    Core Backend ↔ Qdrant

    Core Backend ↔ Postgres

    Core Backend ↔ ComfyUI (placeholder interfaces)

2۔ Propose appropriate message formats for RabbitMQ/Kafka jobs (fields, JSON structure).

3۔ Implement initial FastAPI backend skeleton with:

    Key endpoints (/cases/analyze, etc.)

    RAG integration stubs

    LLM client stubs (for both direct vLLM calls and queued jobs)

    Safety/guardrail stubs

4۔ Provide Dockerfiles and a simple docker-compose for dev that includes:

    FastAPI

    Qdrant

    Postgres

    (Stub) LLM service

5۔ Keep the design LLM-backbone-agnostic and queue-based so we can scale to 1000+ concurrent users and swap models later.

Use concise, production-grade patterns. Focus on architecture, interfaces, and scalability, not UI polish.


Note: You will create proper documentations (.md files) of objectives, acheivemets and todos. You will keep updating the documentations as we progress.


## Temporary Dev Plan:

Will use GPU installed on this machine primarily for vLLM + LLM during dev. 

May call vLLM directly from FastAPI initially, then use LLM workers and RabbitMQ later/after-testing for scalability, but keep RabbitMQ in Docker for testing and validation.

DOcker Containers:
    vLLM + Llama 3.1 8B (GPU)
    FastAPI backend (CPU)
    Qdrant (CPU)
    Postgres (CPU)
    RabbitMQ (CPU)
