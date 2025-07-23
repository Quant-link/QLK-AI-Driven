import requests
import time

TOKEN_INFO = {
    "eth": {
        "address": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        "decimals": 18,
    },
    "usdt": {
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "decimals": 6,
    },
    "usdc": {
        "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "decimals": 6,
    },
    "btc": {
        "address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "decimals": 8,
    },
    "link": {
        "address": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        "decimals": 18
    },
    "uni": {
        "address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "decimals": 18
    },
    "dai": {
        "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "decimals": 18
    },
    "aave": {
        "address": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        "decimals": 18
    },
    "weth": {
        "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "decimals": 18,
    },
    "snx": {
        "address": "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F",
        "decimals": 18,
    },
    "comp": {
        "address": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
        "decimals": 18,
    },
    "mkr": {
        "address": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
        "decimals": 18,
    },
    "crv": {
        "address": "0xD533a949740bb3306d119CC777fa900bA034cd52",
        "decimals": 18,
    },
    "bal": {
        "address": "0xba100000625a3754423978a60c9317c58a424e3D",
        "decimals": 18,
    },
    "1inch": {
        "address": "0x111111111117dC0aa78b770fA6A738034120C302",
        "decimals": 18,
    },
    "chz": {
        "address": "0x3506424F91fD33084466F402d5D97f05F8e3b4AF",
        "decimals": 18,
    },
    "enj": {
        "address": "0xF629cBd94d3791C9250152BD8dfBDF380E2a3B9c",
        "decimals": 18,
    },
    "mana": {
        "address": "0x0F5D2fB29fb7d3CFeE444a200298f468908cC942",
        "decimals": 18,
    },
    "sand": {
        "address": "0x3845badAde8e6dFF049820680d1F14bD3903a5d0",
        "decimals": 18,
    },
    "axs": {
        "address": "0xBB0E17EF65F82Ab018d8EDd776e8DD940327B28b",
        "decimals": 18,
    },
    "sushi": {
        "address": "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",
        "decimals": 18,
    },
    "yfi": {
        "address": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
        "decimals": 18,
    },
    "bat": {
        "address": "0x0D8775F648430679A709E98d2b0Cb6250d2887EF",
        "decimals": 18,
    },
    "zrx": {
        "address": "0xE41d2489571d322189246DaFA5ebDe1F4699F498",
        "decimals": 18,
    },
    "gusd": {
        "address": "0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd",
        "decimals": 2,
    },
    "rai": {
        "address": "0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919",
        "decimals": 18,
    },
    "frax": {
        "address": "0x853d955aCEf822Db058eb8505911ED77F175b99e",
        "decimals": 18,
    },
    "fei": {
        "address": "0x956F47F50A910163D8BF957Cf5846D573E7f87CA",
        "decimals": 18,
    },
    "alusd": {
        "address": "0xA74d4B67b3368E83797a35382AFB776bAAE4F5C8",
        "decimals": 18,
    },
    "susd": {
        "address": "0x57Ab1ec28D129707052df4dF418D58a2D46d5f51",
        "decimals": 18,
    },
    "lusd": {
        "address": "0x5f98805a4e8be255a32880fdec7f6728c6568ba0",
        "decimals": 18,
    },
    "usdp": {
        "address": "0x1456688345527bE1f37E9e627DA0837D6f08C925",
        "decimals": 18,
    },
    "tusd": {
        "address": "0x0000000000085d4780B73119b644AE5ecd22b376",
        "decimals": 18,
    },
    "husd": {
        "address": "0xdF574c24545E5FfEcb9a659c229253D4111d87e1",
        "decimals": 8,
    },
    "dola": {
        "address": "0x865377367054516e17014CcdED1e7d814EDC9ce4",
        "decimals": 18,
    },
    "musd": {
        "address": "0x3f24E1d7a973867fC2A03fE199E5502514E0e11E",
        "decimals": 18,
    },
    "ousd": {
        "address": "0x2A8e1E676Ec238d8A992307B495b45B3fEAa5e86",
        "decimals": 18,
    },
    "usdx": {
        "address": "0xf3527ef8dE265eAa3716FB312c12847bFBA66Cef",
        "decimals": 6,
    },
    "usds": {
        "address": "0xdC035D45d973E3EC169d2276DDab16f1e407384F",
        "decimals": 18,
    },
    "usnbt": {
        "address": "0xA56585d7F8F4D96eFe4449402E650B60336aeC9a",
        "decimals": 4,
    },
    "usn": {
        "address": "0x65666d1B3a40412a9849641f17e41e631509929d",
        "decimals": 18,
    },
    "xsgd": {
        "address": "0x70e8de73ce538da2beed35d14187f6959a8eca96",
        "decimals": 6,
    },
    "vai": {
        "address": "0xD13cfD3133239a3c73a9E535A5c4DadEE36b395c",
        "decimals": 18,
    },
    "usdd": {
        "address": "0x3D7975EcCFc61a2102b08925CbBa0a4D4dBB6555",
        "decimals": 18,
    },
    "eurt": {
        "address": "0xC581b735A1688071A1746c968e0798D642EDE491",
        "decimals": 6,
    },
    "xaut": {
        "address": "0x68749665FF8D2d112Fa859AA293F07A622782F38",
        "decimals": 6,
    },
    "paxg": {
        "address": "0x45804880De22913dAFE09f4980848ECE6EcbAf78",
        "decimals": 18,
    },
    "spell": {
        "address": "0x090185f2135308BaD17527004364eBcC2D37e5F6",
        "decimals": 18,
    },
    "joe": {
        "address": "0x76e222b07C53D28b89b0bAc18602810Fc22B49A8",
        "decimals": 18,
    },
    "floki": {
        "address": "0xcf0C122c6b73ff809C693DB761e7BaeBe62b6a2E",
        "decimals": 9,
    },
    "wbtc": {
        "address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "decimals": 8,
    },
    "reth": {
        "address": "0xBfedbcbe27171C418CDabC2477042554b1904857",
        "decimals": 18,
    },
    "steth": {
        "address": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
        "decimals": 18,
    },
    "wsteth": {
        "address": "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
        "decimals": 18,
    },
    "ankreth": {
        "address": "0x132d8D2C76Db3812403431fAcB00F3453Fc42125",
        "decimals": 18,
    },
    "cbeth": {
        "address": "0xBe9895146f7AF43049ca1c1AE358B0541Ea49704",
        "decimals": 18,
    },
    "sfrxeth": {
        "address": "0xac3E018457B222d93114458476f3E3416Abbe38F",
        "decimals": 18,
    },
    "frxeth": {
        "address": "0x4a4eF6Be54d2666A6D56cf861de7AB3D150a20b6",
        "decimals": 18,
    },
    "crvusd": {
        "address": "0x0655977FEb2f289A4aB78af67BAB0d17aAb84367",
        "decimals": 18,
    },
    "susde": {
        "address": "0x1605A410c8480A18A3e958fAFF3b6D2834fbae22",
        "decimals": 18,
    },
    "gohm": {
        "address": "0x0ab87046fBb341D058F17CBC4c1133F25a20a52f",
        "decimals": 18,
    },
    "cvx": {
        "address": "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B",
        "decimals": 18,
    },
    "lido": {
        "address": "0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1",
        "decimals": 18,
    },
    "ankr": {
        "address": "0x8290333ceF9e6D528dD5618Fb97a76f268f3EDD4",
        "decimals": 18,
    },
    "rocket": {
        "address": "0xD33526068D116cE69F19A9ee46F0bd304F21A51f",
        "decimals": 18,
    },
    "metis": {
        "address": "0x9E32b13ce7f2E80A01932B42553652E053D6ed8e",
        "decimals": 18,
    },
    "boba": {
        "address": "0x42bBFa2e77757C645eeaAd1655E0911a7553Efbc",
        "decimals": 18,
    },
    "arbitrum": {
        "address": "0xB50721BCf8d664c30412Cfbc6cf7a15145234ad1",
        "decimals": 18,
    },
    "optimism": {
        "address": "0x562E362876c8Aee4744FC2c6aaC8394C312d215d",
        "decimals": 18,
    },
    "zksync": {
        "address": "0xabea9132b05a70803a4e85094fd0e1800777fbef", 
        "decimals": 18,
    },
    "linea": {
        "address": "0xD30518A0319DD2BF08565f51e39a01cFa5202565", 
        "decimals": 18,
    },
    "base": {
        "address": "0x07150e919B4De5fD6a63DE1F9384828396f25fDC", 
        "decimals": 18,
    },
    "scroll": {
        "address": "0x8f33F87F8a71F9eD1f5BD456c142e18394BB3436",
        "decimals": 18,
    },
    "mantle": {
        "address": "0x3c3a81e81dc49A522A592e7622A7E711c06bf354",
        "decimals": 18,
    },
    "moonbeam": {
        "address": "0x017bE64db48dfc962221c984b9A6937A5d09E81A",
        "decimals": 18,
    },
    "aurora": {
        "address": "0xAaAAAA20D9E0e2461697782ef11675f668207961",
        "decimals": 18,
    },
    "polygon": {
        "address": "0x455e53CBB86018Ac2B8092FdCd39d8444aFFC3F6",
        "decimals": 18,
    },
    "bsc": {
        "address": "0x095418A82BC2439703b69fbE1210824F2247D77c",
        "decimals": 18,
    },
    "avalanche": {
        "address": "0x1CE0c2827e2eF14D5C4f29a091d735A204794041",
        "decimals": 18,
    },
    "fantom": {
        "address": "0xAD29AbB318791D579433D831ed122aFeAf29dcfe",
        "decimals": 18,
    },
    "harmony": {
        "address": "0x03fF0ff224f904be3118461335064bB48Df47938",
        "decimals": 18,
    },
    "celo": {
        "address": "0x3294395e62F4eB6aF3f1Fcf89f5602D90Fb3Ef69",
        "decimals": 18,
    },
    "heco": {
        "address": "0xA929022c9107643515F5c777cE9a910F0D1e490C",
        "decimals": 18,
    },
    "kava": {
        "address": "0x0C356B7fD36a5357E5A017EF11887ba100C9AB76",
        "decimals": 6,
    },
    "okex": {
        "address": "0x6cC5F688a315f3dC28A7781717a9A798a59fDA7b",
        "decimals": 18,
    },
    "klaytn": {
        "address": "0x4d35e0963c7dbfcc3a9ab2f0dbf99810f75983e5",
        "decimals": 18,
    },
    "near": {
        "address": "0x85F17Cf997934a597031b2E18a9aB6ebD4B9f6a4",
        "decimals": 24,
    },
    "solana": {
        "address": "0xDE9B56f3Bb816f37b4F1b5081058465ed57826A3",
        "decimals": 9,
    },
    "terra": {
        "address": "0xeC9C84D7404C36C2Db463BbcAAFA1dc80a144568",
        "decimals": 6,
    },
    "tron": {
        "address": "0x50327c6c5a14DCaDE707ABad2E27eB517df87AB5",
        "decimals": 6,
    },
    "algorand": {
        "address": "0x5D55058185314e2f80f3D5B2f82f7358c7e82079",
        "decimals": 6,
    },
    "icp": {
        "address": "0x7a1B3b2BfB687A26328E623441eDaEA69Df3deF5",
        "decimals": 8,
    },
    "filecoin": {
        "address": "0x421Bec905240b252EaE78Ebd59484158A3c28B8D",
        "decimals": 18,
    },
    "theta": {
        "address": "0x3883f5e181fccaF8410FA61e12b59BAd963fb645",
        "decimals": 18,
    },
    "elrond": {
        "address": "0xe3fb646fC31Ca12657B17070bC31a52E323b8543",
        "decimals": 18,
    },
    "hive": {
        "address": "0x895f5D0b8456B980786656A33f21642807D1471c",
        "decimals": 3,
    },
    "ocean": {
        "address": "0x967da4048cD07aB37855c090aAF366e4ce1b9F48",
        "decimals": 18,
    },
}

