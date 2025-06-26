# Quest of Life Backend API

Async Python/FastAPI service that powers the Quest of Life website.  
Runs on **Northflank**; the static front-end lives on GitHub Pages.

## Backend Funcionality
- Authentication via Discord OAuth2 for api calls.  


---

## Tech stack

| Layer             | Choice |
| ----------------- | ------ |
| Language          | Python 3.12 |
| Web framework     | FastAPI (async) |
| ASGI server       | Uvicorn |
| ORM / DB driver   | SQLAlchemy 2 (async) |
| Database          | MySQL 8 (Northflank add-on) |
| Dependency mgr    | Poetry |
| Container         | Podman |
| CI / CD           | GitHub Actions → Northflank Pipeline |

---

## Northflank deployment (free tier)

| Role            | Resource name | Plan             |
| --------------- | ------------- | ---------------- |
| **Live API**    | `api-prod`    | `nf-compute-10` (256 MB) |
| **Staging API** | `api-dev` *¹* | `nf-compute-10` (256 MB) |
| **Database**    | `mysql-qol`   | `nf-compute-20` (512 MB) + 4 GB disk |

> *¹ `api-dev` can be scaled to 0 replicas when you’re not actively testing to save costs*

* Only **two** long-running services are allowed on the Developer Sandbox—`api-prod` and `api-dev` use both slots.  
* There is **one** managed add-on (MySQL). **Both services share it, so never run destructive migrations on `api-dev` that could affect prod data.**
