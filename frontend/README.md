# DUKA AI – Frontend
React + Vite + React Router + Axios + Recharts.

## Run
```
npm install
cp .env.example .env     # set VITE_API_URL to your FastAPI base URL
npm run dev
```
## Connecting the backend
The frontend API base defaults to `http://localhost:8000/api`; endpoint paths and field adapters live in `src/services/`. The backend currently supports login/registration, products, employees, a single shop, sales, expenses, subscriptions/plans, and billing history. Login returns `{access_token, token_type, user}`.

The current backend assigns each user to one shop and scopes requests from the token. Multi-shop management is not implemented.

## Employee dashboard
The employee dashboard builds its seven-day sales trend from `GET /sales/me?target_date=YYYY-MM-DD`; the PDF uses the same endpoint's supported `from_date` / `to_date` range filters.

## Current backend limitations
- Date-range reports (`/reports/summary`) are not implemented. The dashboard uses the existing shop dashboard and daily expense summary; report pages display an unavailable message.
- Payment initiation/status endpoints and payment-provider integration are not implemented, so subscribing to a paid plan is disabled. Billing history is read-only.
- Password-reset email/token endpoints and self-service password changes are not implemented. Administrators can reset employee passwords using the existing employee update endpoint.
- Shop creation and multi-shop allocation are not implemented; employee accounts are assigned to the administrator's existing shop.

## Expense and sale fields
Expenses use backend categories and persist description, amount, notes, and creation time. Sales are priced from the product record and are locked on submission; sale notes are not persisted by the backend.

## Languages (English / Kiswahili)
A language selector sits next to the dark-mode button. The choice is saved in the browser. Translations live in `src/i18n/sw.js` (exact English text -> Kiswahili); any text not listed stays in English. Dynamic sentences use the `patterns` list in the same file. PDF reports and text coming from the backend are not translated by the UI.
