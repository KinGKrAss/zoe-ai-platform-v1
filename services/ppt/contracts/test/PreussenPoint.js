const { expect } = require('chai');
const { ethers } = require('hardhat');

describe('PreussenPoint', function () {
  async function fixture() {
    const [admin, user] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory('PreussenPoint');
    const token = await Factory.deploy(admin.address);
    await token.waitForDeployment();
    return { token, admin, user };
  }

  it('has the expected identity and role-controlled minting', async function () {
    const { token, admin, user } = await fixture();
    expect(await token.name()).to.equal('Preussen Point');
    expect(await token.symbol()).to.equal('PPT');
    await expect(token.connect(user).mint(user.address, 1n)).to.be.reverted;
    await token.mint(user.address, 100n);
    expect(await token.balanceOf(user.address)).to.equal(100n);
  });

  it('pauses transfers and allows holder burn', async function () {
    const { token, admin, user } = await fixture();
    await token.mint(user.address, 100n);
    await token.pause();
    await expect(token.connect(user).transfer(admin.address, 1n)).to.be.revertedWith('PPT transfers paused');
    await token.unpause();
    await token.connect(user).burn(10n);
    expect(await token.balanceOf(user.address)).to.equal(90n);
  });
});
