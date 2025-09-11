/**
 * Volatility Capture Engine
 * Advanced pain metrics weighted by leverage and account equity
 * FRY becomes a proxy for actual trader suffering
 */

class VolatilityCaptureEngine {
    constructor() {
        // Pain calculation parameters
        this.basePainThreshold = 0.01; // 1% of account = base pain
        this.maxPainMultiplier = 1000; // Maximum pain multiplier
        this.leverageExponent = 1.5; // How much leverage amplifies pain
        this.equityDecayFactor = 0.7; // How wealth reduces pain sensitivity
        
        // Trader classification thresholds
        this.retailMaxEquity = 50000; // $50k max for retail
        this.whaleMinEquity = 1000000; // $1M min for whale
        this.shrimpsMaxEquity = 5000; // $5k max for shrimps
        
        // Pain tracking
        this.traderProfiles = new Map();
        this.painHistory = new Map();
        this.volatilityEvents = [];
        
        console.log('🌊💸 Volatility Capture Engine initialized');
        console.log('   FRY now measures true trader pain, not just dollar losses');
    }

    /**
     * Calculate Pain-Weighted FRY from a trading loss
     * Core formula: FRY = Loss * Pain_Multiplier
     * Pain_Multiplier = (Leverage^1.5) * (Position_Size/Account_Equity) * Volatility_Factor / Wealth_Dampener
     */
    calculatePainWeightedFry(lossData) {
        const {
            dollarLoss,           // Absolute dollar loss
            accountEquity,        // Total account value
            positionSize,         // Size of the losing position
            leverage,             // Leverage used (1x = no leverage)
            volatility,           // Asset volatility (0-1 scale)
            timeInPosition,       // Hours in position
            traderAddress
        } = lossData;

        // Get or create trader profile
        const profile = this.getTraderProfile(traderAddress, accountEquity);
        
        // 1. Position Risk Factor (what % of account was at risk)
        const positionRiskRatio = Math.min(positionSize / accountEquity, 1.0);
        
        // 2. Leverage Pain Amplifier (leverage hurts exponentially)
        const leveragePainFactor = Math.pow(leverage, this.leverageExponent);
        
        // 3. Volatility Amplifier (higher vol = more unexpected pain)
        const volatilityFactor = 1 + (volatility * 2); // 1x to 3x multiplier
        
        // 4. Time Decay (longer positions hurt more when they fail)
        const timePainFactor = Math.min(1 + (timeInPosition / 24), 3); // Max 3x for 48+ hour holds
        
        // 5. Wealth Dampener (rich people feel less pain per dollar)
        const wealthDampener = Math.pow(accountEquity / this.retailMaxEquity, this.equityDecayFactor);
        const wealthAdjustment = Math.max(0.1, 1 / wealthDampener); // Min 0.1x, max depends on wealth
        
        // 6. Frequency Penalty (repeated losses hurt more psychologically)
        const recentLosses = this.getRecentLosses(traderAddress, 7); // Last 7 days
        const frequencyMultiplier = 1 + (recentLosses.length * 0.2); // +20% per recent loss
        
        // Calculate raw pain multiplier
        const rawPainMultiplier = 
            leveragePainFactor * 
            positionRiskRatio * 
            volatilityFactor * 
            timePainFactor * 
            wealthAdjustment * 
            frequencyMultiplier;
        
        // Cap the pain multiplier
        const cappedPainMultiplier = Math.min(rawPainMultiplier, this.maxPainMultiplier);
        
        // Calculate Pain-Weighted FRY
        const painWeightedFry = dollarLoss * cappedPainMultiplier;
        
        // Update trader profile with this loss
        this.updateTraderProfile(traderAddress, {
            dollarLoss,
            painWeightedFry,
            painMultiplier: cappedPainMultiplier,
            leverage,
            positionRiskRatio,
            timestamp: Date.now()
        });
        
        // Classify the pain level
        const painLevel = this.classifyPainLevel(cappedPainMultiplier);
        const traderType = this.classifyTrader(accountEquity);
        
        console.log(`💔 Pain Analysis: ${traderType} lost $${dollarLoss}`);
        console.log(`   Account: $${accountEquity.toLocaleString()} | ${leverage}x leverage | ${(positionRiskRatio*100).toFixed(1)}% risk`);
        console.log(`   Pain Multiplier: ${cappedPainMultiplier.toFixed(2)}x (${painLevel})`);
        console.log(`   FRY Mined: ${painWeightedFry.toFixed(0)} (vs ${dollarLoss} raw)`);
        
        return {
            dollarLoss,
            painWeightedFry,
            painMultiplier: cappedPainMultiplier,
            painLevel,
            traderType,
            breakdown: {
                leverageFactor: leveragePainFactor,
                positionRisk: positionRiskRatio,
                volatilityFactor,
                timeFactor: timePainFactor,
                wealthAdjustment,
                frequencyMultiplier
            }
        };
    }

