# Configuration Guide

This document explains how environment variables and configuration files work in this project.

## Environment File Structure

The project uses a layered configuration system with environment files:

```
qol_backend_api/
├── app.env.example          # Production config template (committed)
├── app.env                  # Production config (gitignored)
├── dev_example/dev/         # Development config templates (committed)
│   ├── dev.env
│   └── db.env
└── dev/                     # Development config (gitignored)
    ├── dev.env
    └── db.env
```

The `dev_example/` directory contains additional configuration files for the recommended initial setup. See [Gitignore Strategy](#gitignore-strategy) below for more details.

## Configuration Files and Precedence

Environment variables are loaded in this order (later values override earlier ones):

1. **app.env** - Sets up production configuration including database connections
2. **dev.env** - Optionally overwrites app.env settings for development setup (when using dev setup)
3. **db.env** - Overwrites all settings with Docker database configuration when launching the database in Docker

## Gitignore Strategy

- **Committed:** Templates in `dev_example/dev/` and `app.env.example`
- **Gitignored:** Actual config in `dev/` and `app.env`

This allows:
- Sharing configuration templates with the team
- Keeping sensitive credentials out of git
- Easy local customization without affecting the repository
