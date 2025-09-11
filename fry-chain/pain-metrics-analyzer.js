/**
 * Pain Metrics Analyzer
 * Advanced analytics for retail vs whale pain differentiation
 * Builds sophisticated trader suffering indices
 */

const VolatilityCaptureEngine = require('./volatility-capture-engine');

class PainMetricsAnalyzer {
    constructor() {
        this.volatilityEngine = new VolatilityCaptureEngine();
        
        // Advanced pain metrics
        this.painIndices = {
            retailPainIndex: 0,      // How much retail is suffering
            whalePainIndex: 0,       // How much whales are suffering  
            painConcentration: 0,    // Pain distribution inequality
            volatilityPainRatio: 0,  // Pain per unit of market volatility
            leveragePainIndex: 0     // Pain from leverage specifically
        };
        
        // Market correlation tracking
        this.marketCorrelations = new Map();
        this.painSeasonality = new Map();
        
        console.log('📊💔 Pain Metrics Analyzer initialized');
        console.log('   Building advanced suffering indices for trader classification');
    }

    /**
     * Process a trading loss with full pain analysis
     */
    async processLossWithPainAnalysis(lossData) {
        // Enhanced loss data with market context
        const enhancedLossData = await this.enhanceLossWithMarketData(lossData);
        
        // Calculate pain-weighted FRY
        const painAnalysis = this.volatilityEngine.calculatePainWeightedFry(enhancedLossData);
        
        // Update pain indices
        this.updatePainIndices(painAnalysis, enhancedLossData);
        
        // Analyze pain patterns
        const painPatterns = this.analyzePainPatterns(painAnalysis);
        
        // Generate pain insights
        const insights = this.generatePainInsights(painAnalysis, painPatterns);
        
        return {
            ...painAnalysis,
            marketContext: enhancedLossData.marketContext,
            painPatterns,
            insights,
            painIndices: { ...this.painIndices }
        };
    }

    /**
     * Enhance loss data with market context
     */
    async enhanceLossWithMarketData(lossData) {
        const marketContext = {
            btcVolatility: this.calculateAssetVolatility('BTC'),
            ethVolatility: this.calculateAssetVolatility('ETH'),
            marketFear: this.calculateMarketFearIndex(),
            liquidationCascade: this.detectLiquidationCascade(),
            timeOfDay: new Date().getHours(),
            dayOfWeek: new Date().getDay(),
            marketPhase: this.determineMarketPhase()
        };

        return {
            ...lossData,
            marketContext,
            // Enhanced volatility calculation
            volatility: this.calculateContextualVolatility(lossData.asset, marketContext),
            // Market timing pain multiplier
            timingMultiplier: this.calculateTimingMultiplier(marketContext)
        };
    }

    /**
     * Calculate contextual volatility based on market conditions
     */
    calculateContextualVolatility(asset, marketContext) {
        let baseVolatility = 0.3; // Default 30% volatility
        
        // Asset-specific volatility
        if (asset === 'BTC') baseVolatility = marketContext.btcVolatility;
        if (asset === 'ETH') baseVolatility = marketContext.ethVolatility;
        
        // Market fear amplification
        const fearMultiplier = 1 + (marketContext.marketFear * 0.5);
        
        // Liquidation cascade amplification
        const cascadeMultiplier = marketContext.liquidationCascade ? 2.0 : 1.0;
        
        return Math.min(baseVolatility * fearMultiplier * cascadeMultiplier, 1.0);
    }

    /**
     * Calculate timing multiplier (when losses hurt more)
     */
    calculateTimingMultiplier(marketContext) {
        let multiplier = 1.0;
        
        // Weekend losses hurt more (less liquidity, more gaps)
        if (marketContext.dayOfWeek === 0 || marketContext.dayOfWeek === 6) {
            multiplier *= 1.2;
        }
        
        // Late night/early morning losses (3-7 AM) hurt more (thin markets)
        if (marketContext.timeOfDay >= 3 && marketContext.timeOfDay <= 7) {
            multiplier *= 1.3;
        }
        
        // Bear market losses hurt more psychologically
        if (marketContext.marketPhase === 'bear') {
            multiplier *= 1.4;
        }
        
        return multiplier;
    }

