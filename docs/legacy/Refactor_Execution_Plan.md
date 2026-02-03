# 📋 Refactoring Execution Plan: Action Checklist

This document breaks down the high-level strategy from `Refactor_Plan.md` into actionable, trackable tasks. We will use this file to track our progress.

> **Status Legend**:
> - [ ] To Do
> - [x] Completed
> - [~] In Progress

---

## 🔒 Phase 1: Security & Auth (Prioritize Security First)
- [x] **Audit `.gitignore`**: Ensure `.env`, `*.json` (credentials), and `config/secrets.yaml` are ignored.
- [x] **Introduce `.env`**: Create `.env` for local secrets and `.env.example` for the repo.
- [x] **Refactor Config Loading**: Update `src/utils.py` or configuration loader to prioritize Environment Variables over hardcoded strings.
- [x] **Secret Removal**: Scan codebase for any hardcoded API keys or passwords and replace them with `os.getenv()`.
- [x] **Install Auth Library**: Add `streamlit-authenticator` to `requirements.txt`.
- [x] **Create Auth Module**: Implement `src/auth.py` to handle login and roles.
- [x] **Protect Routes**: Wrap `main()` in `app.py`.
- [x] **Logout Functionality**: Add a logout button in the sidebar.

---

## 🐳 Phase 2: Dockerization (Infrastructure as Code)
- [x] **Freeze Dependencies**: Generate a clean `requirements.txt`.
- [x] **Select Base Image**: Choose `python:3.10-slim`.
- [x] **Write `Dockerfile`**: Install `ffmpeg` and dependencies.
- [x] **Write `docker-compose.yml`**: Define services and volumes.

---

## 👥 Phase 3: Role-Based Access Control (RBAC)
- [x] **Schema Update**: Update user config to include roles.
- [x] **Role Logic**: Add `get_user_role` in `src/auth.py`.
- [x] **UI Separation**: Admin sidebar vs Operator view.

---

## 🛠 Phase 4: Async Processing & Web Queue
- [x] **Job Queue**: Implement `JobManager` with background thread.
- [x] **Upload Handling**: Modify `app.py` for async submission.
- [x] **Status Dashboard**: Add real-time job monitoring UI.

---

## 🚀 Phase 5: Admin Dashboard Enhancements (New)
**Objective**: Empower Admins with system visibility and management tools.

### 5.1 System Logging
- [x] **Log Setup**: Create `src/logger.py` to write logs to `logs/app.log` (rotating).
- [x] **Log Viewer UI**: Create a "System Logs" tab in Admin Dashboard to view/filter logs.

### 5.2 File Management
- [x] **File Explorer UI**: View file lists for `Inbox` and `Archive`.
- [x] **File Actions**: Add "Delete" and "Download" buttons for maintenance.

### 5.3 User Management (Bonus)
- [x] **User Manager**: Implement `src/user_manager.py` for yaml-based auth.
- [x] **User UI**: add/delete users in Admin Dashboard.

---

## 🧹 Housekeeping
- [ ] **Documentation Update**: Keep `MASTER_PLAN.md` updated.
