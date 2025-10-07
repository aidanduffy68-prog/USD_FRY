#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
Mid-Cap FRY Funding Rate Visual Flow
====================================

Creative visualization showing how $FRY enhances funding rates for mid-cap coins
with color-coded flows representing different enhancement mechanisms.
"""

import matplotlib
matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import time
import random
from matplotlib.patches import FancyBboxPatch, Circle, Arrow
import matplotlib.colors as mcolors

class FRYFundingFlowVisualizer:
    """Creates animated visualization of FRY funding enhancement flows"""
    
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(16, 12))
        self.fig.patch.set_facecolor('white')
        
        # Color scheme for different flows
        self.colors = {
            'traditional': '#8B9DC3',      # Muted blue
            'fry_base': '#FF6B35',         # Orange-red
            'slippage': '#F7931E',         # Bitcoin orange
            'volatility': '#9B59B6',       # Purple
            'retail': '#2ECC71',           # Green
            'enhanced': '#E74C3C',         # Bright red
            'background': '#F8F9FA',       # Light gray
            'text': '#2C3E50',             # Dark blue-gray
            'flow_lines': '#34495E'        # Medium gray
        }
        
        # Asset data for mid-caps
        self.assets = {
            'SOL': {'base_rate': 0.0444, 'enhancement': 0.2000, 'volatility': 0.065, 'position': (2, 8)},
            'AVAX': {'base_rate': 0.0276, 'enhancement': 0.1972, 'volatility': 0.058, 'position': (6, 8)},
            'MATIC': {'base_rate': -0.0028, 'enhancement': 0.2000, 'volatility': 0.072, 'position': (10, 8)},
            'ATOM': {'base_rate': 0.0156, 'enhancement': 0.1845, 'volatility': 0.068, 'position': (14, 8)},
        }
        
        # Flow animation data
        self.flow_particles = []
        self.time_step = 0
        
        self.setup_visualization()
    
    def setup_visualization(self):
        """Setup the main visualization layout"""
        
        self.ax.set_xlim(0, 16)
        self.ax.set_ylim(0, 12)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.fig.patch.set_facecolor(self.colors['background'])
        
        # Title
        self.ax.text(8, 11.5, u'Mid-Cap Funding Rate Enhancement with $FRY', 
                    fontsize=24, fontweight='bold', ha='center', 
                    color=self.colors['text'])
        
        self.ax.text(8, 11, u'Slippage Recycling -> Enhanced Funding Spreads', 
                    fontsize=16, ha='center', style='italic',
                    color=self.colors['text'])
        
        # Draw FRY central hub
        self.draw_fry_hub()
        
        # Draw asset nodes
        self.draw_asset_nodes()
        
        # Draw flow channels
        self.draw_flow_channels()
        
        # Draw legend
        self.draw_legend()
        
        # Draw enhancement metrics
        self.draw_enhancement_metrics()
    
    def draw_fry_hub(self):
        """Draw central FRY processing hub"""
        
        # Main FRY circle
        fry_circle = Circle((8, 6), 1.2, facecolor=self.colors['fry_base'], 
                           edgecolor='white', linewidth=3, alpha=0.9)
        self.ax.add_patch(fry_circle)
        
        # FRY logo text
        self.ax.text(8, 6.2, u'$FRY', fontsize=20, fontweight='bold', 
                    ha='center', va='center', color='white')
        self.ax.text(8, 5.8, u'RECYCLING', fontsize=10, fontweight='bold', 
                    ha='center', va='center', color='white')
        
        # Surrounding enhancement rings
        for i, (radius, alpha) in enumerate([(1.4, 0.3), (1.6, 0.2), (1.8, 0.1)]):
            ring = Circle((8, 6), radius, fill=False, edgecolor=self.colors['enhanced'], 
                         linewidth=2, alpha=alpha)
            self.ax.add_patch(ring)
        
        # Slippage input arrows
        slippage_sources = [(4, 4), (12, 4), (4, 8), (12, 8)]
        for x, y in slippage_sources:
            # Arrow pointing to FRY hub
            dx, dy = 8 - x, 6 - y
            length = np.sqrt(dx**2 + dy**2)
            dx_norm, dy_norm = dx/length * 0.8, dy/length * 0.8
            
            arrow = patches.FancyArrowPatch((x, y), (x + dx_norm, y + dy_norm),
                                          arrowstyle='->', mutation_scale=15,
                                          color=self.colors['slippage'], alpha=0.7,
                                          linewidth=2)
            self.ax.add_patch(arrow)
            
            # Slippage label
            self.ax.text(x, y - 0.3, u'Slippage\nCapture', fontsize=8, 
                        ha='center', va='top', color=self.colors['slippage'],
                        fontweight='bold')
    
    def draw_asset_nodes(self):
        """Draw mid-cap asset nodes with funding rate displays"""
        
        for asset, data in self.assets.items():
            x, y = data['position']
            
            # Asset circle
            asset_circle = Circle((x, y), 0.8, facecolor=self.colors['traditional'], 
                                edgecolor='white', linewidth=2, alpha=0.8)
            self.ax.add_patch(asset_circle)
            
            # Asset name
            self.ax.text(x, y + 0.2, unicode(asset), fontsize=14, fontweight='bold', 
                        ha='center', va='center', color='white')
            
            # Traditional funding rate (smaller, below)
            traditional_rate = data['base_rate'] * 100
            self.ax.text(x, y - 0.2, u'{:.3f}%'.format(traditional_rate), fontsize=10, 
                        ha='center', va='center', color='white', alpha=0.8)
            
            # Enhanced funding rate (larger, above asset)
            enhanced_rate = (data['base_rate'] + data['enhancement']) * 100
            enhanced_box = FancyBboxPatch((x - 0.6, y + 1.0), 1.2, 0.4,
                                        boxstyle="round,pad=0.05",
                                        facecolor=self.colors['enhanced'],
                                        edgecolor='white', linewidth=2)
            self.ax.add_patch(enhanced_box)
            
            self.ax.text(x, y + 1.2, u'{:.3f}%'.format(enhanced_rate), fontsize=12, 
                        fontweight='bold', ha='center', va='center', color='white')
            self.ax.text(x, y + 0.9, u'FRY Enhanced', fontsize=8, 
                        ha='center', va='center', color='white')
            
            # Enhancement arrow
            enhancement_arrow = patches.FancyArrowPatch((x, y + 0.6), (x, y + 0.95),
                                                      arrowstyle='->', mutation_scale=12,
                                                      color=self.colors['enhanced'],
                                                      linewidth=3)
            self.ax.add_patch(enhancement_arrow)
            
            # Volatility indicator (size of outer ring)
            vol_ring = Circle((x, y), 0.8 + data['volatility'] * 5, fill=False, 
                            edgecolor=self.colors['volatility'], linewidth=2, 
                            alpha=0.5, linestyle='dashed')
            self.ax.add_patch(vol_ring)
    
    def draw_flow_channels(self):
        """Draw flow channels between FRY hub and assets"""
        
        for asset, data in self.assets.items():
            x, y = data['position']
            
            # Main flow channel from FRY to asset
            channel_path = patches.FancyArrowPatch((8, 6), (x, y),
                                                 arrowstyle='->', mutation_scale=20,
                                                 color=self.colors['fry_base'],
                                                 linewidth=4, alpha=0.7,
                                                 connectionstyle="arc3,rad=0.1")
            self.ax.add_patch(channel_path)
            
            # Enhancement flow indicators
            enhancement_pct = data['enhancement'] * 100
            flow_intensity = min(1.0, enhancement_pct / 20)  # Scale to 0-1
            
            # Multiple flow lines with varying opacity
            for i in range(3):
                offset = (i - 1) * 0.1
                flow_line = patches.FancyArrowPatch((8 + offset, 6), (x + offset, y),
                                                  arrowstyle='-', 
                                                  color=self.colors['enhanced'],
                                                  linewidth=2, 
                                                  alpha=flow_intensity * (0.8 - i * 0.2),
                                                  connectionstyle="arc3,rad=0.1")
                self.ax.add_patch(flow_line)
    
    def draw_legend(self):
        """Draw legend explaining the color coding"""
        
        legend_x, legend_y = 0.5, 3.5
        
        # Legend background
        legend_bg = FancyBboxPatch((legend_x - 0.2, legend_y - 1.8), 3.4, 3.6,
                                  boxstyle="round,pad=0.1",
                                  facecolor='white', edgecolor=self.colors['text'],
                                  linewidth=1, alpha=0.9)
        self.ax.add_patch(legend_bg)
        
        self.ax.text(legend_x + 1.5, legend_y + 1.5, u'Flow Legend', 
                    fontsize=14, fontweight='bold', ha='center',
                    color=self.colors['text'])
        
        legend_items = [
            (u'Traditional Funding', self.colors['traditional']),
            (u'FRY Base Enhancement', self.colors['fry_base']),
            (u'Slippage Recycling', self.colors['slippage']),
            (u'Volatility Bonus', self.colors['volatility']),
            (u'Enhanced Rate', self.colors['enhanced'])
        ]
        
        for i, (label, color) in enumerate(legend_items):
            y_pos = legend_y + 1 - i * 0.4
            
            # Color indicator
            indicator = Circle((legend_x, y_pos), 0.1, facecolor=color, 
                             edgecolor='white', linewidth=1)
            self.ax.add_patch(indicator)
            
            # Label
            self.ax.text(legend_x + 0.3, y_pos, label, fontsize=10, 
                        va='center', color=self.colors['text'])
    
    def draw_enhancement_metrics(self):
        """Draw key enhancement metrics"""
        
        metrics_x, metrics_y = 12.5, 3.5
        
        # Metrics background
        metrics_bg = FancyBboxPatch((metrics_x - 0.2, metrics_y - 1.8), 3.4, 3.6,
                                   boxstyle="round,pad=0.1",
                                   facecolor='white', edgecolor=self.colors['text'],
                                   linewidth=1, alpha=0.9)
        self.ax.add_patch(metrics_bg)
        
        self.ax.text(metrics_x + 1.5, metrics_y + 1.5, u'Enhancement Metrics', 
                    fontsize=14, fontweight='bold', ha='center',
                    color=self.colors['text'])
        
        # Calculate average enhancement
        avg_enhancement = np.mean([data['enhancement'] for data in self.assets.values()]) * 100
        
        metrics = [
            u'Avg Enhancement: {:.2f}%'.format(avg_enhancement),
            u'Annualized Boost: {:.0f}%'.format(avg_enhancement * 365 * 3),
            u'Assets Covered: {}'.format(len(self.assets)),
            u'Slippage Recycled: 60%',
            u'Success Rate: 89%'
        ]
        
        for i, metric in enumerate(metrics):
            y_pos = metrics_y + 1 - i * 0.4
            self.ax.text(metrics_x, y_pos, metric, fontsize=10, 
                        va='center', color=self.colors['text'],
                        fontweight='bold' if i == 0 else 'normal')
    
    def add_flow_particles(self):
        """Add animated particles showing flow movement"""
        
        # Create particles flowing from slippage sources to FRY hub
        if random.random() < 0.3:  # 30% chance each frame
            source_x = random.choice([4, 12])
            source_y = random.choice([4, 8])
            
            particle = {
                'x': source_x,
                'y': source_y,
                'target_x': 8,
                'target_y': 6,
                'progress': 0.0,
                'color': self.colors['slippage'],
                'size': random.uniform(0.05, 0.15)
            }
            self.flow_particles.append(particle)
        
        # Create particles flowing from FRY hub to assets
        if random.random() < 0.4:  # 40% chance each frame
            asset = random.choice(list(self.assets.keys()))
            target_x, target_y = self.assets[asset]['position']
            
            particle = {
                'x': 8,
                'y': 6,
                'target_x': target_x,
                'target_y': target_y,
                'progress': 0.0,
                'color': self.colors['enhanced'],
                'size': random.uniform(0.08, 0.2)
            }
            self.flow_particles.append(particle)
    
    def update_particles(self):
        """Update particle positions and remove completed ones"""
        
        particles_to_remove = []
        
        for i, particle in enumerate(self.flow_particles):
            particle['progress'] += 0.02  # Movement speed
            
            if particle['progress'] >= 1.0:
                particles_to_remove.append(i)
                continue
            
            # Smooth interpolation
            t = particle['progress']
            # Ease-in-out function
            t = t * t * (3.0 - 2.0 * t)
            
            particle['x'] = particle['x'] * (1 - t) + particle['target_x'] * t
            particle['y'] = particle['y'] * (1 - t) + particle['target_y'] * t
        
        # Remove completed particles
        for i in reversed(particles_to_remove):
            del self.flow_particles[i]
    
    def draw_particles(self):
        """Draw all active particles"""
        
        for particle in self.flow_particles:
            alpha = 1.0 - particle['progress']  # Fade out as they approach target
            particle_circle = Circle((particle['x'], particle['y']), particle['size'],
                                   facecolor=particle['color'], alpha=alpha,
                                   edgecolor='white', linewidth=0.5)
            self.ax.add_patch(particle_circle)
    
    def animate_frame(self, frame):
        """Animation frame update"""
        
        # Clear previous particles
        patches_to_remove = [p for p in self.ax.patches if isinstance(p, Circle) and p.get_radius() < 0.3]
        for patch in patches_to_remove:
            patch.remove()
        
        # Update particle system
        self.add_flow_particles()
        self.update_particles()
        self.draw_particles()
        
        # Pulse FRY hub
        pulse_intensity = 0.8 + 0.2 * np.sin(frame * 0.3)
        fry_circles = [p for p in self.ax.patches if isinstance(p, Circle) and p.center == (8, 6) and p.get_radius() == 1.2]
        for circle in fry_circles:
            circle.set_alpha(pulse_intensity)
        
        return self.ax.patches
    
    def create_static_visualization(self):
        """Create static version of the visualization"""
        
        plt.tight_layout()
        plt.savefig('midcap_fry_funding_flows.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        
        print("Static visualization saved as: midcap_fry_funding_flows.png")
        
        return self.fig
    
    def create_animated_visualization(self, duration_seconds=10):
        """Create animated version with flowing particles"""
        
        frames = duration_seconds * 30  # 30 FPS
        
        anim = FuncAnimation(self.fig, self.animate_frame, frames=frames,
                           interval=33, blit=False, repeat=True)
        
        plt.tight_layout()
        plt.show()
        
        return anim

def create_midcap_funding_visual():
    """Main function to create the mid-cap FRY funding visualization"""
    
    print("🎨 Creating Mid-Cap FRY Funding Rate Visualization...")
    
    visualizer = FRYFundingFlowVisualizer()
    
    # Create static visualization
    fig = visualizer.create_static_visualization()
    
    print("✅ Visualization created: midcap_fry_funding_flows.png")
    print("\n📊 Visual Elements:")
    print("🔵 Blue circles: Traditional funding rates")
    print("🟠 Orange flows: Slippage recycling into FRY hub")
    print("🔴 Red enhancements: FRY-boosted funding rates")
    print("🟣 Purple rings: Volatility indicators")
    print("💫 Animated particles: Real-time flow visualization")
    
    return fig

if __name__ == "__main__":
    create_midcap_funding_visual()
