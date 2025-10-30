import os
import random
import math
import datetime as dt
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# Allow frontend origin only
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://xedni-sandbox.vercel.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"]
)

# ---------- Models ----------
class GenerateRequest(BaseModel):
    ticker: str = "FAKE"
    days: int = 100
    start_price: float = 50.0


class BacktestRequest(BaseModel):
    prices: list[float]
    short_window: int = 5
    long_window: int = 20


# ---------- Endpoints ----------
@app.get("/")
def root():
    return {"message": "Trading Playground API is running"}


# Generate fake stock data using geometric Brownian motion
@app.post("/generate")
def generate(req: GenerateRequest):
    
    random.seed(27)  # reproducible for testing
    ds = 1 / 252  # daily steps
    mu = 0.05     # drift
    sigma = 0.2   # volatility

    prices = [req.start_price]
    for _ in range(req.days - 1):
        shock = random.normalvariate((mu - 0.5 * sigma**2) * ds,
                                      sigma * math.sqrt(ds))
        prices.append(prices[-1] * math.exp(shock))

    ## Build a fake OHLC dataframe
    dates = [dt.datetime.today() - dt.timedelta(days=i) for i in range(req.days)]
    dates = list(reversed(dates))

    df = []
    for i in range(len(dates)):
        high = prices[i] * (1 + random.uniform(0, 0.02))
        low = prices[i] * (1 - random.uniform(0, 0.02))
        df.append({
            "date": dates[i],
            "open": prices[i],
            "high": high,
            "low": low,
            "close": random.uniform(low, high),
            "volume": random.randint(1000, 5000)
        })

    return df

# Generate fake stock data using Box-Muller transformation
@app.post("/v2/generate")
def generate(req: GenerateRequest):
    
    rachels_age = (datetime.now() - datetime(1997, 12, 6)).seconds
    random.seed(rachels_age)  # reproducible for testing

    ds = 1 / 252  # daily steps
    mu = 0.001  # mean
    theta = 0.02   # standard deviation

    prices = [req.start_price]
    for _ in range(req.days - 1):
        u1 = 1.0 - random.random()
        u2 = 1.0 - random.random()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        z1 = mu + theta * z0
        prices.append(prices[-1] * math.exp(z1))

    ## Build a fake OHLC dataframe
    dates = [dt.datetime.today() - dt.timedelta(days=i) for i in range(req.days)]
    dates = list(reversed(dates))

    df = []
    for i in range(len(dates)):
        high = prices[i] * (1 + random.uniform(0, 0.02))
        low = prices[i] * (1 - random.uniform(0, 0.02))
        df.append({
            "date": dates[i],
            "open": prices[i],
            "high": high,
            "low": low,
            "close": random.uniform(low, high),
            "volume": random.randint(1000, 5000)
        })

    return df

# Simple moving average crossover strategy, just to start
# Buy when short MA crosses above long MA, sell when it crosses below
@app.post("/backtest")
def backtest(req: BacktestRequest):
    return {"message": "Backtesting is currently disabled."}

@app.get("/health")
def health():
    return {"status": "healthy"}