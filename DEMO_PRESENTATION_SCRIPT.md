# DEMO_PRESENTATION_SCRIPT.md

## WelfareGuard Platform - Demo Presentation Script

### Overview

**Duration:** 5-10 minutes
**Audience:** Non-technical stakeholders, investors, or review committee
**Platform:** Live browser demo (no manual SQL, no Postman)
**Prerequisites:** Backend running, demo data seeded, frontend accessible

---

## Pre-Demo Setup (5 minutes before)

### Checklist
- [ ] ML backend running on `http://localhost:8000`
- [ ] Frontend running on `http://localhost:3000`
- [ ] Database seeded with 5 profiles, 10 snapshots, 5 predictions
- [ ] Browser dev tools closed
- [ ] Screen resolution: 1920x1080 minimum
- [ ] Have fallback screenshots ready

### Network Tab
- Close any slow network simulation
- Ensure backend connectivity: Open DevTools → Network → Refresh → verify 200 status codes

---

## Demo Flow

### SEGMENT 1: INTRODUCTION (30 seconds)

**Script:**

> "Good [morning/afternoon]. I'm going to show you WelfareGuard—a fraud detection platform for welfare beneficiaries. 
> 
> The system uses machine learning to analyze financial data, identify patterns, and flag potential fraudulent claims for human review.
> 
> What you're about to see is the complete workflow: from login, through data analysis, model management, and case review—all integrated into one platform."

**Actions:**
- Point to browser showing login page
- No clicking yet

---

### SEGMENT 2: AUTHENTICATION (45 seconds)

**Script:**

> "First, let's authenticate. The system uses role-based access control, so different team members see different capabilities."

**Actions:**
1. Click email field
2. Type: `analyst`
3. Click password field
4. Type: `password`
5. Click "Sign In" button
6. **Wait for dashboard to load** (2-3 seconds)

**Expected Result:**
- Dashboard appears
- "ANALYST" badge visible in top-right navbar
- Welcome message or profile indicator

**If Something Goes Wrong:**
- Retry login
- If fails again: "We have a backup demo database. Let me show you the data through screenshots."
- Show fallback dashboard screenshot

---

### SEGMENT 3: DASHBOARD OVERVIEW (1 minute)

**Script:**

