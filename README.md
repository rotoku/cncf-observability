# CNCF Observability

## Iniciar Stack
```bash
docker compose up -d
```

## Visualizar os logs da Stack
```bash
docker compose logs -f
```

## Parar Stack
```bash
docker compose down -v
```

## Criar ambiente virtual e instalar dependências
```bash
cd app-python-otel
python3 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Rodar a aplicação de teste
```bash
export OTEL_SERVICE_NAME="checkout-python-app"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_EXPORTER_OTLP_INSECURE="true"
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED="true"
export OTEL_PYTHON_LOG_CORRELATION="true"
export OTEL_LOGS_EXPORTER="otlp"
export OTEL_METRICS_EXPORTER="otlp"
export OTEL_TRACES_EXPORTER="otlp"
export OTEL_METRIC_EXPORT_INTERVAL="5000" # Exporta métricas a cada 5s para facilitar o teste

opentelemetry-instrument python app.py
```

## Gerar massa para validar os logs, metrics e traces
```
for i in {1..20}; do
  curl -s http://localhost:5000/checkout
  echo ""
  sleep 0.5
done
```