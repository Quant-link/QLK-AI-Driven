# Quantlink AI Driven Tools

**Quantlink AI Driven Tools** is a real-time DeFi analytics platform that detects arbitrage opportunities and executes TWAP (Time-Weighted Average Price) and DCA (Dollar Cost Averaging) strategies across decentralized exchanges. It leverages live market data, token registries, and custom execution logic to enable smarter crypto trading.

---

## System Architecture

The platform follows a modular architecture with distinct layers for frontend presentation, backend processing, and external integrations:

```
flowchart TD
    A[Frontend (React)] -->|REST API| B[Backend (FastAPI / Python)]
    B --> C[DEX Aggregators]
    C --> C1[1inch API]
    C --> C2[OpenOcean API]
    C --> C3[0x API]
    B --> D[Market Data Providers]
    D --> D1[CoinGecko]
    D --> D2[Dexscreener]
    B --> E[Arbitrage Engine]
    B --> F[TWAP Executor]
    B --> G[DCA Executor]
    E -->|Detected Opportunities| A
    F -->|TWAP Results| A
    G -->|DCA Logs| A
```

---

## Project Structure

```
Quantlink_AI_Driven_Tools/
├── backend/
│   ├── main.py                  # Entry point for the backend API
│   ├── strategies/
│   │   ├── arbitrage_and_twap.py # Arbitrage detection & TWAP execution
│   │   ├── dca.py               # Dollar Cost Averaging strategy
│   │   ├── market_data.py       # Market data API routes
│   │   └── risk_overview.py     # Risk overview endpoints
│   ├── routing/
│   │   └── dex_clients/         # DEX client modules (1inch, 0x, OpenOcean)
│   ├── config/
│   │   ├── tokens.py            # Token registry loader / manager
│   │   └── tokens.json          # Token metadata (dynamic, incl. QLK)
│   └── utils/                   # Utilities (logging, helpers, etc.)
├── frontend/
│   ├── src/
│   │   ├── components/          # UI components (tables, cards, etc.)
│   │   ├── pages/               # Page-level components
│   │   ├── api/                 # Axios-based API functions
│   │   └── App.tsx              # Main app entry
│   └── vite.config.ts           # Vite configuration
├── .env.example                 # Sample environment variables
└── README.md                    # Project documentation
```

---

## Core Features

* **Arbitrage Detection**
  Continuously monitors price differences between **1inch, OpenOcean, SushiSwap, UniSwap & etc. and 0x** to identify profitable arbitrage opportunities.

* **TWAP Execution**
  Executes **Time-Weighted Average Price** strategies with interval-based trade slicing.

* **DCA Execution**
  Adds **Dollar Cost Averaging** plans for QLK and supported tokens, using live spot + DEX aggregator data. Supports configurable intervals (5, 10, 15 steps).

* **Live Token Analytics**
  Dynamic token registry via `tokens.json` & `tokens.py` (integrated with **Ethereum top-100 fetcher**) ensures up-to-date token addresses and decimals.

* **DEX Routing Logic**
  Incorporates slippage, gas cost, and execution speed for optimal pathfinding.

* **Modern Web Interface**
  Built with **React + Vite**, featuring responsive tables like *Recent Opportunities* with live updates.
  
---

## Installation Guide

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Fill in required API keys & addresses
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access the interface at: **[http://localhost:5173](http://localhost:5173)**

---

## Usage Instructions

1. Start backend server with:

   ```bash
   uvicorn main:app --reload
   ```
2. Launch frontend dev server with:

   ```bash
   npm run dev
   ```
3. Open `http://localhost:5173`
4. Monitor:

   * Arbitrage opportunities (real-time spreads & DEX routes)
   * TWAP strategy execution logs
   * DCA strategies (5/10/15-step plans)

---

## Environment Configuration

`.env` (backend) requires:

```env
COINGECKO_API_KEY=...
COINGECKO_BASE_URL=...
QLK_CG_ID=quantlink
QLK_ADDRESS_ETHEREUM=0xe226B7Ae83a44Bb98F67BEA28C4ad73B0925C49E
ONEINCH_API_KEY=...
ZEROX_API_KEY=...
OPENOCEAN_API_KEY=...
SIM_FROM_ADDRESS=0xYourTestWallet
SLIPPAGE_BPS=1
```

---

## Sample Output

```
Comparing USDT → QLK (via aggregators):
1inch: 4629.54 QLK
OpenOcean: 4612.33 QLK
0x: 4625.90 QLK
Arbitrage Opportunity: Buy on OpenOcean, Sell on 1inch
Potential Profit: 17.21 QLK (~$50.32)
```

---

## Technical Notes

* **Backend:** Python + FastAPI with threaded DCA/TWAP execution.
* **Token Registry:** `tokens.json` dynamically refreshed from CoinGecko & Ethereum; manual entries supported for custom tokens (e.g., QLK).
* **DEX Clients:** Live integrations with 1inch, OpenOcean, SushiSwap, UniSwap & etc. and 0x for quote & swap APIs.
* **Frontend:** React tables/cards optimized for dynamic data (fixed column widths, truncation for long addresses).

---
