// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title ProofOfLossToken (FRY)
 * @dev Enhanced FRY token with Proof of Loss consensus integration
 * Quantifies trading losses as immutable blockchain proof
 */
contract ProofOfLossToken is ERC20, Ownable, ReentrancyGuard {
    
    // PoL Constants
    uint256 public constant FRY_PER_DOLLAR_LOST = 1; // 1 FRY per $1 lost (1:1 peg)
    uint256 public constant MIN_LOSS_THRESHOLD = 1e18; // $1 minimum loss
    uint256 public constant MAX_LOSS_MULTIPLIER = 100; // 100x max multiplier
    uint256 public constant VALIDATOR_LOSS_REQUIREMENT = 1000e18; // $1000 to become validator
    uint256 public constant BLOCK_MINING_THRESHOLD = 100e18; // $100 to mine blocks
    
    // PoL State Variables
    mapping(address => uint256) public totalVerifiedLosses;
    mapping(address => uint256) public totalFryMined;
    mapping(address => uint256) public lossMultiplier;
    mapping(address => bool) public isValidator;
    mapping(bytes32 => bool) public verifiedLossHashes;
    
    // Loss tracking
    struct LossRecord {
        address trader;
        uint256 lossAmount;
        uint256 adjustedLoss;
        uint256 fryMinted;
        uint256 multiplier;
        string exchange;
        string asset;
        uint256 timestamp;
        bytes32 proofHash;
    }
    
    mapping(bytes32 => LossRecord) public lossRecords;
    bytes32[] public allLossIds;
    
    // Virtual FRY from unrealized losses
    mapping(address => int256) public unrealizedPnL;
    mapping(address => uint256) public virtualFryBalance;
    
    // Events
    event LossVerified(
        address indexed trader,
        bytes32 indexed lossId,
        uint256 lossAmount,
        uint256 adjustedLoss,
        uint256 fryMinted,
        uint256 multiplier
    );
    
    event ValidatorRegistered(address indexed validator, uint256 totalLosses);
    event BlockMined(address indexed miner, uint256 totalLosses, uint256 fryReward);
    event VirtualFryUpdated(address indexed trader, int256 unrealizedPnL, uint256 virtualFry);
    
    constructor() ERC20("FRY Token", "FRY") {
        // Mint initial supply to deployer (existing 4.96M FRY)
        _mint(msg.sender, 4960000 * 10**decimals());
    }
    
    /**
     * @dev Verify and mint FRY from trading losses
     * @param lossAmount Dollar amount of verified loss (in wei, $1 = 1e18)
     * @param exchange Name of exchange where loss occurred
     * @param asset Asset that was traded
     * @param proofHash Hash of loss verification proof
     */
    function verifyAndMintFromLoss(
        uint256 lossAmount,
        string memory exchange,
        string memory asset,
        bytes32 proofHash
    ) external nonReentrant returns (bytes32 lossId) {
        require(lossAmount >= MIN_LOSS_THRESHOLD, "Loss below minimum threshold");
        require(!verifiedLossHashes[proofHash], "Loss already verified");
        
        // Calculate loss multiplier based on trader's history
        uint256 multiplier = calculateLossMultiplier(msg.sender, lossAmount);
        uint256 adjustedLoss = lossAmount * multiplier / 100; // Multiplier is in percentage
        uint256 fryToMint = adjustedLoss * FRY_PER_DOLLAR_LOST / 1e18;
        
        // Generate unique loss ID
        lossId = keccak256(abi.encodePacked(
            msg.sender,
            lossAmount,
            exchange,
            asset,
            block.timestamp,
            proofHash
        ));
        
        // Record the loss
        lossRecords[lossId] = LossRecord({
            trader: msg.sender,
            lossAmount: lossAmount,
            adjustedLoss: adjustedLoss,
            fryMinted: fryToMint,
            multiplier: multiplier,
            exchange: exchange,
            asset: asset,
            timestamp: block.timestamp,
            proofHash: proofHash
        });
        
        allLossIds.push(lossId);
        verifiedLossHashes[proofHash] = true;
        
        // Update trader's loss history
        totalVerifiedLosses[msg.sender] += lossAmount;
        totalFryMined[msg.sender] += fryToMint;
        
        // Update loss multiplier for future losses
        updateLossMultiplier(msg.sender);
        
        // Mint FRY tokens
        _mint(msg.sender, fryToMint);
        
        // Check if trader can become validator
        if (totalVerifiedLosses[msg.sender] >= VALIDATOR_LOSS_REQUIREMENT && !isValidator[msg.sender]) {
            isValidator[msg.sender] = true;
            emit ValidatorRegistered(msg.sender, totalVerifiedLosses[msg.sender]);
        }
        
        emit LossVerified(msg.sender, lossId, lossAmount, adjustedLoss, fryToMint, multiplier);
        
        return lossId;
    }
    
    /**
     * @dev Calculate loss multiplier based on trader's history
     */
    function calculateLossMultiplier(address trader, uint256 currentLoss) public view returns (uint256) {
        uint256 multiplier = 100; // Base 1.0x multiplier (100%)
        
        // Size bonus: Larger losses get higher multipliers
        if (currentLoss >= 10000e18) multiplier += 500; // +5.0x
        else if (currentLoss >= 5000e18) multiplier += 300; // +3.0x
        else if (currentLoss >= 1000e18) multiplier += 200; // +2.0x
        else if (currentLoss >= 100e18) multiplier += 100; // +1.0x
        
        // Consistency bonus: More total losses = higher multiplier
        uint256 totalLosses = totalVerifiedLosses[trader];
        if (totalLosses >= 50000e18) multiplier += 200; // +2.0x for $50k+ losses
        else if (totalLosses >= 25000e18) multiplier += 150; // +1.5x for $25k+ losses
        else if (totalLosses >= 10000e18) multiplier += 100; // +1.0x for $10k+ losses
        else if (totalLosses >= 5000e18) multiplier += 50;   // +0.5x for $5k+ losses
        
        // Cap at maximum multiplier
        if (multiplier > MAX_LOSS_MULTIPLIER * 100) {
            multiplier = MAX_LOSS_MULTIPLIER * 100;
        }
        
        return multiplier;
    }
    
    /**
     * @dev Update trader's loss multiplier
     */
    function updateLossMultiplier(address trader) internal {
        lossMultiplier[trader] = calculateLossMultiplier(trader, 0);
    }
    
    /**
     * @dev Update virtual FRY balance from unrealized P&L
     * @param trader Address of the trader
     * @param unrealizedPnLAmount Unrealized P&L in wei ($1 = 1e18)
     */
    function updateVirtualFry(address trader, int256 unrealizedPnLAmount) external {
        require(msg.sender == owner() || isValidator[msg.sender], "Only owner or validators can update virtual FRY");
        
        unrealizedPnL[trader] = unrealizedPnLAmount;
        
        // Convert unrealized losses to virtual FRY (1:1 peg)
        if (unrealizedPnLAmount < 0) {
            uint256 unrealizedLoss = uint256(-unrealizedPnLAmount);
            virtualFryBalance[trader] = unrealizedLoss * FRY_PER_DOLLAR_LOST / 1e18;
        } else {
            virtualFryBalance[trader] = 0;
        }
        
        emit VirtualFryUpdated(trader, unrealizedPnLAmount, virtualFryBalance[trader]);
    }
    
    /**
     * @dev Get total FRY value (real + virtual)
     */
    function getTotalFryValue(address trader) external view returns (uint256) {
        return balanceOf(trader) + virtualFryBalance[trader];
    }
    
    /**
     * @dev Mine a Proof of Loss block (validator only)
     * @param totalBlockLosses Total verified losses in the block
     */
    function minePoLBlock(uint256 totalBlockLosses) external nonReentrant {
        require(isValidator[msg.sender], "Only validators can mine blocks");
        require(totalVerifiedLosses[msg.sender] >= BLOCK_MINING_THRESHOLD, "Insufficient losses to mine");
        
        // Calculate mining reward (10% of block's FRY rewards)
        uint256 blockFryRewards = totalBlockLosses * FRY_PER_DOLLAR_LOST / 1e18;
        uint256 minerReward = blockFryRewards / 10; // 10% miner reward
        
        // Mint miner reward
        _mint(msg.sender, minerReward);
        totalFryMined[msg.sender] += minerReward;
        
        emit BlockMined(msg.sender, totalBlockLosses, minerReward);
    }
    
    /**
     * @dev Get trader's loss statistics
     */
    function getTraderStats(address trader) external view returns (
        uint256 totalLosses,
        uint256 totalMined,
        uint256 currentMultiplier,
        uint256 realBalance,
        uint256 virtualBalance,
        uint256 totalValue,
        bool canMineBlocks,
        bool validatorStatus
    ) {
        totalLosses = totalVerifiedLosses[trader];
        totalMined = totalFryMined[trader];
        currentMultiplier = lossMultiplier[trader];
        realBalance = balanceOf(trader);
        virtualBalance = virtualFryBalance[trader];
        totalValue = realBalance + virtualBalance;
        canMineBlocks = totalLosses >= BLOCK_MINING_THRESHOLD;
        validatorStatus = isValidator[trader];
    }
    
    /**
     * @dev Get network statistics
     */
    function getNetworkStats() external view returns (
        uint256 totalNetworkLosses,
        uint256 totalNetworkFry,
        uint256 totalLossEvents,
        uint256 activeValidators
    ) {
        // Calculate totals (simplified - in production would use more efficient tracking)
        for (uint256 i = 0; i < allLossIds.length; i++) {
            LossRecord memory record = lossRecords[allLossIds[i]];
            totalNetworkLosses += record.lossAmount;
            totalNetworkFry += record.fryMinted;
        }
        
        totalLossEvents = allLossIds.length;
        
        // Count validators (simplified)
        // In production, would maintain a validator count variable
        activeValidators = 0; // Would need to implement proper counting
    }
    
    /**
     * @dev Get loss record by ID
     */
    function getLossRecord(bytes32 lossId) external view returns (LossRecord memory) {
        return lossRecords[lossId];
    }
    
    /**
     * @dev Get recent loss records for a trader
     */
    function getRecentLosses(address trader, uint256 count) external view returns (bytes32[] memory) {
        bytes32[] memory recentLosses = new bytes32[](count);
        uint256 found = 0;
        
        // Search backwards through all losses
        for (uint256 i = allLossIds.length; i > 0 && found < count; i--) {
            bytes32 lossId = allLossIds[i - 1];
            if (lossRecords[lossId].trader == trader) {
                recentLosses[found] = lossId;
                found++;
            }
        }
        
        return recentLosses;
    }
    
    /**
     * @dev Emergency functions (owner only)
     */
    function emergencyMint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
    
    function setValidator(address validator, bool status) external onlyOwner {
        isValidator[validator] = status;
        if (status) {
            emit ValidatorRegistered(validator, totalVerifiedLosses[validator]);
        }
    }
}

