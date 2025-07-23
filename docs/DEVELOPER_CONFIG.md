# Developer Configuration Guide

This document explains how to customize your development environment without affecting the shared project configuration.

## Developer-Specific Configuration

This project supports developer-specific configuration that won't be tracked by Git, allowing each developer to customize their environment without affecting others.

## Available Configuration Files

1. **`config/app.env`** - Application environment variables
2. **`config/db.env`** - Database configuration
3. **`config/dev.env`** - Developer-specific environment overrides
4. **`config/python-dev-packages.txt`** - User-specific Python packages for development
5. **`config/apt-build-packages.txt`** - Build-time apt dependencies for compiling Python packages
6. **`config/apt-runtime-packages.txt`** - Runtime tools for interactive development

All these files are gitignored and can be customized per developer.

## Setup Instructions

### Environment Variables

1. **Application Settings**: Copy `config/app.env.example` to `config/app.env` and customize (optional)
   ```bash
   cp config/app.env.example config/app.env
   # Edit config/app.env with your preferred settings
   ```

2. **Database Settings**: Copy `config/db.env.example` to `config/db.env` and customize (required for database profiles)
   ```bash
   cp config/db.env.example config/db.env
   # Edit config/db.env with your database configuration
   ```

3. **Developer Settings**: Copy `config/dev.env.example` to `config/dev.env` and customize
   ```bash
   cp config/dev.env.example config/dev.env
   # Edit config/dev.env with your developer-specific settings
   ```

### Development Tools

1. **Build Dependencies**: Copy `config/apt-build-packages.txt.example` to `config/apt-build-packages.txt` and customize
   ```bash
   cp config/apt-build-packages.txt.example config/apt-build-packages.txt
   # Edit config/apt-build-packages.txt to add/remove build dependencies for Python packages
   ```

2. **Runtime Packages**: Copy `config/apt-runtime-packages.txt.example` to `config/apt-runtime-packages.txt` and customize
   ```bash
   cp config/apt-runtime-packages.txt.example config/apt-runtime-packages.txt
   # Edit config/apt-runtime-packages.txt to add/remove interactive development tools
   ```

3. **Custom Python Packages**: Copy `config/python-dev-packages.txt.example` to `config/python-dev-packages.txt` and customize
   ```bash
   cp config/python-dev-packages.txt.example config/python-dev-packages.txt
   # Edit config/python-dev-packages.txt to add or remove Python packages
   ```

### How Development Packages Work

The Docker development environment uses a streamlined approach to managing development dependencies:

1. **Base Project Dependencies**:
   - Core dependencies are defined in `pyproject.toml` under the `main` and `testing` groups
   - These dependencies are always installed in their respective Docker images

2. **Developer-Specific Dependencies**:
   - Personal development tools are specified in `config/python-dev-packages.txt`
   - Each line should contain one package (with optional version specifier)
   - Comments (lines starting with #) are ignored
   - Example:
     ```
     black==23.7.0
     mypy>=1.8.0
     pylint
     # This line is ignored
     ```

3. **System Packages**:
   - Build dependencies are specified in `config/apt-build-packages.txt` (needed for Python package compilation)
   - Runtime tools are specified in `config/apt-runtime-packages.txt` (for interactive development)
   - Examples:
     ```
     # In config/apt-build-packages.txt (build-time dependencies)
     gcc
     libffi-dev
     default-libmysqlclient-dev
     ```
     ```
     # In config/apt-runtime-packages.txt (runtime tools)
     vim
     git
     curl
     postgresql-client
     ```

4. **Docker Integration**:
   - During container build, the Dockerfile reads these files and installs the specified packages
   - This happens at build time, so you need to rebuild your dev container when changing these files
   - Packages are installed with Poetry into a separate "dev" group
   ```

## How It Works

## Using Docker for Development

The project's Dockerfile supports a multi-stage build process that includes a customizable development environment:

1. **Build a Development Image**
   ```bash
   # Build the development image with your custom packages
   docker build -t qol-backend-dev --target dev .
   ```

2. **Run Development Container**
   ```bash
   # Run container with your code mounted as a volume for live editing
   docker run -it --name qol-dev -p 8080:8080 -v $(pwd):/qol_backend_api qol-backend-dev
   ```

3. **Access Your Container**
   ```bash
   # If container is already created but stopped
   docker start qol-dev
   
   # Get a shell in the running container
   docker exec -it qol-dev bash
   ```

4. **Run Your Code**
   ```bash
   # Inside the container
   python -m src.app
   ```

### Tips for Docker Development

- **Rebuild After Package Changes**: If you update `config/python-dev-packages.txt` or `config/apt-*-packages.txt`, you need to rebuild the Docker image:
  ```bash
  docker build -t qol-backend-dev --target dev .
  ```

- **Volume Mounting**: The `-v $(pwd):/qol_backend_api` flag mounts your local code into the container, so you can edit files locally and run them in the container without rebuilding.

- **Port Forwarding**: The `-p 8080:8080` flag forwards port 8080 from the container to your host machine.

### Environment Variables

- `config/app.env` defines basic application settings (optional, used by all services)
- `config/db.env` defines database connection settings (required for database profiles only)
- `config/dev.env` can override settings in the other files (optional, used by dev services only)

Environment file usage by service:
- Production services: `config/app.env` only
- Testing services: `config/app.env` only (plus `config/db.env` for testing-db)
- Development services: `config/app.env` and `config/dev.env` (plus `config/db.env` for dev-db)

The precedence order (later files override earlier ones):
1. `config/app.env` (loaded first - lowest priority)
2. `config/db.env` (loaded second in database services)
3. `config/dev.env` (loaded last in development services - highest priority)

### Development Tools

- `config/apt-build-packages.txt` and `config/apt-runtime-packages.txt` list apt packages to install in the development container
- `config/python-dev-packages.txt` lists all Python packages for your development environment

These are automatically installed during container build.

**How Dependency Management Works**:
- `pyproject.toml`: Contains only production and testing dependencies
  - Main dependencies (always installed)
  - Testing dependencies (installed in testing and dev environments)
- `.devpackages`: Contains all development tools specific to your workflow

**Benefits of This Approach**:
1. Clean separation between production/testing code and development tools
2. Development tools don't affect the main project's dependency resolution
3. Each developer can customize their environment without affecting others
4. The lock file remains focused on production and testing dependencies

## Usage Examples

### Running with Developer Configuration

```bash
# Development without database
docker compose --profile dev up --build

# Development with database
docker compose --profile dev-db --profile db up --build
```

### Adding Custom Development Tools

1. Add apt packages to `.dev-apt-packages`:
   ```
   vim
   git
   postgresql-client
   ```

2. Add Python packages to `.devpackages`:
   ```
   # My preferred development packages
   jupyter
   ipykernel
   httpie
   ```

3. Rebuild the development container:
   ```bash
   docker compose --profile dev up --build
   ```

## Best Practices

1. **Keep it minimal**: Only add packages you actually need
2. **Document non-standard packages**: If your code requires specific tools, document them
3. **Version consistency**: Try to specify package versions for repeatability
4. **Backup your configs**: Consider keeping copies of your configs in a personal location

## Troubleshooting

### Package installation failures

If an apt package fails to install, check:
- Package name is correct
- No comments or empty lines in the package specification
- The package is available in the Debian repositories

If a Python package fails to install, check:
- Package name is correct
- Version specifier is valid
- No conflicts with existing dependencies
