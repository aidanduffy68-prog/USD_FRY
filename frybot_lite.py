#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FryBot Lite - Interactive Demo for Git Documentation
===================================================

A simplified, interactive version of FryBot that demonstrates core FRY mechanics
without requiring external dependencies. Perfect for embedding in documentation.

Usage:
    python frybot_lite.py

Features:
- Interactive trade simulation
- FRY minting calculations
- Slippage harvesting demo
- Pain multiplier system
- Simple CLI interface
"""

import random
import math
import time
from datetime import datetime

class FryBoyLite:
    """
    Lightweight FryBoy simulator for documentation demos
    """
    
    def __init__(self):
        self.version = "FryBoy Lite v1.0"
        self.fry_balance = 0.0
        self.total_trades = 0
        self.total_slippage_harvested = 0.0
        self.pain_multiplier = 1.0
        
        # Market simulation parameters
        self.market_volatility = 0.02  # 2% base volatility
        self.base_slippage = 0.001     # 0.1% base slippage
        
        print("🍟 " + self.version + " Initialized")
        print("=" * 50)
    
    def calculate_slippage(self, trade_size, market_cap, volatility_factor=1.0):
        """Calculate realistic slippage based on trade size and market conditions"""
        # Slippage increases with trade size and decreases with market cap
        size_impact = (trade_size / market_cap) * 100
        volatility_impact = volatility_factor * self.market_volatility
        
        slippage = self.base_slippage + (size_impact * 0.01) + volatility_impact
        return min(slippage, 0.05)  # Cap at 5% max slippage
    
    def calculate_pain_multiplier(self, loss_amount):
        """Calculate pain-based multiplier for FRY minting"""
        # Larger losses get higher multipliers (diminishing returns)
        if loss_amount <= 100:
            return 1.0
        elif loss_amount <= 500:
            return 1.5
        elif loss_amount <= 1000:
            return 2.0
        elif loss_amount <= 5000:
            return 3.0
        else:
            return 4.0
    
    def simulate_trade(self, trade_size, coin_name="EXAMPLE", market_cap=10000000):
        """Simulate a single trade and calculate FRY minting"""
        
        print("\n📊 Simulating Trade: $" + "{:,.2f}".format(trade_size) + " " + coin_name)
        print("-" * 40)
        
        # Simulate market conditions
        volatility_factor = random.uniform(0.5, 2.0)
        slippage_rate = self.calculate_slippage(trade_size, market_cap, volatility_factor)
        
        # Calculate losses
        slippage_loss = trade_size * slippage_rate
        
        # Simulate additional trading friction
        network_fees = random.uniform(5, 25)
        timing_loss = trade_size * random.uniform(0.0001, 0.001)
        
        total_loss = slippage_loss + network_fees + timing_loss
        
        # Calculate FRY minting
        pain_multiplier = self.calculate_pain_multiplier(total_loss)
        base_fry_rate = 0.5  # 0.5 FRY per $1 loss
        fry_minted = total_loss * base_fry_rate * pain_multiplier
        
        # Update balances
        self.fry_balance += fry_minted
        self.total_trades += 1
        self.total_slippage_harvested += total_loss
        
        # Display results
        print("Market Cap: $" + "{:,.0f}".format(market_cap))
        print("Volatility Factor: {:.2f}x".format(volatility_factor))
        print("Slippage Rate: {:.3f}%".format(slippage_rate*100))
        print("Slippage Loss: ${:.2f}".format(slippage_loss))
        print("Network Fees: ${:.2f}".format(network_fees))
        print("Timing Loss: ${:.2f}".format(timing_loss))
        print("Total Loss: ${:.2f}".format(total_loss))
        print("Pain Multiplier: {:.1f}x".format(pain_multiplier))
        print("FRY Minted: {:.2f} FRY".format(fry_minted))
        
        return {
            'trade_size': trade_size,
            'total_loss': total_loss,
            'fry_minted': fry_minted,
            'slippage_rate': slippage_rate,
            'pain_multiplier': pain_multiplier
        }
    
    def run_batch_simulation(self, num_trades=5):
        """Run multiple trades to show FRY accumulation"""
        
        print("\n🔄 Running Batch Simulation (" + str(num_trades) + " trades)")
        print("=" * 50)
        
        trade_sizes = [random.uniform(1000, 10000) for _ in range(num_trades)]
        coins = ["DOGE", "SHIB", "PEPE", "FLOKI", "BONK"]
        market_caps = [random.uniform(5000000, 500000000) for _ in range(num_trades)]
        
        results = []
        for i, (size, coin, mcap) in enumerate(zip(trade_sizes, coins, market_caps)):
            print("\n--- Trade " + str(i+1) + "/" + str(num_trades) + " ---")
            result = self.simulate_trade(size, coin, mcap)
            results.append(result)
            time.sleep(0.5)  # Dramatic pause
        
        return results
    
    def show_portfolio_summary(self):
        """Display current FryBot Lite portfolio status"""
        
        print("\n💰 FryBoy Lite Portfolio Summary")
        print("=" * 50)
        print("Total FRY Balance: {:.2f} FRY".format(self.fry_balance))
        print("Total Trades Executed: " + str(self.total_trades))
        print("Total Slippage Harvested: ${:.2f}".format(self.total_slippage_harvested))
        
        if self.total_trades > 0:
            avg_fry_per_trade = self.fry_balance / self.total_trades
            avg_loss_per_trade = self.total_slippage_harvested / self.total_trades
            print("Average FRY per Trade: {:.2f}".format(avg_fry_per_trade))
            print("Average Loss per Trade: ${:.2f}".format(avg_loss_per_trade))
            
            # Estimate FRY value (hypothetical)
            estimated_fry_value = self.fry_balance * random.uniform(0.8, 1.2)
            print("Estimated FRY Value: ${:.2f}".format(estimated_fry_value))
            
            recovery_rate = (estimated_fry_value / self.total_slippage_harvested) * 100
            print("Loss Recovery Rate: {:.1f}%".format(recovery_rate))
    
    def explain_mechanics(self):
        """Explain how FryBot Lite works"""
        
        print("\n🧠 How FryBoy Lite Works")
        print("=" * 50)
        print("1. SLIPPAGE DETECTION:")
        print("   • Monitors your trades for slippage losses")
        print("   • Calculates impact based on trade size vs market cap")
        print("   • Includes network fees and timing losses")
        print()
        print("2. PAIN MULTIPLIER SYSTEM:")
        print("   • Small losses (≤$100): 1.0x multiplier")
        print("   • Medium losses ($100-$500): 1.5x multiplier") 
        print("   • Large losses ($500-$1000): 2.0x multiplier")
        print("   • Huge losses ($1000-$5000): 3.0x multiplier")
        print("   • Massive losses (>$5000): 4.0x multiplier")
        print()
        print("3. FRY MINTING:")
        print("   • Base rate: 0.5 FRY per $1 lost")
        print("   • Multiplied by pain factor")
        print("   • Automatically credited to your balance")
        print()
        print("4. RECOVERY MECHANISM:")
        print("   • FRY tokens represent your harvested losses")
        print("   • Can be used for fee rebates, governance, staking")
        print("   • Turns trading friction into tradeable assets")
    
    def interactive_demo(self):
        """Run interactive demo session"""
        
        print("\n🎮 Interactive FryBoy Lite Demo")
        print("=" * 50)
        
        while True:
            print("\nChoose an option:")
            print("1. Simulate Single Trade")
            print("2. Run Batch Simulation (5 trades)")
            print("3. View Portfolio Summary")
            print("4. Explain FRY Mechanics")
            print("5. Reset Portfolio")
            print("6. Exit Demo")
            
            try:
                choice = input("\nEnter choice (1-6): ").strip()
                
                if choice == "1":
                    try:
                        size = float(input("Enter trade size ($): "))
                        coin = input("Enter coin name (optional): ").strip() or "DEMO"
                        mcap = float(input("Enter market cap ($, optional): ") or "10000000")
                        self.simulate_trade(size, coin, mcap)
                    except ValueError:
                        print("❌ Invalid input. Please enter valid numbers.")
                
                elif choice == "2":
                    self.run_batch_simulation()
                
                elif choice == "3":
                    self.show_portfolio_summary()
                
                elif choice == "4":
                    self.explain_mechanics()
                
                elif choice == "5":
                    self.fry_balance = 0.0
                    self.total_trades = 0
                    self.total_slippage_harvested = 0.0
                    print("✅ Portfolio reset successfully!")
                
                elif choice == "6":
                    print("👋 Thanks for trying FryBoy Lite!")
                    break
                
                else:
                    print("❌ Invalid choice. Please enter 1-6.")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print("❌ Error: " + str(e))

def main():
    """Main entry point for FryBot Lite"""
    
    print("🍟 Welcome to FryBoy Lite!")
    print("Interactive FRY Token Mechanics Demo")
    print("=" * 50)
    print("This is a simplified demonstration of FryBoy's core mechanics.")
    print("Perfect for understanding how slippage harvesting works!")
    print()
    
    # Initialize FryBoy Lite
    fryboy = FryBoyLite()
    
    # Show quick demo
    print("🚀 Quick Demo - Let's simulate some trades!")
    fryboy.run_batch_simulation(3)
    fryboy.show_portfolio_summary()
    fryboy.explain_mechanics()
    
    # Ask if user wants interactive mode
    import sys
    print("\n🎮 Want to try the interactive demo? (y/n): ")
    sys.stdout.flush()
    if input().lower().startswith('y'):
        fryboy.interactive_demo()
    else:
        print("👋 Thanks for trying FryBoy Lite!")

if __name__ == "__main__":
    main()
