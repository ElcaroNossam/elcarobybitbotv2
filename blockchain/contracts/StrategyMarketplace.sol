// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title StrategyMarketplace
 * @dev Marketplace for buying/selling strategy NFTs with ELCARO tokens
 * 
 * Features:
 * - List strategy NFTs for sale
 * - Buy strategies with ELCARO tokens
 * - Creator royalties (5-10%)
 * - Platform fee (2.5%)
 * - Subscription payments
 */
contract StrategyMarketplace is ReentrancyGuard, Ownable {
    
    IERC20 public elcaroToken;
    IERC721 public strategyNFT;
    
    // Platform fee (2.5% = 250 basis points)
    uint256 public marketplaceFee = 250;
    uint256 public constant FEE_DENOMINATOR = 10000;
    
    // Listing structure
    struct Listing {
        address seller;
        uint256 tokenId;
        uint256 price;          // Price in ELCARO tokens
        uint256 royaltyPercent; // Creator royalty in basis points (500 = 5%)
        bool isActive;
    }
    
    // Subscription structure
    struct Subscription {
        string plan;            // 'basic' or 'premium'
        uint256 expiresAt;      // Timestamp when subscription expires
    }
    
    // Listing ID counter
    uint256 private _listingIdCounter;
    
    // Mappings
    mapping(uint256 => Listing) public listings;
    mapping(uint256 => address) public creators;  // tokenId => creator address
    mapping(address => Subscription) public subscriptions;
    
    // Active listing IDs
    uint256[] private _activeListings;
    
    // Subscription prices (in ELCARO tokens with 18 decimals)
    mapping(string => mapping(uint256 => uint256)) public subscriptionPrices;
    
    // Events
    event StrategyListed(uint256 indexed listingId, address indexed seller, uint256 indexed tokenId, uint256 price);
    event StrategySold(uint256 indexed listingId, address indexed buyer, address indexed seller, uint256 tokenId, uint256 price);
    event ListingCancelled(uint256 indexed listingId);
    event SubscriptionPurchased(address indexed user, string plan, uint256 months, uint256 amount);
    event MarketplaceFeeUpdated(uint256 newFee);
    
    constructor(address _elcaroToken, address _strategyNFT) {
        elcaroToken = IERC20(_elcaroToken);
        strategyNFT = IERC721(_strategyNFT);
        
        // Set subscription prices (1 ELCARO = $1 USD)
        // Basic plan
        subscriptionPrices["basic"][1] = 50 * 10**18;   // $50
        subscriptionPrices["basic"][3] = 135 * 10**18;  // $135
        subscriptionPrices["basic"][6] = 240 * 10**18;  // $240
        subscriptionPrices["basic"][12] = 420 * 10**18; // $420
        
        // Premium plan
        subscriptionPrices["premium"][1] = 100 * 10**18;  // $100
        subscriptionPrices["premium"][3] = 270 * 10**18;  // $270
        subscriptionPrices["premium"][6] = 480 * 10**18;  // $480
        subscriptionPrices["premium"][12] = 840 * 10**18; // $840
    }
    
    /**
     * @dev List strategy NFT for sale
     * @param tokenId NFT token ID
     * @param price Price in ELCARO tokens (with 18 decimals)
     * @param royaltyPercent Creator royalty in basis points (e.g., 500 = 5%)
     */
    function listStrategy(
        uint256 tokenId,
        uint256 price,
        uint256 royaltyPercent
    ) external nonReentrant returns (uint256) {
        require(strategyNFT.ownerOf(tokenId) == msg.sender, "Not token owner");
        require(price > 0, "Price must be greater than 0");
        require(royaltyPercent <= 2500, "Royalty too high (max 25%)");
        
        // Transfer NFT to marketplace (escrow)
        strategyNFT.transferFrom(msg.sender, address(this), tokenId);
        
        _listingIdCounter++;
        uint256 listingId = _listingIdCounter;
        
        listings[listingId] = Listing({
            seller: msg.sender,
            tokenId: tokenId,
            price: price,
            royaltyPercent: royaltyPercent,
            isActive: true
        });
        
        // Track creator if first listing
        if (creators[tokenId] == address(0)) {
            creators[tokenId] = msg.sender;
        }
        
        _activeListings.push(listingId);
        
        emit StrategyListed(listingId, msg.sender, tokenId, price);
        
        return listingId;
    }
    
    /**
     * @dev Buy strategy from marketplace
     * @param listingId Listing ID
     */
    function buyStrategy(uint256 listingId) external nonReentrant {
        Listing storage listing = listings[listingId];
        require(listing.isActive, "Listing not active");
        require(listing.seller != msg.sender, "Cannot buy own listing");
        
        uint256 price = listing.price;
        address seller = listing.seller;
        uint256 tokenId = listing.tokenId;
        
        // Calculate fees
        uint256 platformFeeAmount = (price * marketplaceFee) / FEE_DENOMINATOR;
        uint256 royaltyAmount = (price * listing.royaltyPercent) / FEE_DENOMINATOR;
        uint256 sellerAmount = price - platformFeeAmount - royaltyAmount;
        
        // Transfer ELCARO tokens
        require(
            elcaroToken.transferFrom(msg.sender, address(this), platformFeeAmount),
            "Platform fee transfer failed"
        );
        
        if (royaltyAmount > 0) {
            address creator = creators[tokenId];
            require(
                elcaroToken.transferFrom(msg.sender, creator, royaltyAmount),
                "Royalty transfer failed"
            );
        }
        
        require(
            elcaroToken.transferFrom(msg.sender, seller, sellerAmount),
            "Seller payment failed"
        );
        
        // Transfer NFT to buyer
        strategyNFT.transferFrom(address(this), msg.sender, tokenId);
        
        // Mark listing as inactive
        listing.isActive = false;
        
        emit StrategySold(listingId, msg.sender, seller, tokenId, price);
    }
    
    /**
     * @dev Cancel listing and return NFT
     */
    function cancelListing(uint256 listingId) external nonReentrant {
        Listing storage listing = listings[listingId];
        require(listing.isActive, "Listing not active");
        require(listing.seller == msg.sender, "Not listing owner");
        
        // Return NFT to seller
        strategyNFT.transferFrom(address(this), msg.sender, listing.tokenId);
        
        listing.isActive = false;
        
        emit ListingCancelled(listingId);
    }
    
    /**
     * @dev Purchase subscription with ELCARO tokens
     * @param plan Subscription plan ('basic' or 'premium')
     * @param months Duration in months (1, 3, 6, or 12)
     */
    function purchaseSubscription(string memory plan, uint256 months) external nonReentrant {
        require(
            months == 1 || months == 3 || months == 6 || months == 12,
            "Invalid duration"
        );
        
        uint256 price = subscriptionPrices[plan][months];
        require(price > 0, "Invalid plan or duration");
        
        // Transfer ELCARO tokens to marketplace
        require(
            elcaroToken.transferFrom(msg.sender, address(this), price),
            "Payment failed"
        );
        
        // Calculate expiration
        uint256 durationSeconds = months * 30 days;
        uint256 newExpiry;
        
        Subscription storage sub = subscriptions[msg.sender];
        if (sub.expiresAt > block.timestamp) {
            // Extend existing subscription
            newExpiry = sub.expiresAt + durationSeconds;
        } else {
            // New subscription
            newExpiry = block.timestamp + durationSeconds;
        }
        
        sub.plan = plan;
        sub.expiresAt = newExpiry;
        
        emit SubscriptionPurchased(msg.sender, plan, months, price);
    }
    
    /**
     * @dev Get user's subscription status
     */
    function getSubscription(address user) external view returns (string memory plan, uint256 expiresAt) {
        Subscription memory sub = subscriptions[user];
        return (sub.plan, sub.expiresAt);
    }
    
    /**
     * @dev Get listing details
     */
    function getListing(uint256 listingId) external view returns (
        address seller,
        uint256 tokenId,
        uint256 price,
        bool isActive
    ) {
        Listing memory listing = listings[listingId];
        return (listing.seller, listing.tokenId, listing.price, listing.isActive);
    }
    
    /**
     * @dev Get all active listing IDs
     */
    function getActiveListings() external view returns (uint256[] memory) {
        uint256 activeCount = 0;
        
        // Count active listings
        for (uint256 i = 0; i < _activeListings.length; i++) {
            if (listings[_activeListings[i]].isActive) {
                activeCount++;
            }
        }
        
        // Build array
        uint256[] memory active = new uint256[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < _activeListings.length; i++) {
            if (listings[_activeListings[i]].isActive) {
                active[index] = _activeListings[i];
                index++;
            }
        }
        
        return active;
    }
    
    /**
     * @dev Get royalty info for token
     */
    function getRoyaltyInfo(uint256 tokenId) external view returns (address creator, uint256 royaltyPercent) {
        return (creators[tokenId], 500);  // Default 5% royalty
    }
    
    /**
     * @dev Set marketplace fee (owner only)
     */
    function setMarketplaceFee(uint256 newFee) external onlyOwner {
        require(newFee <= 1000, "Fee too high (max 10%)");
        marketplaceFee = newFee;
        emit MarketplaceFeeUpdated(newFee);
    }
    
    /**
     * @dev Get marketplace fee percentage
     */
    function getMarketplaceFee() external view returns (uint256) {
        return marketplaceFee;
    }
    
    /**
     * @dev Withdraw accumulated fees (owner only)
     */
    function withdrawFees() external onlyOwner {
        uint256 balance = elcaroToken.balanceOf(address(this));
        require(balance > 0, "No fees to withdraw");
        require(elcaroToken.transfer(owner(), balance), "Transfer failed");
    }
}
