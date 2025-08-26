# Quantlink AI Driven Tools

**Quantlink AI Driven Tools** is a real-time DeFi analytics platform that detects arbitrage opportunities and executes TWAP (Time-Weighted Average Price) strategies across decentralized exchanges. It leverages live market data, price feeds, and custom execution logic to enable smarter crypto trading.

## System Architecture

The platform follows a modular architecture with distinct layers for frontend presentation, backend processing, and external integrations:

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

## Project Structure

The codebase is organized into clear separation between frontend and backend components:

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
└── README.md                 # Project documentation
```

## Core Features

**Arbitrage Detection** - The system continuously monitors price differences between multiple **DEX aggregators** using both **1inch** and **OpenOcean** price feeds to identify profitable arbitrage opportunities.

**TWAP Execution** - Implements sophisticated **Time-Weighted Average Price** strategies with interval-based trade slicing to minimize market impact and optimize execution prices.

**Live Token Analytics** - Provides comprehensive market data including real-time price feeds, liquidity depth analysis, and trading volume metrics across supported tokens.

**DEX Routing Logic** - Employs intelligent routing algorithms that consider slippage tolerance, gas costs, and profitability metrics to determine optimal execution paths.

**Modern Web Interface** - Features a responsive user interface built with **Vite** and **React** for real-time monitoring and strategy management.

## Installation Guide

### Backend Setup (Python)

Navigate to the backend directory and set up the Python environment:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Configure your API credentials
uvicorn main:app --reload
```

### Frontend Setup (React)

Initialize the frontend development environment:

```bash
cd frontend
npm install
npm run dev
```

Access the application interface at: **http://localhost:5173**

## Usage Instructions

1. Initialize the backend server using `uvicorn main:app --reload` command
2. Launch the frontend development server with `npm run dev`
3. Navigate to the application URL at `http://localhost:5173`
4. Monitor arbitrage opportunities and review TWAP execution results through the dashboard interface

## Environment Configuration

Create a `.env` file in the backend directory with the following configuration parameters:

```env
COINGECKO_API_KEY=your_coingecko_api_key
COINGECKO_BASE_URL=required_URL
QLK_CG_ID=quantlink
ETHEREUM_API_KEY=your_ethereum_api_key
ALCHEMY_API_KEY=your_alchemy_api_key
QLK_ADDRESS_ETHEREUM=0xe226B7Ae83a44Bb98F67BEA28C4ad73B0925C49E
```

## Sample Output

The system provides detailed execution logs and opportunity analysis:

```
Comparing prices for 1 ETH → USDT:
1inch: 3743.25 USDT
OpenOcean: 3741.10 USDT
Arbitrage Opportunity Detected: Buy from OpenOcean, Sell on 1inch
Potential Profit: 2.15 USDT (0.057% spread)
```

## Technical Implementation

The platform utilizes **Python FastAPI** for backend processing, implementing asynchronous request handling for optimal performance. The **React frontend** communicates through RESTful APIs, providing real-time updates via WebSocket connections when available. Market data aggregation occurs through multiple **price feed providers** to ensure accuracy and redundancy in arbitrage detection algorithms.