    /**
     * Update pain indices based on new loss
     */
    updatePainIndices(painAnalysis, lossData) {
        const { traderType, painWeightedFry, dollarLoss } = painAnalysis;
        const weight = dollarLoss / 1000; // Weight by loss size
        
        // Update retail pain index
        if (['Shrimp', 'Retail'].includes(traderType)) {
            this.painIndices.retailPainIndex = this.updateIndex(
                this.painIndices.retailPainIndex, 
                painAnalysis.painMultiplier, 
                weight
            );
        }
        
        // Update whale pain index
        if (traderType === 'Whale') {
            this.painIndices.whalePainIndex = this.updateIndex(
                this.painIndices.whalePainIndex,
                painAnalysis.painMultiplier,
                weight
            );
        }
        
        // Update leverage pain index
        if (lossData.leverage > 1) {
            const leveragePain = painAnalysis.breakdown.leverageFactor;
            this.painIndices.leveragePainIndex = this.updateIndex(
                this.painIndices.leveragePainIndex,
                leveragePain,
                weight
            );
        }
        
        // Update pain concentration (Gini coefficient for pain distribution)
        this.updatePainConcentration();
        
        // Update volatility pain ratio
        this.updateVolatilityPainRatio(painAnalysis, lossData);
    }

    /**
     * Update index with exponential moving average
     */
    updateIndex(currentIndex, newValue, weight) {
        const alpha = Math.min(weight / 100, 0.1); // Adaptive smoothing
        return currentIndex * (1 - alpha) + newValue * alpha;
    }

    /**
     * Update pain concentration index
     */
    updatePainConcentration() {
        const networkMetrics = this.volatilityEngine.calculateNetworkPainMetrics();
        
        const totalRetailPain = (networkMetrics.Shrimp?.totalPainFry || 0) + 
                               (networkMetrics.Retail?.totalPainFry || 0);
        const totalWhalePain = networkMetrics.Whale?.totalPainFry || 0;
        const totalPain = totalRetailPain + totalWhalePain;
        
        if (totalPain > 0) {
            // Higher concentration = more pain concentrated in retail
            this.painIndices.painConcentration = totalRetailPain / totalPain;
        }
    }

    /**
     * Update volatility pain ratio
     */
    updateVolatilityPainRatio(painAnalysis, lossData) {
        const marketVolatility = lossData.marketContext.btcVolatility;
        if (marketVolatility > 0) {
            const painPerVolatility = painAnalysis.painMultiplier / marketVolatility;
            this.painIndices.volatilityPainRatio = this.updateIndex(
                this.painIndices.volatilityPainRatio,
                painPerVolatility,
                1
            );
        }
    }

    /**
     * Analyze pain patterns
     */
    analyzePainPatterns(painAnalysis) {
        const { traderType, painMultiplier, breakdown } = painAnalysis;
        
        return {
            // Pain source analysis
            primaryPainSource: this.identifyPrimaryPainSource(breakdown),
            
            // Trader behavior patterns
            behaviorPattern: this.identifyBehaviorPattern(traderType, breakdown),
            
            // Risk profile
            riskProfile: this.calculateRiskProfile(breakdown),
            
            // Pain sustainability
            painSustainability: this.calculatePainSustainability(painAnalysis),
            
            // Recovery likelihood
            recoveryLikelihood: this.calculateRecoveryLikelihood(painAnalysis)
        };
    }

    /**
     * Identify primary source of pain
     */
    identifyPrimaryPainSource(breakdown) {
        const sources = {
            leverage: breakdown.leverageFactor,
            position_size: breakdown.positionRisk * 10,
            volatility: breakdown.volatilityFactor,
            timing: breakdown.timeFactor,
            frequency: breakdown.frequencyMultiplier,
            wealth: 1 / breakdown.wealthAdjustment
        };
        
        const maxSource = Object.entries(sources)
            .sort(([,a], [,b]) => b - a)[0];
        
        return {
            source: maxSource[0],
            intensity: maxSource[1],
            description: this.describePainSource(maxSource[0], maxSource[1])
        };
    }

