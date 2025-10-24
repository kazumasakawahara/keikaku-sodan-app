# Implementation Tasks: Phase 1 MVP

## 1. Project Setup and Infrastructure

- [ ] 1.1 Create project directory structure according to design
- [ ] 1.2 Create `requirements.txt` with all dependencies (FastAPI, SQLAlchemy, etc.)
- [ ] 1.3 Create `.gitignore` file (exclude .venv, *.db, __pycache__, etc.)
- [ ] 1.4 Create `.env.example` with configuration template
- [ ] 1.5 Set up virtual environment with `uv venv`
- [ ] 1.6 Install dependencies with `uv pip install -r requirements.txt`
- [ ] 1.7 Verify installation by running `python --version` and `uvicorn --version`

**Validation**: Directory structure matches design.md, dependencies install without errors

---

## 2. Database Models and Schema

- [ ] 2.1 Create `app/database/connection.py` with SQLAlchemy engine and session setup
- [ ] 2.2 Create `app/models/__init__.py` with Base model
- [ ] 2.3 Create `app/models/staff.py` (Staff model with password_hash field)
- [ ] 2.4 Create `app/models/user.py` (User model with all fields from design)
- [ ] 2.5 Create `app/models/notebook.py` (Notebook model with user relationship)
- [ ] 2.6 Create `app/models/consultation.py` (Consultation model with user and staff relationships)
- [ ] 2.7 Create `app/models/organization.py` (Organization model)
- [ ] 2.8 Create `app/models/user_organization.py` (UserOrganization association model)
- [ ] 2.9 Add indexes to all models as specified in design.md
- [ ] 2.10 Create `scripts/init_db.py` to initialize database and create tables

**Validation**: Run `python scripts/init_db.py` successfully creates SQLite database with all tables and indexes

---

## 3. Configuration and Settings

- [ ] 3.1 Create `app/config.py` with settings class (database URL, secret key, session timeout)
- [ ] 3.2 Add environment variable loading (python-dotenv)
- [ ] 3.3 Configure session middleware settings
- [ ] 3.4 Set up password hashing configuration (bcrypt)

**Validation**: Configuration loads correctly from environment variables

---

## 4. Authentication Implementation

- [ ] 4.1 Create `app/schemas/auth.py` with LoginRequest, LoginResponse schemas
- [ ] 4.2 Create `app/services/auth_service.py` with password hashing and verification functions
- [ ] 4.3 Create `app/api/auth.py` with login, logout, get_current_user endpoints
- [ ] 4.4 Implement session management middleware
- [ ] 4.5 Create authentication dependency for protecting routes
- [ ] 4.6 Create authorization decorator for role-based access control
- [ ] 4.7 Create `app/templates/login.html` with Bootstrap 5 styling
- [ ] 4.8 Test login with valid credentials (should redirect to dashboard)
- [ ] 4.9 Test login with invalid credentials (should show error message)
- [ ] 4.10 Test session timeout (30 minutes)

**Validation**: Authentication system works end-to-end with session management and authorization

---

## 5. User Management Implementation

- [ ] 5.1 Create `app/schemas/user.py` with UserCreate, UserUpdate, UserResponse schemas
- [ ] 5.2 Create `app/services/user_service.py` with age calculation function
- [ ] 5.3 Create `app/services/user_service.py` with CRUD operations
- [ ] 5.4 Create `app/api/users.py` with all REST endpoints (GET, POST, PUT, DELETE)
- [ ] 5.5 Implement search and filter logic (name, staff, disability level)
- [ ] 5.6 Implement pagination (50 records per page)
- [ ] 5.7 Create `app/templates/users/list.html` with search/filter UI
- [ ] 5.8 Create `app/templates/users/detail.html` with tab navigation
- [ ] 5.9 Create `app/templates/users/form.html` for create/edit
- [ ] 5.10 Add JavaScript for age auto-calculation display
- [ ] 5.11 Implement role-based access control (staff see only assigned users)
- [ ] 5.12 Test user CRUD operations (create, read, update, delete)
- [ ] 5.13 Test search and filtering functionality
- [ ] 5.14 Test pagination navigation

