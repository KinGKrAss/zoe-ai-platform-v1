import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const port = Number(process.env.PORT || 3000);

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', system: 'Z1 Command Center', service: 'z1-command-center', version: '0.1.0' });
});

app.get('/api/modules', (_req, res) => {
  res.json([
    { id: 'zoe', name: 'Zoë Core', status: 'online' },
    { id: 'gaia', name: 'GAIA', status: 'standby' },
    { id: 'fortuna', name: 'FORTUNA', status: 'standby' },
    { id: 'electra', name: 'ELECTRA', status: 'standby' },
    { id: 'diplomatie', name: 'DIPLOMATIE', status: 'standby' },
    { id: 'ppt', name: 'PPT', status: 'standby' }
  ]);
});

app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`Z1 Command Center listening on http://localhost:${port}`);
});
