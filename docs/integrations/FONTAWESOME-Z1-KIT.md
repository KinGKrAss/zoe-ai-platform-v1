# Z1 Command Center — Font Awesome Kit Integration

## Target configuration

- Kit name: `Z1 Command Center`
- Icon selection: `By Icon`
- Technology: `SVG`
- Embed method: `JavaScript`
- Font Awesome version: `Latest 7.x` unless the project pins a release
- Domain limiting: enable when the production Z1 domain is known

## Recommended icon inventory

### Core
- `fa-solid fa-house`
- `fa-solid fa-gauge-high`
- `fa-solid fa-bars`
- `fa-solid fa-magnifying-glass`
- `fa-solid fa-bell`
- `fa-solid fa-user`

### Gaia / Real Estate
- `fa-solid fa-building`
- `fa-solid fa-city`
- `fa-solid fa-map-location-dot`
- `fa-solid fa-location-dot`
- `fa-solid fa-key`

### Fortuna / Finance
- `fa-solid fa-coins`
- `fa-solid fa-euro-sign`
- `fa-solid fa-chart-line`
- `fa-solid fa-chart-pie`
- `fa-solid fa-wallet`
- `fa-solid fa-money-bill-transfer`

### Electra / Energy
- `fa-solid fa-bolt`
- `fa-solid fa-solar-panel`
- `fa-solid fa-wind`
- `fa-solid fa-leaf`
- `fa-solid fa-plug`
- `fa-solid fa-gauge`

### Carbon Intelligence
- `fa-solid fa-cloud`
- `fa-solid fa-smog`
- `fa-solid fa-industry`
- `fa-solid fa-arrow-trend-up`
- `fa-solid fa-arrow-trend-down`
- `fa-solid fa-circle-exclamation`
- `fa-solid fa-circle-check`

### Zoe / AI
- `fa-solid fa-brain`
- `fa-solid fa-robot`
- `fa-solid fa-sparkles`
- `fa-solid fa-comments`
- `fa-solid fa-lightbulb`
- `fa-solid fa-microchip`

### System
- `fa-solid fa-server`
- `fa-solid fa-database`
- `fa-solid fa-code`
- `fa-solid fa-shield-halved`
- `fa-solid fa-lock`
- `fa-solid fa-gear`
- `fa-solid fa-circle-nodes`

## Integration contract

Font Awesome supplies the icon assets; Z1 owns semantic naming and component usage. The application must not depend on a Kit code being committed to Git.

Store the hosted Kit code only as a deployment secret/configuration value, for example:

```text
FONTAWESOME_KIT_CODE=<secret>
```

The application should render the Kit script from configuration and fail gracefully when the value is absent.

## HTML integration

```html
<script
  src="https://kit.fontawesome.com/YOUR_KIT_CODE.js"
  crossorigin="anonymous">
</script>
```

Replace `YOUR_KIT_CODE` at deployment time. Never commit a private API key or account credential.

## Z1 semantic mapping

| Z1 module | Semantic icon |
|---|---|
| CORE | `fa-gauge-high` |
| GAIA | `fa-building` |
| FORTUNA | `fa-coins` |
| ELECTRA | `fa-bolt` |
| CARBON | `fa-cloud` / `fa-leaf` |
| ZOE | `fa-brain` |
| SYSTEM | `fa-server` |

## Custom Z1 icons

If a Font Awesome Pro Kit is available, custom Z1/Zoë/Electra/Carbon icons can be uploaded later. Keep those custom assets in the Kit rather than hard-coding them into application code. Font Awesome assigns Kit-uploaded icons their own Kit prefix.
