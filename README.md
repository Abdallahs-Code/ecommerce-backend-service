# Ecommerce Backend Service

This project is a simple ecommerce backend built using FastAPI, SQLAlchemy, SQLite, and JWT authentication.

## Requirements

- Python 3.10 or higher
- pip

## How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/Abdallahs-Code/ecommerce-backend-service.git
cd ecommerce-backend-service
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a .env file

In the root directory of the project, create a file named:

```
.env
```

Add the following content:

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=supersecretkey123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

You can change these values if needed.

- `DATABASE_URL` defines where the SQLite database file is stored.
- `SECRET_KEY` is used to sign JWT tokens.
- `ALGORITHM` is the JWT signing algorithm.
- `ACCESS_TOKEN_EXPIRE_MINUTES` controls how long access tokens remain valid.

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

The server will run at:

```
http://127.0.0.1:8000
```

Interactive API documentation and testing is available at:

```
http://127.0.0.1:8000/docs
```

## Database

The SQLite database file (`app.db`) is created automatically the first time the application runs.

It will appear in the project root directory unless you change the `DATABASE_URL`.

### Inspecting the Database

At any time, you can inspect the database by running:

```bash
python inspect_db.py
```

This script will display the existing tables and their contents.

## Authentication

Authentication is handled using JWT tokens stored in cookies.

The following endpoints are publicly accessible:

- `POST /api/auth/signup`
- `POST /api/auth/login`

All other endpoints require authentication.