    /**
     * Get or create trader profile
     */
    getTraderProfile(address, currentEquity) {
        if (!this.traderProfiles.has(address)) {
            this.traderProfiles.set(address, {
                address,
                firstSeen: Date.now(),
                totalDollarLosses: 0,
                totalPainWeightedFry: 0,
                lossCount: 0,
                maxEquity: currentEquity,
                minEquity: currentEquity,
                avgLeverage: 0,
                maxPainMultiplier: 0,
                lossHistory: []
            });
        }
        
        const profile = this.traderProfiles.get(address);
        profile.maxEquity = Math.max(profile.maxEquity, currentEquity);
        profile.minEquity = Math.min(profile.minEquity, currentEquity);
        
        return profile;
    }

    /**
     * Update trader profile with new loss
     */
    updateTraderProfile(address, lossData) {
        const profile = this.traderProfiles.get(address);
        
        profile.totalDollarLosses += lossData.dollarLoss;
        profile.totalPainWeightedFry += lossData.painWeightedFry;
        profile.lossCount += 1;
        profile.maxPainMultiplier = Math.max(profile.maxPainMultiplier, lossData.painMultiplier);
        
        // Update average leverage
        profile.avgLeverage = ((profile.avgLeverage * (profile.lossCount - 1)) + lossData.leverage) / profile.lossCount;
        
        // Add to loss history (keep last 50)
        profile.lossHistory.push(lossData);
        if (profile.lossHistory.length > 50) {
            profile.lossHistory.shift();
        }
        
        // Store in pain history for network analysis
        if (!this.painHistory.has(address)) {
            this.painHistory.set(address, []);
        }
        this.painHistory.get(address).push({
            timestamp: lossData.timestamp,
            dollarLoss: lossData.dollarLoss,
            painWeightedFry: lossData.painWeightedFry,
            painMultiplier: lossData.painMultiplier
        });
    }

    /**
     * Get recent losses for frequency calculation
     */
    getRecentLosses(address, days) {
        const cutoff = Date.now() - (days * 24 * 60 * 60 * 1000);
        const history = this.painHistory.get(address) || [];
        return history.filter(loss => loss.timestamp > cutoff);
    }

    /**
     * Classify trader type based on account equity
     */
    classifyTrader(equity) {
        if (equity <= this.shrimpsMaxEquity) return 'Shrimp';
        if (equity <= this.retailMaxEquity) return 'Retail';
        if (equity < this.whaleMinEquity) return 'Fish';
        return 'Whale';
    }

    /**
     * Classify pain level based on multiplier
     */
    classifyPainLevel(multiplier) {
        if (multiplier >= 100) return 'Excruciating';
        if (multiplier >= 50) return 'Agonizing';
        if (multiplier >= 20) return 'Severe';
        if (multiplier >= 10) return 'High';
        if (multiplier >= 5) return 'Moderate';
        if (multiplier >= 2) return 'Mild';
        return 'Minimal';
    }

    /**
     * Calculate network pain metrics
     */
    calculateNetworkPainMetrics() {
        const allProfiles = Array.from(this.traderProfiles.values());
        
        // Segment by trader type
        const segments = {
            Shrimp: allProfiles.filter(p => p.maxEquity <= this.shrimpsMaxEquity),
            Retail: allProfiles.filter(p => p.maxEquity > this.shrimpsMaxEquity && p.maxEquity <= this.retailMaxEquity),
            Fish: allProfiles.filter(p => p.maxEquity > this.retailMaxEquity && p.maxEquity < this.whaleMinEquity),
            Whale: allProfiles.filter(p => p.maxEquity >= this.whaleMinEquity)
        };

        const metrics = {};
        
        for (const [type, profiles] of Object.entries(segments)) {
            const totalDollarLosses = profiles.reduce((sum, p) => sum + p.totalDollarLosses, 0);
            const totalPainFry = profiles.reduce((sum, p) => sum + p.totalPainWeightedFry, 0);
            const avgPainMultiplier = profiles.length > 0 ? 
                profiles.reduce((sum, p) => sum + (p.totalPainWeightedFry / Math.max(p.totalDollarLosses, 1)), 0) / profiles.length : 0;
            
            metrics[type] = {
                traderCount: profiles.length,
                totalDollarLosses,
                totalPainFry,
                avgPainMultiplier,
                painEfficiency: totalDollarLosses > 0 ? totalPainFry / totalDollarLosses : 0,
                avgEquity: profiles.length > 0 ? profiles.reduce((sum, p) => sum + p.maxEquity, 0) / profiles.length : 0
            };
        }

        return metrics;
    }

