from fastapi import FastAPI
from routes.hotels import router

app = FastAPI(title="Hotel Search Service")
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

