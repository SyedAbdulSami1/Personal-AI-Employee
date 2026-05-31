# Hospital CRM - Master Build Prompt

You are an AI Employee. Your job is:

## Phase 1: Skill Creation (Do this FIRST)
Create these skill files in .claude/skills/crm/ folder:

### Database Skills:
1. crm_db_setup.md - SQLite schema creation
2. crm_db_patient.md - Patient CRUD operations
3. crm_db_doctor.md - Doctor CRUD operations
4. crm_db_appointment.md - Appointment CRUD
5. crm_db_billing.md - Billing CRUD
6. crm_db_backup.md - Daily backup

### Backend Skills:
7. crm_api_setup.md - FastAPI project setup
8. crm_api_auth.md - Login/logout JWT
9. crm_api_patient.md - Patient endpoints
10. crm_api_doctor.md - Doctor endpoints
11. crm_api_appointment.md - Booking endpoints
12. crm_api_billing.md - Invoice endpoints
13. crm_api_reports.md - Analytics endpoints
14. crm_api_whatsapp.md - WhatsApp integration

### Frontend Skills:
15. crm_ui_setup.md - React project setup
16. crm_ui_login.md - Login page
17. crm_ui_dashboard.md - Main dashboard
18. crm_ui_patients.md - Patient list/form
19. crm_ui_doctors.md - Doctor schedule
20. crm_ui_appointments.md - Booking calendar
21. crm_ui_billing.md - Invoice generator
22. crm_ui_reports.md - Charts/analytics

### FTE Integration Skills:
23. crm_fte_reminders.md - Auto appointment reminders
24. crm_fte_reports.md - Daily/weekly reports
25. crm_fte_whatsapp.md - Patient notifications
26. crm_fte_billing.md - Auto invoice generation
27. crm_fte_analytics.md - Patient statistics

### Demo Data Skills:
28. crm_demo_patients.md - 20 fake patients
29. crm_demo_doctors.md - 5 fake doctors
30. crm_demo_appointments.md - 30 fake appointments
31. crm_demo_billing.md - Sample invoices

### Testing Skills:
32. crm_test_api.md - API testing
33. crm_test_ui.md - UI testing
34. crm_test_fte.md - FTE integration test

## Phase 2: Build Rules
- NEVER call LLM if skill exists
- Check .claude/skills/crm/ FIRST
- If skill missing → create it → use it
- Log every action to /Logs/crm/
- Update skill if it fails

## Phase 3: Build Order
1. Database first
2. Backend APIs second  
3. Frontend third
4. FTE integration last
5. Demo data final

## Output Required
- Working CRM at http://localhost:3000
- All APIs at http://localhost:8001
- FTE dashboard integration
- Demo video ready

## Self-Improvement Rules
- If any step fails → update that skill
- If LLM called → save response as new skill
- Every build → optimize existing skills
- Remove garbage from skills weekly