require('@nomicfoundation/hardhat-toolbox');

const networks = {};

// Production is intentionally configured only from CI/runtime secrets.
// No RPC URL or private key is committed to the repository.
if (process.env.PPT_RPC_URL && process.env.PRIVATE_KEY) {
  networks.production = {
    url: process.env.PPT_RPC_URL,
    accounts: [process.env.PRIVATE_KEY],
  };
}

module.exports = {
  solidity: '0.8.24',
  paths: { sources: '.', tests: './test', cache: './cache', artifacts: './artifacts' },
  networks,
};
