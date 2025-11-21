# -*- coding: utf-8 -*-
"""
Generate "The Federal AI Security Timing Problem" visual
Timeline mismatch showing AI threats vs. government procurement
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set up the figure
fig, ax = plt.subplots(figsize=(12, 6.75), facecolor='#0a0a0a')
ax.patch.set_facecolor('#0a0a0a')

# Remove axes
ax.axis('off')

# Title
title_text = "The Federal AI Security Timing Problem"
ax.text(6, 6.2, title_text, fontsize=32, fontweight='bold', 
        ha='center', va='center', color='#ffffff', family='sans-serif')

# Left side: AI Threats
left_x = 1.5
left_y = 3.5
left_width = 2.5
left_height = 1.5

# Red/orange gradient background for threats
threat_box = FancyBboxPatch(
    (left_x - left_width/2, left_y - left_height/2),
    left_width, left_height,
    boxstyle="round,pad=0.1",
    edgecolor='#ff4444',
    facecolor='#1a0a0a',
    linewidth=2.5,
    zorder=1
)
ax.add_patch(threat_box)

# AI Threats label
ax.text(left_x, left_y + 0.8, "AI THREATS", fontsize=18, fontweight='bold',
        ha='center', va='center', color='#ff4444', family='sans-serif')

# Time: 24-48 hours
ax.text(left_x, left_y + 0.2, "24-48", fontsize=28, fontweight='bold',
        ha='center', va='center', color='#ff8800', family='sans-serif')
ax.text(left_x, left_y - 0.2, "HOURS", fontsize=14, fontweight='bold',
        ha='center', va='center', color='#ffaa00', family='sans-serif')

# Threat examples
threat_text = "- Model exploitation\n- API vulnerabilities\n- Data poisoning"
ax.text(left_x, left_y - 0.9, threat_text, fontsize=11,
        ha='center', va='top', color='#cccccc', family='sans-serif')

# Right side: Government Procurement
right_x = 10.5
right_y = 3.5
right_width = 2.5
right_height = 1.5

# Blue gradient background for government
gov_box = FancyBboxPatch(
    (right_x - right_width/2, right_y - right_height/2),
    right_width, right_height,
    boxstyle="round,pad=0.1",
    edgecolor='#0066cc',
    facecolor='#0a0a1a',
    linewidth=2.5,
    zorder=1
)
ax.add_patch(gov_box)

# Government Procurement label
ax.text(right_x, right_y + 0.8, "GOVERNMENT", fontsize=18, fontweight='bold',
        ha='center', va='center', color='#0099ff', family='sans-serif')
ax.text(right_x, right_y + 0.5, "PROCUREMENT", fontsize=18, fontweight='bold',
        ha='center', va='center', color='#0099ff', family='sans-serif')

# Time: 18 months
ax.text(right_x, right_y - 0.1, "18", fontsize=28, fontweight='bold',
        ha='center', va='center', color='#0066cc', family='sans-serif')
ax.text(right_x, right_y - 0.5, "MONTHS", fontsize=14, fontweight='bold',
        ha='center', va='center', color='#0099ff', family='sans-serif')

# Procurement details
proc_text = "- Contract cycles\n- Bureaucratic delays\n- Security reviews"
ax.text(right_x, right_y - 1.0, proc_text, fontsize=11,
        ha='center', va='top', color='#cccccc', family='sans-serif')

# Middle: Gap arrow showing mismatch
arrow_start = (left_x + left_width/2 + 0.3, left_y)
arrow_end = (right_x - right_width/2 - 0.3, right_y)

# Gap arrow (yellow/orange warning)
gap_arrow = FancyArrowPatch(
    arrow_start, arrow_end,
    arrowstyle='->', mutation_scale=30,
    color='#ffaa00', linewidth=4,
    zorder=2
)
ax.add_patch(gap_arrow)

# Gap label
gap_x = (left_x + right_x) / 2
gap_y = left_y + 0.6
ax.text(gap_x, gap_y, "THE GAP", fontsize=16, fontweight='bold',
        ha='center', va='center', color='#ffaa00', family='sans-serif')
ax.text(gap_x, gap_y - 0.3, "where adversaries operate", fontsize=12,
        ha='center', va='center', color='#ffaa00', family='sans-serif', style='italic')

# Current security response (below)
current_x = 6
current_y = 1.2
current_width = 3
current_height = 0.8

current_box = FancyBboxPatch(
    (current_x - current_width/2, current_y - current_height/2),
    current_width, current_height,
    boxstyle="round,pad=0.1",
    edgecolor='#666666',
    facecolor='#1a1a1a',
    linewidth=2,
    zorder=1
)
ax.add_patch(current_box)

ax.text(current_x, current_y + 0.2, "CURRENT SECURITY RESPONSE", fontsize=14, fontweight='bold',
        ha='center', va='center', color='#999999', family='sans-serif')
ax.text(current_x, current_y - 0.2, "7+ DAYS", fontsize=20, fontweight='bold',
        ha='center', va='center', color='#cccccc', family='sans-serif')

# Bottom insight
insight_text = "The gap between threat speed and response speed is where adversaries operate"
ax.text(6, 0.3, insight_text, fontsize=13, fontstyle='italic',
        ha='center', va='center', color='#888888', family='sans-serif')

# Set limits
ax.set_xlim(0, 12)
ax.set_ylim(0, 6.75)

# Save
plt.tight_layout()
plt.savefig('Deal Room/Assets/timing_mismatch_visual.png', 
            facecolor='#0a0a0a', dpi=150, bbox_inches='tight', pad_inches=0.2)
print("✓ Visual generated: Deal Room/Assets/timing_mismatch_visual.png")

plt.close()

