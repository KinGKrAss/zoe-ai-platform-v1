const $=id=>document.getElementById(id);
const hasEthereum=typeof window.ethereum!=='undefined';
$('status').textContent=hasEthereum?'● Wallet verfügbar':'● Wallet nicht erkannt';
$('connect').addEventListener('click',async()=>{
  if(!hasEthereum){alert('Bitte MetaMask installieren/aktivieren.');return;}
  try{const accounts=await window.ethereum.request({method:'eth_requestAccounts'});$('status').textContent=`● Verbunden: ${accounts[0].slice(0,6)}…${accounts[0].slice(-4)}`;}catch(e){console.error(e)}
});
$('pay').addEventListener('click',()=>alert('PPT Payment wird über MetaMask signiert. Contract, Chain und Empfänger müssen vor Production aus Z1-Konfiguration geladen werden.'));