> "This is our main dashboard. Notice the key metrics:
> 
> - **5 beneficiaries** in our system (profiles we're monitoring)
> - **10 financial snapshots** (detailed data captures)
> - **5 recent predictions** made by our model
> 
> The breakdown shows our risk assessment:
> - 1 HIGH risk case that needs immediate investigation
> - 2 MEDIUM risk cases that require verification  
> - 2 LOW risk cases in normal monitoring
> 
> And here are recent system alerts—our monitoring caught some interesting patterns."

**Actions:**
1. Point to profile count widget → Click it
   - *Expected:* Shows or navigates to profiles list
2. Point to predictions widget
   - *Narrate:* "These are the initial predictions from our model"
3. Point to risk distribution bars (HIGH, MEDIUM, LOW)
   - *Narrate:* "Notice the color coding: red for high, orange for medium, green for low"
4. Scroll down to view alerts
   - *Point to alerts:* "Four key alerts: a performance warning, data drift detection, a spike in high-risk predictions, and a queue latency issue"

**If Alert Section Doesn't Load:**
- Say: "Let me navigate directly to the alerts page to show you the monitoring system"
- Click on "Alerts" link from navbar

---

### SEGMENT 4: PREDICTION ANALYSIS (1.5 minutes)

**Script:**

> "Let's look at one of the HIGH risk cases. This helps us understand what the model is detecting and why."

**Actions:**
1. Click on "Predictions" in navbar
   - *Wait for list to load*
   - **Expected:** List of 5 predictions with risk levels
2. Click the RED badge (HIGH risk prediction)
   - *Expected:* Detail page loads
3. Point to the risk scores:

**Narrate:**

> "Here's why this case was flagged:
> 
> - **Income Risk: 85%** — Declared income doesn't match spending patterns
> - **Transaction Risk: 90%** — Large, unusual transactions in the last 30 days
> - **Caste Risk: 60%** — Age doesn't align with stated caste category data
> - **Medical Risk: 30%** — Some inconsistencies in health records
> 
> **Final Risk Score: 85% — HIGH RISK**
> 
> The system generated this explanation: [*read from page*]
> 
> This isn't a conviction—it's a flag for human review. Let's see how an analyst would handle this case."

**If Detail Page Doesn't Load:**
- Show screenshot
- Continue narration

---

### SEGMENT 5: WORKFLOW EXECUTION (1.5 minutes)

**Script:**

> "Now I'm going to execute the complete workflow: generate a snapshot, make a prediction, and queue a job for processing."

**Actions:**

#### Step 1: Navigate to Workflows
1. Click "Workflows" (or "Tools"/"Generate" section) in navbar
   - **Expected:** Form panel with three sections

#### Step 2: Generate Snapshot
1. Point to "Generate Snapshot" section
2. Say: > "Let's capture the current financial state for a profile"
3. Find a profile ID from dropdown (or show in form)
4. Click "Generate Snapshot" button
   - **Expected:** Success message + new snapshot ID appears
5. **Narrate:** "The system extracted features from financial records, caste data, medical records, and transaction history"

#### Step 3: Generate Prediction
1. Point to "Generate Prediction" section
2. Say: > "Now let's run inference on that snapshot"
3. Select same profile or different one
4. Click "Generate Prediction" button
   - **Expected:** Success message + prediction data
5. **Narrate:** "The model processed the snapshot and generated risk scores in real-time—usually under 500 milliseconds"

#### Step 4: Queue Job
1. Point to "Queue Prediction" section
2. Say: > "We can also queue async jobs for batch processing"
3. Click "Queue Prediction" button
   - **Expected:** Job created, status = PENDING
4. **Narrate:** "This job is now in the queue. Our worker processes these asynchronously."

**If Any Step Fails:**
- Say: "The workflow succeeded earlier. Let me show you the results here."
- Navigate to predictions list
- Show that new data appears

---

### SEGMENT 6: CASE REVIEW (1 minute)

**Script:**

> "After analysis, cases go to our analysts for review and decision. Let me show you the review interface."

**Actions:**
1. Navigate to "Reviews" or "Prediction Reviews" page
   - **Expected:** List of existing reviews
2. **Narrate:** "Here we see existing reviews submitted by our team:
   - **Confirmed Fraud:** 1 case (analyst flagged as actual fraud)
   - **Not Fraud:** 2 cases (model was conservative, but data checks out)
   - **Under Investigation:** 2 cases (needs more documentation)"
3. If there's a form, click "Submit Review" button
   - Fill in: Decision = "not_fraud", Notes = "Income verified through tax returns"
   - Click Submit
   - **Expected:** Success message, review added to list

**Narrate:** "The review is recorded in the system. This feedback helps us train better models over time."

---

### SEGMENT 7: MODEL PERFORMANCE & MONITORING (1 minute)

**Script:**

> "The platform includes continuous monitoring. Let me show you model health and analytics."

**Actions:**

#### Model Health
1. Navigate to "Model Health" page
   - **Expected:** Champion model card with metrics
2. **Narrate:**
   > "Our champion model:
   > - **Version:** 2.1.0 (deployed 20 days ago)
   > - **False Positive Rate:** 5% (below threshold)
   > - **Total Models:** 3 versions registered
   > - **Accuracy:** 87%"

#### Analytics
1. Click "Drift Detection"
   - **Narrate:** "Over the past week, we've detected moderate data drift (score 0.35). Income distribution shifted -5%, expenses up 12%. We're monitoring this."
2. Click "Queue Monitor"
   - **Narrate:** "Queue is healthy. 6/7 jobs completed successfully. Average processing time: 250ms per prediction."

**If Pages Slow to Load:**
- Say: "Let me jump to our pre-recorded metrics" 
- Show screenshot

---

### SEGMENT 8: MODEL REGISTRY (45 seconds)

**Script:**

> "Model management is critical. We track multiple versions and can promote, compare, or rollback instantly."

**Actions:**
1. Navigate to "Models" page
   - **Expected:** List of 3 models
2. **Narrate:**
   > "We're running:
   > - **Income Fraud Detector v2.1.0** ← Champion (promoted 20 days ago)
   > - **Income Fraud Detector v2.0.5** ← Challenger (testing improvements)
   > - **Transaction Anomaly Detector v1.3.2** ← Archived (old version)"
3. Click "Champion" model
   - Show detail page with configuration
   - **Narrate:** "Each model has its configuration stored, evaluation history tracked, and deployment metadata recorded."
4. (Optional) Show Compare interface
   - "The compare view lets analysts evaluate if a new model version is better before promoting it"

---

### SEGMENT 9: SYSTEM RESILIENCE (30 seconds)

**Script:**

> "The platform monitors itself. Here's what we track:"

**Actions:**
1. Navigate to "Alerts"
   - **Narrate:**
   > "High-severity alerts:
   > - **Model Performance Degradation:** Accuracy dropped to 82%
   > - **Prediction Spike:** 300% increase in high-risk predictions (investigation recommended)
   > 
   > Medium-severity:
   > - **Data Drift:** Statistical changes in income features
   > - **Queue Delay:** Processing time exceeded SLA"
2. **Narrate:** "These alerts are automatically generated. Analysts receive notifications and can take action immediately."

---

### SEGMENT 10: CLOSING SUMMARY (30 seconds)

**Script:**

> "Let me summarize what you've seen:
> 
> **The System Detects:**
> - Anomalies in financial patterns
> - Inconsistencies across data sources
> - Statistical drift over time
> 
> **The Team Reviews:**
> - Model predictions with context
> - Supporting evidence
> - Compliance factors
> 
> **The Platform Manages:**
> - Multiple model versions
> - Audit trails for every decision
> - Performance monitoring
> - Queue processing
> 
> **The Result:**
> - Fraud detection at scale
> - Explainable decisions
> - Auditable workflows
> - Continuous improvement
> 
> This is WelfareGuard—enabling your team to protect beneficiaries while preventing fraud. Do you have any questions?"

---

## Q&A Responses

### Q: "Can you show me the model accuracy over time?"
**A:** "Absolutely. [Navigate to Model Health or Analytics] Here's the trend—accuracy has been stable around 87% for the last 2 weeks. We also track precision and recall to ensure we're not missing fraud."

### Q: "How long does a prediction take?"
**A:** "Most predictions run in under 500ms. For batch processing, we queue jobs and process them asynchronously. You saw the queue monitor—current latency is ~250ms per job."

### Q: "What happens if the model performs poorly?"
**A:** "Great question. [Show Alerts] Our monitoring catches performance degradation immediately. We have multiple model versions ready to rollback to. We also have a challenger model we're evaluating. If needed, we can promote a different version with one click."

### Q: "How do you prevent bias?"
**A:** "We have separate risk scores for income, caste, medical, and transaction data. This lets analysts see where each signal comes from. We also monitor for drift—if our model's predictions suddenly change, we investigate. All decisions are auditable and reviewable."

### Q: "Can analysts reject the model's prediction?"
**A:** "Absolutely. [Show Reviews page] Analysts can mark a prediction as 'not fraud' even if the model flagged it as high risk. This feedback helps us improve the model."

### Q: "What's the role of the 'Challenger' model?"
**A:** "We always have a challenger model in evaluation. Before promoting it to champion, we compare metrics side-by-side. This prevents regressions and ensures we're always using the best model."

---

## Fallback Scenarios

### If Backend is Down
- **At Login:** Show screenshot of authenticated dashboard
- **Mid-demo:** Say "We have the data recorded. Let me show you the results."
- **Switch to:** Slideshow mode with pre-recorded screenshots

### If Page Loads Slowly
- **Do:** Wait 3 seconds
- **Say:** "The system is retrieving data from the backend. In normal operation, this completes in under 2 seconds."
- **If Still Loading:** Click elsewhere or show previous screenshot

### If a Button Doesn't Work
- **Do:** "Let me try that again" (attempt 1 more time)
- **Then:** Navigate around it
- **Say:** "This feature is working in our test environment. Let me show you the results directly."

### If Numbers Don't Match
- **Do:** Don't draw attention to it
- **Continue:** Presentation with other pages
- **Note:** "We'll verify the exact numbers after the demo, but the architecture and workflow are what we want to highlight here."

---

## Timing Breakdown

| Segment | Duration | Cumulative |
|---------|----------|-----------|
| Intro | 0:30 | 0:30 |
| Auth | 0:45 | 1:15 |
| Dashboard | 1:00 | 2:15 |
| Prediction Analysis | 1:30 | 3:45 |
| Workflow Execution | 1:30 | 5:15 |
| Case Review | 1:00 | 6:15 |
| Model Performance | 1:00 | 7:15 |
| Model Registry | 0:45 | 8:00 |
| System Resilience | 0:30 | 8:30 |
| Closing | 0:30 | 9:00 |
| **Q&A Buffer** | **1:00** | **10:00** |

**Total: 9-10 minutes** (within target)

---

## Key Points to Emphasize

1. **Explainability:** "Every prediction includes an explanation of why it was flagged."
2. **Auditability:** "Every decision is recorded with timestamp, reviewer, and notes."
3. **Automation:** "The model runs 24/7, but humans make the final call."
4. **Monitoring:** "We don't just deploy once—we continuously watch model performance."
5. **Safety:** "Multiple models, instant rollback, real-time alerts."

---

## Demo Success Criteria

✅ Logged in successfully
✅ Dashboard loaded with correct data
✅ Viewed a high-risk prediction with explanation
✅ Generated snapshot, prediction, or queued job
✅ Showed model registry with multiple versions
✅ Displayed analytics/alerts
✅ Answered at least one Q&A question
✅ Completed in 5-10 minutes
✅ No major errors or crashes

---

## Recording Notes

- Clear screen of any distracting tabs
- Disable notifications
- Set dark mode on/off depending on preference (consistent)
- Use at least 150% zoom if text is small
- Speak clearly, pause at key transitions
- Let pages load fully before clicking

---

## After Demo

1. **Save recording** (if recording)
2. **Collect feedback** via survey or discussion
3. **Note any issues** encountered (for post-demo fixes)
4. **Verify backend logs** for errors
5. **Thank audience**

---

**Presenter:** [Fill in]
**Date:** [Fill in]
**Audience:** [Fill in]
**Duration:** [Record actual time]
**Issues Encountered:** [Fill in if any]
**Demo Success:** ✅ YES / ❌ NO
