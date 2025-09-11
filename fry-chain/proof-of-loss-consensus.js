 * Proof of Loss Consensus Engine
 * First blockchain consensus mechanism based on quantified trading losses
 */

class ProofOfLossConsensus {
    constructor() {
        this.lossThreshold = 1.0; // Minimum $1 loss to participate
        this.miningRewardRate = 1.0; // 1 FRY per $1 lost (1:1 peg)
        this.maxLossMultiplier = 100.0; // Maximum 100x loss multiplier
        this.lossDecayPeriod = 86400; // 24 hours in seconds
        this.validatorLossRequirement = 1000.0; // $1000 loss to become validator
        
        this.lossRegistry = new Map(); // Track verified losses
        this.validators = new Map(); // Active validators with loss history
        this.pendingLossVerifications = [];
        
        console.log('🍟📉 Proof of Loss Consensus Engine initialized');
        console.log(`   Minimum Loss Threshold: $${this.lossThreshold}`);
        console.log(`   Mining Rate: ${this.miningRewardRate} FRY per $1 lost (1:1 peg)`);
        console.log(`   Validator Requirement: $${this.validatorLossRequirement} total losses`);
    }

    /**
     * Verify a trading loss from external sources (Hyperliquid, etc.)
     */
    async verifyTradingLoss(userAddress, lossData) {
        const {
            amount,
            timestamp,
            exchange,
            tradeId,
            asset,
            proof
        } = lossData;

        // Validate loss meets minimum threshold
        if (amount < this.lossThreshold) {
            return {
                success: false,
                error: `Loss amount $${amount} below minimum threshold $${this.lossThreshold}`
            };
        }

        // Verify proof of loss (API signatures, trade confirmations, etc.)
        const proofValid = await this.validateLossProof(proof, exchange, tradeId);
        if (!proofValid) {
            return {
                success: false,
                error: 'Invalid loss proof provided'
            };
        }

        // Calculate loss multiplier based on user's loss history
        const lossMultiplier = this.calculateLossMultiplier(userAddress, amount);
        const adjustedLoss = amount * lossMultiplier;
        
        // Calculate FRY mining reward
        const fryReward = adjustedLoss * this.miningRewardRate;

        // Register the verified loss
        const lossId = this.generateLossId(userAddress, timestamp, tradeId);
        this.lossRegistry.set(lossId, {
            userAddress,
            originalAmount: amount,
            adjustedAmount: adjustedLoss,
            multiplier: lossMultiplier,
            fryReward,
            timestamp,
            exchange,
            asset,
            verified: true,
            blockHeight: null // Will be set when mined into block
        });

        console.log(`✅ Loss verified: $${amount} → ${adjustedLoss.toFixed(2)} (${lossMultiplier}x) → ${fryReward.toFixed(0)} FRY`);

        return {
            success: true,
            lossId,
            originalAmount: amount,
            adjustedAmount: adjustedLoss,
            multiplier: lossMultiplier,
            fryReward,
            canMineBlock: this.canUserMineBlock(userAddress)
        };
    }

    /**
     * Calculate loss multiplier based on user's trading history
     */
    calculateLossMultiplier(userAddress, currentLoss) {
        const userLosses = this.getUserLossHistory(userAddress);
        
        // Base multiplier
        let multiplier = 1.0;
        
        // Consistency bonus: More losses = higher multiplier
        const lossCount = userLosses.length;
        if (lossCount >= 10) multiplier += 2.0;
        else if (lossCount >= 5) multiplier += 1.0;
        else if (lossCount >= 2) multiplier += 0.5;
        
        // Size bonus: Larger losses get higher multipliers
        if (currentLoss >= 10000) multiplier += 5.0;
        else if (currentLoss >= 5000) multiplier += 3.0;
        else if (currentLoss >= 1000) multiplier += 2.0;
        else if (currentLoss >= 100) multiplier += 1.0;
        
        // Frequency bonus: Recent losses get bonus
        const recentLosses = userLosses.filter(loss => 
            (Date.now() / 1000) - loss.timestamp < 3600 // Last hour
        );
        if (recentLosses.length >= 3) multiplier += 1.5;
        
        // Cap at maximum multiplier
        return Math.min(multiplier, this.maxLossMultiplier);
    }

    /**
     * Determine if user can mine a block based on their losses
     */
    canUserMineBlock(userAddress) {
        const userLosses = this.getUserLossHistory(userAddress);
        const totalLosses = userLosses.reduce((sum, loss) => sum + loss.adjustedAmount, 0);
        
        // Must have at least $100 in verified losses to mine
        return totalLosses >= 100.0;
    }

