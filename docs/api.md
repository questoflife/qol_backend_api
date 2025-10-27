# Quest of Life Backend API Documentation

This document describes all REST API endpoints available in the Quest of Life Backend API.

# Authentication

The API uses Discord OAuth2 for authentication. Sessions are managed via secure HTTP-only cookies (4-hour timeout) with CSRF protection for state-changing operations.

### Authentication Flow

1. User initiates login via `/login`
2. User is redirected to Discord for authorization (using `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`)
3. Discord redirects back to `/oauth/callback` with authorization code
4. If successful: Session is created and user is redirected to `LOGIN_REDIRECT`
5. If failed/cancelled: User is redirected to `LOGIN_REDIRECT` without session
6. Frontend retrieves CSRF token via `/me` endpoint
7. CSRF token must be included in `X-CSRF-Token` header for state-changing requests


# Authentication Endpoints

### `GET /login`

Initiates Discord OAuth2 login flow.

- **Rate Limit:** 5/minute
- **Authentication:** None
- **Response:** `302` redirect to Discord authorization page

### `GET /oauth/callback`

OAuth2 callback endpoint. Discord redirects here after user authorization.

- **Rate Limit:** 10/minute
- **Authentication:** None (OAuth2 flow)
- **Query Parameters:** `code` (string), `state` (string), `error` (string, if authorization failed)
- **Response:** `303` redirect to `LOGIN_REDIRECT` with session cookie (if successful)
- **Errors:** `400` if Discord user fetch fails, `500` if OAuth client not configured

### `POST /logout`

Logs out the current user by clearing the session.

- **Rate Limit:** 10/minute
- **Authentication:** None (operates on current session)
- **Response:** `200` - `{"ok": true}`

### `GET /me`

Retrieves current authenticated user information and CSRF token.

- **Rate Limit:** 30/minute
- **Authentication:** Required (session cookie)
- **Response:** `200` - `{"discord_id": "...", "csrf_token": "..."}`
- **Errors:** `401` if not logged in

---

## User Data Endpoints

### `GET /user/text`

Retrieves the stored text for the current authenticated user. Returns empty string if no text stored.

- **Rate Limit:** 60/minute
- **Authentication:** Required (session cookie)
- **Response:** `200` - `{"text": "..."}`
- **Errors:** `401` if not logged in

### `PUT /user/text`

Sets or updates the stored text for the current authenticated user. Text is stripped of leading/trailing whitespace. Max 10,000 characters. Cannot contain null bytes or excessive control characters (max 10, excluding newlines/tabs).

- **Rate Limit:** 30/minute
- **Authentication:** Required (session cookie + CSRF token)
- **Headers:** `X-CSRF-Token` (required), `Content-Type: application/json`
- **Request Body:** `{"text": "..."}`
- **Response:** `200` - `{"text": "..."}`
- **Errors:** `401` if not logged in, `403` if CSRF token invalid, `413` if body exceeds 50KB, `422` if validation fails

---

## Health Check Endpoints

### `GET /health`

Basic health check for load balancers and monitoring.

- **Rate Limit:** None
- **Authentication:** None
- **Response:** `200` - `{"status": "healthy"}`

### `GET /readiness`

Readiness check that verifies database connectivity.

- **Rate Limit:** None
- **Authentication:** None
- **Response:** `200` - `{"status": "ready"}` or `503` - `{"status": "not ready", "detail": "Database unavailable"}`

---

## Security Features

### CORS
- Only `FRONTEND_ORIGIN` is allowed
- Credentials (cookies) enabled
- Methods: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`
- Headers: `Authorization`, `Content-Type`, `X-CSRF-Token`

### CSRF Protection
All state-changing endpoints (POST, PUT, DELETE) require CSRF token from `/me` in `X-CSRF-Token` header.

### Rate Limiting
All endpoints implement rate limiting (see individual endpoints). Returns `429` when exceeded.

### Request Size Limits
- Maximum request body: 50KB
- Maximum text field: 10,000 characters

### Security Headers
All responses include: `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Referrer-Policy`, `Content-Security-Policy`. Sensitive endpoints also include strict cache control headers.
