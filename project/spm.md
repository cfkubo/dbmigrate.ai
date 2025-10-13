# Service Performance Monitoring (SPM) Setup

This document outlines the setup for Service Performance Monitoring (SPM) in the project, leveraging OpenTelemetry Collector, Jaeger for tracing, and Prometheus for metrics.

## 1. Implementation Details

To enable SPM, an OpenTelemetry Collector has been integrated into the development environment. The collector acts as an intermediary, receiving traces from the application, forwarding them to Jaeger, and extracting span metrics to be scraped by Prometheus.

### `config-spm.yaml`

A new configuration file, `config-spm.yaml`, has been added to the project root. This file configures the OpenTelemetry Collector with the following:

*   **Receivers**: Configured to receive OTLP (OpenTelemetry Protocol) traces via gRPC (port 4317) and HTTP (port 4318).
*   **Processors**: Uses a batch processor for efficient trace handling.
*   **Exporters**:
    *   `jaeger_storage_exporter`: Forwards traces to the Jaeger instance.
    *   `spanmetrics`: Extracts metrics from spans (e.g., latency, error rates) and exposes them.
    *   `prometheus`: Exposes the span metrics on port 8889 for Prometheus to scrape.
*   **Extensions**: Configures Jaeger query and storage, pointing to Prometheus for metrics storage.

### `gini.sh` Modifications

The `gini.sh` script has been updated to orchestrate the OpenTelemetry Collector:

*   **OpenTelemetry Collector Container**: A new Docker container named `otel-collector` is started using the `otel/opentelemetry-collector-contrib:latest` image.
*   **Configuration Mount**: The `config-spm.yaml` file is mounted into the `otel-collector` container at `/etc/otel-collector-config.yaml`, and the collector is started with this configuration.
*   **Port Mappings**: The `otel-collector` exposes ports `4317` (OTLP gRPC), `4318` (OTLP HTTP), `8888` (Prometheus metrics from collector's internal telemetry), and `8889` (Prometheus metrics from `spanmetrics` exporter).
*   **`OTEL_EXPORTER_OTLP_ENDPOINT`**: The application's `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable is now set to `http://otel-collector:4317`, directing all traces to the OpenTelemetry Collector.

## 2. How to Run the Application for Performance Monitoring

1.  **Start the environment**: Execute the `gini.sh` script from your project root:
    ```bash
    ./gini.sh
    ```
    This script will start all necessary Docker containers, including the `otel-collector`, Jaeger, and Prometheus, and then launch the API server and Gradio UI.

2.  **Access Monitoring Tools**:
    *   **Jaeger UI (Tracing)**: Open your web browser and navigate to `http://localhost:16686`. You should see traces from your application here.
    *   **Prometheus UI (Metrics)**: Open your web browser and navigate to `http://localhost:9090`. You can query for metrics exposed by the `otel-collector` (e.g., `span_metrics_calls_total`, `span_metrics_latency_bucket`).

3.  **Interact with the Application**: As you use the application (e.g., make API calls via the Gradio UI), traces and metrics will be generated and sent to the OpenTelemetry Collector, then forwarded to Jaeger and Prometheus respectively.

## 3. Troubleshooting

If you encounter issues with SPM, here are some common troubleshooting steps:

*   **OpenTelemetry Collector not starting**:
    *   Check the Docker logs for the `otel-collector` container:
        ```bash
        docker logs otel-collector
        ```
    *   Ensure there are no port conflicts.
    *   Verify that `config-spm.yaml` is correctly formatted and accessible.

*   **Traces not appearing in Jaeger**:
    *   **Verify `OTEL_EXPORTER_OTLP_ENDPOINT`**: Ensure the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable is correctly set to `http://otel-collector:4317` in the environment where your application is running.
    *   **Check Collector Logs**: Look for errors or warnings in the `otel-collector` logs that indicate issues forwarding traces to Jaeger.
    *   **Check Jaeger Logs**: Examine the Jaeger container logs for any issues receiving traces.
    *   **Network Connectivity**: Ensure the `otel-collector` and `jaeger` containers are on the same Docker network (`gini-network`).

*   **Metrics not appearing in Prometheus**:
    *   **Check Collector Logs**: Look for errors or warnings in the `otel-collector` logs related to the `spanmetrics` exporter or Prometheus exporter.
    *   **Prometheus Targets**: In the Prometheus UI (`http://localhost:9090/targets`), verify that the `otel-collector` is listed as a target and is in a "UP" state. The Prometheus configuration (`prometheus.yml`) should be set up to scrape the `otel-collector` on port `8889`.
    *   **Query Metrics**: Try querying for specific span metrics in Prometheus, such as `span_metrics_calls_total` or `span_metrics_latency_bucket`.

*   **Application not sending traces**:
    *   **`api/tracing.py`**: Ensure that `setup_tracing(app)` is correctly called in your FastAPI application's startup sequence.
    *   **Dependencies**: Verify that all OpenTelemetry-related Python dependencies are installed (`opentelemetry-sdk`, `opentelemetry-exporter-otlp`, `opentelemetry-instrumentation-fastapi`). These should be handled by `requirements.txt`.

By following these steps, you should be able to effectively monitor the performance of your application using the integrated SPM solution.