    /**
     * Mine a Proof of Loss block
     */
    async mineProofOfLossBlock(minerAddress, lossProofs) {
        // Verify miner eligibility
        if (!this.canUserMineBlock(minerAddress)) {
            return {
                success: false,
                error: 'Insufficient verified losses to mine block'
            };
        }

        // Validate all loss proofs in the block
        const validatedLosses = [];
        let totalBlockLosses = 0;
        let totalFryRewards = 0;

        for (const lossProof of lossProofs) {
            const verification = await this.verifyTradingLoss(lossProof.userAddress, lossProof.lossData);
            if (verification.success) {
                validatedLosses.push(verification);
                totalBlockLosses += verification.adjustedAmount;
                totalFryRewards += verification.fryReward;
            }
        }

        // Calculate block difficulty based on total losses
        const blockDifficulty = this.calculateBlockDifficulty(totalBlockLosses);
        
        // Miner gets bonus FRY for mining the block
        const minerBonus = Math.floor(totalFryRewards * 0.1); // 10% of block rewards
        
        const block = {
            miner: minerAddress,
            timestamp: Math.floor(Date.now() / 1000),
            totalLosses: totalBlockLosses,
            totalFryRewards: totalFryRewards + minerBonus,
            minerBonus,
            difficulty: blockDifficulty,
            lossCount: validatedLosses.length,
            validatedLosses,
            proofOfLoss: this.generateProofOfLoss(validatedLosses)
        };

        console.log(`⛏️ PoL Block mined by ${minerAddress}`);
        console.log(`   Total Losses: $${totalBlockLosses.toFixed(2)}`);
        console.log(`   FRY Rewards: ${totalFryRewards.toFixed(0)} + ${minerBonus} bonus`);
        console.log(`   Difficulty: ${blockDifficulty}`);

        return {
            success: true,
            block
        };
    }

    /**
     * Calculate block difficulty based on network loss activity
     */
    calculateBlockDifficulty(totalBlockLosses) {
        // Higher losses = higher difficulty (more valuable block)
        let difficulty = 1337; // Base difficulty
        
        if (totalBlockLosses >= 100000) difficulty *= 10;
        else if (totalBlockLosses >= 50000) difficulty *= 5;
        else if (totalBlockLosses >= 10000) difficulty *= 3;
        else if (totalBlockLosses >= 1000) difficulty *= 2;
        
        return difficulty;
    }

    /**
     * Generate cryptographic proof of losses for block
     */
    generateProofOfLoss(validatedLosses) {
        const lossData = validatedLosses.map(loss => ({
            user: loss.userAddress,
            amount: loss.adjustedAmount,
            multiplier: loss.multiplier,
            timestamp: loss.timestamp
        }));
        
        // Simple hash for now (would use proper Merkle tree in production)
        const proofString = JSON.stringify(lossData);
        return this.simpleHash(proofString);
    }

    /**
     * Validate external loss proof (API signatures, etc.)
     */
    async validateLossProof(proof, exchange, tradeId) {
        // In production, this would verify:
        // - API signatures from exchanges
        // - Trade confirmations
        // - Blockchain transaction hashes
        // - Oracle price feeds
        
        // For demo, accept all proofs as valid
        return true;
    }

    /**
     * Get user's loss history
     */
    getUserLossHistory(userAddress) {
        const userLosses = [];
        for (const [lossId, loss] of this.lossRegistry.entries()) {
            if (loss.userAddress === userAddress) {
                userLosses.push(loss);
            }
        }
        return userLosses.sort((a, b) => b.timestamp - a.timestamp);
    }

    /**
     * Register as validator (requires significant loss history)
     */
    registerValidator(userAddress) {
        const userLosses = this.getUserLossHistory(userAddress);
        const totalLosses = userLosses.reduce((sum, loss) => sum + loss.originalAmount, 0);
        
        if (totalLosses >= this.validatorLossRequirement) {
            this.validators.set(userAddress, {
                totalLosses,
                registrationTime: Date.now(),
                validatedBlocks: 0,
                reputation: 1.0
            });
            
            console.log(`🏛️ New validator registered: ${userAddress} (${totalLosses.toFixed(2)} total losses)`);
            return true;
        }
        
        return false;
    }

    /**
     * Get network statistics
     */
    getNetworkStats() {
        const totalLosses = Array.from(this.lossRegistry.values())
            .reduce((sum, loss) => sum + loss.originalAmount, 0);
        
        const totalFryMined = Array.from(this.lossRegistry.values())
            .reduce((sum, loss) => sum + loss.fryReward, 0);
        
        return {
            totalVerifiedLosses: totalLosses,
            totalFryMined,
            totalLossEvents: this.lossRegistry.size,
            activeValidators: this.validators.size,
            averageLossMultiplier: this.calculateAverageLossMultiplier()
        };
    }

    calculateAverageLossMultiplier() {
        const losses = Array.from(this.lossRegistry.values());
        if (losses.length === 0) return 1.0;
        
        const totalMultiplier = losses.reduce((sum, loss) => sum + loss.multiplier, 0);
        return totalMultiplier / losses.length;
    }

    // Utility functions
    generateLossId(userAddress, timestamp, tradeId) {
        return this.simpleHash(`${userAddress}-${timestamp}-${tradeId}`);
    }

    simpleHash(input) {
        let hash = 0;
        for (let i = 0; i < input.length; i++) {
            const char = input.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash).toString(16);
    }
}

module.exports = ProofOfLossConsensus;
