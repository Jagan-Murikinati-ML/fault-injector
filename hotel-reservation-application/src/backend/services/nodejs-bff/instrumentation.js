// instrumentation.js
// OpenTelemetry instrumentation for Node.js BFF service
// 
// IMPORTANT: This file MUST be imported BEFORE any other imports in server.js
// This ensures that all HTTP/Express/Axios libraries are instrumented before they are used

const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// Check if tracing is enabled via environment variable
const TRACING_ENABLED = process.env.TRACING_ENABLED === 'true';

if (TRACING_ENABLED) {
  console.log('🔍 [TRACING] Initializing OpenTelemetry for nodejs-bff...');
  console.log(`📡 [TRACING] Exporting to: ${process.env.OTEL_EXPORTER_OTLP_ENDPOINT}`);

  // Create OpenTelemetry SDK
  const sdk = new NodeSDK({
    // Resource identifies this service in traces
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'nodejs-bff',
      [SemanticResourceAttributes.SERVICE_NAMESPACE]: 'hotel-reservation',
      [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
    }),
    
    // OTLP exporter sends traces to OpenTelemetry Collector
    traceExporter: new OTLPTraceExporter({
      url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT + '/v1/traces',
      headers: {},
    }),
    
    // Auto-instrumentations for common libraries
    instrumentations: [
      getNodeAutoInstrumentations({
        // HTTP/HTTPS instrumentation (incoming and outgoing requests)
        '@opentelemetry/instrumentation-http': {
          enabled: true,
          // Ignore health check endpoints
          ignoreIncomingRequestHook: (req) => {
            return req.url === '/health';
          },
        },
        // Express.js instrumentation
        '@opentelemetry/instrumentation-express': {
          enabled: true,
        },
        // Axios instrumentation (HTTP client for calling search-service)
        '@opentelemetry/instrumentation-axios': {
          enabled: true,
        },
      }),
    ],
  });

  // Start the SDK
  sdk.start();
  console.log('✅ [TRACING] OpenTelemetry initialized successfully');
  console.log('✅ [TRACING] Auto-instrumentation enabled for: HTTP, Express, Axios');

  // Graceful shutdown on process termination
  process.on('SIGTERM', () => {
    sdk.shutdown()
      .then(() => console.log('🛑 [TRACING] OpenTelemetry shut down successfully'))
      .catch((error) => console.error('❌ [TRACING] Error shutting down OpenTelemetry', error))
      .finally(() => process.exit(0));
  });
} else {
  console.log('⚠️  [TRACING] Tracing is DISABLED (TRACING_ENABLED=false)');
  console.log('⚠️  [TRACING] Set TRACING_ENABLED=true to enable distributed tracing');
}

module.exports = { TRACING_ENABLED };

