# Demo Data Guide

This document explains the demo dataset used for platform validation and demonstrations.

## Overview

The demo dataset includes:
- 5 realistic student profiles (mix of fraud/non-fraud cases)
- 10 feature snapshots across financial and transaction data
- 5 predictions with varying risk levels
- 5 prediction reviews with different outcomes
- 4 monitoring alerts with realistic scenarios
- 2 drift snapshots showing data distribution changes
- 3 model versions (1 champion, 1 challenger, 1 archived)

## Demo Profiles

| Name | Email | Location | Profile Type | Risk Pattern |
|------|-------|----------|--------------|--------------|
| Rajesh Kumar | rajesh.kumar@welfare.in | Mumbai | Legitimate | LOW - Normal behavior |
| Priya Singh | priya.singh@welfare.in | Delhi | Fraud Case | HIGH - Income mismatch |
| Amit Patel | amit.patel@welfare.in | Bangalore | Under Investigation | MEDIUM - Unusual transactions |
| Neha Sharma | neha.sharma@welfare.in | Hyderabad | Legitimate | LOW - Consistent pattern |
| Suresh Reddy | suresh.reddy@welfare.in | Chennai | Legitimate | MEDIUM - Low savings rate |

## Risk Level Distribution

```
HIGH Risk (20%):     1 profile  → Full investigation flow
MEDIUM Risk (40%):   2 profiles → Requires verification
LOW Risk (40%):      2 profiles → Routine monitoring
```

## Feature Data Characteristics

### Financial Features
- Annual Income: ₹250K - ₹450K
- Monthly Expenses: ₹20K - ₹45K
- Savings Rate: 30% - 50%
- Account Age: 24 - 120 months
- Transaction Frequency: 45 - 85 per month

### Transaction Features
- Avg Transaction: ₹5K - ₹9K
- Max Transaction: ₹50K - ₹90K
- Geographic Anomalies: 0-3 per profile
- High-Risk Transactions: 0-8 per profile

## Prediction Distribution

```
Total Predictions:   5
├─ HIGH RISK:       1 (20%)
├─ MEDIUM RISK:     2 (40%)
└─ LOW RISK:        2 (40%)

Review Outcomes:
├─ Confirmed Fraud:        1 (20%)
├─ Not Fraud:              2 (40%)
└─ Under Investigation:    2 (40%)
```

## Alert Scenarios

1. **Model Performance Degradation** (Severity: HIGH)
   - Accuracy dropped to 82% (below 85% threshold)
   - Triggers model retraining workflow

2. **Data Drift Detection** (Severity: MEDIUM)
   - Income feature showing 5% mean shift
   - Requires feature monitoring review

3. **Prediction Anomaly** (Severity: HIGH)
   - 300% spike in high-risk predictions
   - Requires immediate investigation

4. **Queue Processing Delay** (Severity: MEDIUM)
   - Processing time 5.2s (exceeds 5s SLA)
   - System optimization needed

## Drift Analysis

### Recent Drift (1 day ago)
- Drift Score: 0.35 (MODERATE)
- Income: -5% change
- Expenses: +12% change
- Risk Distribution: +15.6% increase in average risk

### Historical Drift (2 days ago)
- Drift Score: 0.12 (LOW)
- Income: -0.5% change
- Expenses: +0.8% change
- Risk Distribution: +2.2% increase in average risk

## Model Registry

### Champion Model
- **Name:** Income Fraud Detector
- **Version:** 2.1.0
- **Algorithm:** Random Forest (200 estimators)
- **Status:** ACTIVE
- **Deployed:** 20 days ago
- **Performance:** 87% accuracy

### Challenger Model
- **Name:** Income Fraud Detector
- **Version:** 2.0.5
- **Algorithm:** Gradient Boosting (150 estimators)
- **Status:** ACTIVE
- **Deployed:** 35 days ago
- **Performance:** 85% accuracy

### Historical Model
- **Name:** Transaction Anomaly Detector
- **Version:** 1.3.2
- **Algorithm:** Isolation Forest
- **Status:** ACTIVE
- **Deployed:** 50 days ago

## Demo Workflow Sequence

### End-to-End Workflow (5-7 minutes)

1. **Login** (30 seconds)
   - Username/Password: Backend analyst credentials
   - Verify RBAC-aware dashboard

2. **Dashboard Review** (1 minute)
   - Verify all 5 profiles loaded
   - Check prediction counts: 5 total
   - Verify risk distribution: HIGH(1), MEDIUM(2), LOW(2)

3. **Prediction Detail** (1 minute)
   - Select a HIGH-risk prediction (Priya Singh)
   - Review features and risk scores
   - Explain risk calculation

4. **Workflow Execution** (2 minutes)
   - Generate snapshot for a profile
   - Create prediction from snapshot
   - Queue prediction job (if available)

5. **Review Submission** (1 minute)
   - Access prediction reviews page
   - Submit review for HIGH-risk case
   - Verify review appears in list

6. **Analytics & Monitoring** (1 minute)
   - Check predictions analytics
   - Review alerts (4 total)
   - Check drift detection (2 snapshots)

7. **Model Registry** (1 minute)
   - List all models (3 total)
   - View champion model details
   - Show model lifecycle (promote/rollback)

## Data Integrity Checks

Before presentation:

- [ ] All 5 profiles are created
- [ ] All 10 feature snapshots are generated
- [ ] All 5 predictions are created with correct risk levels
- [ ] All 5 reviews are submitted with outcomes
- [ ] All 4 alerts are visible in alert center
- [ ] All 2 drift snapshots are recorded
- [ ] Champion model is marked as "champion"
- [ ] Dashboard summary shows correct counts

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No profiles appear | Check student_profiles table population |
| Dashboard shows 0 predictions | Verify prediction_records creation |
| Alerts missing | Check monitoring_alerts table |
| Models not shown | Verify model_versions table has rows |
| Risk levels incorrect | Validate risk_level enum values |

## Performance Expectations

- Dashboard load: < 2 seconds
- Prediction detail: < 1 second
- Analytics page: < 2 seconds
- Model list: < 1 second
- Alerts list: < 1 second

## Notes

- All timestamps use UTC timezone
- IDs are UUIDs for consistency with backend
- Financial values are in Indian Rupees (₹)
- Profile names are representative, not real persons
- All data is synthetic and for demonstration only
