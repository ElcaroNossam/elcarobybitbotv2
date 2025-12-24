// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title ElcaroToken
 * @dev ELCARO - Native token for ElCaro Trading Platform
 * 
 * Features:
 * - Standard ERC-20 functionality
 * - Minting (owner only)
 * - Burning (anyone can burn their own tokens)
 * - Pausable (emergency stop)
 * - Used for all platform payments
 * 
 * Tokenomics:
 * - Symbol: ELCARO
 * - Decimals: 18
 * - Initial Supply: 100,000,000 ELCARO
 * - Max Supply: 1,000,000,000 ELCARO
 */
contract ElcaroToken is ERC20, ERC20Burnable, Ownable, Pausable {
    
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18;  // 1 billion tokens
    
    // Paused addresses (emergency stop for specific users)
    mapping(address => bool) private _pausedAccounts;
    
    event AccountPaused(address indexed account);
    event AccountUnpaused(address indexed account);
    
    constructor() ERC20("ElCaro Token", "ELCARO") {
        // Mint initial supply to deployer
        _mint(msg.sender, 100_000_000 * 10**18);  // 100 million initial supply
    }
    
    /**
     * @dev Mint new tokens (owner only)
     * Cannot exceed MAX_SUPPLY
     */
    function mint(address to, uint256 amount) public onlyOwner {
        require(totalSupply() + amount <= MAX_SUPPLY, "Max supply exceeded");
        _mint(to, amount);
    }
    
    /**
     * @dev Pause all transfers (emergency)
     */
    function pause() public onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause transfers
     */
    function unpause() public onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Pause specific account
     */
    function pauseAccount(address account) public onlyOwner {
        _pausedAccounts[account] = true;
        emit AccountPaused(account);
    }
    
    /**
     * @dev Unpause specific account
     */
    function unpauseAccount(address account) public onlyOwner {
        _pausedAccounts[account] = false;
        emit AccountUnpaused(account);
    }
    
    /**
     * @dev Check if account is paused
     */
    function isPaused(address account) public view returns (bool) {
        return _pausedAccounts[account];
    }
    
    /**
     * @dev Override _beforeTokenTransfer to implement pause logic
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        require(!_pausedAccounts[from], "Sender account is paused");
        require(!_pausedAccounts[to], "Recipient account is paused");
        super._beforeTokenTransfer(from, to, amount);
    }
}
