future_pred = []
symbol = "AAPL"
save_i


from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from prometheus_client import Counter, REGISTRY, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from models import PredictionRequest

prediction_counter = Counter("prediction_requests", "Count of prediction requests",["symbol"])

app = FastAPI()
Instrumentator().instrument(app).expose(app)
@app.get("/metrics")
async def metrics():
    return JSONResponse(content=generate_latest(REGISTRY))

async def save_data(symbol, future_pred):
    # Prediction Counter
    prediction_counter.labels(symbol).inc()
    # MongoDB

@app.post("/predict/")
async def predict(request: PredictionRequest):
        ## rest of the code
        save_data(symbol, future_pred)
        return {"symbol": symbol, "predictions": future_pred, "saved_id": str(saved_id)}
