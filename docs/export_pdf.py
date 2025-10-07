#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Export Tool for Rekt Dark CDO Documentation
Converts the markdown documentation to a professional PDF report
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

def create_rekt_dark_pdf():
    """Create a professional PDF report for the Rekt Dark CDO system"""
    
    # Create PDF document
    filename = "REKT_DARK_CDO_System_Architecture.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, 
                          rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkred
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.darkgreen
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        backColor=colors.lightgrey,
        borderColor=colors.grey,
        borderWidth=1,
        borderPadding=8
    )
    
    # Build document content
    story = []
    
    # Title page
    story.append(Paragraph("REKT DARK CDO", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("SYSTEM ARCHITECTURE & TECHNICAL SPECIFICATION", heading_style))
    story.append(Spacer(1, 20))
    
    # Executive summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(
        "Rekt Dark is a sophisticated dark pool system that converts trading losses into "
        "investable assets for institutional buyers while maintaining complete trader anonymity "
        "through cryptographic commitments and aggregate pooling.",
        body_style
    ))
    story.append(Spacer(1, 20))
    
    # System flow diagram (text representation)
    story.append(Paragraph("Complete System Flow", heading_style))
    flow_text = """
    Retail Trader (Hyperliquid)
            ↓
    Executes leveraged trades (wins/losses)
            ↓
    Loss Oracle (Mint $FRY)
            ↓
    Only triggered on losses (proof-of-loss)
            ↓
    $FRY Rekt Pool (Dark Pool)
            ↓
    ┌─────────────────┬─────────────────┐
    ↓                 ↓                 ↓
Retail View      MM/Exchange      Institutional
Simplified       Full Access      Dark Pool Access
happy/sad        Arbitrage,       Risk-Rated
face/score       Hedging, Alpha   Tranches
    """
    story.append(Paragraph(flow_text, code_style))
    story.append(PageBreak())
    
    # Technical Architecture
    story.append(Paragraph("Detailed Technical Architecture", heading_style))
    
    # Phase 1
    story.append(Paragraph("Phase 1: Trader Onboarding & Consent", subheading_style))
    story.append(Paragraph(
        "• Trader UI: Web interface for opt-in consent and collateral locking<br/>"
        "• PreCollateralManager: Smart contract managing locked collateral and permissions<br/>"
        "• Opt-in Consent: Cryptographic signature authorizing loss attestation",
        body_style
    ))
    
    # Phase 2
    story.append(Paragraph("Phase 2: Loss Detection & Attestation", subheading_style))
    story.append(Paragraph(
        "• Loss Oracle: Verifies signed loss attestations from multiple sources<br/>"
        "• Miner/Watcher: Monitors Hyperliquid API for real-time P&L changes<br/>"
        "• Attestation: Cryptographically signed proof of loss with volatility multipliers",
        body_style
    ))
    
    # Phase 3
    story.append(Paragraph("Phase 3: Dark Pool Commitment", subheading_style))
    story.append(Paragraph(
        "• Sealed Attestation: Hash commitment hiding trader identity<br/>"
        "• DarkPool Contract: On-chain contract managing aggregate FRY pool<br/>"
        "• Merkle Tree: Cryptographic structure for batch commitments<br/>"
        "• FRY Minting: 1:1 peg with volatility multipliers (up to 50x)",
        body_style
    ))
    
    # Tranche structure table
    story.append(Paragraph("Tranche Structure & Risk Ratings", heading_style))
    
    tranche_data = [
        ['Rating', 'Yield', 'Min Purchase', 'Risk Profile', 'Target Buyers'],
        ['AAA', '2.0%', '$1,000,000', 'Safest retail losses', 'Sovereign wealth, pension funds'],
        ['AA', '3.5%', '$500,000', 'Mid-tier losses', 'Conservative institutions'],
        ['A', '5.0%', '$250,000', 'Moderate risk', 'Traditional hedge funds'],
        ['BBB', '7.5%', '$100,000', 'Investment grade ceiling', 'Balanced portfolios'],
        ['BB', '12.0%', '$50,000', 'Junk grade', 'Aggressive funds'],
        ['B', '18.0%', '$25,000', 'High risk', 'Distressed debt specialists'],
        ['CCC', '30.0%', '$10,000', 'Distressed whale losses', 'Maximum risk appetite']
    ]
    
    tranche_table = Table(tranche_data, colWidths=[0.8*inch, 0.8*inch, 1.2*inch, 1.8*inch, 2.2*inch])
    tranche_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(tranche_table)
    story.append(PageBreak())
    
    # Institutional buyer matrix
    story.append(Paragraph("Institutional Buyer Matrix", heading_style))
    
    buyer_data = [
        ['Institution', 'AUM', 'Risk Profile', 'Preferred Tranches'],
        ['Binance Ventures', '$50B', '70%', 'AA, A, BBB'],
        ['Wintermute Trading', '$2B', '90%', 'BBB, BB, B'],
        ['Alameda Research', '$10B', '100%', 'B, CCC'],
        ['Citadel Securities', '$400B', '40%', 'AAA, AA'],
        ['GIC Singapore', '$690B', '30%', 'AAA, AA, A']
    ]
    
    buyer_table = Table(buyer_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 1.8*inch])
    buyer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(buyer_table)
    story.append(Spacer(1, 20))
    
    # Economic mechanics
    story.append(Paragraph("Economic Mechanics", heading_style))
    
    story.append(Paragraph("FRY Token Economics", subheading_style))
    story.append(Paragraph(
        "• Base Rate: 1 FRY per $1 USD lost (1:1 peg)<br/>"
        "• Volatility Multipliers: 1x to 50x based on:<br/>"
        "  - Leverage (up to 10x multiplier)<br/>"
        "  - Position size (up to 5x multiplier)<br/>"
        "  - Loss severity (up to 3x multiplier)<br/>"
        "  - Liquidation bonus (2x multiplier)",
        body_style
    ))
    
    story.append(Paragraph("Revenue Streams", subheading_style))
    story.append(Paragraph(
        "1. Management Fees: 2% annual fee on tranche notional<br/>"
        "2. Performance Fees: 20% of excess returns above risk-free rate<br/>"
        "3. Transaction Fees: 0.1% on all tranche purchases<br/>"
        "4. Liquidity Provision: Spread capture on secondary market",
        body_style
    ))
    
    # Dark Pool Manipulation Results
    story.append(Paragraph("FRY Dark Pool Manipulation Simulation Results", heading_style))
    
    story.append(Paragraph("Campaign Overview", subheading_style))
    story.append(Paragraph(
        "The integrated dark pool manipulation system successfully executed 4 coordinated "
        "market manipulation strategies with $500M initial capital, demonstrating how "
        "sophisticated manipulation can weaponize dark pools for institutional profit.",
        body_style
    ))
    
    manipulation_data = [
        ['Strategy', 'FRY Minted', 'Collateral Absorbed', 'Manipulation Cost', 'ROI'],
        ['Directional Squeeze', '22,827', '$2,570', '$125M', '-99.8%'],
        ['Volatility Pump', '18,450', '$1,891', '$89M', '-99.8%'],
        ['Liquidation Cascade', '31,251', '$3,420', '$156M', '-99.8%'],
        ['Collateral Drain', '45,680', '$4,890', '$198M', '-99.8%']
    ]
    
    manipulation_table = Table(manipulation_data, colWidths=[1.8*inch, 1.2*inch, 1.4*inch, 1.4*inch, 1.0*inch])
    manipulation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(manipulation_table)
    story.append(Spacer(1, 15))
    
    # Current market statistics
    story.append(Paragraph("Enhanced Market Statistics", heading_style))
    
    stats_data = [
        ['Metric', 'Value', 'Description'],
        ['Total FRY Minted', '118,208', 'Tokens from manipulation campaigns'],
        ['Collateral Swept', '$12,771', 'USD absorbed from liquidations'],
        ['Active Tranches', '70', 'Available investment products'],
        ['Market Utilization', '3.0%', 'Percentage of tranches sold'],
        ['Institutional Buyers', '5', 'Pre-loaded market participants'],
        ['Manipulation Capital', '$500M', 'Initial capital for campaigns'],
        ['Liquidations Triggered', '47', 'Total positions liquidated'],
        ['Average Leverage', '82.5x', 'Mean leverage of liquidated positions']
    ]
    
    stats_table = Table(stats_data, colWidths=[2.0*inch, 1.5*inch, 2.9*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(stats_table)
    story.append(PageBreak())
    
    # Anonymization mechanisms
    story.append(Paragraph("Anonymization & Privacy Mechanisms", heading_style))
    
    story.append(Paragraph("1. Trader Identity Protection", subheading_style))
    story.append(Paragraph(
        "• Hash Commitments: SHA-256 hashing of trader addresses with timestamps<br/>"
        "• Merkle Tree Batching: Individual losses bundled into anonymous batches<br/>"
        "• Aggregate Pooling: Only pool-level statistics visible to buyers",
        body_style
    ))
    
    story.append(Paragraph("2. Loss Packaging Process", subheading_style))
    packaging_flow = "Individual Loss → Hash Commitment → Merkle Leaf → Batch Commitment → Tranche\n     (Private)      (Sealed)       (Anonymous)     (Aggregate)      (Public)"
    story.append(Paragraph(packaging_flow, code_style))
    
    story.append(Paragraph("3. Institutional View Restrictions", subheading_style))
    story.append(Paragraph(
        "• No Individual Data: Buyers see only aggregate statistics<br/>"
        "• Risk Metrics Only: Leverage, liquidation rates, asset breakdown<br/>"
        "• Temporal Aggregation: Time-weighted averages, not individual timestamps",
        body_style
    ))
    
    # Technical Implementation Files
    story.append(Paragraph("Technical Implementation Files", heading_style))
    
    story.append(Paragraph("Core System Files", subheading_style))
    story.append(Paragraph(
        "• core/dark_pool_manipulation_sim.py - Main manipulation engine<br/>"
        "• core/rekt_dark_cdo_enhanced.py - Enhanced CDO with institutional buyers<br/>"
        "• core/integrated_dark_pool_system_clean.py - Clean integrated system<br/>"
        "• core/dark_pool_manipulation_results.json - Comprehensive results",
        body_style
    ))
    
    story.append(Paragraph("Documentation & Reports", subheading_style))
    story.append(Paragraph(
        "• docs/REKT_DARK_SYSTEM_ARCHITECTURE.md - System documentation<br/>"
        "• docs/export_pdf.py - PDF report generator<br/>"
        "• Complete project at: /CascadeProjects/windsurf-project/",
        body_style
    ))
    
    # System Architecture Summary
    story.append(Paragraph("Integrated System Architecture", heading_style))
    
    story.append(Paragraph("Market Manipulation Engine", subheading_style))
    story.append(Paragraph(
        "1. Directional Squeeze: Coordinated price movements to trigger liquidations<br/>"
        "2. Volatility Pump: Artificial volatility creation for cascade effects<br/>"
        "3. Liquidation Cascade: Chain reaction liquidation triggering<br/>"
        "4. Collateral Drain: Systematic draining of overleveraged positions",
        body_style
    ))
    
    story.append(Paragraph("Dark Pool Integration", subheading_style))
    story.append(Paragraph(
        "• Loss Sweeping: Anonymized collateral absorption from liquidations<br/>"
        "• FRY Minting: Frictional-Rekt-Yield tokens with volatility multipliers<br/>"
        "• CDO Packaging: Institutional-grade tranche creation from losses<br/>"
        "• Buyer Matching: Risk-based institutional buyer assignment",
        body_style
    ))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Status: DRAFT CONCEPT FINALIZED", heading_style))
    story.append(Paragraph("Generated: {}".format(datetime.now().strftime('%B %d, %Y at %I:%M %p')), body_style))
    story.append(Paragraph("Version: 1.0.0", body_style))
    
    # Build PDF
    doc.build(story)
    
    return filename

if __name__ == "__main__":
    print("Generating FRY Dark Pool Manipulation PDF report...")
    filename = create_rekt_dark_pdf()
    print("PDF exported successfully: {}".format(filename))
    print("File size: {:.1f} KB".format(os.path.getsize(filename) / 1024))
