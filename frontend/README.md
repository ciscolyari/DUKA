# DUKA AI – Frontend
React + Vite + React Router + Axios + Recharts.

## Run
```
npm install
cp .env.example .env     # set VITE_API_URL to your FastAPI base URL
npm run dev
```
## Connecting the backend
All HTTP calls live in `src/services/`. Edit the paths there to match your routers. Expected shapes are in the comments and in the pages (e.g. `/auth/login` returns `{access_token, user:{full_name, role, shop_name}}`; `/reports/summary` returns today_sales, today_expenses, total_sales, total_expenses, products, low_stock, employees, plan, days_left, trend[], top_products[], by_employee[], by_category[]).
The backend must enforce all rules (stock, locked sales, shop isolation, roles). The UI only mirrors them.
\n## Multiple shops\nAn admin can own many shops (`/shops`). The selected shop id is sent as the `X-Shop-ID` header on every request. The backend must check that the shop belongs to the logged-in admin and filter every query by it. Employees belong to one shop; the backend must take it from their token and ignore the header.\n
## Employee dashboard
`GET /reports/employee-summary` should return `{ week_total, trend: [{date, total}] }` for the logged-in employee and their shop. `GET /sales/me?from=&to=` returns only that employee's sales (default: today). The PDF is generated in the browser from that response (jsPDF).

## Connecting to the FastAPI backend
1. `cp .env.example .env` and set `VITE_API_URL` to your API base (include any router prefix, e.g. `http://localhost:8000/api`).
2. Allow the frontend origin and our headers in `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["Authorization", "Content-Type", "X-Shop-ID"])
```
3. Paths are in `src/services/*.js`; change them there if your routes differ.

## Uniqueness and shop allocation (enforce in the backend)
- Employee `username` must be unique across the whole system (it is the login). Shop `name` must be unique per admin.
- Return HTTP 409 with `{"detail": "Username already exists"}`; the UI shows that text.
- `POST/PUT /employees` takes `shop_id`; verify the shop belongs to the logged-in admin. Responses include `shop_name`.
- Reject an unknown `shop_id`, or one that belongs to another admin, with 404/422 and a clear `detail`.
- Password rules: only the admin changes passwords. `POST /auth/change-password` must return 403 for employees. Add `PATCH /employees/{id}/password` `{new_password}` for the admin to reset an employee's password (check the employee belongs to one of the admin's shops).

## Forgot password
- `POST /auth/forgot-password {username}`: always answer 200 with a generic body (do not reveal whether the account exists). Only for **admin** accounts, email a single-use, expiring token (e.g. 30 min, store only its hash) as `{FRONTEND_URL}/reset-password?token=...`. Employees get nothing; their admin resets the password.
- `POST /auth/reset-password {token, new_password}`: 400 with a clear `detail` if the token is invalid or expired. Invalidate the token after use.
- This needs SMTP (or an email API) configured on the backend.

## Employee expenses and sale notes
- Employees can add expenses (`POST /expenses`) but `GET /expenses` must return only their own, and `PUT/DELETE /expenses/{id}` are admin-only. Admins see every expense with `recorded_by`.
- `POST /sales` accepts an optional `note` (max 120 chars); return it in sales lists.

## Languages (English / Kiswahili)
A language selector sits next to the dark-mode button. The choice is saved in the browser. Translations live in `src/i18n/sw.js` (exact English text -> Kiswahili); any text not listed stays in English. Dynamic sentences use the `patterns` list in the same file. PDF reports and text coming from the backend are not translated by the UI.
