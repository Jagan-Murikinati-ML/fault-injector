"""
instrumentation.py
OpenTelemetry instrumentation setup for Python Search Service

This module sets up distributed tracing for the FastAPI application.
It can be enabled/disabled via the TRACING_ENABLED environment variable.
"""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor

# Check if tracing is enabled via environment variable
TRACING_ENABLED = os.getenv("TRACING_ENABLED", "false").lower() == "true"


def setup_tracing(app):
    """
    Setup OpenTelemetry tracing for FastAPI application
    
    This function:
    1. Creates a TracerProvider with service metadata
    2. Configures OTLP exporter to send traces to OpenTelemetry Collector
    3. Instruments FastAPI to automatically create spans for HTTP requests
    4. Instruments Elasticsearch client to trace database queries
    
    Args:
        app: FastAPI application instance
    
    Returns:
        None
    """
    if not TRACING_ENABLED:
        print("⚠️  [TRACING] Tracing is DISABLED (TRACING_ENABLED=false)")
        print("⚠️  [TRACING] Set TRACING_ENABLED=true to enable distributed tracing")
        return
    
    print("🔍 [TRACING] Initializing OpenTelemetry for search-service...")
    
    # Create resource with service information
    # This metadata will be attached to all spans
    resource = Resource(attributes={
        SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "search-service"),
        SERVICE_NAMESPACE: "hotel-reservation",
        SERVICE_VERSION: "1.0.0",
    })
    
    # Create TracerProvider with the resource
    provider = TracerProvider(resource=resource)
    
    # Create OTLP exporter to send traces to OpenTelemetry Collector
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    exporter = OTLPSpanExporter(
        endpoint=f"{otlp_endpoint}/v1/traces",
        headers={}
    )
    
    # Add BatchSpanProcessor to batch spans before sending
    # This improves performance by reducing network calls
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    
    # Set the global TracerProvider
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI application
    # This automatically creates spans for all HTTP requests
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument Elasticsearch client
    # This automatically creates spans for all Elasticsearch queries
    ElasticsearchInstrumentor().instrument()
    
    print("✅ [TRACING] OpenTelemetry initialized successfully")
    print(f"📡 [TRACING] Exporting traces to: {otlp_endpoint}")
    print("✅ [TRACING] Auto-instrumentation enabled for: FastAPI, Elasticsearch")

