const hre = require('hardhat');

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const admin = process.env.PPT_ADMIN_ADDRESS || deployer.address;
  if (!process.env.PPT_ALLOW_DEPLOY) {
    throw new Error('Set PPT_ALLOW_DEPLOY=1 explicitly before deployment');
  }
  const factory = await hre.ethers.getContractFactory('PreussenPoint');
  const contract = await factory.deploy(admin);
  await contract.waitForDeployment();
  console.log(JSON.stringify({
    contract: await contract.getAddress(),
    admin,
    deployer: deployer.address,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString()
  }, null, 2));
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
