# Architecture Guide

This document provides a deep dive into the project's architecture and code structure.

## Layers

The application is designed with a classic three-layer architecture to separate concerns:

```
[API Layer] → [Service/Backend Layer] → [Repository/Database Layer]
```

1.  **API Layer (`src/api/`)**
    -   **Responsibility:** Handles all HTTP request/response logic. It defines the API endpoints, parses incoming data (using Pydantic schemas), and formats the responses.
    -   **Implementation:** Built with FastAPI. It should not contain any business logic. It calls the service layer to perform actions.

2.  **Service/Backend Layer (`src/backend/`)**
    -   **Responsibility:** Contains the core business logic of the application. It orchestrates operations, performs validation, and makes decisions.
    -   **Implementation:** Plain Python functions. It interacts with the repository layer to access and store data.

3.  **Repository/Database Layer (`src/database/`)**
    -   **Responsibility:** Manages all interactions with the database. It handles creating, reading, updating, and deleting (CRUD) data.
    -   **Implementation:** Uses SQLAlchemy 2.0 for asynchronous database operations. This layer should not contain any business logic.

## Request Flow Example

Here’s how a request to set a user's key-value pair flows through the system:

1.  A `POST /user/data` request hits the API.
2.  The endpoint in `src/api/user_dict.py` receives the request.
3.  It validates the incoming JSON against the `UserValue` Pydantic schema.
4.  The API calls the `set_user_key_value` function in `src/backend/service.py`.
5.  The service layer might perform additional logic (e.g., checking user permissions).
6.  The service layer then calls the `set_key_value` function in `src/database/repository.py`.
7.  The repository function constructs and executes the SQL query using SQLAlchemy to insert or update the data in the database.
8.  The result is returned up the chain.

## Key Modules

-   `src/app.py`: The main entry point of the application. It initializes the FastAPI app and includes the API routers.
-   `src/backend/auth.py`: Handles authentication logic, currently using a mocked Discord OAuth2 flow.
-   `src/database/models.py`: Defines the SQLAlchemy database models (i.e., the table schemas).
-   `src/database/config.py`: Manages database session and connection settings.
