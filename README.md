# ⚡ Quantlink AI Driven Tools

**Quantlink AI Driven Tools** is a real-time DeFi analytics platform that detects arbitrage opportunities and executes TWAP (Time-Weighted Average Price) strategies across decentralized exchanges. It leverages live market data, price feeds, and custom execution logic to enable smarter crypto trading.

---

## 🧠 System Architecture

```
flowchart TD
    A[Frontend (React)] -->|REST API| B[Backend (Python)]
    B --> C[DEX Aggregators]
    C --> C1[1inch API]
    C --> C2[OpenOcean API]
    B --> D[Market Data Providers]
    D --> D1[CoinGecko]
    D --> D2[Dexscreener]
    B --> E[Arbitrage Engine]
    B --> F[TWAP Executor]
    E -->|Detected Opportunities| A
    F -->|TWAP Results| A
```

---

## 📁 Project Structure

```
Quantlink_AI_Driven_Tools/
├── backend/
│   ├── main.py                # Entry point for the backend API
│   ├── arbitrage_and_twap.py # Arbitrage detection & TWAP execution
│   ├── utils/
│   │   ├── dex_clients/       # 1inch & OpenOcean client modules
│   │   ├── token_loader.py    # Token metadata and symbol mapping
│   │   └── logger.py          # Logging configuration
│   └── config/
│       └── tokens.json        # Top 100 token info
├── frontend/
│   ├── src/
│   │   ├── components/        # UI components (tables, filters, etc.)
│   │   ├── pages/             # Page-level components
│   │   ├── api/               # Axios-based API functions
│   │   └── App.tsx           # Main app entry
│   └── vite.config.ts        # Vite configuration
├── .env.example              # Sample environment variables
└── README.md                 # You're here!
```

---

## 🔧 Features

* ✅ **Arbitrage Detection** using 1inch and OpenOcean price feeds
* ⏱️ **TWAP Execution** with interval-based trade slicing
* 📊 **Live Token Analytics** including price, liquidity, and volume
* 🔄 **DEX Routing Logic** based on slippage and profitability
* 🌐 **Modern Web UI** powered by Vite and React

---

## 🚀 Installation

### Backend (Python)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Fill in your API keys
uvicorn main:app --reload
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Open the app in your browser at:
👉 [http://localhost:5173](http://localhost:5173)

---

## 🧪 Usage

1. Start the backend with `uvicorn main:app --reload`
2. Start the frontend with `npm run dev`
3. Navigate to `http://localhost:5173`
4. View arbitrage opportunities and TWAP execution results in real-time

---

## 🌍 Environment Variables

`.env` file (for backend):

```env
ONEINCH_API_KEY=your_1inch_api_key
OPENOCEAN_API_KEY=your_openocean_api_key
DEXTOOLS_API_KEY=your_dextools_api_key
COINGECKO_URL=https://api.coingecko.com
```

---

## 📸 Sample Output

```
🔍 Comparing prices for 1 ETH → USDT:
1inch: 3743.25 USDT
OpenOcean: 3741.10 USDT
✅ Arbitrage Opportunity: Buy from OpenOcean, Sell on 1inch
```

---
---


