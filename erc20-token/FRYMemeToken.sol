// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title FRY Meme Token - Ultimate Loser's Arcade
 * @dev The only token where losing makes you richer
 * 
 * Features:
 * - Inverse reward mechanics (losses = rewards)
 * - Rekt multipliers for bigger losses
 * - Degen staking pools
 * - Loss leaderboards
 * - Meme mechanics and community features
 */
contract FRYMemeToken is ERC20, Ownable, ReentrancyGuard {
    
    // ========== CONSTANTS ==========
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1 billion FRY
    uint256 public constant INITIAL_SUPPLY = 500_000_000 * 10**18; // 500M initial
    uint256 public constant REKT_REWARD_POOL = 300_000_000 * 10**18; // 300M for rewards
    uint256 public constant COMMUNITY_POOL = 200_000_000 * 10**18; // 200M for community
    
    // ========== MEME MECHANICS ==========
    
    struct RektStats {
        uint256 totalLosses;        // Total USD losses reported
        uint256 fryEarned;          // Total FRY earned from losses
        uint256 rektMultiplier;     // Current multiplier (1x to 10x)
        uint256 lastRektTime;       // Last time user got rekt
        bool isDegenerate;          // Special status for big losers
    }
    
    struct StakePool {
        string name;                // Pool name ("Diamond Hands", "Ape Mode", etc.)
        uint256 totalStaked;        // Total FRY staked in pool
        uint256 rewardMultiplier;   // Reward multiplier for this pool
        uint256 minStake;           // Minimum stake required
        bool isActive;              // Pool status
    }
    
    // ========== STATE VARIABLES ==========
    
    mapping(address => RektStats) public rektStats;
    mapping(uint256 => StakePool) public stakePools;
    mapping(address => mapping(uint256 => uint256)) public userStakes; // user => poolId => amount
    
    address[] public rektLeaderboard;
    uint256 public totalRektRewards;
    uint256 public nextPoolId;
    
    // Reward rates (basis points, 10000 = 100%)
    uint256 public baseRewardRate = 1000; // 10% of loss in FRY
    uint256 public maxMultiplier = 1000; // 10x max multiplier
    
    // ========== EVENTS ==========
    
    event RektReported(address indexed user, uint256 lossAmount, uint256 fryRewarded, uint256 newMultiplier);
    event DegenStatusAwarded(address indexed user, uint256 totalLosses);
    event StakePoolCreated(uint256 indexed poolId, string name, uint256 rewardMultiplier);
    event FRYStaked(address indexed user, uint256 indexed poolId, uint256 amount);
    event FRYUnstaked(address indexed user, uint256 indexed poolId, uint256 amount);
    event MemeEvent(string eventType, address indexed user, uint256 value, string message);
    
    // ========== CONSTRUCTOR ==========
    
    constructor() ERC20("FRY Token", "FRY") {
        // Mint initial supply to deployer
        _mint(msg.sender, INITIAL_SUPPLY);
        
        // Create initial stake pools
        _createStakePool("Diamond Hands", 150, 1000 * 10**18); // 1.5x rewards, min 1k FRY
        _createStakePool("Ape Mode", 200, 5000 * 10**18);      // 2x rewards, min 5k FRY
        _createStakePool("Degen Elite", 300, 25000 * 10**18);  // 3x rewards, min 25k FRY
        _createStakePool("Rekt Lords", 500, 100000 * 10**18);  // 5x rewards, min 100k FRY
    }
    
    // ========== REKT MECHANICS ==========
    
    /**
     * @dev Report a trading loss to earn FRY rewards
     * @param lossAmountUSD Loss amount in USD (scaled by 1e18)
     * @param proofHash Hash of loss proof (screenshot, transaction, etc.)
     */
    function reportRekt(uint256 lossAmountUSD, bytes32 proofHash) external nonReentrant {
        require(lossAmountUSD > 0, "No loss, no reward!");
        require(lossAmountUSD <= 1_000_000 * 10**18, "Loss too big, even for us");
        
        RektStats storage stats = rektStats[msg.sender];
        
        // Calculate FRY reward based on loss and multiplier
        uint256 baseReward = (lossAmountUSD * baseRewardRate) / 10000;
        uint256 multiplier = _calculateMultiplier(stats.totalLosses, lossAmountUSD);
        uint256 fryReward = (baseReward * multiplier) / 100;
        
        // Update user stats
        stats.totalLosses += lossAmountUSD;
        stats.fryEarned += fryReward;
        stats.rektMultiplier = multiplier;
        stats.lastRektTime = block.timestamp;
        
        // Award degen status for big losers (>$10k total losses)
        if (!stats.isDegenerate && stats.totalLosses >= 10000 * 10**18) {
            stats.isDegenerate = true;
            emit DegenStatusAwarded(msg.sender, stats.totalLosses);
            emit MemeEvent("DEGEN_UNLOCKED", msg.sender, stats.totalLosses, "Welcome to the degen club!");
        }
        
        // Mint FRY reward
        require(totalSupply() + fryReward <= MAX_SUPPLY, "Max supply reached");
        _mint(msg.sender, fryReward);
        totalRektRewards += fryReward;
        
        // Update leaderboard
        _updateLeaderboard(msg.sender);
        
        emit RektReported(msg.sender, lossAmountUSD, fryReward, multiplier);
        
        // Meme events for big losses
        if (lossAmountUSD >= 1000 * 10**18) {
            emit MemeEvent("BIG_REKT", msg.sender, lossAmountUSD, "Ouch! That's gonna leave a mark!");
        }
        if (lossAmountUSD >= 10000 * 10**18) {
            emit MemeEvent("LEGENDARY_REKT", msg.sender, lossAmountUSD, "LEGENDARY REKT! You're a true degen!");
        }
    }
    
    /**
     * @dev Calculate reward multiplier based on loss history
     */
    function _calculateMultiplier(uint256 totalLosses, uint256 currentLoss) internal view returns (uint256) {
        // Base multiplier starts at 100 (1x)
        uint256 multiplier = 100;
        
        // Bonus for total loss milestones
        if (totalLosses >= 1000 * 10**18) multiplier += 50;   // $1k+ total: 1.5x
        if (totalLosses >= 5000 * 10**18) multiplier += 100;  // $5k+ total: 2.5x
        if (totalLosses >= 25000 * 10**18) multiplier += 200; // $25k+ total: 4.5x
        if (totalLosses >= 100000 * 10**18) multiplier += 300; // $100k+ total: 7.5x
        
        // Bonus for big single losses
        if (currentLoss >= 1000 * 10**18) multiplier += 25;   // $1k+ loss: +0.25x
        if (currentLoss >= 5000 * 10**18) multiplier += 50;   // $5k+ loss: +0.5x
        if (currentLoss >= 25000 * 10**18) multiplier += 100; // $25k+ loss: +1x
        
        // Cap at max multiplier
        if (multiplier > maxMultiplier) multiplier = maxMultiplier;
        
        return multiplier;
    }
    
    // ========== STAKING MECHANICS ==========
    
    /**
     * @dev Stake FRY in a degen pool
     */
    function stakeFRY(uint256 poolId, uint256 amount) external nonReentrant {
        require(poolId < nextPoolId, "Pool doesn't exist");
        require(amount > 0, "Can't stake nothing");
        require(balanceOf(msg.sender) >= amount, "Insufficient FRY");
        
        StakePool storage pool = stakePools[poolId];
        require(pool.isActive, "Pool not active");
        require(amount >= pool.minStake, "Below minimum stake");
        
        // Transfer FRY to contract
        _transfer(msg.sender, address(this), amount);
        
        // Update stake tracking
        userStakes[msg.sender][poolId] += amount;
        pool.totalStaked += amount;
        
        emit FRYStaked(msg.sender, poolId, amount);
        emit MemeEvent("STAKED", msg.sender, amount, pool.name);
    }
    
    /**
     * @dev Unstake FRY from a pool
     */
    function unstakeFRY(uint256 poolId, uint256 amount) external nonReentrant {
        require(poolId < nextPoolId, "Pool doesn't exist");
        require(amount > 0, "Can't unstake nothing");
        require(userStakes[msg.sender][poolId] >= amount, "Insufficient stake");
        
        StakePool storage pool = stakePools[poolId];
        
        // Update stake tracking
        userStakes[msg.sender][poolId] -= amount;
        pool.totalStaked -= amount;
        
        // Transfer FRY back to user
        _transfer(address(this), msg.sender, amount);
        
        emit FRYUnstaked(msg.sender, poolId, amount);
    }
    
    // ========== ADMIN FUNCTIONS ==========
    
    function _createStakePool(string memory name, uint256 rewardMultiplier, uint256 minStake) internal {
        stakePools[nextPoolId] = StakePool({
            name: name,
            totalStaked: 0,
            rewardMultiplier: rewardMultiplier,
            minStake: minStake,
            isActive: true
        });
        
        emit StakePoolCreated(nextPoolId, name, rewardMultiplier);
        nextPoolId++;
    }
    
    function createStakePool(string memory name, uint256 rewardMultiplier, uint256 minStake) external onlyOwner {
        _createStakePool(name, rewardMultiplier, minStake);
    }
    
    function updateRewardRate(uint256 newRate) external onlyOwner {
        require(newRate <= 5000, "Rate too high"); // Max 50%
        baseRewardRate = newRate;
    }
    
    function _updateLeaderboard(address user) internal {
        // Simple leaderboard update (can be optimized)
        bool found = false;
        for (uint i = 0; i < rektLeaderboard.length; i++) {
            if (rektLeaderboard[i] == user) {
                found = true;
                break;
            }
        }
        if (!found) {
            rektLeaderboard.push(user);
        }
    }
    
    // ========== VIEW FUNCTIONS ==========
    
    function getRektStats(address user) external view returns (RektStats memory) {
        return rektStats[user];
    }
    
    function getStakePool(uint256 poolId) external view returns (StakePool memory) {
        return stakePools[poolId];
    }
    
    function getUserStake(address user, uint256 poolId) external view returns (uint256) {
        return userStakes[user][poolId];
    }
    
    function getLeaderboard() external view returns (address[] memory) {
        return rektLeaderboard;
    }
    
    function calculateReward(uint256 lossAmountUSD, address user) external view returns (uint256) {
        RektStats memory stats = rektStats[user];
        uint256 baseReward = (lossAmountUSD * baseRewardRate) / 10000;
        uint256 multiplier = _calculateMultiplier(stats.totalLosses, lossAmountUSD);
        return (baseReward * multiplier) / 100;
    }
}
