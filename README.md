# Alterdata Data Processing System

## Project Description

A web application for processing, analyzing, and reporting financial transactions. The system allows importing CSV files with transactions, validating them, storing them in a database, and generating summary reports for customers and products.

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
4. Start the development server:
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

### Browsing Transactions

- List: `GET /transactions/`  
    Filtering by `customer_id` and `product_id` available
- Details: `GET /transactions/<transaction_id>/`

### Reports

- Customer summary: `GET /reports/customer-summary/<customer_id>/`
    - Optional parameters: `start_date`, `end_date`
    - Returns: total transaction value in PLN, number of unique products, earliest transaction date
- Product summary: `GET /reports/product-summary/<product_id>/`
    - Returns: total quantity, total value in PLN, number of unique customers

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
- SQLite
