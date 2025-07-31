# Architecture Guide

This document explains the codebase structure and architectural patterns used in this project.

## Three-Layer Architecture

The application follows a clean three-layer architecture with strict dependency flow:

```
src/api/     →     src/backend/     →     src/database/
(FastAPI)          (Business Logic)      (SQLAlchemy)
```

**Dependency Rule:** Each layer only depends on the layer below it:
- API layer calls Backend layer functions
- Backend layer calls Database layer functions  
- Database layer only interacts with the database

## API Endpoints

### GET Endpoints

#### GET /user/dict/{key}

Retrieve a value by key for the current user.

- **Path:** `key` - The key to retrieve
- **Auth:** Current user (from auth)
- **Returns:** `{key, value}` - Returns empty string if key doesn't exist

### POST Endpoints

#### POST /user/dict

Set a key-value pair for the current user.

- **Body:** `{key, value}` - Key-value pair to store
- **Auth:** Current user (from auth)  
- **Returns:** `{message}` - Success confirmation

## Authentication (Mocked)

Currently uses mocked authentication in `src/backend/auth.py`:
- All requests are assigned to the same example user
- No actual authentication is performed
- OAuth integration is planned for future implementation
