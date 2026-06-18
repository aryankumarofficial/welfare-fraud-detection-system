# PHASE_11_MASTER_CHECKLIST.md

## Phase 11: Demo Readiness — Master Checklist

### Quick Reference for Demo Day

Use this checklist to track final preparation status.

---

## 📋 Pre-Demo Tasks (48 Hours Before)

### Setup & Infrastructure
- [ ] ML backend service running (`http://localhost:8000`)
- [ ] Frontend Next.js app running (`http://localhost:3000`)
- [ ] Database connection verified
- [ ] Redis/BullMQ worker running
- [ ] Backend health check passes
- [ ] All required npm packages installed

### Demo Data
- [ ] Run seed data script: `npx ts-node scripts/seed-demo-data.ts`
- [ ] Verify 5 profiles created
- [ ] Verify 10 snapshots generated
- [ ] Verify 5 predictions with correct risk levels
- [ ] Verify 4 alerts in system
- [ ] Verify 2 drift snapshots
- [ ] Verify 3 models registered

### Documentation Review
- [ ] Read DEMO_PRESENTATION_SCRIPT.md completely
- [ ] Review DEMO_DATA_GUIDE.md for data reference
- [ ] Review all validation reports
- [ ] Prepare Q&A responses
- [ ] Identify backup screenshots locations

---

## 🔍 Pre-Demo Validation (30 Minutes Before)

### Authentication Flow
- [ ] Login page loads (`http://localhost:3000/login`)
- [ ] Valid credentials accepted
- [ ] Invalid credentials rejected with error
- [ ] Dashboard loads after successful login
- [ ] Logout button functional
- [ ] Token stored in localStorage
- [ ] Protected routes redirect unauthenticated users

### Dashboard Display
- [ ] Dashboard accessible at `/admin/dashboard`
- [ ] Profile count widget shows: **5**
- [ ] Snapshots widget shows: **10**
- [ ] Predictions widget shows: **5**
- [ ] HIGH risk shows: **1** (red badge)
- [ ] MEDIUM risk shows: **2** (orange badge)
- [ ] LOW risk shows: **2** (green badge)
- [ ] Recent alerts section visible with 4 alerts
- [ ] All counts update within 2 seconds

### Core Page Navigation
- [ ] Predictions page loads (list of 5)
- [ ] Prediction detail loads (risk scores visible)
- [ ] Analytics pages load (dashboard, drift, alerts, queue)
- [ ] Model registry loads (3 models visible)
- [ ] Model detail loads (champion model)
- [ ] No 404 errors on any page

### Data Consistency
- [ ] Dashboard total = sum of all risk levels (5 = 1+2+2)
- [ ] Predictions match count (5 predictions shown)
- [ ] Risk distribution accurate
- [ ] Alerts match expected 4 types
- [ ] Models match expected 3 total

---

## 🎯 Final System Check (5 Minutes Before)

### Browser Readiness
- [ ] Browser cache cleared (Ctrl+Shift+Delete)
- [ ] Developer console closed (F12)
- [ ] DevTools network monitor closed
- [ ] Single tab open showing login page
- [ ] Screen resolution: 1920x1080 minimum
- [ ] Font size readable (no zoom needed)
- [ ] Dark mode consistent (if used)

### Network & Performance
- [ ] Network latency < 100ms (checked in DevTools)
- [ ] API responses all 200/201 status
- [ ] No failed requests in Network tab
- [ ] No console errors (F12 to verify)
- [ ] All images loaded
- [ ] CSS and JS files loaded

### Credentials Verified
- [ ] Username ready (e.g., "analyst")
- [ ] Password ready (e.g., "password")
- [ ] Backend auth endpoint working
- [ ] Token generation confirmed

---

## 🎬 Demo Execution Checklist

### Segment 1: Introduction (0:30)
- [ ] Screen visible to audience
- [ ] Browser window maximized
- [ ] Script point 1: Explain WelfareGuard purpose
- [ ] Script point 2: Describe ML fraud detection
- [ ] Script point 3: Mention integrated workflow

