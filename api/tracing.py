import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_tracing(app):
    # Service name can be configured via environment variable or hardcoded
    service_name = "spf-converter-api"

    resource = Resource.create(attributes={
        "service.name": service_name,
        "service.instance.id": "instance-1" # You might want to make this dynamic
    })

    # Set up the TracerProvider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Configure OTLP exporter
    # The endpoint is the address of the OpenTelemetry Collector
    # It's configured via the OTEL_EXPORTER_OTLP_ENDPOINT environment variable
    otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