**Validation**: User management works with all CRUD operations, age auto-calculation, and authorization

---

## 6. Notebook Management Implementation

- [ ] 6.1 Create `app/schemas/notebook.py` with NotebookCreate, NotebookResponse schemas
- [ ] 6.2 Create `app/services/notebook_service.py` with CRUD operations
- [ ] 6.3 Create `app/api/notebooks.py` with REST endpoints
- [ ] 6.4 Create UI for notebook tab in user detail page
- [ ] 6.5 Add modal/form for adding new notebook
- [ ] 6.6 Implement edit and delete functionality for notebooks
- [ ] 6.7 Test multiple notebooks per user (e.g., 療育手帳 + 精神障害者保健福祉手帳)
- [ ] 6.8 Test notebook CRUD operations

**Validation**: Multiple notebooks can be managed per user with proper UI display

---

## 7. Consultation Records Implementation

- [ ] 7.1 Create `app/schemas/consultation.py` with ConsultationCreate, ConsultationResponse schemas
- [ ] 7.2 Create `app/services/consultation_service.py` with CRUD and filtering logic
- [ ] 7.3 Create `app/api/consultations.py` with REST endpoints
- [ ] 7.4 Create `app/templates/consultations/list.html` with period/type/staff filters
- [ ] 7.5 Create `app/templates/consultations/form.html` for create/edit
- [ ] 7.6 Create `app/templates/consultations/detail.html` for viewing full record
- [ ] 7.7 Add consultation records tab to user detail page
- [ ] 7.8 Implement default datetime (current datetime) on form load
- [ ] 7.9 Implement default staff assignment (current logged-in user)
- [ ] 7.10 Implement consultation type icons (来所🏢, 訪問🏠, 電話📞)
- [ ] 7.11 Implement role-based access (staff see only their assigned users' records)
- [ ] 7.12 Test consultation CRUD operations
- [ ] 7.13 Test filtering by period, type, staff
- [ ] 7.14 Test timeline display (chronological order)

**Validation**: Consultation records work with filtering, timeline display, and authorization

---

## 8. Organization Management Implementation

- [ ] 8.1 Create `app/schemas/organization.py` with OrganizationCreate, OrganizationResponse schemas
- [ ] 8.2 Create `app/services/organization_service.py` with CRUD operations
- [ ] 8.3 Create `app/api/organizations.py` with REST endpoints
- [ ] 8.4 Create `app/templates/organizations/list.html` with type filter
- [ ] 8.5 Create `app/templates/organizations/form.html` for create/edit
- [ ] 8.6 Create `app/templates/organizations/detail.html`
- [ ] 8.7 Implement organization type icons (事業所🏢, 医療機関🏥, 後見人⚖️)
- [ ] 8.8 Test organization CRUD operations
- [ ] 8.9 Test search and type filtering

**Validation**: Organization management works with type filtering and proper UI display

---

## 9. User-Organization Relationship Implementation

- [ ] 9.1 Create `app/schemas/user_organization.py` with relationship schemas
- [ ] 9.2 Create `app/services/user_organization_service.py` with link/unlink operations
- [ ] 9.3 Create API endpoints for linking/unlinking organizations
- [ ] 9.4 Create UI in user detail page for managing organization relationships
- [ ] 9.5 Add modal for selecting organization and entering relationship details
- [ ] 9.6 Implement frequency and relationship type selection
- [ ] 9.7 Implement start_date and end_date management
- [ ] 9.8 Display active relationships (end_date IS NULL) by default
- [ ] 9.9 Add option to show terminated relationships
- [ ] 9.10 Test linking/unlinking organizations to users
- [ ] 9.11 Test relationship type and frequency recording

**Validation**: User-organization relationships work with proper relationship metadata

---

## 10. Staff Management Implementation

- [ ] 10.1 Create `app/schemas/staff.py` with StaffCreate, StaffUpdate, StaffResponse schemas
- [ ] 10.2 Create `app/services/staff_service.py` with CRUD and password management
- [ ] 10.3 Create `app/api/staff.py` with REST endpoints (admin-only access)
- [ ] 10.4 Create `app/templates/staff/list.html` (admin-only page)
- [ ] 10.5 Create `app/templates/staff/form.html` for create/edit (admin-only)
- [ ] 10.6 Implement username uniqueness validation
- [ ] 10.7 Implement password strength validation (minimum 8 characters)
- [ ] 10.8 Implement role icons (admin👑, staff👤)
- [ ] 10.9 Implement activate/deactivate functionality
- [ ] 10.10 Prevent self-deactivation
- [ ] 10.11 Prevent deactivation of last admin
- [ ] 10.12 Create profile edit page for staff to edit their own info
- [ ] 10.13 Test staff CRUD operations (admin-only)
- [ ] 10.14 Test access control (non-admin cannot access staff management)
- [ ] 10.15 Test password change functionality

**Validation**: Staff management works with admin-only access and proper validation

---

## 11. Dashboard Implementation

- [ ] 11.1 Create `app/templates/dashboard.html` with Bootstrap 5 layout
- [ ] 11.2 Implement "Today's Schedule" section (upcoming consultations)
- [ ] 11.3 Implement "Recent Consultations" section (last 5 records)
- [ ] 11.4 Implement "Important Notices" section (notebook renewal alerts - placeholder)
- [ ] 11.5 Implement "Statistics" section (total users, consultations this month, assigned users)
- [ ] 11.6 Add quick links to main functions
- [ ] 11.7 Test dashboard display for admin (all data)
- [ ] 11.8 Test dashboard display for staff (own data only)

**Validation**: Dashboard displays relevant information based on user role

---

## 12. UI/UX Implementation

- [ ] 12.1 Create `app/templates/base.html` with Bootstrap 5 and sidebar navigation
- [ ] 12.2 Create `app/static/css/custom.css` with color scheme from design
- [ ] 12.3 Implement responsive sidebar (hamburger menu for tablets)
- [ ] 12.4 Add breadcrumb navigation
- [ ] 12.5 Implement success/error flash messages
- [ ] 12.6 Add confirmation dialogs for delete operations
- [ ] 12.7 Implement form validation error display (red text below fields)
- [ ] 12.8 Add loading indicators for async operations
- [ ] 12.9 Test responsive layout on PC and tablet sizes
- [ ] 12.10 Test accessibility (keyboard navigation, screen reader compatibility)

**Validation**: UI is consistent, responsive, and accessible

---

## 13. Static Files and Assets

- [ ] 13.1 Download and include Bootstrap 5 CSS/JS
- [ ] 13.2 Create custom CSS for color scheme and spacing
- [ ] 13.3 Add icons (emoji or icon font) for organization types, consultation types, roles
- [ ] 13.4 Optimize static file loading (CDN vs local)

**Validation**: Static files load correctly and UI looks as designed

---

## 14. Seed Data and Testing

- [ ] 14.1 Create `scripts/seed_data.py` with sample data (users, staff, organizations, consultations)
- [ ] 14.2 Use fake data (no real personal information)
- [ ] 14.3 Create at least 3 staff members (1 admin, 2 regular staff)
- [ ] 14.4 Create at least 10 users with varied data
- [ ] 14.5 Create at least 20 consultation records
- [ ] 14.6 Create at least 5 organizations
- [ ] 14.7 Link users to organizations with relationships
- [ ] 14.8 Test data loading: `python scripts/seed_data.py`

**Validation**: Seed data loads successfully and appears correctly in UI

---

## 15. API Documentation

- [ ] 15.1 Ensure all endpoints have proper docstrings
- [ ] 15.2 Add Pydantic schema descriptions
- [ ] 15.3 Verify Swagger UI is accessible at `/docs`
- [ ] 15.4 Verify ReDoc is accessible at `/redoc`
- [ ] 15.5 Test API endpoints via Swagger UI

**Validation**: API documentation is complete and functional

---

## 16. Error Handling and Logging

- [ ] 16.1 Implement global exception handler in FastAPI
- [ ] 16.2 Create custom error pages (404, 403, 500)
- [ ] 16.3 Add logging configuration (log to file and console)
- [ ] 16.4 Log authentication attempts (success/failure)
- [ ] 16.5 Log CRUD operations with user context
- [ ] 16.6 Test error scenarios (invalid input, unauthorized access, database errors)

**Validation**: Errors are handled gracefully and logged properly

---

## 17. Database Backup Script

- [ ] 17.1 Create `scripts/backup_db.py` to copy SQLite database file
- [ ] 17.2 Add timestamp to backup filename (e.g., `backup_20250124_1530.db`)
- [ ] 17.3 Create `backups/` directory automatically if not exists
- [ ] 17.4 Test backup script: `python scripts/backup_db.py`
- [ ] 17.5 Add documentation for manual backup procedure

**Validation**: Backup script creates timestamped backup files successfully

---

## 18. Main Application Entry Point

- [ ] 18.1 Create `app/main.py` with FastAPI application instance
- [ ] 18.2 Register all API routers (auth, users, consultations, organizations, staff)
- [ ] 18.3 Add session middleware
- [ ] 18.4 Add static file mounting
- [ ] 18.5 Add template rendering configuration (Jinja2)
- [ ] 18.6 Add CORS middleware if needed (for future API access)
- [ ] 18.7 Test server startup: `uvicorn app.main:app --reload`
- [ ] 18.8 Verify all routes are registered: check `/docs`

**Validation**: Application starts without errors and all routes are accessible

---

## 19. Integration Testing

- [ ] 19.1 Test complete user journey: login → dashboard → create user → view user → logout
- [ ] 19.2 Test consultation record workflow: login → create consultation → filter consultations → view details
- [ ] 19.3 Test organization management: login → create organization → link to user → view relationship
- [ ] 19.4 Test staff management (admin): login → create staff → assign users → test staff login
- [ ] 19.5 Test authorization: regular staff cannot access other staff's users or staff management
- [ ] 19.6 Test edge cases: empty database, single user, multiple notebooks per user
- [ ] 19.7 Test browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] 19.8 Test tablet responsiveness (iPad size)