    /**
     * Describe pain source
     */
    describePainSource(source, intensity) {
        const descriptions = {
            leverage: intensity > 5 ? 'Excessive leverage addiction' : 'Moderate leverage use',
            position_size: intensity > 3 ? 'Catastrophic position sizing' : 'Risky position sizing',
            volatility: intensity > 2.5 ? 'Caught in volatility storm' : 'Normal market volatility',
            timing: intensity > 2 ? 'Terrible market timing' : 'Poor entry timing',
            frequency: intensity > 2 ? 'Compulsive trading pattern' : 'Frequent trading',
            wealth: intensity > 5 ? 'Retail trader vulnerability' : 'Limited capital buffer'
        };
        
        return descriptions[source] || 'Unknown pain source';
    }

    /**
     * Identify behavior pattern
     */
    identifyBehaviorPattern(traderType, breakdown) {
        const { leverageFactor, positionRisk, frequencyMultiplier } = breakdown;
        
        if (leverageFactor > 10 && positionRisk > 0.5) {
            return 'Degenerate Gambler';
        }
        if (frequencyMultiplier > 3) {
            return 'Compulsive Trader';
        }
        if (positionRisk > 0.8) {
            return 'All-In Addict';
        }
        if (traderType === 'Whale' && leverageFactor < 2) {
            return 'Conservative Whale';
        }
        if (traderType === 'Shrimp' && leverageFactor > 5) {
            return 'Desperate Shrimp';
        }
        
        return 'Standard Retail';
    }

    /**
     * Calculate risk profile
     */
    calculateRiskProfile(breakdown) {
        const riskScore = 
            (breakdown.leverageFactor / 10) * 0.4 +
            (breakdown.positionRisk) * 0.3 +
            (breakdown.frequencyMultiplier / 5) * 0.2 +
            (breakdown.volatilityFactor / 3) * 0.1;
        
        if (riskScore > 2) return 'Extreme Risk';
        if (riskScore > 1.5) return 'High Risk';
        if (riskScore > 1) return 'Moderate Risk';
        return 'Low Risk';
    }

    /**
     * Calculate pain sustainability
     */
    calculatePainSustainability(painAnalysis) {
        const { traderType, painMultiplier } = painAnalysis;
        
        // Whales can sustain more pain
        const baseTolerancce = traderType === 'Whale' ? 50 : 
                              traderType === 'Fish' ? 20 :
                              traderType === 'Retail' ? 10 : 5;
        
        const sustainabilityRatio = baseTolerancce / painMultiplier;
        
        if (sustainabilityRatio > 2) return 'Sustainable';
        if (sustainabilityRatio > 1) return 'Manageable';
        if (sustainabilityRatio > 0.5) return 'Concerning';
        return 'Unsustainable';
    }

    /**
     * Calculate recovery likelihood
     */
    calculateRecoveryLikelihood(painAnalysis) {
        const { traderType, breakdown } = painAnalysis;
        
        let recoveryScore = 0.5; // Base 50%
        
        // Wealth helps recovery
        if (traderType === 'Whale') recoveryScore += 0.3;
        else if (traderType === 'Fish') recoveryScore += 0.1;
        else if (traderType === 'Shrimp') recoveryScore -= 0.2;
        
        // Lower leverage = better recovery
        if (breakdown.leverageFactor < 2) recoveryScore += 0.2;
        else if (breakdown.leverageFactor > 10) recoveryScore -= 0.3;
        
        // Position sizing discipline
        if (breakdown.positionRisk < 0.2) recoveryScore += 0.1;
        else if (breakdown.positionRisk > 0.8) recoveryScore -= 0.2;
        
        return Math.max(0, Math.min(1, recoveryScore));
    }