    /**
     * Generate pain leaderboard
     */
    generatePainLeaderboard(limit = 10) {
        const profiles = Array.from(this.traderProfiles.values())
            .sort((a, b) => b.totalPainWeightedFry - a.totalPainWeightedFry)
            .slice(0, limit);

        return profiles.map((profile, index) => ({
            rank: index + 1,
            address: profile.address,
            traderType: this.classifyTrader(profile.maxEquity),
            totalDollarLosses: profile.totalDollarLosses,
            totalPainFry: profile.totalPainWeightedFry,
            avgPainMultiplier: profile.totalPainWeightedFry / Math.max(profile.totalDollarLosses, 1),
            lossCount: profile.lossCount,
            maxEquity: profile.maxEquity,
            avgLeverage: profile.avgLeverage,
            maxPainMultiplier: profile.maxPainMultiplier
        }));
    }

    /**
     * Analyze volatility impact across trader segments
     */
    analyzeVolatilityImpact(volatilityEvent) {
        const { asset, volatilitySpike, timeWindow, priceMove } = volatilityEvent;
        
        // Find all losses during this volatility event
        const eventLosses = [];
        const eventStart = Date.now() - (timeWindow * 60 * 60 * 1000);
        
        for (const [address, history] of this.painHistory.entries()) {
            const eventSpecificLosses = history.filter(loss => 
                loss.timestamp >= eventStart && 
                Math.abs(loss.timestamp - Date.now()) <= (timeWindow * 60 * 60 * 1000)
            );
            
            eventLosses.push(...eventSpecificLosses.map(loss => ({
                ...loss,
                address,
                traderType: this.classifyTrader(this.traderProfiles.get(address).maxEquity)
            })));
        }

        // Analyze impact by trader segment
        const impactAnalysis = {};
        const segments = ['Shrimp', 'Retail', 'Fish', 'Whale'];
        
        for (const segment of segments) {
            const segmentLosses = eventLosses.filter(loss => loss.traderType === segment);
            const totalDollarLoss = segmentLosses.reduce((sum, loss) => sum + loss.dollarLoss, 0);
            const totalPainFry = segmentLosses.reduce((sum, loss) => sum + loss.painWeightedFry, 0);
            
            impactAnalysis[segment] = {
                affectedTraders: segmentLosses.length,
                totalDollarLoss,
                totalPainFry,
                avgPainMultiplier: totalDollarLoss > 0 ? totalPainFry / totalDollarLoss : 0,
                painPerTrader: segmentLosses.length > 0 ? totalPainFry / segmentLosses.length : 0
            };
        }

        return {
            event: volatilityEvent,
            totalAffected: eventLosses.length,
            impactBySegment: impactAnalysis,
            painConcentration: this.calculatePainConcentration(eventLosses)
        };
    }

    /**
     * Calculate pain concentration (how much pain is concentrated in retail vs whales)
     */
    calculatePainConcentration(losses) {
        const retailLosses = losses.filter(l => ['Shrimp', 'Retail'].includes(l.traderType));
        const whaleLosses = losses.filter(l => l.traderType === 'Whale');
        
        const retailPain = retailLosses.reduce((sum, l) => sum + l.painWeightedFry, 0);
        const whalePain = whaleLosses.reduce((sum, l) => sum + l.painWeightedFry, 0);
        const totalPain = retailPain + whalePain;
        
        return {
            retailPainShare: totalPain > 0 ? retailPain / totalPain : 0,
            whalePainShare: totalPain > 0 ? whalePain / totalPain : 0,
            painConcentrationRatio: whalePain > 0 ? retailPain / whalePain : Infinity
        };
    }

    /**
     * Get trader's pain profile
     */
    getTraderPainProfile(address) {
        const profile = this.traderProfiles.get(address);
        if (!profile) return null;

        const recentLosses = this.getRecentLosses(address, 30); // Last 30 days
        const traderType = this.classifyTrader(profile.maxEquity);
        
        return {
            address,
            traderType,
            totalDollarLosses: profile.totalDollarLosses,
            totalPainFry: profile.totalPainWeightedFry,
            avgPainMultiplier: profile.totalPainWeightedFry / Math.max(profile.totalDollarLosses, 1),
            lossCount: profile.lossCount,
            equityRange: {
                max: profile.maxEquity,
                min: profile.minEquity,
                current: profile.maxEquity // Simplified
            },
            avgLeverage: profile.avgLeverage,
            maxPainMultiplier: profile.maxPainMultiplier,
            recentActivity: {
                lossesLast30Days: recentLosses.length,
                painFryLast30Days: recentLosses.reduce((sum, l) => sum + l.painWeightedFry, 0)
            },
            painRank: this.calculatePainRank(address)
        };
    }

    /**
     * Calculate trader's pain rank
     */
    calculatePainRank(address) {
        const allProfiles = Array.from(this.traderProfiles.values())
            .sort((a, b) => b.totalPainWeightedFry - a.totalPainWeightedFry);
        
        const rank = allProfiles.findIndex(p => p.address === address) + 1;
        return {
            rank,
            totalTraders: allProfiles.length,
            percentile: ((allProfiles.length - rank) / allProfiles.length) * 100
        };
    }
}

module.exports = VolatilityCaptureEngine;
