from fastapi import FastAPI
from routes.hotels import router
from routes.hotels import router
from instrumentation import setup_tracing

app = FastAPI(title="Hotel Search Service")

# Setup OpenTelemetry tracing (must be called before adding routes)
setup_tracing(app)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