    /**
     * Generate pain insights
     */
    generatePainInsights(painAnalysis, painPatterns) {
        const insights = [];
        
        // Pain level insights
        if (painAnalysis.painLevel === 'Excruciating') {
            insights.push('🚨 CRITICAL: This trader is experiencing maximum pain');
        }
        
        // Trader type insights
        if (painAnalysis.traderType === 'Shrimp' && painAnalysis.painMultiplier > 20) {
            insights.push('🦐 Shrimp in severe distress - likely to capitulate');
        }
        
        if (painAnalysis.traderType === 'Whale' && painAnalysis.painMultiplier > 5) {
            insights.push('🐋 Whale feeling pain - rare occurrence, market impact likely');
        }
        
        // Behavioral insights
        if (painPatterns.behaviorPattern === 'Degenerate Gambler') {
            insights.push('🎰 Degenerate gambling pattern detected - intervention needed');
        }
        
        // Risk insights
        if (painPatterns.riskProfile === 'Extreme Risk') {
            insights.push('⚠️ Extreme risk profile - account destruction imminent');
        }
        
        // Recovery insights
        if (painPatterns.recoveryLikelihood < 0.3) {
            insights.push('💀 Low recovery probability - potential permanent exit');
        }
        
        // Market insights
        if (this.painIndices.painConcentration > 0.8) {
            insights.push('📊 Pain highly concentrated in retail - potential capitulation event');
        }
        
        return insights;
    }

    /**
     * Generate comprehensive pain report
     */
    generatePainReport() {
        const networkMetrics = this.volatilityEngine.calculateNetworkPainMetrics();
        const leaderboard = this.volatilityEngine.generatePainLeaderboard(20);
        
        return {
            timestamp: new Date().toISOString(),
            
            // Pain indices
            painIndices: { ...this.painIndices },
            
            // Network metrics by trader type
            networkMetrics,
            
            // Top sufferers
            painLeaderboard: leaderboard,
            
            // Market insights
            marketInsights: this.generateMarketInsights(networkMetrics),
            
            // Pain distribution analysis
            painDistribution: this.analyzePainDistribution(networkMetrics),
            
            // Volatility impact analysis
            volatilityImpact: this.analyzeCurrentVolatilityImpact()
        };
    }

    /**
     * Generate market insights from pain data
     */
    generateMarketInsights(networkMetrics) {
        const insights = [];
        
        // Retail vs whale pain comparison
        const retailPain = (networkMetrics.Shrimp?.avgPainMultiplier || 0) + 
                          (networkMetrics.Retail?.avgPainMultiplier || 0);
        const whalePain = networkMetrics.Whale?.avgPainMultiplier || 0;
        
        if (retailPain > whalePain * 5) {
            insights.push('Retail traders suffering disproportionately - potential bottom signal');
        }
        
        if (whalePain > 10) {
            insights.push('Whales experiencing significant pain - major market move likely');
        }
        
        // Pain concentration insights
        if (this.painIndices.painConcentration > 0.9) {
            insights.push('Extreme pain concentration in retail - capitulation phase');
        }
        
        return insights;
    }

    /**
     * Analyze pain distribution
     */
    analyzePainDistribution(networkMetrics) {
        const segments = ['Shrimp', 'Retail', 'Fish', 'Whale'];
        const distribution = {};
        
        let totalPain = 0;
        segments.forEach(segment => {
            totalPain += networkMetrics[segment]?.totalPainFry || 0;
        });
        
        segments.forEach(segment => {
            const segmentPain = networkMetrics[segment]?.totalPainFry || 0;
            distribution[segment] = {
                painShare: totalPain > 0 ? segmentPain / totalPain : 0,
                avgPainMultiplier: networkMetrics[segment]?.avgPainMultiplier || 0,
                traderCount: networkMetrics[segment]?.traderCount || 0
            };
        });
        
        return distribution;
    }

    /**
     * Mock market data calculations (would integrate with real APIs)
     */
    calculateAssetVolatility(asset) {
        return 0.3 + (Math.random() * 0.4); // 30-70% volatility
    }

    calculateMarketFearIndex() {
        return Math.random(); // 0-1 fear index
    }

    detectLiquidationCascade() {
        return Math.random() < 0.1; // 10% chance of cascade
    }

    determineMarketPhase() {
        const phases = ['bull', 'bear', 'crab', 'recovery'];
        return phases[Math.floor(Math.random() * phases.length)];
    }

    analyzeCurrentVolatilityImpact() {
        // Mock volatility event analysis
        return {
            currentVolatility: this.calculateAssetVolatility('BTC'),
            painAmplification: this.painIndices.volatilityPainRatio,
            affectedSegments: ['Retail', 'Shrimp'],
            estimatedCapitulation: Math.random() < 0.3
        };
    }
}

module.exports = PainMetricsAnalyzer;
