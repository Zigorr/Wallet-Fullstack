# Wallet: Personal Finance Tracker (Backend)

This document outlines the development plan and technical specifications for the Wallet application's backend service.

## Project Vision

The goal is to build a practical and personal full-stack budgeting tool, similar to [Wallet by BudgetBakers](https://web.budgetbakers.com/). The application will provide core functionality for tracking finances across various accounts, with a focus on a robust, API-first design that can serve both web and mobile clients.

---

## Technology Stack

*   **Framework:** **FastAPI**
*   **Database:** **PostgreSQL**
*   **Dependencies:** Managed via `requirements.txt`.
*   **ORM & Migrations:** **SQLAlchemy** & **Alembic**
*   **Data Validation:** **Pydantic**
*   **Authentication:** **JWT** with **Passlib** (for hashing) and **python-jose** (for tokens).

---

## Phase 1 Blueprint: The Core API

This phase focuses on building a complete and secure backend API using a flat project structure.

*   **1. Project Scaffolding:**
    *   **Method:** Create Python modules directly inside the `Wallet-Backend` directory (`main.py`, `database.py`, `models.py`, `schemas.py`, `crud.py`, `config.py`, `dependencies.py`).
    *   **Goal:** A simplified, flat project structure for easier module access. A `routers/` subdirectory will be used to organize endpoint logic.

*   **2. Password Validation Strategy:**
    *   **Method:** Define a regular expression for strong passwords in the application config.
    *   **Tools:** Python's `re` module for backend validation.
    *   **Details:** The registration endpoint will validate new passwords against the regex. A new DTO and a public endpoint (`/api/v1/config/validation`) will be created to pass the regex rules to the frontend, ensuring validation logic is perfectly synchronized.

*   **3. Database Schema & Migrations:**
    *   **Method:** Define tables as Python classes in `models.py` using the SQLAlchemy ORM. Use Alembic to generate and apply database migrations.
    *   **Goal:** A version-controlled database schema that is managed through code.

*   **4. API Logic & Implementation:**
    *   **Method:**
        *   Use **Pydantic** in `schemas.py` to define strict data contracts (DTOs) for all API requests and responses.
        *   Centralize all database operations (Create, Read, Update, Delete) in `crud.py`.
        *   Implement secure authentication in `routers/auth.py`, using **Passlib** to hash passwords and **python-jose** to issue JWTs.
        *   Protect all data-related endpoints by requiring a valid JWT, verified by a reusable function in `dependencies.py`.
    *   **Goal:** A fully functional, secure, and well-documented API ready for the frontend.

---

## Future Phases

*   **Phase 2:** Web Interface (React)
*   **Phase 3:** Budgeting & Insights
*   **Phase 4:** Mobile App (React Native)
*   **Phase 5:** Advanced Features & Polish 