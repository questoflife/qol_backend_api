# Development Guide

Essential workflow and technical requirements for contributing to this project.

## Git Workflow

We have three managed branches:

- **`main`** - Production releases only - live
- **`qa`** - QA before a new release
- **`dev`** - For testing on the deployment servers. This resource is shared by all developers, so perform as many checks as possible locally first.

Developers can create other private branches for their own development with direct commits, but these three branches should only ever be updated with pull requests.

If you change development files for local configuration, please consider carefully whether they should be updated as defaults for everybody, or only kept on your private branches.

## Technical Requirements

### Line Endings (Important for Windows!)

**All files must use LF (Unix) line endings**, especially on Windows machines.

This is critical for the VS Code container setup - the bind mount shares files between Windows and the Linux container. Mixed line endings will cause issues.

The project is already configured for this in `.editorconfig`, but if you modify editor settings, ensure LF line endings are maintained:

```
* text=auto eol=lf
```

### Configuration Management

**Never commit sensitive data** (passwords, API keys).
Use .env files for locally storing sensitive information and local configurations.
