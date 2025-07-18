# Alterdata Data Processing System

## Project Description

A web application for processing, analyzing, and reporting financial transactions. The system allows importing CSV files with transactions, validating them, storing them in a database, and generating summary reports for customers and products. Uses Celery and Redis for synchronous file processing.

## Directory Structure

- `backend/` – main Django application directory
    - `api/` – handles import, listing, and transaction details
    - `authentication/` – user management and authorization
    - `core/` – project configuration, settings, routing
    - `lib/` – additional libraries
    - `reports/` – summary report generation

## Installation

1. Clone the repository.
2. Install dependencies:
     ```sh
     pip install -r requirements.txt
     ```
3. Run migrations:
     ```sh
     python backend/manage.py migrate
     ```
4. Start Redis server (required for Celery):
     ```sh
     redis-server
     ```
5. Start Celery worker:
     ```sh
     celery -A backend worker -l info
     ```
6. Start the development server:
     ```sh
     python backend/manage.py runserver
     ```

## Usage

### Transaction Import

- Endpoint: `POST /transactions/upload`
- Accepts a CSV file with fields:  
    `transaction_id, timestamp, amount, currency, customer_id, product_id, quantity`
- File validation:  
    - Only `.csv` files
    - Maximum size: 50 MB
    - Checks header correctness and data types
- **Background processing:**  
    Uploaded files are processed asynchronously using Celery. The user receives a task ID to check the status.

**Sample response after file upload:**
```json
{
    "message": "CSV file is being processed.",
    "file_name": "data.csv",
    "task_id": "ff1adde1-30b7-41d7-b354-7bb666b9a55f"
}
```

### Browsing Transactions

- List: `GET /transactions/`  
    Filtering by `customer_id` and `product_id` available
- Details: `GET /transactions/<transaction_id>/`

**Sample response for a transaction list:**
```json
{
    "count": 16,
    "next": "http://127.0.0.1:8000/transactions/?page=2",
    "previous": null,
    "results": [
        {
            "transaction_id": "216c5b6b-db29-4b52-a229-a34c5453ae6f",
            "timestamp": "2025-07-15T21:12:07.469495Z",
            "amount": "199.99",
            "currency": "PLN",
            "customer_id": "d5a925c7-a57f-4b47-b313-dbbf849de93a",
            "product_id": "a3c965dc-1130-4131-8c34-13ed8ef84406",
            "quantity": 2
        },
        {
            "transaction_id": "a2be5756-fcdb-4626-bee2-82c13269531c",
            "timestamp": "2025-07-15T21:12:08.149812Z",
            "amount": "49.50",
            "currency": "EUR",
            "customer_id": "fd26bae1-30f1-4965-9fff-f784de6f78db",
            "product_id": "7aab2d1a-ee88-4456-8631-fc30dc8ee210",
            "quantity": 1
        },
        ...
    ]
}
```

**Sample response for transaction details:**
```json
{
    "transaction_id": "89053e31-fb70-4cde-9c1d-806abeb27956",
    "timestamp": "2025-07-15T21:17:27.309702Z",
    "amount": "199.99",
    "currency": "PLN",
    "customer_id": "32211460-546a-4227-b4d1-3a2890014b8f",
    "product_id": "17a419c1-a012-4a21-8976-b823a09dd4e4",
    "quantity": 2
}
```

### Reports

- Customer summary: `GET /reports/customer-summary/<customer_id>/`
    - Optional parameters: `start_date`, `end_date`
    - Returns: total transaction value in PLN, number of unique products, earliest transaction date
- Product summary: `GET /reports/product-summary/<product_id>/`
    - Returns: total quantity, total value in PLN, number of unique customers

**Sample response for customer summary:**
```json
{
  "customer_id": "f3a2e210-bd6a-49c9-812e-bd4b23cd1e12",
  "total_value_pln": 249.49,
  "unique_products": 2,
  "earliest_transaction": "2025-07-13T08:45:10Z"
}
```

**Sample response for product summary:**
```json
{
  "product_id": "aa12e3f5-987a-48ec-802a-d0c821fef302",
  "total_quantity": 2,
  "total_value_pln": 199.99,
  "unique_customers": 1
}
```

### Authorization

- API access requires authentication (JWT, by default via Django REST Framework).
- Users have roles (`regular`, `admin`).

Authorization endpoints:

1. POST `/auth/token`
         - Allows users to log in to the system.
         - Requires authentication data (username and password).
         - Returns an access token upon successful authentication.
    
2. POST `/auth/register`
         - Allows registration of a new user.
         - Requires registration data (username and password).
         - Returns registration confirmation or access token.
    
3. POST `/auth/token/refresh`
         - Used to refresh the access token.
         - Requires a valid refresh token.
         - Returns a new access token.

**Sapmle token respone**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Sample register response**
```json
{
  "message": "User registered successfully.",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Asynchronous Processing (Celery & Redis)

- Celery is used for background processing of transaction imports.
- Redis is required as the message broker.
- Task status can be checked via dedicated endpoints:
    - `GET /tasks/status/<task_id>/` – returns current status and result if available.

**Sample task status response:**
```json
{
    "task_id": "796db546-bbde-47ae-9223-cbd0babe5cb8",
    "status": "SUCCESS",
    "result": {
        "errors": [...]
    }
}
```

## Tests

Unit and integration tests are located in:
- `backend/api/tests/`
- `backend/reports/tests/`

Run tests:
```sh
pytest backend/
```

## Configuration

- Main settings: [backend/core/settings.py](backend/core/settings.py)
- Logging: [backend/lib/logging_config.py](backend/lib/logging_config.py)
- Exchange rates: [backend/reports/lib/constants.py](backend/reports/lib/constants.py)
- Celery configuration: [backend/core/celery.py](backend/core/celery.py)

## Sample CSV File

```
transaction_id,timestamp,amount,currency,customer_id,product_id,quantity
d4a3f861-6c22-44f7-8121-09df0d5b79f3,2025-07-14T12:15:30Z,199.99,PLN,f3a2e210-bd6a-49c9-812e-bd4b23cd1e12,aa12e3f5-987a-48ec-802a-d0c821fef302,2
a1f3e2b6-78fd-4a2d-9e2b-bd9f4f9a7261,2025-07-13T08:45:10Z,49.50,EUR,77c8ab6a-d8fa-4f27-b7a3-d11c1a1f97f6,92b06a1d-5c67-43f7-b39a-beb4d6fabb12,1
```

## Technologies

- Python 3.x
- Django 5.x
- Django REST Framework
- Celery
- Redis
- SQLite

