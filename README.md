# 🏪 DUKA

### Shop Sales, Inventory & Employee Management System

DUKA is a shop management system designed for businesses that sell different types of products and need a simple way to manage **inventory, employees, sales, and daily revenue**.

The system gives the shop owner full control over the business while allowing employees to record sales through their own accounts.

---

## 📌 What is DUKA?

DUKA connects three important parts of a shop:

```text
              DUKA
                │
       ┌────────┼────────┐
       ↓        ↓        ↓
    Products  Employees  Sales
       │        │        │
       └────────┼────────┘
                ↓
             Stock
                ↓
         Daily Reports
```

The Administrator manages the shop, products, employees, and reports.

Employees are responsible for recording sales.

Whenever a sale is successfully submitted, DUKA automatically updates the stock and records the transaction.

---

# 🎯 Purpose of DUKA

DUKA is built to solve common problems in shop management, such as:

* Manually calculating daily sales
* Losing track of available stock
* Not knowing which employee made a sale
* Employees changing sales after submission
* Difficulty tracking repeated sales of the same product
* Difficulty knowing total sales for the day
* Lack of a centralized sales history

DUKA provides one system where all these activities can be tracked.

---

# 👥 User Types

DUKA has two main user roles:

### 1. Administrator

The Administrator is the shop owner or manager.

### 2. Employee

An Employee is a worker who records sales using a sub-account created by the Administrator.

---

# 👨‍💼 Administrator

The Administrator has full control over the shop.

## Administrator Responsibilities

The Administrator can:

* Register the shop
* Login to the system
* Add products
* Edit products
* Delete products
* Manage stock
* Create employee accounts
* Manage employee accounts
* View all sales
* View sales by employee
* View daily sales
* View total shop sales
* Monitor remaining stock
* View reports
* Handle exceptional sales situations

---

# 🧑‍💼 Employee

Employees use accounts created by the Administrator.

An employee does **not** create a public account.

For example:

```text
Employee Name: John

Username: cashier01
Password: ********
```

The Administrator provides these credentials to the employee.

The employee can then login and start recording sales.

---

# 🔐 Login Flow

When the DUKA application starts, the user sees:

```text
                 DUKA
                  │
        ┌─────────┴─────────┐
        │                   │
        ↓                   ↓
 Login as Admin       Login as Employee
        │                   │
        ↓                   ↓
Admin Dashboard      Employee Dashboard
```

For a new shop owner:

```text
Register as Administrator
           ↓
      Create Account
           ↓
          Login
           ↓
   Administrator Dashboard
```

Employees are created by the Administrator.

---

# 📦 Product Management

Products are managed by the Administrator.

Each product contains information such as:

```text
Product Name
Description
Selling Price
Stock Quantity
Created At
Updated At
```

Example:

```text
Product: Sugar 1kg
Price: 3,000 TZS
Stock: 100
```

The Administrator can update product information whenever necessary.

Employees can view available products but cannot modify them.

---

# 🛒 How Sales Work

The employee records a sale by selecting a product and entering the quantity.

Example:

```text
NEW SALE

Product:
Coca Cola 500ml

Quantity:
5

Unit Price:
1,000 TZS

Total:
5,000 TZS

[ SUBMIT SALE ]
```

When the employee submits the sale, DUKA automatically performs the following operations:

```text
Employee submits sale
        ↓
Check product
        ↓
Check available stock
        ↓
Calculate total
        ↓
Create sale transaction
        ↓
Deduct sold quantity from stock
        ↓
Update daily sales
        ↓
Show remaining stock
        ↓
Lock transaction
```

---

# 📊 Automatic Stock Management

Stock is updated automatically after every successful sale.

Example:

### Initial Stock

```text
Coca Cola 500ml
Stock = 100
```

Employee sells 5:

```text
100 - 5 = 95
```

Remaining:

```text
95
```

Later the employee sells another 10:

```text
95 - 10 = 85
```

Remaining:

```text
85
```

The system always calculates from the **current stock**.

---

# 🔄 Repeated Sales

The same product can be sold many times during the day.

Example:

```text
Coca Cola 500ml

Sale 1 → 5
Sale 2 → 10
Sale 3 → 3
```

DUKA calculates:

```text
Total sold:

5 + 10 + 3 = 18
```

If the starting stock was 100:

```text
100 - 18 = 82
```

The employee will see:

```text
Coca Cola 500ml

Sold Today: 18
Remaining Stock: 82
```

The product is **not duplicated** every time it is sold.

There is only one product record, while multiple sales reference that product.

---

# 🚫 Stock Validation

DUKA does not allow an employee to sell more products than are available.

Example:

```text
Available Stock: 3

Requested Quantity: 5
```

