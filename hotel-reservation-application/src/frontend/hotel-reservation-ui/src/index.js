import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { initTracing } from './tracing';

// Initialize OpenTelemetry tracing BEFORE rendering the app
// This ensures all fetch/axios calls are instrumented
initTracing();

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

