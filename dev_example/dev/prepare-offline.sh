#!/bin/bash

# Script to prepare Docker environment for offline use
# Run this when you have internet connection to cache all required images

set -e

# Pull BuildKit frontend (the dockerfile:1 parser)
docker pull docker.io/docker/dockerfile:1

# Pull base images used in Dockerfiles
docker pull python:3.12-slim

# Build Docker images for offline use

# Production builds
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml -f dev/docker-compose.prod.db-override.yml build

# Development builds
docker compose -f dev/docker-compose.dev.yml build runtime-base testing-builder
docker compose -f dev/docker-compose.dev.yml build
docker compose -f dev/docker-compose.dev.yml -f dev/docker-compose.dev.db-override.yml build runtime-base testing-builder
docker compose -f dev/docker-compose.dev.yml -f dev/docker-compose.dev.db-override.yml build

echo "Docker environment prepared for offline use."