The system rejects the sale:

```text
❌ Sale Failed

Insufficient Stock

Available: 3
Requested: 5
```

The stock remains unchanged.

```text
Stock = 3
```

---

# 🔒 Submitted Sales Are Locked

Once an employee submits a sale, the transaction becomes locked.

Example:

```text
Sale #1025

Product: Sugar 1kg
Quantity: 2
Total: 6,000 TZS

Status: SUBMITTED
```

The employee can view the sale but cannot:

```text
❌ Edit
❌ Change quantity
❌ Change product
❌ Change price
❌ Delete
```

This protects the accuracy of sales records.

---

# 📋 Employee Daily Sales

Every employee can view a list of the sales they made during the day.

Example:

```text
MY SALES
Date: 07/09/2026

Time     Product          Qty      Amount
------------------------------------------------
08:10    Sugar 1kg         2       6,000
09:25    Rice 1kg          3      10,500
10:40    Bread             2       4,000
11:15    Coca Cola         5       5,000
13:30    Rice 1kg          2       7,000
------------------------------------------------
TOTAL                             32,500 TZS
```

The employee can see what they sold, but cannot modify completed transactions.

---

# 💰 Daily Sales Total

DUKA automatically calculates the total amount sold.

For example:

```text
Employee: cashier01

Sales:
10,000
15,000
5,000

----------------
Total:
30,000 TZS
```

The Administrator can see the total for the entire shop.

Example:

```text
TODAY'S SHOP SALES

Employee          Total
--------------------------------
cashier01         185,000 TZS
cashier02         240,000 TZS
cashier03         125,000 TZS
--------------------------------
SHOP TOTAL        550,000 TZS
```

---

# 📈 Daily Sales Summary

DUKA can also group repeated sales of the same product.

Example:

```text
TODAY'S PRODUCT SALES

Product          Qty Sold       Revenue
------------------------------------------------
Coca Cola          18           18,000 TZS
Sugar               7           21,000 TZS
Rice               12           42,000 TZS
Bread                5           10,000 TZS
------------------------------------------------
TOTAL                            91,000 TZS
```

This gives the Administrator a quick overview of the day's business.

---

# 👨‍💼 Employee Management

The Administrator can create employee sub-accounts.

Example:

```text
SHOP
 │
 └── ADMIN
       │
       ├── cashier01
       ├── cashier02
       ├── cashier03
       └── cashier04
```

Each employee has their own username and password.

This allows every sale to be connected to the employee who made it.

For example:

```text
Sale #1050

Employee: cashier02
Product: Rice 1kg
Quantity: 3
Total: 10,500 TZS
```

---

# 🔐 Permissions

| Action                |            Admin | Employee |
| --------------------- | ---------------: | -------: |
| Register              |                ✅ |        ❌ |
| Login                 |                ✅ |        ✅ |
| Create Employee       |                ✅ |        ❌ |
| Add Product           |                ✅ |        ❌ |
| Edit Product          |                ✅ |        ❌ |
| Delete Product        |                ✅ |        ❌ |
| View Products         |                ✅ |        ✅ |
| Record Sale           |                ✅ |        ✅ |
| Submit Sale           |                ✅ |        ✅ |
| View Remaining Stock  |                ✅ |        ✅ |
| View Own Sales        |                ✅ |        ✅ |
| View All Sales        |                ✅ |        ❌ |
| View Daily Total      |                ✅ |        ✅ |
| Edit Submitted Sale   |                ❌ |        ❌ |
| Delete Submitted Sale | Admin-controlled |        ❌ |
| View Reports          |                ✅ |        ❌ |

---

# 🧠 Core Business Rules

DUKA follows these rules:

### Rule 1 — Employee Accounts

Employees cannot register themselves.

The Administrator creates their accounts.

### Rule 2 — Product Management

Only the Administrator can create, edit, or delete products.

### Rule 3 — Stock

Stock cannot become negative.

```text
stock >= 0
```

### Rule 4 — Sales

A sale cannot be submitted if there is insufficient stock.

### Rule 5 — Automatic Stock Update

Every successful sale automatically reduces the product stock.

```text
remaining_stock =
current_stock - quantity_sold
```

### Rule 6 — Transaction Lock

Once a sale is submitted, the employee cannot edit or delete it.

### Rule 7 — Historical Prices

The price used during a sale is stored with the sale.

Changing the product's current price does not change old sales.

### Rule 8 — Daily Total

Daily totals are calculated from valid submitted sales.

### Rule 9 — Multiple Sales

The same product can appear in multiple transactions without creating duplicate products.

### Rule 10 — Shop Isolation

Users can only access data belonging to their own shop.

---

# 🔄 Complete System Flow

