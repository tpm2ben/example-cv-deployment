import logging
import random
import time
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

#  Flask app that integrates Prometheus metrics, logging, and simulates random error responses for testing:
# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests',
                        ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds',
                            'HTTP request latency in seconds',
                            ['method', 'endpoint'])


@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics."""
    logging.info("Metrics endpoint was scraped")
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


@app.route('/')
def home():
    start_time = time.time()
    logging.info(f"Handling request to {request.path} with method {request.method}")

    # Simulate random error with 20% chance
    if random.random() < 0.2:
        error_msg = "Simulated random error for testing"
        logging.error(error_msg)
        # Record metrics for error response
        REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status=500).inc()
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(duration)
        response = jsonify({'error': error_msg})
        response.status_code = 500
        return response

    # Normal successful response
    result = "Hello, World!"
    duration = time.time() - start_time
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(duration)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status=200).inc()

    logging.info(f"Request handled in {duration:.6f} seconds, response: {result}")
    return result


if __name__ == '__main__':
    app.run(port=8080)
