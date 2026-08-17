# Finanzfuchs

Finanzfuchs is the financial-intelligence layer between Z1/FORTUNA and PPT.

Responsibilities:

- monitor token supply and transfer activity;
- consume verified reserve snapshots;
- track configured wallet balances without receiving private keys;
- calculate coverage indicators from independently verified data;
- flag risk states and reconciliation breaks;
- publish normalized observations to Z1.

Finanzfuchs never stores seed phrases or private keys and never mints PPT directly.