STABLES = ["USDT", "USDC", "DAI"]
SEARCH_TIMEOUT = 10
RATE_LIMIT_PAUSE = 0.2

def _search_dexscreener(q: str) -> list[dict]:
    resp = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={q}", timeout=SEARCH_TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("pairs", [])

def resolve_pair_address(address: str, stable: str) -> dict:
    """
    İlk önce sözleşme adresiyle arama yapar, quoteToken==stable olan havuzları alır,
    likiditeye göre en büyük bulur.
    """
    pairs = _search_dexscreener(address)
    matches = [p for p in pairs if p.get("quoteToken",{}).get("symbol","").upper()==stable]
    if not matches:
        raise ValueError(f"No {stable} pool for {address}")
    best = max(matches, key=lambda p: p["liquidity"]["usd"])
    return {"chain": best["chainId"], "pair_address": best["pairAddress"], "liquidity": best["liquidity"]["usd"]}


def resolve_pair_symbol(symbol: str, stable: str) -> dict:
    """
    Adreste bulamadıysak sembolle arama yapar, quoteToken==stable en yüksek havuzu döner.
    """
    pairs = _search_dexscreener(symbol)
    matches = [p for p in pairs if p.get("quoteToken",{}).get("symbol","").upper()==stable]
    if not matches:
        raise ValueError(f"No {stable} pool for symbol {symbol}")
    best = max(matches, key=lambda p: p["liquidity"]["usd"])
    return {"chain": best["chainId"], "pair_address": best["pairAddress"], "liquidity": best["liquidity"]["usd"]}


