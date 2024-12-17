async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contract with account:", deployer.address);
  
    const CredentialManager = await ethers.getContractFactory("CredentialManager");
    
    try {
        const contract = await CredentialManager.deploy();
        
        // Explicitly wait for the deployment transaction
        const deployedContract = await contract.waitForDeployment();
  
        console.log("CredentialManager deployed to:", await deployedContract.getAddress());
    } catch (error) {
        console.error("Deployment failed:", error);
        throw error;
    }
}
  
main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });