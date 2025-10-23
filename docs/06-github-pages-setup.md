# GitHub Pages Integration Setup

## Discord OAuth Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. OAuth2 → Add Redirect URI:
   ```
   <YOUR_BACKEND_URL>/oauth/callback
   ```

## Northflank Environment Variables

```bash
FRONTEND_ORIGIN=https://questoflife.github.io/qol_website_dev
API_BASE_URL=<YOUR_BACKEND_URL>
DISCORD_CLIENT_ID=<your_client_id>
DISCORD_CLIENT_SECRET=<your_client_secret>
SECRET_KEY=<your_secret_key>

# Database config
DB_HOST=<your_db_host>
DB_PORT=3306
DB_NAME=qol
DB_USER=<your_db_user>
DB_PASSWORD=<your_db_password>

# Optional
RUN_INTEGRATION_TESTS=true
```

## Update Test Page

Edit `qol_website_dev/api-test.html` line 223:
```javascript
const API_BASE = '<YOUR_BACKEND_URL>';
```

## OAuth Flow

1. User clicks "Login" → redirects to `<BACKEND>/login`
2. Backend redirects to Discord
3. Discord redirects back to `<BACKEND>/oauth/callback`
4. Backend sets session cookie and redirects to `<FRONTEND>/welcome`

## Troubleshooting

- **Cookie issues**: Verify `FRONTEND_ORIGIN` has no trailing slash
- **CORS errors**: Check browser console, verify environment variables match
- **401 errors**: Session expired or cookies not sent - check `credentials: 'include'` in fetch calls