### Segment 2: Authentication (0:45)
- [ ] Click on login form
- [ ] Type username: `analyst`
- [ ] Type password: `password`
- [ ] Click Sign In button
- [ ] **Wait** for dashboard load (2-3 seconds)
- [ ] **VERIFY:** Dashboard appears
- [ ] **VERIFY:** "ANALYST" badge visible
- [ ] Explain role-based access control

### Segment 3: Dashboard Overview (1:00)
- [ ] Point to profile count: 5
- [ ] Point to snapshots: 10
- [ ] Point to predictions: 5
- [ ] Highlight risk distribution bars
- [ ] Explain HIGH (1) = needs investigation
- [ ] Explain MEDIUM (2) = requires verification
- [ ] Explain LOW (2) = routine monitoring
- [ ] Scroll to alerts section
- [ ] Show 4 system alerts

### Segment 4: Prediction Analysis (1:30)
- [ ] Navigate to Predictions page
- [ ] **WAIT** for list to load
- [ ] Click on HIGH risk prediction (red badge)
- [ ] **WAIT** for detail page
- [ ] Point to income_risk score: **0.85**
- [ ] Point to transaction_risk score: **0.90**
- [ ] Point to final_risk: **0.85**
- [ ] Read explanation text
- [ ] Explain why flagged
- [ ] Point to model version: v2.1.0

### Segment 5: Workflow Execution (1:30)
- [ ] Navigate to Workflows page
- [ ] **Generate Snapshot Step:**
  - [ ] Select profile ID
  - [ ] Click "Generate Snapshot"
  - [ ] **WAIT** for success
  - [ ] Show snapshot ID returned
  - [ ] Explain feature extraction
- [ ] **Generate Prediction Step:**
  - [ ] Select profile ID
  - [ ] Click "Generate Prediction"
  - [ ] **WAIT** for success
  - [ ] Show risk scores
  - [ ] Explain model inference
- [ ] **Queue Job Step:**
  - [ ] Click "Queue Prediction"
  - [ ] **WAIT** for job created
  - [ ] Show job status: PENDING
  - [ ] Explain async processing

### Segment 6: Case Review (1:00)
- [ ] Navigate to Reviews page
- [ ] Show existing reviews (5 total)
- [ ] Explain review outcomes:
  - [ ] Confirmed Fraud: 1 (20%)
  - [ ] Not Fraud: 2 (40%)
  - [ ] Under Investigation: 2 (40%)
- [ ] Point to review interface
- [ ] Explain how analyst submits decision
- [ ] Mention feedback improves model

### Segment 7: Model Performance (1:00)
- [ ] Navigate to Model Health page
- [ ] Show champion model: **v2.1.0**
- [ ] Show status: **ACTIVE**
- [ ] Show false positive rate: **5%**
- [ ] Show accuracy: **87%**
- [ ] Navigate to Drift Detection
- [ ] Show drift score: **0.35 (MODERATE)**
- [ ] Explain feature distribution changes
- [ ] Navigate to Queue Monitor
- [ ] Show queue stats (PENDING, PROCESSING, COMPLETED)
- [ ] Show success rate percentage

### Segment 8: Model Registry (0:45)
- [ ] Navigate to Models page
- [ ] Show all 3 models:
  - [ ] v2.1.0 (CHAMPION) ⭐
  - [ ] v2.0.5 (CHALLENGER)
  - [ ] v1.3.2 (ARCHIVED)
- [ ] Click on champion model detail
- [ ] Show configuration JSON
- [ ] Show evaluation metrics
- [ ] Show evaluation history
- [ ] Explain promotion workflow
- [ ] Return to models list

### Segment 9: System Resilience (0:30)
- [ ] Navigate to Alerts page
- [ ] Show all 4 alerts with severity
- [ ] Explain automatic monitoring
- [ ] Point to performance warning
- [ ] Point to drift detection alert
- [ ] Point to prediction spike alert
- [ ] Explain alert-driven responses

