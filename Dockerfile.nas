FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BUSINESS_CYCLE_SERVICE_MODE=private_nas_research \
    BUSINESS_CYCLE_PUBLIC_EXPOSURE=false \
    BUSINESS_CYCLE_BIND_HOST=0.0.0.0 \
    BUSINESS_CYCLE_BIND_PORT=8000 \
    BUSINESS_CYCLE_HEALTHCHECK_URL=http://127.0.0.1:8000/healthz

WORKDIR /app

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install --no-install-recommends --yes ca-certificates curl \
    && install -d /usr/share/postgresql-common/pgdg \
    && curl --fail --silent --show-error \
        --output /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
        https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
        > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install --no-install-recommends --yes postgresql-client-16 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY specs ./specs
COPY docs/project_north_star.md docs/investment_cycle_product_doctrine.md \
    docs/phase_execution_standing_contract.md docs/nas_dynamic_service_architecture.md \
    docs/nas_v1_operator_runbook.md docs/product_alignment_cleanup_plan_phase127.md \
    docs/product_alignment_cleanup_plan_phase128.md \
    docs/product_alignment_cleanup_plan_phase129.md \
    docs/product_alignment_cleanup_plan_phase130.md \
    docs/full_cycle_state_portfolio_roadmap_phase129_133.md \
    ./docs/

RUN mkdir -p /usr/local/lib/python3.10/specs /usr/local/lib/python3.10/docs \
    && cp -a /app/specs/. /usr/local/lib/python3.10/specs/ \
    && cp -a /app/docs/. /usr/local/lib/python3.10/docs/ \
    && cp /app/pyproject.toml /usr/local/lib/python3.10/pyproject.toml \
    && cp /app/README.md /usr/local/lib/python3.10/README.md

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir .

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=5 \
    CMD python -m business_cycle.service.healthcheck

CMD ["python", "-m", "business_cycle.service.nas_runtime_server", "--host", "0.0.0.0", "--port", "8000"]