def resolve_best_any(address: str) -> dict:

    pairs = _search_dexscreener(address)
    if not pairs:
        raise ValueError(f"No pools at all for {address}")
    best = max(pairs, key=lambda p: p["liquidity"]["usd"])
    return {"chain": best["chainId"], "pair_address": best["pairAddress"], "liquidity": best["liquidity"]["usd"]}


def fetch_all_liquidities() -> list[dict]:
    results = []
    for sym, info in TOKEN_INFO.items():
        addr = info["address"]
        result = None

        for stable in STABLES:
            try:
                result = resolve_pair_address(addr, stable)
                break
            except Exception:
                pass

        if result is None:
            for stable in STABLES:
                try:
                    result = resolve_pair_symbol(sym, stable)
                    break
                except Exception:
                    pass

        if result is None:
            try:
                result = resolve_best_any(addr)
            except Exception:
                result = {"chain": None, "pair_address": None, "liquidity": 0.0}

        results.append({
            "symbol":    sym.upper().ljust(8),
            "chain":     str(result["chain"] or "—").ljust(12),
            "pair":      result["pair_address"] or "No pool",
            "liquidity": result["liquidity"],
        })

        time.sleep(RATE_LIMIT_PAUSE)

    return sorted(results, key=lambda x: x["liquidity"])


if __name__ == "__main__":
    for t in fetch_all_liquidities():
        print(f"{t['symbol']} → chain {t['chain']}, pair {t['pair']}, liq ${t['liquidity']:,.2f}")