### Segment 10: Closing Summary (0:30)
- [ ] Summarize what was shown
- [ ] Recap key features:
  - [ ] Fraud detection at scale
  - [ ] Explainable decisions
  - [ ] Human review workflow
  - [ ] Model management
- [ ] Open for Q&A

---

## ⏱️ Timing Verification

Record actual times:

| Segment | Target | Actual | ✓/✗ |
|---------|--------|--------|-----|
| Intro | 0:30 | _:__ | |
| Auth | 0:45 | _:__ | |
| Dashboard | 1:00 | _:__ | |
| Prediction | 1:30 | _:__ | |
| Workflow | 1:30 | _:__ | |
| Review | 1:00 | _:__ | |
| Performance | 1:00 | _:__ | |
| Registry | 0:45 | _:__ | |
| Resilience | 0:30 | _:__ | |
| Closing | 0:30 | _:__ | |
| **TOTAL** | **9:00** | **_:__** | |

**Target:** 5-10 minutes ✅

---

## 🆘 Troubleshooting Quick Links

### If Login Fails
→ See E2E_VALIDATION_REPORT.md, Phase 1

### If Dashboard Empty
→ See DASHBOARD_POPULATION_REPORT.md

### If API Error
→ See API_VALIDATION_REPORT.md

### If Queue Not Working
→ See QUEUE_VALIDATION_REPORT.md

### If Model Page Blank
→ See MODEL_REGISTRY_VALIDATION.md

### If Slow Load
→ Check network latency in DevTools Network tab

### If Button Doesn't Work
→ Retry, then use alternative route (show API result)

---

## 💾 Key Resources

**Seeding Demo Data:**
```bash
npx ts-node scripts/seed-demo-data.ts
```

**Starting Services:**
```bash
# Backend (in services/ml directory)
uvicorn app:app --reload

# Frontend (in apps/web directory)
npm run dev
```

**URLs:**
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Dashboard: `http://localhost:3000/admin/dashboard`
- API Docs: `http://localhost:8000/docs` (if available)

---

## 📊 Data Quick Reference

### Demo Profiles
1. **Rajesh Kumar** - LOW risk
2. **Priya Singh** - HIGH risk ⚠️
3. **Amit Patel** - MEDIUM risk
4. **Neha Sharma** - LOW risk
5. **Suresh Reddy** - MEDIUM risk

### Risk Scores (Priya Singh - HIGH case)
- Income Risk: **0.85**
- Caste Risk: **0.60**
- Transaction Risk: **0.90**
- Medical Risk: **0.30**
- **Final Risk: 0.85** → HIGH

### Models
- Champion: Income Fraud Detector **v2.1.0** (87% accuracy)
- Challenger: Income Fraud Detector **v2.0.5** (85% accuracy)
- Archived: Transaction Anomaly **v1.3.2**

### Alerts (4 total)
1. Model Performance Degradation (HIGH)
2. Data Drift Detection (MEDIUM)
3. Prediction Anomaly (HIGH)
4. Queue Processing Delay (MEDIUM)

---

## ✅ Sign-Off

### Pre-Demo Verification
- [ ] All systems operational
- [ ] Demo data loaded
- [ ] Script reviewed
- [ ] Timing validated
- [ ] Ready to present

**Prepared By:** _______________
**Date:** _______________
**Status:** ✅ READY / ⚠️ ISSUES / ❌ NOT READY

### During Demo
- [ ] Script followed
- [ ] Timings on track
- [ ] Q&A addressed
- [ ] No major errors

**Presenter:** _______________
**Audience:** _______________
**Duration:** ___ minutes

### Post-Demo
- [ ] Feedback collected
- [ ] Issues documented
- [ ] Next steps identified

**Issues Encountered:**
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

**Improvements for Next Demo:**
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

**Demo Success:** ✅ YES / ❌ NO

---

## 📝 Notes Section

Use this space for last-minute notes or reminders:

```




```

---

**Print this checklist and bring to demo day!**

**Last Updated:** 2026-01-19
**Version:** 1.0 - Phase 11 Demo Ready
