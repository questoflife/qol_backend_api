# Environment Configuration
Environment variables for development are specified in `.devcontainer/.env`. See `.env.example` for documentation and examples.

For production, environment variables must be injected manually into the Docker container. How this is done is specific to the service you use to host the app. 

# Repo Structure
`src` contains the code required for production.
`tests` contains tests

`src` is spit into three layers: `api`, `backend`, and `database`.
- **`api`** contains the code relevant to API, including all of the security, api endpoints, and networking. Everything FastAPI lives here. It calls functions from `backend`.
- **`backend`** implements all of the computations and backend logic. If we're only retrieving information from the database, then it is trivial and only forwarding functions from `database`. If any more complicated computations need to be performed, this is where they will be implemented.
- **`database`** contains the code for interacting with the database via SQLAlchemy, including error handling and checks. It provides functions that can safely be used by the `backend` to retrieve or store data in the database.

