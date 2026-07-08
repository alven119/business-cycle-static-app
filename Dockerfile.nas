FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BUSINESS_CYCLE_SERVICE_MODE=private_nas_research \
    BUSINESS_CYCLE_PUBLIC_EXPOSURE=false \
    BUSINESS_CYCLE_BIND_HOST=0.0.0.0 \
    BUSINESS_CYCLE_BIND_PORT=8000 \
    BUSINESS_CYCLE_HEALTHCHECK_URL=http://127.0.0.1:8000/healthz

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY specs ./specs
COPY docs/project_north_star.md docs/investment_cycle_product_doctrine.md \
    docs/phase_execution_standing_contract.md docs/nas_dynamic_service_architecture.md \
    ./docs/

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir .

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=5 \
    CMD python -m business_cycle.service.healthcheck

CMD ["python", "-m", "business_cycle.service.nas_runtime_server", "--host", "0.0.0.0", "--port", "8000"]
