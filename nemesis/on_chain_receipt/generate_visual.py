"""
Generate PNG Visual: Verifiable Scoring Primitives
Creates a visual diagram showing off-chain vs on-chain comparison
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import json

def generate_visual_png(output_path="nemesis/on_chain_receipt/verifiable_scoring_visual.png"):
    """Generate PNG visual diagram"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(5, 11.5, 'GH SYSTEMS — VERIFIABLE SCORING PRIMITIVES', 
            ha='center', va='center', fontsize=20, fontweight='bold')
    ax.text(5, 11, 'Intelligence Becomes Verifiable Objects', 
            ha='center', va='center', fontsize=14, style='italic', color='#666')
    
    # Off-Chain Box (Left)
    off_chain_box = FancyBboxPatch((0.5, 4), 4, 6, 
                                    boxstyle="round,pad=0.3",
                                    edgecolor='#2d5016', linewidth=2,
                                    facecolor='#e8f5e9', alpha=0.3)
    ax.add_patch(off_chain_box)
    
    ax.text(2.5, 9.5, 'OFF-CHAIN', ha='center', va='center', 
            fontsize=16, fontweight='bold', color='#2d5016')
    ax.text(2.5, 9, '(Proprietary)', ha='center', va='center', 
            fontsize=12, color='#666')
    
    # Off-chain content
    off_chain_items = [
        '• Full AI models',
        '• Complete intelligence packages',
        '• All proprietary systems',
        '• Transaction history',
        '• Network analysis',
        '• AI model outputs',
        '• Intelligence sources'
    ]
    
    for i, item in enumerate(off_chain_items):
        ax.text(2.5, 8.2 - i*0.4, item, ha='center', va='center', 
                fontsize=10, color='#333')
    
    ax.text(2.5, 4.5, 'Size: ~2.3MB', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='#2d5016',
            bbox=dict(boxstyle='round', facecolor='#fff', edgecolor='#2d5016', pad=0.5))
    
    # Scoring Primitives (Middle - what gets verified)
    scoring_box = FancyBboxPatch((4.2, 6), 1.6, 4,
                                 boxstyle="round,pad=0.2",
                                 edgecolor='#ff6b00', linewidth=2,
                                 facecolor='#fff3e0', alpha=0.5)
    ax.add_patch(scoring_box)
    
    ax.text(5, 9.5, 'SCORING', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#ff6b00')
    ax.text(5, 9, 'PRIMITIVES', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#ff6b00')
    
    scoring_items = [
        'Risk Scores',
        'Behavioral',
        'Signatures',
        'Threat',
        'Assessments'
    ]
    
    for i, item in enumerate(scoring_items):
        ax.text(5, 8.2 - i*0.35, item, ha='center', va='center',
                fontsize=9, color='#333')
    
    # Arrow from off-chain to scoring
    arrow1 = FancyArrowPatch((4.5, 8), (4.2, 8),
                            arrowstyle='->', mutation_scale=20,
                            color='#ff6b00', linewidth=2)
    ax.add_patch(arrow1)
    
    # Arrow from scoring to on-chain
    arrow2 = FancyArrowPatch((5.8, 8), (6.1, 8),
                            arrowstyle='->', mutation_scale=20,
                            color='#1976d2', linewidth=2)
    ax.add_patch(arrow2)
    
    # On-Chain Box (Right)
    on_chain_box = FancyBboxPatch((5.5, 4), 4, 6,
                                   boxstyle="round,pad=0.3",
                                   edgecolor='#1976d2', linewidth=2,
                                   facecolor='#e3f2fd', alpha=0.3)
    ax.add_patch(on_chain_box)
    
    ax.text(7.5, 9.5, 'ON-CHAIN', ha='center', va='center',
            fontsize=16, fontweight='bold', color='#1976d2')
    ax.text(7.5, 9, '(Verifiable Proof)', ha='center', va='center',
            fontsize=12, color='#666')
    
    # On-chain content
    on_chain_items = [
        '• Cryptographic hash',
        '• Timestamp',
        '• GH Systems signature',
        '• Minimal metadata',
        '• Actor ID',
        '• Threat level',
        '• Package type'
    ]
    
    for i, item in enumerate(on_chain_items):
        ax.text(7.5, 8.2 - i*0.4, item, ha='center', va='center',
                fontsize=10, color='#333')
    
    ax.text(7.5, 4.5, 'Size: ~400 bytes', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#1976d2',
            bbox=dict(boxstyle='round', facecolor='#fff', edgecolor='#1976d2', pad=0.5))
    
    # Reduction percentage
    ax.text(5, 3.5, '99.98% SIZE REDUCTION', ha='center', va='center',
            fontsize=14, fontweight='bold', color='#d32f2f',
            bbox=dict(boxstyle='round', facecolor='#ffebee', edgecolor='#d32f2f', pad=0.8))
    
    # Bottom text
    ax.text(5, 2.5, '✓ Scoring primitives are verifiable', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#2d5016')
    ax.text(5, 2, '✓ Intelligence becomes verifiable objects', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#2d5016')
    ax.text(5, 1.5, '✓ Trust without exposure', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#2d5016')
    
    # Footer
    ax.text(5, 0.5, 'GH Systems — Verifiable Scoring Primitives', ha='center', va='center',
            fontsize=10, color='#666', style='italic')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Visual saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    output = generate_visual_png()
    print(f"\n✓ PNG visual generated: {output}")