```text
                         DUKA
                          │
             ┌────────────┴────────────┐
             │                         │
             ↓                         ↓
      ADMINISTRATOR                EMPLOYEE
             │                         │
             ↓                         ↓
      Manage Products               Login
             │                         │
             ↓                         ↓
      Create Employees          Employee Dashboard
             │                         │
             ↓                         ↓
       Monitor Inventory          Select Product
             │                         │
             │                    Enter Quantity
             │                         │
             │                         ↓
             │                    Submit Sale
             │                         │
             │                         ↓
             │                   Check Stock
             │                         │
             │              ┌──────────┴──────────┐
             │              │                     │
             │            Enough              Not Enough
             │              │                     │
             │              ↓                     ↓
             │          Save Sale              Reject
             │              │
             │              ↓
             │        Deduct Stock
             │              │
             │              ↓
             │      Update Daily Sales
             │              │
             │              ↓
             │      Show Remaining Stock
             │              │
             │              ↓
             │       Lock Transaction
             │              │
             └──────────────┴──────────────┐
                                            ↓
                                      Sales Reports
                                            │
                                            ↓
                                      Daily Total
                                            │
                                            ↓
                                      ADMINISTRATOR
```

---

# 🏗️ System Architecture

```text
┌──────────────────────────────┐
│           FRONTEND           │
│             React            │
└───────────────┬──────────────┘
                │
                │ REST API
                ↓
┌──────────────────────────────┐
│           BACKEND            │
│            FastAPI           │
│                              │
│ Authentication               │
│ User Management              │
│ Product Management           │
│ Sales Management             │
│ Inventory Management         │
│ Reports                      │
└───────────────┬──────────────┘
                │
                ↓
┌──────────────────────────────┐
│          PostgreSQL          │
│                              │
│ Users                        │
│ Shops                        │
│ Products                     │
│ Sales                        │
│ Sale Items                   │
└──────────────────────────────┘
```

---

# 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* PostgreSQL
* Alembic

### Frontend

* React
* JavaScript
* CSS

### Security

* JWT Authentication
* Password Hashing
* Role-Based Access Control

### API

* REST API
* OpenAPI
* Swagger UI

---

# 📁 Repository Structure

```text
DUKA/
│
├── README.md
├── .gitignore
├── .env.example
│
├── backend/
│   ├── requirements.txt
│   ├── alembic.ini
│   │
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │
│   └── app/
│       ├── main.py
│       │
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   └── security.py
│       │
│       ├── models/
│       │   ├── shop.py
│       │   ├── user.py
│       │   ├── product.py
│       │   ├── sale.py
│       │   └── sale_item.py
│       │
│       ├── schemas/
│       │   ├── auth.py
│       │   ├── user.py
│       │   ├── product.py
│       │   └── sale.py
│       │
│       ├── routers/
│       │   ├── auth.py
│       │   ├── users.py
│       │   ├── products.py
│       │   ├── sales.py
│       │   ├── dashboard.py
│       │   └── reports.py
│       │
│       ├── services/
│       │   ├── auth_service.py
│       │   ├── product_service.py
│       │   ├── sale_service.py
│       │   └── report_service.py
│       │
│       └── dependencies/
│           └── auth.py
│
├── frontend/
│   ├── package.json
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── context/
│       ├── App.jsx
│       └── main.jsx
│
└── docs/
    ├── system-design.md
    ├── database-design.md
    └── api-documentation.md
```

---

# 🚀 Development Plan

DUKA will be developed progressively.

```text
PHASE 1
Project Setup
     ↓
PHASE 2
Database Design
     ↓
PHASE 3
Authentication & Roles
     ↓
PHASE 4
Product & Inventory
     ↓
PHASE 5
Sales System
     ↓
PHASE 6
Automatic Stock Updates
     ↓
PHASE 7
Daily Sales & Reports
     ↓
PHASE 8
Admin & Employee Dashboards
     ↓
PHASE 9
Testing
     ↓
PHASE 10
Deployment
```

---

# 🎯 Final Goal

The final DUKA system should make shop management simple:

```text
ADMIN
 │
 ├── Manage Products
 ├── Manage Employees
 ├── Monitor Stock
 ├── Monitor Sales
 └── View Reports
          │
          ↓
         DUKA
          ↑
          │
     EMPLOYEES
          │
          ↓
     Record Sales
          │
          ↓
    Submit Transaction
          │
          ↓
    Automatic Stock Update
          │
          ↓
     Daily Sales Update
          │
          ↓
      Daily Total
```

## ⭐ DUKA Principle

> **The employee records the sale. DUKA manages the calculation, stock update, and transaction history. The Administrator remains in control of the business.**
