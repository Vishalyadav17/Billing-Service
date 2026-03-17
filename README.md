# Billing System

A billing application built with FastAPI and PostgreSQL.

## Setup

**Prerequisites:** Python 3.11+, PostgreSQL running locally

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE billing_system;"

# Install dependencies
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create .env file in the root directory
# Add your Postgres credentials to the .env file
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/billing_system

# Run
python main.py
```

App runs at http://localhost:8000. Tables are created automatically on first startup.

## Pages

| URL | Description |
|---|---|
| `/billing` | Billing form + bill result (same page) |
| `/purchases` | Purchase history search by email |
| `/purchases/{id}` | Single purchase detail |
| `/admin/products` | Product management |
| `/docs` | Swagger UI |

## Test Flow

1. Go to `/admin/products` and click **Seed Default Products** to load sample data.
2. Go to `/billing`, enter a customer email and click **Add New** to add products (e.g. `PROD001`, qty `2`).
3. Fill in denomination counts for the shop's available cash, enter the amount paid and click **Generate Bill**.
4. The bill result appears on the same page — showing per-item breakdown, totals and change denomination.
5. Go to `/purchases`, search by the same email to see purchase history.

## Assumptions

1. Denominations are fixed as `[500, 50, 20, 10, 5, 2, 1]` — these represent the bills/coins available in the shop.
2. Change calculation uses a greedy algorithm (largest denomination first), constrained by the counts entered in the form.
3. Rounded-down net price = `math.floor(net_price)` — this is the amount the customer actually pays.
4. Balance = `cash_paid - rounded_net_price`.
5. Stock is decremented on every bill generation. Billing is blocked if stock is insufficient.
6. Unit price and tax % are snapshotted at bill time so purchase history stays accurate even if product prices change later.
7. Invoice email is sent as a background task via Gmail SMTP. Set `SMTP_USER` and `SMTP_PASS` in `.env` to enable it (see Setup above). If not configured, the email step is skipped gracefully and the bill is still generated normally.
8. Product codes are user-defined strings (e.g. `PROD001`) and are case-insensitive — auto-uppercased on save.
9. No authentication is needed — this is an internal shop tool.
