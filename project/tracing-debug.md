# Debugging OpenTelemetry Tracing Setup

This document outlines the step-by-step process used to debug and resolve issues in the OpenTelemetry tracing pipeline.

---

### Issue 1: Invalid 'jaeger' Exporter in OpenTelemetry Collector

*   **Symptom**: The `otel-collector` container would exit immediately after starting. Logs showed the error: `'exporters' unknown type: "jaeger"`.
*   **Root Cause**: The version of the OpenTelemetry Collector being used no longer includes a native `jaeger` exporter. Traces should be sent to Jaeger using the standard OpenTelemetry Protocol (OTLP).
*   **Resolution**: Modified `otel-collector-config.yaml` to replace the `jaeger` exporter with an `otlp` exporter pointing to the Jaeger container (`jaeger:4317`).

    **Before:**
    ```yaml
    exporters:
      jaeger:
        endpoint: localhost:14250
        tls:
          insecure: true
    ```

    **After:**
    ```yaml
    exporters:
      otlp:
        endpoint: jaeger:4317
        tls:
          insecure: true
    ```

---


### Issue 2: Deprecated 'logging' Exporter

*   **Symptom**: After fixing the exporter type, the `otel-collector` still failed. Logs showed the error: `'exporters' the logging exporter has been deprecated, use the debug exporter instead`.
*   **Root Cause**: The `logging` exporter has been replaced by the `debug` exporter for printing telemetry data to the console.
*   **Resolution**: Modified `otel-collector-config.yaml` to replace the `logging` exporter with the `debug` exporter.

    **Before:**
    ```yaml
    exporters:
      # ...
      logging:
        loglevel: debug
    
    service:
      pipelines:
        traces:
          exporters: [otlp, logging]
    ```

    **After:**
    ```yaml
    exporters:
      # ...
      debug:
        verbosity: detailed

    service:
      pipelines:
        traces:
          exporters: [otlp, debug]
    ```

---


### Issue 3: Application Failing to Connect (StatusCode.UNAVAILABLE)

*   **Symptom**: The Python application logs showed `Failed to export traces to localhost:4317, error code: StatusCode.UNAVAILABLE`.
*   **Root Cause**: The application was running on the host, but the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable in `gini.sh` was set to `http://localhost:4317`. The `http://` prefix can confuse the OTLP gRPC exporter, which expects the endpoint in a `hostname:port` format.
*   **Resolution**: Removed the `http://` prefix from the environment variable in `gini.sh`.

    **Before:**
    ```bash
    export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
    ```

    **After:**
    ```bash
    export OTEL_EXPORTER_OTLP_ENDPOINT="localhost:4317"
    ```

---


### Issue 4: Manual `curl` Fails and No Collector Logs

*   **Symptom**: A manual `curl` command to the collector's HTTP port (`4318`) resulted in an `Empty reply from server`. Critically, no new logs appeared in the `otel-collector`, indicating the request never reached the application.
*   **Root Cause**: The collector logs revealed it was binding its listeners to `127.0.0.1` (localhost) *inside* the container. For Docker's port mapping to work, the service must bind to `0.0.0.0` (all interfaces).
*   **Resolution**: Modified `otel-collector-config.yaml` to explicitly define the receiver endpoints and bind them to `0.0.0.0`.

    **Before:**
    ```yaml
    receivers:
      otlp:
        protocols:
          grpc:
          http:
    ```

    **After:**
    ```yaml
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    ```

---


### Manual Validation with a Sample Span

To confirm that the OpenTelemetry Collector is receiving data and forwarding it to Jaeger, you can send a single, minimal trace payload directly to the collector's HTTP endpoint.

This `curl` command sends a JSON payload that represents a single span. This is useful for ensuring the collector is running and correctly configured to receive OTLP/HTTP requests.

```bash
curl -X POST -H "Content-Type: application/json" http://localhost:4318/v1/traces -d \
'{
  "resource_spans": [
    {
      "resource": {
        "attributes": [
          {
            "key": "service.name",
            "value": {
              "stringValue": "manual-test-service"
            }
          }
        ]
      },
      "scope_spans": [
        {
          "scope": {},
          "spans": [
            {
              "trace_id": "0102030405060708090a0b0c0d0e0f10",
              "span_id": "1112131415161718",
              "name": "manual-test-span",
              "kind": "SPAN_KIND_SERVER",
              "start_time_unix_nano": "1700000000000000000",
              "end_time_unix_nano": "1700000001000000000",
              "attributes": [],
              "status": {
                "code": "STATUS_CODE_OK"
              }
            }
          ]
        }
      ]
    }
  ]
}'
```

*   **How to Verify:**
    1.  Run the `curl` command above.
    2.  Open the Jaeger UI in your browser (usually at `http://localhost:16686`).
    3.  In the "Search" tab, select `manual-test-service` from the "Service" dropdown.
    4.  Click "Find Traces".

If the command was successful, you will see a trace named `manual-test-span` in the results. This confirms that your OpenTelemetry Collector is correctly receiving traces via HTTP and exporting them to Jaeger.


### Testing with curl

While debugging, we didn't use `curl` to directly test the OpenTelemetry collector. Instead, we used `curl` to send requests to the application's API endpoints and then observed the resulting traces in Jaeger to confirm that the tracing pipeline was working correctly.

Here are the `curl` commands that were used to test the application:

**1. Start a Conversion Job**

This command sends a POST request to the `/convert` endpoint to start a new database schema conversion job.

```bash
curl -X POST http://127.0.0.1:8000/convert \
-H "Content-Type: application/json" \
-d 
'{
    "oracle_db_url": "oracle://user:password@host:port/service",
    "postgres_db_url": "postgresql://user:password@host:port/database",
    "schemas": ["schema1", "schema2"]
}'
```

*   **How it worked for debugging:** After running this command, we would check the application logs to see if the request was received and a job ID was created. Then, we would go to the Jaeger UI to find the trace for this request. A successful trace would show spans from the FastAPI application, the database interactions, and the message being sent to the RabbitMQ queue.

**2. Check Job Status**

This command sends a GET request to the `/jobs/job/{job_id}` endpoint to check the status of a conversion job. Replace `{job_id}` with the actual job ID returned from the `/convert` request.

```bash
curl -X GET http://127.0.0.1:8000/jobs/job/{job_id}
```

*   **How it worked for debugging:** This command helped us verify that the job was created and that we could retrieve its status. In Jaeger, we could see the trace for this request and confirm that it was being handled correctly by the application.

These `curl` commands were successful in helping us test the application and verify that the tracing was working end-to-end.

---


### Key Takeaways

1.  **Check Exporter Names**: OpenTelemetry Collector components can be renamed or deprecated. Always check your collector version's documentation for valid component names.
2.  **OTLP is Standard**: When exporting to modern observability backends like Jaeger, prefer the `otlp` exporter.
3.  **Mind the Protocol Scheme**: OTLP gRPC exporters often expect `hostname:port`, and adding a protocol scheme like `http://` can cause connection failures.
4.  **Bind to `0.0.0.0` in Docker**: A service in a Docker container must bind to `0.0.0.0` to be accessible from the host via mapped ports. Binding to `127.0.0.1` restricts access to within the container itself.
