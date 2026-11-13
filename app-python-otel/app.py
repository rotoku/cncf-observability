import logging
import random
import time
from flask import Flask, jsonify
from opentelemetry import metrics, trace

# Configuração básica de log (o agente OTel injetará trace_id e span_id automaticamente)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] - %(message)s",
)
logger = logging.getLogger("checkout-service")

app = Flask(__name__)

# Inicializa Tracer e Meter
tracer = trace.get_tracer("checkout.tracer", "1.0.0")
meter = metrics.get_meter("checkout.meter", "1.0.0")

# Criação das Métricas
request_counter = meter.create_counter(
    name="checkout_requests_total",
    description="Total de requisições recebidas no checkout",
    unit="1",
)

latency_histogram = meter.create_histogram(
    name="checkout_duration_ms",
    description="Tempo de processamento do checkout em milissegundos",
    unit="ms",
)


@app.route("/checkout", methods=["GET"])
def checkout():
    start_time = time.time()
    
    # Cria um span manual para representar uma regra de negócio interna
    with tracer.start_as_current_span("validar-pagamento") as span:
        # Simula latência variável entre 50ms e 400ms
        delay = random.uniform(0.05, 0.4)
        time.sleep(delay)

        # Simula 20% de chance de erro para testar alertas/filtros
        if random.random() < 0.2:
            span.set_attribute("payment.status", "failed")
            span.set_status(trace.Status(trace.StatusCode.ERROR, "Saldo insuficiente"))
            logger.error("Falha ao processar pagamento: saldo insuficiente no gateway.")
            
            duration_ms = (time.time() - start_time) * 1000
            request_counter.add(1, {"status": "error"})
            latency_histogram.record(duration_ms, {"status": "error"})
            return jsonify({"status": "error", "message": "Falha no pagamento"}), 400

        span.set_attribute("payment.status", "approved")
        logger.info("Pagamento aprovado com sucesso em %.2f ms", delay * 1000)

        duration_ms = (time.time() - start_time) * 1000
        request_counter.add(1, {"status": "success"})
        latency_histogram.record(duration_ms, {"status": "success"})

        return jsonify({"status": "approved", "latency_ms": round(duration_ms, 2)}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)