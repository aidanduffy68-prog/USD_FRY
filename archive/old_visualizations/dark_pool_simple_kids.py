#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dark Pool Integration - Super Simple Version
===========================================

A chart so simple that a fifth grader could understand it!
Uses basic shapes, bright colors, and simple words.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arrow
import numpy as np
import time

class KidsSimpleDarkPoolVisualizer:
    def __init__(self):
        # Color scheme - Red and yellow to match ML dashboard
        self.red = '#DC143C'      # Crimson red (primary)
        self.yellow = '#FFD700'   # Gold yellow (accent)
        self.dark_red = '#8B0000' # Dark red (secondary)
        self.orange = '#FF8C00'   # Dark orange (tertiary)
        self.white = '#FFFFFF'    # White background
        self.black = '#000000'    # Black text

    def draw_big_box(self, ax, x, y, width, height, text, color):
        """Draw a big colorful box with simple text"""
        # Draw the box
        box = Rectangle((x, y), width, height,
                       facecolor=color, edgecolor='black',
                       linewidth=3, alpha=0.9)
        ax.add_patch(box)
        
        # Add big text - always black for readability
        ax.text(x + width/2, y + height/2, text,
               ha='center', va='center',
               fontsize=12, fontweight='bold',
               color='black')

    def draw_arrow_simple(self, ax, x1, y1, x2, y2, color='black'):
        """Draw a simple thick arrow"""
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color=color, lw=4))

    def draw_circle(self, ax, x, y, radius, text, color):
        """Draw a circle with text"""
        circle = Circle((x, y), radius, facecolor=color, 
                       edgecolor='black', linewidth=3, alpha=0.9)
        ax.add_patch(circle)
        
        ax.text(x, y, text, ha='center', va='center',
               fontsize=10, fontweight='bold',
               color='black')

    def create_kids_simple_chart(self):
        """Create super simple chart for kids"""
        
        print("Making a chart so simple, even kids can understand it!")
        
        # Create big figure
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 10)
        ax.set_aspect('equal')
        
        # Remove title and subtitle - only text in boxes
        
        # === STEP 1: TRADING LOSSES ===
        self.draw_big_box(ax, 0.5, 7.5, 3, 1.2,
                         'Trading Losses\n$2.5M Daily',
                         self.red)
        
        # === STEP 2: LOSS TRACKING ===
        self.draw_big_box(ax, 5.5, 7.5, 3, 1.2,
                         'Loss Tracking\nProof-of-Loss',
                         self.yellow)
        
        # === STEP 3: FRY MINTING ===
        self.draw_big_box(ax, 10.5, 7.5, 3, 1.2,
                         'FRY Minting\n+8.2x Multiplier',
                         self.orange)
        
        # Remove arrows
        
        # === THE PROCESSING ENGINE ===
        self.draw_big_box(ax, 4, 5.5, 6, 1.2,
                         'REKT DARK POOL\nLoss -> Token Conversion',
                         self.yellow)
        
        # Remove section header
        
        # Retail distribution - immediate
        self.draw_circle(ax, 2.5, 3.5, 0.8, 'Retail\nImmediate\n70%', self.red)
        
        # Institutional distribution - vested
        self.draw_circle(ax, 7, 3.5, 0.8, 'Institutional\nVested\n20%', self.yellow)
        
        # Burn mechanism
        self.draw_circle(ax, 11.5, 3.5, 0.8, 'Burn\nMechanism\n10%', self.dark_red)
        
        # Remove arrows
        
        # === KEY MECHANICS BOX ===
        self.draw_big_box(ax, 0.5, 1.5, 3, 1.2,
                         'Key Mechanics\nPain-Based Multipliers',
                         self.red)
        
        # === PERFORMANCE METRICS BOX ===
        self.draw_big_box(ax, 10.5, 1.5, 3, 1.2,
                         'Daily Metrics\n2.5M FRY Minted',
                         self.yellow)
        
        
        # Remove axes - kids don't need them!
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # Make background white
        try:
            ax.set_facecolor('white')
        except AttributeError:
            ax.set_axis_bgcolor('white')
        fig.patch.set_facecolor('white')
        
        plt.tight_layout()
        
        # Save with timestamp
        timestamp = int(time.time())
        filename = 'dark_pool_kids_red_yellow_{}.png'.format(timestamp)
        
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        
        print('Dark Pool Kids Chart (Red & Yellow) saved: {}'.format(filename))
        
        plt.close()
        return filename

def main():
    """Generate super simple kids version"""
    
    print("Creating Dark Pool Chart for Kids...")
    
    visualizer = KidsSimpleDarkPoolVisualizer()
    filename = visualizer.create_kids_simple_chart()
    
    print('\nDark Pool Kids Chart Complete!')
    print('Features:')
    print('• Red and yellow color scheme matching ML dashboard')
    print("• Simple 3-step process")
    print("• Easy words a 5th grader can read")
    print("• Fun colors and thick arrows")
    print("• Simple rules explained")
    print("\nFile: {}".format(filename))

if __name__ == "__main__":
    main()
