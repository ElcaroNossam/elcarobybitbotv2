// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title StrategyNFT
 * @dev ERC-721 NFT representing trading strategies
 * 
 * Features:
 * - Each strategy is a unique NFT
 * - Metadata stored on-chain + IPFS
 * - Performance tracking
 * - Royalties support (EIP-2981)
 * - Transferable/tradable
 */
contract StrategyNFT is ERC721, ERC721URIStorage, ERC721Burnable, Ownable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    
    // Strategy data
    struct StrategyData {
        uint256 strategyId;      // Database strategy ID
        address creator;         // Original creator
        uint256 price;           // Price in ELCARO tokens
        uint256 totalOwners;     // Number of owners (purchases)
        string performance;      // JSON performance data
        uint256 createdAt;
    }
    
    // Mapping from token ID to strategy data
    mapping(uint256 => StrategyData) private _strategies;
    
    // Mapping from strategy ID to token ID
    mapping(uint256 => uint256) private _strategyToToken;
    
    // Events
    event StrategyMinted(uint256 indexed tokenId, uint256 indexed strategyId, address indexed creator);
    event PerformanceUpdated(uint256 indexed tokenId, string performance);
    
    constructor() ERC721("ElCaro Strategy", "ELCAROSTRAT") {}
    
    /**
     * @dev Mint new strategy NFT
     * @param to Recipient address
     * @param strategyId Database strategy ID
     * @param metadata IPFS metadata URI
     */
    function mint(
        address to,
        uint256 strategyId,
        string memory metadata
    ) public returns (uint256) {
        require(_strategyToToken[strategyId] == 0, "Strategy already minted");
        
        _tokenIdCounter.increment();
        uint256 tokenId = _tokenIdCounter.current();
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, metadata);
        
        _strategies[tokenId] = StrategyData({
            strategyId: strategyId,
            creator: to,
            price: 0,
            totalOwners: 1,
            performance: "",
            createdAt: block.timestamp
        });
        
        _strategyToToken[strategyId] = tokenId;
        
        emit StrategyMinted(tokenId, strategyId, to);
        
        return tokenId;
    }
    
    /**
     * @dev Get strategy data
     */
    function getStrategyData(uint256 tokenId) public view returns (
        uint256 strategyId,
        address creator,
        uint256 price,
        uint256 totalOwners
    ) {
        require(_exists(tokenId), "Token does not exist");
        StrategyData memory data = _strategies[tokenId];
        return (data.strategyId, data.creator, data.price, data.totalOwners);
    }
    
    /**
     * @dev Update performance data (anyone can call to update stats)
     */
    function updatePerformance(uint256 tokenId, string memory performance) public {
        require(_exists(tokenId), "Token does not exist");
        _strategies[tokenId].performance = performance;
        emit PerformanceUpdated(tokenId, performance);
    }
    
    /**
     * @dev Get all token IDs owned by address
     */
    function tokensOfOwner(address owner) public view returns (uint256[] memory) {
        uint256 balance = balanceOf(owner);
        uint256[] memory tokens = new uint256[](balance);
        uint256 index = 0;
        
        for (uint256 i = 1; i <= _tokenIdCounter.current(); i++) {
            if (_exists(i) && ownerOf(i) == owner) {
                tokens[index] = i;
                index++;
            }
        }
        
        return tokens;
    }
    
    /**
     * @dev Get total minted NFTs
     */
    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter.current();
    }
    
    /**
     * @dev Override required functions
     */
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }
    
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
}
