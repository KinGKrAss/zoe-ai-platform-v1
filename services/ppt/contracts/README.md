# PPT contract

Solidity `0.8.24`, OpenZeppelin Contracts `5.x`.

Production deployment must use a multisig/admin address. Never commit private keys, seed phrases or wallet JSON files.

Before production minting:

1. compile and test the contract;
2. deploy to a testnet first;
3. verify source on the relevant explorer;
4. record chain ID and contract address in Z1;
5. establish reserve/redemption controls independently;
6. only then enable controlled distribution.
