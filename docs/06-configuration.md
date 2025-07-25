# Configuration Guide

## Quick Start (Works out of the box)

The project includes default configuration files that allow it to run immediately after cloning:

```bash
git clone <repository>
cd qol_backend_api
docker compose up --build dev-db
```

## Customizing Configuration

### Default vs Override Files

The project uses a two-layer configuration system:

- **Default files** (committed to git): `config/*.env.default`
- **Override files** (optional, gitignored): `config/*.env`

### To customize settings:

1. Copy a default file:
   ```bash
   cp config/db.env.default config/db.env
   ```

2. Edit your copy:
   ```bash
   # config/db.env
   MYSQL_PASSWORD=my-secure-password
   DATABASE_URL=mysql://qol_user:my-secure-password@db:3306/qol_backend
   ```

3. Your overrides will be used automatically

### Command-line overrides

You can also override environment files using Docker Compose:

```bash
# Use a different env file entirely
docker compose --env-file config/production.env up prod

# Override specific variables
MYSQL_PASSWORD=custom-password docker compose up dev-db
```

## Configuration Files

| File | Purpose | Required |
|------|---------|----------|
| `config/app.env.default` | Default app settings | ✓ (committed) |
| `config/app.env` | App overrides | Optional |
| `config/db.env.default` | Default database settings | ✓ (committed) |
| `config/db.env` | Database overrides | Optional |
| `config/dev.env.default` | Default dev settings | ✓ (committed) |
| `config/dev.env` | Dev overrides | Optional |
| `config/dockerfile-dev.env.default` | Default Docker build config | ✓ (committed) |
| `config/dockerfile-dev.env` | Docker build overrides | Optional |

## Loading Order

Environment variables are loaded in this order (later overrides earlier):

1. `*.env.default` files (defaults)
2. `*.env` files (your overrides)
3. Command-line variables (highest priority)
