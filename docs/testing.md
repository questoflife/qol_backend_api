# Testing
Uses pytest

For instructions look at the `README.md`.

## Configuration
`.devcontainer/.env` also contains env variables that specify the configuration for testing.
It is loaded in `tests/settings.py`.

## Structure
*Run Locally:*
- `test_database.py` contains tests of the database layer, i.e. communication between this app and the MySQL server.
- `test_api.py` contains tests of the api endpoints and their functionality. It bypasses security.#

*Run on Server (from `dev` branch):*
- `test_oauth_integration.py` contains some tests for oauth and security. It does not communicate with the oauth server itself. True integration tests must be performed manually from the dev website frontend.

