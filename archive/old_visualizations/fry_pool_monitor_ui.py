#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRY Cross-DEX Pool Monitor (CLI)
--------------------------------
Monitors FRY-related pools across various DEXes. Pools may be simulated if they
don't exist yet. Useful for concept validation and demo.

Usage:
    python core/fry_pool_monitor_ui.py

Features:
- Simulated discovery of FRY pools across DEXes
- Periodic refresh of metrics (TVL, APY, Funding, Backing, Efficiency)
- Filter by DEX or Asset
- Export current snapshot to JSON
- Clean, readable CLI layout using FRY color scheme
"""

import sys
import time
import json
import random
from datetime import datetime
from typing import List, Dict

FRY_RED = "\033[91m"
FRY_YELLOW = "\033[93m"
FRY_BLACK = "\033[30m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

DEXES = [
    "Hyperliquid", "dYdX", "Uniswap v3", "Sushi", "GMX", "Raydium", "Osmosis", "BaseDEX"
]

ASSETS = [
    "$dydx", "$HYPE", "$ETH", "$BTC", "$USDC", "$FRY"
]

# Seed pools (some simulated, some hypothetical)
SEED_POOLS = [
    {"dex": "dYdX", "pair": "FRY-$dydx", "native": True, "exists": False},
    {"dex": "Hyperliquid", "pair": "FRY-USD", "native": False, "exists": False},
    {"dex": "Uniswap v3", "pair": "FRY-$dydx", "native": True, "exists": False},
    {"dex": "Uniswap v3", "pair": "FRY-$USDC", "native": False, "exists": False},
    {"dex": "GMX", "pair": "FRY-$ETH", "native": False, "exists": False},
    {"dex": "Raydium", "pair": "FRY-SOL", "native": False, "exists": False},
    {"dex": "Osmosis", "pair": "FRY-OSMO", "native": False, "exists": False},
]


def _rand_walk(prev: float, vol: float, lo: float, hi: float) -> float:
    """Bounded random walk for metric simulation."""
    step = random.uniform(-vol, vol)
    val = max(lo, min(hi, prev * (1.0 + step)))
    return val


def _init_metrics() -> Dict:
    tvl = random.uniform(50_000, 2_000_000)
    apy = random.uniform(0.05, 0.45)  # 5% - 45%
    funding = random.uniform(-0.10, 0.10)  # -10% to +10%
    backing = random.uniform(0.40, 0.85)
    efficiency = random.uniform(1.5, 10.0)
    return {
        "tvl": tvl,
        "apy": apy,
        "funding": funding,
        "backing": backing,
        "efficiency": efficiency,
        "exists": random.random() < 0.2  # 20% chance currently exists
    }


def _format_money(x: float) -> str:
    return "$" + f"{x:,.0f}"


def _format_pct(x: float) -> str:
    return f"{x*100:.1f}%"


def _format_ratio(x: float) -> str:
    return f"{x:.1f}x"


def _header(title: str) -> None:
    print()
    print(FRY_RED + BOLD + title + RESET)
    print(DIM + ("-" * len(title)) + RESET)


def _print_table(rows: List[List[str]], headers: List[str]) -> None:
    col_widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            col_widths[i] = max(col_widths[i], len(cell))
    fmt = "  ".join("{:<" + str(w) + "}" for w in col_widths)
    print(BOLD + fmt.format(*headers) + RESET)
    print("  ".join("-" * w for w in col_widths))
    for r in rows:
        print(fmt.format(*r))


class FRYPoolMonitor:
    def __init__(self):
        self.pools: List[Dict] = []
        for p in SEED_POOLS:
            m = _init_metrics()
            self.pools.append({**p, **m})
        self.last_refresh = datetime.utcnow()
        self.filter_dex: str = "ALL"
        self.filter_asset: str = "ALL"

    def refresh(self) -> None:
        # Random walk update
        for p in self.pools:
            p["tvl"] = _rand_walk(p["tvl"], 0.10, 10_000, 5_000_000)
            p["apy"] = max(0.0, min(0.60, _rand_walk(p["apy"], 0.15, 0.00, 0.60)))
            p["funding"] = max(-0.30, min(0.30, _rand_walk(p["funding"], 0.20, -0.30, 0.30)))
            p["backing"] = max(0.20, min(0.95, _rand_walk(p["backing"], 0.05, 0.20, 0.95)))
            p["efficiency"] = max(0.5, min(25.0, _rand_walk(p["efficiency"], 0.20, 0.5, 25.0)))
            # Occasional existence flips to simulate deployment
            if random.random() < 0.03:
                p["exists"] = not p["exists"]
        self.last_refresh = datetime.utcnow()

    def filtered(self) -> List[Dict]:
        res = self.pools
        if self.filter_dex != "ALL":
            res = [p for p in res if p["dex"].lower() == self.filter_dex.lower()]
        if self.filter_asset != "ALL":
            res = [p for p in res if self.filter_asset.lower() in p["pair"].lower()]
        return res

    def render(self) -> None:
        _header("FRY Cross-DEX Pool Monitor (Simulated)")
        print(f"Last Refresh: {self.last_refresh.isoformat()}Z")
        print(f"Filter: DEX={self.filter_dex} | Asset={self.filter_asset}")

        rows: List[List[str]] = []
        for p in self.filtered():
            status = (FRY_YELLOW + "LIVE" + RESET) if p["exists"] else (DIM + "SIM" + RESET)
            native = FRY_RED + "NATIVE" + RESET if p["native"] else DIM + "TRAD" + RESET
            rows.append([
                p["dex"],
                p["pair"],
                native,
                status,
                _format_money(p["tvl"]),
                _format_pct(p["apy"]),
                _format_pct(p["funding"]),
                _format_pct(p["backing"]),
                _format_ratio(p["efficiency"]),
            ])

        _print_table(
            rows,
            headers=["DEX", "Pair", "Type", "Status", "TVL", "APY", "Funding", "Backing", "Efficiency"],
        )

        print()
        print(BOLD + "Legend:" + RESET)
        print("  " + FRY_RED + "NATIVE" + RESET + " = Native token denomination (FRY-*native*)")
        print("  " + DIM + "TRAD" + RESET + "   = Traditional (FRY-stable/ETH/etc)")
        print("  " + FRY_YELLOW + "LIVE" + RESET + "   = Deployed | " + DIM + "SIM" + RESET + " = Simulated")

    def export_json(self, path: str) -> None:
        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "filters": {"dex": self.filter_dex, "asset": self.filter_asset},
            "pools": self.filtered(),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(FRY_YELLOW + f"Snapshot exported to {path}" + RESET)

    def menu(self) -> None:
        while True:
            self.render()
            print()
            print(BOLD + "Actions:" + RESET)
            print("  1) Refresh now")
            print("  2) Toggle auto-refresh (every 3s) once")
            print("  3) Filter by DEX")
            print("  4) Filter by Asset (e.g., $dydx, $HYPE, $FRY)")
            print("  5) Export JSON snapshot")
            print("  6) Quit")

            choice = input("Select: ").strip()
            if choice == "1":
                self.refresh()
                continue
            elif choice == "2":
                print("Auto-refreshing 10 times (3s interval)... Press Ctrl+C to stop.")
                try:
                    for _ in range(10):
                        self.refresh()
                        self.render()
                        time.sleep(3)
                except KeyboardInterrupt:
                    print("\nStopped.")
                continue
            elif choice == "3":
                print("Available DEXes:", ", ".join(DEXES))
                val = input("Enter DEX (or 'ALL'): ").strip()
                if val:
                    self.filter_dex = val
                continue
            elif choice == "4":
                print("Assets hint:", ", ".join(ASSETS))
                val = input("Enter asset substring (e.g., $dydx) or 'ALL': ").strip()
                if val:
                    self.filter_asset = val
                continue
            elif choice == "5":
                path = f"fry_pool_monitor_snapshot_{int(time.time())}.json"
                self.export_json(path)
                continue
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Try again.")


def main():
    monitor = FRYPoolMonitor()
    monitor.refresh()
    monitor.menu()


if __name__ == "__main__":
    main()
