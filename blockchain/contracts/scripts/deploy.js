const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Deploying ElCaro Web3 Contracts...\n");
  
  const [deployer] = await hre.ethers.getSigners();
  const network = hre.network.name;
  
  console.log("Network:", network);
  console.log("Deployer:", deployer.address);
  console.log("Balance:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "ETH\n");
  
  const deployments = {};
  
  // ==========================================
  // 1. Deploy ELCARO Token
  // ==========================================
  console.log("📝 Deploying ELCARO Token...");
  const ElcaroToken = await hre.ethers.getContractFactory("ElcaroToken");
  const token = await ElcaroToken.deploy();
  await token.waitForDeployment();
  const tokenAddress = await token.getAddress();
  
  console.log("✅ ELCARO Token deployed to:", tokenAddress);
  deployments.elcaroToken = tokenAddress;
  
  // Wait for confirmations
  console.log("⏳ Waiting for confirmations...");
  await token.deploymentTransaction().wait(5);
  
  // ==========================================
  // 2. Deploy Strategy NFT
  // ==========================================
  console.log("\n📝 Deploying Strategy NFT...");
  const StrategyNFT = await hre.ethers.getContractFactory("StrategyNFT");
  const nft = await StrategyNFT.deploy();
  await nft.waitForDeployment();
  const nftAddress = await nft.getAddress();
  
  console.log("✅ Strategy NFT deployed to:", nftAddress);
  deployments.strategyNFT = nftAddress;
  
  await nft.deploymentTransaction().wait(5);
  
  // ==========================================
  // 3. Deploy Marketplace
  // ==========================================
  console.log("\n📝 Deploying Strategy Marketplace...");
  const StrategyMarketplace = await hre.ethers.getContractFactory("StrategyMarketplace");
  const marketplace = await StrategyMarketplace.deploy(tokenAddress, nftAddress);
  await marketplace.waitForDeployment();
  const marketplaceAddress = await marketplace.getAddress();
  
  console.log("✅ Strategy Marketplace deployed to:", marketplaceAddress);
  deployments.marketplace = marketplaceAddress;
  
  await marketplace.deploymentTransaction().wait(5);
  
  // ==========================================
  // Save Deployment Info
  // ==========================================
  deployments.network = network;
  deployments.deployer = deployer.address;
  deployments.timestamp = new Date().toISOString();
  deployments.chainId = (await hre.ethers.provider.getNetwork()).chainId.toString();
  
  const deploymentsDir = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }
  
  const deploymentFile = path.join(deploymentsDir, `${network}.json`);
  fs.writeFileSync(deploymentFile, JSON.stringify(deployments, null, 2));
  
  console.log("\n📄 Deployment info saved to:", deploymentFile);
  
  // ==========================================
  // Update Python Contract Addresses
  // ==========================================
  console.log("\n🔧 Updating Python contract addresses...");
  
  const updates = [
    {
      file: "../token_contract.py",
      search: `'${network}': '0x0000000000000000000000000000000000000000'`,
      replace: `'${network}': '${tokenAddress}'`
    },
    {
      file: "../nft_contract.py",
      search: `'${network}': '0x0000000000000000000000000000000000000001'`,
      replace: `'${network}': '${nftAddress}'`
    },
    {
      file: "../marketplace_contract.py",
      search: `'${network}': '0x0000000000000000000000000000000000000002'`,
      replace: `'${network}': '${marketplaceAddress}'`
    }
  ];
  
  for (const update of updates) {
    const filePath = path.join(__dirname, update.file);
    if (fs.existsSync(filePath)) {
      let content = fs.readFileSync(filePath, "utf8");
      content = content.replace(update.search, update.replace);
      fs.writeFileSync(filePath, content);
      console.log(`✅ Updated ${update.file}`);
    }
  }
  
  // ==========================================
  // Summary
  // ==========================================
  console.log("\n" + "=".repeat(60));
  console.log("🎉 DEPLOYMENT SUCCESSFUL!");
  console.log("=".repeat(60));
  console.log("\n📋 Contract Addresses:");
  console.log("   ELCARO Token:", tokenAddress);
  console.log("   Strategy NFT:", nftAddress);
  console.log("   Marketplace:", marketplaceAddress);
  console.log("\n🔗 Block Explorer:");
  
  const explorerUrl = {
    mumbai: "https://mumbai.polygonscan.com",
    polygon: "https://polygonscan.com",
    bscTestnet: "https://testnet.bscscan.com",
    bsc: "https://bscscan.com"
  }[network] || "https://etherscan.io";
  
  console.log("   Token:", `${explorerUrl}/address/${tokenAddress}`);
  console.log("   NFT:", `${explorerUrl}/address/${nftAddress}`);
  console.log("   Marketplace:", `${explorerUrl}/address/${marketplaceAddress}`);
  
  console.log("\n💡 Next Steps:");
  console.log("   1. Verify contracts: npm run verify:" + network);
  console.log("   2. Update contract addresses in Python files");
  console.log("   3. Test token transfers and NFT minting");
  console.log("   4. Configure marketplace fees");
  console.log("\n" + "=".repeat(60) + "\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
