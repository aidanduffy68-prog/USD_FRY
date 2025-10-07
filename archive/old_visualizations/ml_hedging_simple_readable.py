#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ML-Enhanced Adaptive Hedging Dashboard - Simple & Readable
=========================================================

Clean, simplified version with plain colors for maximum readability.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import time

class SimpleMLHedgingDashboard:
    def __init__(self):
        # Red and yellow color scheme
        self.colors = {
            'red': '#DC143C',             # Crimson red
            'yellow': '#FFD700',          # Gold yellow
            'dark_red': '#8B0000',        # Dark red
            'light_yellow': '#FFFF99',    # Light yellow
            'orange': '#FF8C00',          # Dark orange
            'white': '#FFFFFF',           # White
            'text_black': '#000000'       # Black text
        }
    
    def create_simple_dashboard(self):
        """Create simplified ML hedging dashboard"""
        
        print("Creating Simple ML-Enhanced Adaptive Hedging Dashboard...")
        
        # Create figure with white background
        fig = plt.figure(figsize=(16, 10), facecolor='white')
        
        # Remove main title for cleaner look
        
        # === HEDGE RATIO COMPARISON (Top Left) ===
        ax1 = plt.subplot(2, 3, 1)
        scenarios = ['Bull', 'Sideways', 'Volatile', 'Bear', 'Crisis']
        traditional = [42.5, 45.2, 48.1, 51.3, 55.7]
        ml_enhanced = [43.6, 51.8, 53.8, 58.8, 72.5]
        # Ensure all data is numeric for Python 2.7 compatibility
        traditional = [float(x) for x in traditional]
        ml_enhanced = [float(x) for x in ml_enhanced]
        
        x = np.arange(len(scenarios))
        width = 0.35
        
        ax1.bar(x - width/2, traditional, width, label='Traditional', 
                color=self.colors['red'], alpha=0.8)
        ax1.bar(x + width/2, ml_enhanced, width, label='ML-Enhanced', 
                color=self.colors['yellow'], alpha=0.8)
        
        ax1.set_title('HEDGE RATIO COMPARISON', fontweight='bold', color=self.colors['text_black'])
        ax1.set_xlabel('Scenario', color=self.colors['text_black'])
        ax1.set_ylabel('Hedge Ratio (%)', color=self.colors['text_black'])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        try:
            ax1.set_facecolor('white')
        except AttributeError:
            ax1.set_axis_bgcolor('white')
        
        # === MARKET REGIME DISTRIBUTION (Top Center) ===
        ax2 = plt.subplot(2, 3, 2)
        regimes = ['Crisis', 'Trending Bull', 'Trending Bear', 'Sideways', 'Volatile']
        sizes = [25, 15, 10, 20, 30]
        colors_pie = [self.colors['red'], self.colors['yellow'], self.colors['dark_red'], 
                     self.colors['light_yellow'], self.colors['orange']]
        
        ax2.pie(sizes, labels=regimes, colors=colors_pie, autopct='%1.1f%%', startangle=90)
        ax2.set_title('MARKET REGIME DISTRIBUTION', fontweight='bold', color=self.colors['text_black'])
        try:
            ax2.set_facecolor('white')
        except AttributeError:
            ax2.set_axis_bgcolor('white')
        
        # === PERFORMANCE BY REGIME (Top Right) ===
        ax3 = plt.subplot(2, 3, 3)
        regimes_short = ['Bull', 'Sideways', 'Volatile', 'Bear', 'Crisis']
        improvements = [1.1, 6.6, 5.7, 7.5, 16.8]
        
        # Ensure all data is numeric for Python 2.7 compatibility
        improvements = [float(x) for x in improvements]
        
        x_pos = np.arange(len(regimes_short))
        bars = ax3.bar(x_pos, improvements, color=self.colors['yellow'], alpha=0.8)
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(regimes_short)
        ax3.set_title('PERFORMANCE BY REGIME', fontweight='bold', color=self.colors['text_black'])
        ax3.set_ylabel('Improvement (%)', color=self.colors['text_black'])
        ax3.grid(True, alpha=0.3)
        try:
            ax3.set_facecolor('white')
        except AttributeError:
            ax3.set_axis_bgcolor('white')
        
        # Add value labels on bars
        for bar, value in zip(bars, improvements):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    '{}%'.format(value), ha='center', va='bottom', fontweight='bold')
        
        # === HEDGE RATIO EVOLUTION (Bottom Left) ===
        ax4 = plt.subplot(2, 3, 4)
        time_steps = range(11)
        traditional_evolution = [42, 44, 43, 46, 45, 47, 44, 48, 46, 49, 47]
        ml_evolution = [43, 46, 47, 52, 51, 55, 53, 58, 56, 61, 59]
        # Ensure all data is numeric for Python 2.7 compatibility
        traditional_evolution = [float(x) for x in traditional_evolution]
        ml_evolution = [float(x) for x in ml_evolution]
        
        ax4.plot(time_steps, traditional_evolution, 'o-', color=self.colors['red'], 
                linewidth=2, label='Traditional', markersize=6)
        ax4.plot(time_steps, ml_evolution, 's-', color=self.colors['yellow'], 
                linewidth=2, label='ML-Enhanced', markersize=6)
        
        ax4.set_title('HEDGE RATIO EVOLUTION', fontweight='bold', color=self.colors['text_black'])
        ax4.set_xlabel('Scenario', color=self.colors['text_black'])
        ax4.set_ylabel('Hedge Ratio (%)', color=self.colors['text_black'])
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        try:
            ax4.set_facecolor('white')
        except AttributeError:
            ax4.set_axis_bgcolor('white')
        
        # === PERFORMANCE SUMMARY (Bottom Center) ===
        ax5 = plt.subplot(2, 3, 5)
        methods = ['Traditional\nAvg', 'ML-Enhanced\nAvg', 'Improvement']
        values = [44.8, 52.7, 8.1]
        # Ensure all data is numeric for Python 2.7 compatibility
        values = [float(x) for x in values]
        colors_bar = [self.colors['red'], self.colors['yellow'], self.colors['orange']]
        
        x_pos_methods = np.arange(len(methods))
        bars = ax5.bar(x_pos_methods, values, color=colors_bar, alpha=0.8)
        ax5.set_xticks(x_pos_methods)
        ax5.set_xticklabels(methods)
        ax5.set_title('PERFORMANCE SUMMARY', fontweight='bold', color=self.colors['text_black'])
        ax5.set_ylabel('Percentage (%)', color=self.colors['text_black'])
        ax5.grid(True, alpha=0.3)
        try:
            ax5.set_facecolor('white')
        except AttributeError:
            ax5.set_axis_bgcolor('white')
        
        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    '{}%'.format(value), ha='center', va='bottom', fontweight='bold')
        
        # === ML FRAMEWORK COMPONENTS (Bottom Right) ===
        ax6 = plt.subplot(2, 3, 6)
        components = ['Traditional\nLPI', 'Regime\nDetection', 'RL\nOptimization']
        weights = [40, 35, 25]
        # Ensure all data is numeric for Python 2.7 compatibility
        weights = [float(x) for x in weights]
        
        x_pos_components = np.arange(len(components))
        bars = ax6.bar(x_pos_components, weights, color=[self.colors['red'], self.colors['yellow'], self.colors['orange']], 
                      alpha=0.8)
        ax6.set_xticks(x_pos_components)
        ax6.set_xticklabels(components)
        ax6.set_title('ML FRAMEWORK COMPONENTS', fontweight='bold', color=self.colors['text_black'])
        ax6.set_ylabel('Weight (%)', color=self.colors['text_black'])
        ax6.grid(True, alpha=0.3)
        try:
            ax6.set_facecolor('white')
        except AttributeError:
            ax6.set_axis_bgcolor('white')
        
        # Add value labels
        for bar, value in zip(bars, weights):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    '{}%'.format(value), ha='center', va='bottom', fontweight='bold')
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        
        # Save with timestamp
        timestamp = int(time.time())
        filename = "ml_hedging_red_yellow_{}.png".format(timestamp)
        
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        
        print("Red & Yellow ML Hedging Dashboard saved: {}".format(filename))
        
        # Display key improvements
        print("\nSIMPLIFIED DASHBOARD FEATURES:")
        print("-" * 40)
        print("• Clean white background for readability")
        print("• Simple blue/green color scheme")
        print("• Clear black text throughout")
        print("• Removed complex gradients and effects")
        print("• Enhanced grid lines for data clarity")
        print("• Bold value labels on all charts")
        print("• Professional color palette")
        
        plt.close()
        return filename

def main():
    """Generate simple readable ML hedging dashboard"""
    
    print("Creating Simple & Readable ML-Enhanced Adaptive Hedging Dashboard...")
    
    dashboard = SimpleMLHedgingDashboard()
    filename = dashboard.create_simple_dashboard()
    
    print("\nRed & Yellow ML Hedging Dashboard Complete!")
    print("Improvements:")
    print("• Red and yellow color scheme")
    print("• White background for maximum readability")
    print("• Clear black text and labels")
    print("• Professional appearance")
    print("• Enhanced data visibility")
    print("\nFile: {}".format(filename))

if __name__ == "__main__":
    main()
