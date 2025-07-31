# Development Guide

Essential workflow and technical requirements for contributing to this project.

## Git Workflow

We use a simple two-branch workflow:

- **`main`** - Production releases only
- **`dev`** - Integration branch for development

**Key points:**
- Create feature branches from `main`
- Submit pull requests to `dev` (local tests must pass, code review required)
- Online unit and integration tests run on `dev`
- Releases are created from `dev` to `main`

## Technical Requirements

### Line Endings (Important for Windows!)

**All files must use LF (Unix) line endings**, especially on Windows machines.

This is critical for the VS Code container setup - the bind mount shares files between Windows and the Linux container. Mixed line endings will cause issues.

The project is already configured for this, but if you modify editor settings, ensure LF line endings are maintained:

```
* text=auto eol=lf
```

### Configuration Management

- **Never commit sensitive data** (passwords, API keys)
- Use the template → local copy pattern:
  - Modify templates in `dev_example/dev/` to commit configuration changes
  - Your local copies in `dev/` are gitignored for personal preferences
- See [Configuration Guide](02-configuration.md) for details
