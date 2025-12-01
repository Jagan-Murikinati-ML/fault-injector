// tracing.js
// Browser-side OpenTelemetry instrumentation for React Frontend
//
// This file sets up distributed tracing in the browser to track user interactions
// and HTTP requests made to the backend services.

import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { getWebAutoInstrumentations } from '@opentelemetry/auto-instrumentations-web';
import { ZoneContextManager } from '@opentelemetry/context-zone';
import { W3CTraceContextPropagator } from '@opentelemetry/core';

// Check if tracing is enabled via environment variable
// In React, environment variables must start with REACT_APP_
const TRACING_ENABLED = process.env.REACT_APP_TRACING_ENABLED === 'true';

/**
 * Initialize OpenTelemetry browser tracing
 * 
 * This function:
 * 1. Creates a WebTracerProvider for browser-side tracing
 * 2. Configures OTLP exporter to send traces to OpenTelemetry Collector
 * 3. Auto-instruments fetch() and XMLHttpRequest to inject trace headers
 * 4. Sets up W3C Trace Context propagation
 */
export const initTracing = () => {
  if (!TRACING_ENABLED) {
    console.log('⚠️  [TRACING] Browser tracing is DISABLED (REACT_APP_TRACING_ENABLED=false)');
    console.log('⚠️  [TRACING] Set REACT_APP_TRACING_ENABLED=true to enable distributed tracing');
    return;
  }

  console.log('🔍 [TRACING] Initializing OpenTelemetry for React Frontend...');

  // Create resource with service information
  const resource = new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 
      process.env.REACT_APP_OTEL_SERVICE_NAME || 'frontend',
    [SemanticResourceAttributes.SERVICE_NAMESPACE]: 'hotel-reservation',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  });

  // Create WebTracerProvider for browser tracing
  const provider = new WebTracerProvider({
    resource,
  });

  // Create OTLP exporter to send traces to OpenTelemetry Collector
  const exporter = new OTLPTraceExporter({
    url: process.env.REACT_APP_OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces',
    headers: {},
  });

  // Add BatchSpanProcessor to batch spans before sending
  provider.addSpanProcessor(new BatchSpanProcessor(exporter, {
    scheduledDelayMillis: 500, // Send every 500ms
  }));

  // Use ZoneContextManager for async context propagation
  const contextManager = new ZoneContextManager();

  // Register the provider with W3C Trace Context propagation
  provider.register({
    contextManager,
    propagator: new W3CTraceContextPropagator(),
  });

  // Auto-instrument fetch() and XMLHttpRequest
  registerInstrumentations({
    tracerProvider: provider,
    instrumentations: [
      getWebAutoInstrumentations({
        // Instrument fetch API (used by axios)
        '@opentelemetry/instrumentation-fetch': {
          enabled: true,
          // Propagate trace headers to ALL URLs (including localhost)
          propagateTraceHeaderCorsUrls: /.*/,
          // Clear timing resources to avoid memory leaks
          clearTimingResources: true,
          // Add custom attributes to spans
          applyCustomAttributesOnSpan: (span, request, result) => {
            // Add user information if available
            const user = localStorage.getItem('user');
            if (user) {
              try {
                const userData = JSON.parse(user);
                span.setAttribute('user.id', userData.id || 'unknown');
                span.setAttribute('user.email', userData.email || 'unknown');
              } catch (e) {
                // Ignore parsing errors
              }
            }
          },
        },
        // Instrument XMLHttpRequest (fallback for older code)
        '@opentelemetry/instrumentation-xml-http-request': {
          enabled: true,
          propagateTraceHeaderCorsUrls: /.*/,
        },
        // Disable document load instrumentation (not needed for SPA)
        '@opentelemetry/instrumentation-document-load': {
          enabled: false,
        },
        // Disable user interaction instrumentation (can be noisy)
        '@opentelemetry/instrumentation-user-interaction': {
          enabled: false,
        },
      }),
    ],
  });

  console.log('✅ [TRACING] OpenTelemetry initialized successfully');
  console.log(`📡 [TRACING] Exporting traces to: ${exporter.url}`);
  console.log('✅ [TRACING] Auto-instrumentation enabled for: fetch, XMLHttpRequest');
};