**Validation**: All user workflows work end-to-end without errors

---

## 20. Documentation and Handoff

- [ ] 20.1 Update `README.md` with setup instructions
- [ ] 20.2 Update `CLAUDE.md` with any design changes
- [ ] 20.3 Update `HANDOVER.md` with Phase 1 completion status
- [ ] 20.4 Create user manual (basic operations guide) in `docs/user_manual.md`
- [ ] 20.5 Document known issues and limitations
- [ ] 20.6 Document Phase 2 prerequisites and recommendations

**Validation**: Documentation is complete and accurate

---

## Completion Criteria

Phase 1 MVP is considered complete when:

✅ All 20 task sections are completed
✅ Database schema matches design specifications
✅ All 5 core capabilities (authentication, users, consultations, organizations, staff) are functional
✅ UI is responsive and matches wireframe design
✅ Authorization works correctly (admin vs staff roles)
✅ Age auto-calculation works
✅ Logical deletion works for all entities
✅ Seed data loads and displays correctly
✅ API documentation is accessible
✅ Integration tests pass
✅ Application can be deployed on local server

## Next Steps After Phase 1

After Phase 1 completion:
1. Gather user feedback from actual usage
2. Identify priority improvements
3. Plan Phase 2 features (service plans, monitoring, PDF output)
4. Consider PostgreSQL migration if multi-office expansion is planned
