# -*- coding: utf-8 -*-
"""
FRY v2 Funding Arbitrage Workflow Chart Generator
Creates comprehensive workflow visualization for market makers
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

class FRYWorkflowChart:
    """
    Creates professional workflow chart for FRY v2 funding arbitrage
    """
    
    def __init__(self):
        # Set up matplotlib for white background compatibility
        plt.rcParams['figure.facecolor'] = '#ffffff'
        plt.rcParams['axes.facecolor'] = '#ffffff'
        plt.rcParams['text.color'] = '#2d3748'
        
        self.colors = {
            'background': '#ffffff',    # White background
            'box': '#f7fafc',           # Light gray boxes
            'text': '#2d3748',          # Dark gray text
            'arrow': '#4299e1',         # Blue arrows
            'accent': '#2E8B57',        # Sea green accent (FRY color)
            'warning': '#e53e3e',       # Red for warnings
            'success': '#38a169',       # Green for success
            'border': '#cbd5e0'         # Light border color
        }
    
    def create_workflow_chart(self):
        """Create the complete FRY v2 workflow chart"""
        
        fig, ax = plt.subplots(1, 1, figsize=(20, 16))
        fig.patch.set_facecolor(self.colors['background'])
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 16)
        ax.axis('off')
        ax.set_axis_bgcolor(self.colors['background'])
        
        # Title
        ax.text(10, 15.5, u'FRY v2 Funding Arbitrage Workflow for Market Makers', 
                fontsize=24, fontweight='bold', ha='center', color=self.colors['text'])
        
        # Phase 1: Market Scanning
        self.draw_phase_box(ax, 1, 13, 4, 1.5, u"Phase 1: Market Scanning", self.colors['accent'])
        self.draw_process_box(ax, 1.2, 12.2, 1.6, 0.6, u"Scan 6 Venues\n(Binance, OKX, etc.)")
        self.draw_process_box(ax, 3.2, 12.2, 1.6, 0.6, u"Check Funding Rates\nEvery 8 Hours")
        
        # Phase 2: Opportunity Analysis
        self.draw_phase_box(ax, 6, 13, 4, 1.5, u"Phase 2: Opportunity Analysis", self.colors['arrow'])
        self.draw_process_box(ax, 6.2, 12.2, 1.6, 0.6, u"Calculate Spreads\n& Profitability")
        self.draw_process_box(ax, 8.2, 12.2, 1.6, 0.6, u"Estimate Slippage\nCosts per Venue")
        
        # Phase 3: Risk Assessment
        self.draw_phase_box(ax, 11, 13, 4, 1.5, u"Phase 3: Risk Assessment", self.colors['warning'])
        self.draw_process_box(ax, 11.2, 12.2, 1.6, 0.6, u"Liquidity Paradox\nIndex Check")
        self.draw_process_box(ax, 13.2, 12.2, 1.6, 0.6, u"Circuit Breaker\nStatus Check")
        
        # Phase 4: Position Execution
        self.draw_phase_box(ax, 16, 13, 3.5, 1.5, u"Phase 4: Execution", self.colors['success'])
        self.draw_process_box(ax, 16.2, 12.2, 1.5, 0.6, u"Long Low Rate\nVenue")
        self.draw_process_box(ax, 18, 12.2, 1.5, 0.6, u"Short High Rate\nVenue")
        
        # Central Decision Diamond
        self.draw_decision_diamond(ax, 10, 10, u"Profitable\nOpportunity?")
        
        # FRY Minting Engine (Central)
        self.draw_phase_box(ax, 7, 8, 6, 1.5, u"FRY Minting Engine", self.colors['accent'])
        self.draw_process_box(ax, 7.2, 7.2, 2.6, 0.6, u"Calculate Actual\nSlippage Costs")
        self.draw_process_box(ax, 10.2, 7.2, 2.6, 0.6, u"Mint FRY Tokens\n(1:1 with slippage)")
        
        # Safety Systems
        self.draw_phase_box(ax, 1, 5.5, 8, 1.5, u"Safety & Monitoring Systems", self.colors['warning'])
        self.draw_process_box(ax, 1.2, 4.7, 2.3, 0.6, u"Inflow Rate Monitor\n(Circuit Breaker)")
        self.draw_process_box(ax, 3.8, 4.7, 2.3, 0.6, u"Paradox Score\nTracking")
        self.draw_process_box(ax, 6.4, 4.7, 2.3, 0.6, u"System Health\nDashboard")
        
        # Dark Pool Integration
        self.draw_phase_box(ax, 11, 5.5, 8, 1.5, u"Dark Pool Integration", self.colors['arrow'])
        self.draw_process_box(ax, 11.2, 4.7, 2.3, 0.6, u"Anonymize\nTrader Identity")
        self.draw_process_box(ax, 13.8, 4.7, 2.3, 0.6, u"Package Loss\nCollateral")
        self.draw_process_box(ax, 16.4, 4.7, 2.3, 0.6, u"Institutional\nSales")
        
        # Results & Reporting
        self.draw_phase_box(ax, 1, 2.5, 18, 1.5, u"Results & Reporting", self.colors['success'])
        self.draw_process_box(ax, 1.2, 1.7, 3, 0.6, u"Traditional Arbitrage\nProfit: $XXX")
        self.draw_process_box(ax, 4.5, 1.7, 3, 0.6, u"FRY Tokens Minted\nXXX FRY")
        self.draw_process_box(ax, 8, 1.7, 3, 0.6, u"Total Value Created\n$XXX + FRY")
        self.draw_process_box(ax, 11.5, 1.7, 3, 0.6, u"System Health\nScore: XX/100")
        self.draw_process_box(ax, 15, 1.7, 3.8, 0.6, u"JSON Export &\nAnalytics")
        
        # Draw arrows connecting the workflow
        self.draw_workflow_arrows(ax)
        
        # Add legend
        self.draw_legend(ax)
        
        plt.tight_layout()
        filename = "fry_v2_funding_arbitrage_workflow.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor=self.colors['background'], edgecolor='none')
        plt.close()
        
        print("✅ FRY v2 workflow chart saved: {}".format(filename))
        return filename
    
    def draw_phase_box(self, ax, x, y, width, height, text, color):
        """Draw a phase header box"""
        box = FancyBboxPatch((x, y), width, height,
                           boxstyle="round,pad=0.1",
                           facecolor=color, edgecolor=self.colors['border'], linewidth=2)
        ax.add_patch(box)
        ax.text(x + width/2, y + height/2, text, ha='center', va='center',
                fontsize=14, fontweight='bold', color='white')
    
    def draw_process_box(self, ax, x, y, width, height, text):
        """Draw a process box"""
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle="round,pad=0.05",
                            facecolor=self.colors['box'], alpha=0.9,
                            edgecolor=self.colors['border'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + width/2, y + height/2, text,
                fontsize=10, ha='center', va='center',
                color=self.colors['text'], weight='normal')
    
    def draw_decision_diamond(self, ax, x, y, text):
        """Draw a decision diamond"""
        diamond = patches.RegularPolygon((x, y), 4, radius=1,
                                       orientation=np.pi/4,
                                       facecolor=self.colors['box'], alpha=0.9,
                                       edgecolor=self.colors['warning'], linewidth=2)
        ax.add_patch(diamond)
        ax.text(x, y, text, fontsize=11, fontweight='bold',
                ha='center', va='center', color=self.colors['text'])
    
    def draw_workflow_arrows(self, ax):
        """Draw arrows connecting workflow elements"""
        arrow_props = dict(arrowstyle='->', lw=2, color=self.colors['arrow'])
        
        # Phase 1 to Phase 2
        ax.annotate('', xy=(6, 13.7), xytext=(5, 13.7), arrowprops=arrow_props)
        
        # Phase 2 to Phase 3
        ax.annotate('', xy=(11, 13.7), xytext=(10, 13.7), arrowprops=arrow_props)
        
        # Phase 3 to Decision
        ax.annotate('', xy=(10, 11), xytext=(12.5, 12.2), arrowprops=arrow_props)
        
        # Decision to Execution (YES)
        ax.annotate(u'YES', xy=(16, 12.5), xytext=(11, 10.5), 
                   arrowprops=arrow_props, fontsize=12, color=self.colors['success'])
        
        # Decision to FRY Minting
        ax.annotate('', xy=(10, 8.5), xytext=(10, 9), arrowprops=arrow_props)
        
        # Execution to Safety Systems
        ax.annotate('', xy=(5, 6.5), xytext=(17, 12), arrowprops=arrow_props)
        
        # FRY Minting to Dark Pool
        ax.annotate('', xy=(15, 6.2), xytext=(10, 7.2), arrowprops=arrow_props)
        
        # Safety & Dark Pool to Results
        ax.annotate('', xy=(10, 3.5), xytext=(5, 4.7), arrowprops=arrow_props)
        ax.annotate('', xy=(10, 3.5), xytext=(15, 4.7), arrowprops=arrow_props)
    
    def draw_legend(self, ax):
        """Draw workflow legend"""
        legend_x = 0.5
        legend_y = 0.5
        
        ax.text(legend_x, legend_y + 0.8, u'Key Features:', fontsize=12, fontweight='bold')
        ax.text(legend_x, legend_y + 0.5, u'\u2022 Slippage-based FRY minting (not profit-based)', fontsize=10)
        ax.text(legend_x, legend_y + 0.2, u'\u2022 Circuit breaker protection against paradox loops', fontsize=10)
        ax.text(legend_x, legend_y - 0.1, u'\u2022 Multi-venue cross-arbitrage execution', fontsize=10)
        ax.text(legend_x, legend_y - 0.4, u'\u2022 Dark pool integration for institutional flow', fontsize=10)

def main():
    """Generate FRY v2 workflow chart"""
    
    print("🎨 Generating FRY v2 Funding Arbitrage Workflow Chart...")
    print("=" * 60)
    
    chart_generator = FRYWorkflowChart()
    filename = chart_generator.create_workflow_chart()
    
    print("\n📊 Workflow Chart Details:")
    print("• Complete v2 arbitrage process flow")
    print("• Market maker focused workflow")
    print("• Safety systems integration")
    print("• FRY minting process visualization")
    print("• Dark pool and institutional components")
    
    print("\n✅ FRY v2 workflow chart generation complete!")

if __name__ == "__main__":
    main()
