# Z1 Command Center

Minimal runnable M2 application shell for the Z1 / Zoë platform.

## Run locally

```bash
npm install
npm start
```

Open `http://localhost:3000`.

## API

- `GET /api/health` – application health
- `GET /api/modules` – Z1 module registry

This is the application shell, not the completed production intelligence layer. Zoë reasoning, authentication, persistent memory access, connectors and domain modules are added in subsequent M2 increments.
