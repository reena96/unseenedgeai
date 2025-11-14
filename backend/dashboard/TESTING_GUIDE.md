# Testing Guide for Dashboard Changes (Tasks 27 & 28)

## Prerequisites

### 1. Install Dependencies
```bash
cd /Users/reena/gauntletai/unseenedgeai/backend

# Install new dependencies (reportlab for PDF export)
pip install -r dashboard/requirements.txt

# Or install reportlab directly
pip install reportlab>=4.0.0
```

### 2. Verify Backend API is Running
```bash
# In one terminal, start the backend API
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Verify it's running
curl http://localhost:8000/api/v1/health
```

### 3. Seed Test Data (if needed)
```bash
# Make sure you have sample students and assessments
cd backend
python scripts/seed_data.py  # If this exists
```

---

## Testing Admin Dashboard (Task 27)

### Start the Admin Dashboard
```bash
cd /Users/reena/gauntletai/unseenedgeai/backend

streamlit run dashboard/admin_dashboard.py --server.port=8502
```

**Login Credentials:**
- Username: `admin`
- Password: `admin123`

---

### ✅ Test 1: Real Historical Data Queries

**What Changed:** Trend analysis and cohort graphs now use real historical data instead of simulated data.

**How to Test:**

1. Navigate to **"📈 Trends & Progress"** page
2. Select different time periods (4 weeks, 12 weeks, etc.)
3. **Expected Results:**
   - Title should say "(Real Data)" if historical data exists
   - Title should say "(Snapshot)" or "(No Historical Data)" if no history
   - Graphs should show actual data trends, not simulated linear progressions

4. Scroll to **"Cohort Progress (Longitudinal)"**
5. **Expected Results:**
   - Title indicates "Real Data" or "Current Snapshot"
   - If real data exists, you'll see actual monthly progression by grade

**Verification:**
```bash
# Check if historical assessments exist
curl http://localhost:8000/api/v1/assessments/{student_id}?limit=50
```

---

### ✅ Test 2: PDF Export Functionality

**What Changed:** Added professional PDF report generation with tables and formatting.

**How to Test:**

1. Navigate to **"📥 Export Reports"** page
2. You should now see **3 columns** (CSV, TXT, PDF)
3. Click **"🔄 Generate PDF"** button
4. **Expected Results:**
   - Spinner appears: "Generating PDF report..."
   - Success message: "✅ PDF generated successfully!"
   - Download button appears: "📥 Download PDF"

5. Click the download button
6. Open the downloaded PDF file
7. **Verify PDF Contains:**
   - Title: "UnseenEdge AI - School-Wide Skill Assessment Report"
   - Summary Statistics table
   - Skill Averages table with all 7 skills
   - Grade Distribution table
   - Professional formatting with colors and borders

**If PDF Generation Fails:**
```bash
# Make sure reportlab is installed
pip show reportlab

# If not installed:
pip install reportlab
```

---

### ✅ Test 3: Alert System for Low-Performing Groups

**What Changed:** Automatic detection of groups needing support, displayed on School Overview page.

**How to Test:**

1. Navigate to **"📊 School Overview"** page
2. Look for a section with alerts **after the metrics** and **before the main chart**
3. **Expected Results:**

   **If alerts exist:**
   - Warning banner: "⚠️ X Alert(s) Detected: Groups needing support"
   - Expandable section: "📋 View All Alerts"
   - Each alert shows:
     - Severity emoji (🔴 High or 🟡 Medium)
     - Group name (e.g., "Grade 7")
     - Skill affected
     - Score percentage
     - Number of students
     - Recommendation

   **If no alerts:**
   - Success message: "✅ No alerts: All groups performing above threshold!"

4. **Test with Different Scenarios:**
   - Expand the alerts to see details
   - Check if alerts make sense (low scores flagged, equity gaps identified)

**Manual Testing with Sample Data:**
To force alerts for testing, you can temporarily modify the threshold:
```python
# In admin_dashboard.py, temporarily change threshold from 0.60 to 0.90
alerts = identify_low_performing_groups(df, threshold=0.90)
```

---

### ✅ Test 4: Usability Testing Documentation

**What Changed:** Created comprehensive usability testing plan document.

**How to Test:**

1. Open the file:
```bash
cat backend/dashboard/ADMIN_USABILITY_TESTING_PLAN.md
# Or open in your editor
```

2. **Verify Document Contains:**
   - Testing objectives (5 objectives)
   - Target participants (2-3 administrators)
   - 6 detailed test scenarios with success criteria
   - Data collection methods
   - Success benchmarks (75%+ SUS score, etc.)
   - Interview questions
   - Timeline and deliverables

---

## Testing Student Portal (Task 28)

### Start the Student Portal
```bash
cd /Users/reena/gauntletai/unseenedgeai/backend

streamlit run dashboard/student_portal.py --server.port=8503
```

**Login Credentials:**
- Username: `student123`
- Password: `password`

---

### ✅ Test 5: Enhanced Achievement Badges

**What Changed:** Expanded from 4 to 12 badge types with sophisticated detection logic.

**How to Test:**

1. Login to the student portal
2. Look at the **"🏆 Your Achievements"** section
3. **Expected Results:**
   - You should see MORE badges than before (up to 12 possible)
   - New badges include:
     - ❤️ Empathy Expert
     - 🧩 Problem Crusher
     - 💬 Communication Star
     - 🤝 Team MVP
     - 🎨 Well-Rounded
     - 🌟 Rising Star
     - 📈 On Fire!
     - 💪 Bounce-Back Boss

4. **Test Badge Logic:**
   - Badges should match the student's actual skill levels
   - Students with 80%+ in a skill should see skill-specific badges
   - Students with all skills >70% should see "All-Star"
   - Students with balanced skills should see "Well-Rounded"

**Check Console for Badge Detection:**
In the Streamlit app, you can add temporary logging:
```python
# Add after badges_earned = check_badges_earned(...)
st.write(f"Debug: {len(badges_earned)} badges earned")
```

---

### ✅ Test 6: Reflection Journal Persistence

**What Changed:** Reflections now save to files and provide feedback.

**How to Test:**

1. Scroll to **"📝 My Reflections"** section
2. Write a test reflection:
   ```
   I'm proud of my empathy skills today. I helped a classmate who was struggling with math. Next time, I want to work on staying calm when I get frustrated.
   ```

3. Click **"💾 Save My Reflection"** button
4. **Expected Results:**
   - Success message: "✅ Your reflection has been saved! Great job thinking about your growth!"
   - Info message: "💡 Your teacher can see your reflections to better support your learning."

5. **Verify File Creation:**
```bash
# Check reflections directory
ls -la /Users/reena/gauntletai/unseenedgeai/backend/dashboard/reflections/

# View the saved reflection
cat backend/dashboard/reflections/{student_id}_reflections.txt
```

6. **Test Error Handling:**
   - Try saving an empty reflection
   - Expected: "✏️ Write something first before saving!"

---

### ✅ Test 7: Historical Data for Improvement Tracking

**What Changed:** Badge system now uses historical data to detect improvement streaks.

**How to Test:**

1. The system automatically fetches historical data on load
2. If historical data exists with improvements, you should see:
   - **📈 On Fire!** badge (for students improving in 2+ skills by 5%+)

3. **Verify API Call:**
   - Check Streamlit logs for API calls to `/assessments/{student_id}`
   - Should see: `GET /assessments/{student_id}?limit=50`

4. **Test Without Historical Data:**
   - New students should still see badges based on current scores
   - Should NOT see improvement badges

---

### ✅ Test 8: User Testing Documentation

**What Changed:** Created student user testing plan and accessibility audit.

**How to Test:**

1. **View User Testing Plan:**
```bash
cat backend/dashboard/STUDENT_USER_TESTING_PLAN.md
```

2. **Verify Document Contains:**
   - 7 age-appropriate test scenarios
   - Comprehension assessment questions
   - Emoji-based satisfaction survey
   - Ethical considerations for testing with children
   - Target: 85%+ comprehension

3. **View Accessibility Audit:**
```bash
cat backend/dashboard/ACCESSIBILITY_AUDIT.md
```

4. **Verify Audit Contains:**
   - WCAG 2.1 AA compliance assessment
   - Screen reader testing results (NVDA, VoiceOver, JAWS)
   - Keyboard navigation testing
   - Color contrast analysis
   - Prioritized fixes (P0, P1, P2)

---

## Integration Testing

### Test Complete User Flows

#### Admin Flow: Identifying and Acting on Alerts

1. **Login** to admin dashboard
2. **Navigate** to School Overview
3. **View alerts** in expandable section
4. **Navigate** to Equity Analysis
5. **Analyze** the demographic group mentioned in alert
6. **Navigate** to Heatmaps
7. **Drill down** to specific classroom
8. **Export** PDF report for principal meeting

#### Student Flow: Viewing Progress and Reflecting

1. **Login** to student portal
2. **View** skill web (radar chart)
3. **Read** growth feedback messages
4. **Check** achievement badges earned
5. **View** progress timeline
6. **Write** reflection about one skill
7. **Save** reflection successfully

---

## Performance Testing

### Test with Large Datasets

1. **Admin Dashboard with 100+ Students:**
```bash
# The admin dashboard limits to 100 students for demo
# Verify load time is <5 seconds
```

2. **Check for Console Errors:**
   - Open browser DevTools (F12)
   - Check Console tab for JavaScript errors
   - Check Network tab for failed API calls

---

## Regression Testing

### Verify Existing Features Still Work

#### Admin Dashboard:
- ✅ Login/logout
- ✅ School-wide skill distribution bar chart
- ✅ Skill-specific histograms
- ✅ Equity analysis by gender/ethnicity/grade
- ✅ Grade/class heatmaps
- ✅ Student drill-down with radar chart
- ✅ CSV export
- ✅ Text summary export

#### Student Portal:
- ✅ Login/logout
- ✅ Skill radar chart
- ✅ Skill bar chart
- ✅ Feedback messages
- ✅ Mobile responsiveness

---

## Common Issues & Troubleshooting

### Issue 1: PDF Generation Fails

**Symptoms:**
- Error message: "PDF export requires reportlab"
- No download button appears

**Solution:**
```bash
pip install reportlab>=4.0.0

# Restart Streamlit
# Ctrl+C to stop
streamlit run dashboard/admin_dashboard.py --server.port=8502
```

---

### Issue 2: No Historical Data

**Symptoms:**
- Trend graphs show "No Historical Data" or "Current Snapshot"
- Improvement badges not appearing

**Solution:**
```bash
# Create some historical assessments via API
curl -X POST http://localhost:8000/api/v1/assessments/{student_id} \
  -H "Content-Type: application/json" \
  -d '{"skill_type": "empathy", "use_cached": false}'

# Wait a day or manually adjust created_at timestamps in database
```

---

### Issue 3: Reflections Not Saving

**Symptoms:**
- Error message appears
- No file created in reflections/ directory

**Solution:**
```bash
# Create reflections directory manually
mkdir -p backend/dashboard/reflections

# Check permissions
chmod 755 backend/dashboard/reflections
```

---

### Issue 4: API Not Responding

**Symptoms:**
- Dashboard shows "❌ API Disconnected"
- Dashboards can't load data

**Solution:**
```bash
# Restart the backend API
cd backend
uvicorn app.main:app --reload --port 8000

# Verify health endpoint
curl http://localhost:8000/api/v1/health/detailed
```

---

## Automated Testing (Future)

### Unit Tests to Write

```python
# tests/test_admin_dashboard.py
def test_identify_low_performing_groups():
    """Test alert detection logic"""
    df = create_test_dataframe()
    alerts = identify_low_performing_groups(df, threshold=0.60)
    assert len(alerts) > 0
    assert alerts[0]["severity"] in ["high", "medium"]

def test_export_to_pdf():
    """Test PDF generation"""
    df = create_test_dataframe()
    pdf_buffer = export_to_pdf(df)
    assert pdf_buffer is not None
    assert len(pdf_buffer.getvalue()) > 0

# tests/test_student_portal.py
def test_check_badges_earned():
    """Test badge detection logic"""
    skills = [{"skill_type": "empathy", "score": 0.85}] * 7
    badges = check_badges_earned(skills)
    assert len(badges) >= 5  # Should earn multiple badges

def test_save_reflection():
    """Test reflection persistence"""
    api = StudentAPI("http://localhost:8000/api/v1")
    success = api.save_reflection("test_student", "Test reflection")
    assert success == True
```

---

## Checklist: All Features Tested

### Admin Dashboard (Task 27):
- [ ] Real historical data in trends (or graceful fallback)
- [ ] Real historical data in cohort graphs (or graceful fallback)
- [ ] PDF export generates successfully
- [ ] PDF contains all expected sections
- [ ] Alerts appear when groups underperform
- [ ] Alerts show correct severity and recommendations
- [ ] Alerts expandable section works
- [ ] Usability testing plan document exists and is comprehensive

### Student Portal (Task 28):
- [ ] 12 achievement badges types available
- [ ] Badges awarded based on correct logic
- [ ] Skill-specific badges appear for mastery (80%+)
- [ ] Balanced skills badge for well-rounded students
- [ ] Improvement badge when historical data shows growth
- [ ] Reflection journal saves successfully
- [ ] Reflection creates timestamped file
- [ ] Success/error messages display correctly
- [ ] User testing plan document exists
- [ ] Accessibility audit document exists

### Documentation:
- [ ] ADMIN_USABILITY_TESTING_PLAN.md is comprehensive
- [ ] STUDENT_USER_TESTING_PLAN.md is age-appropriate
- [ ] ACCESSIBILITY_AUDIT.md covers WCAG 2.1 AA
- [ ] All documents are professionally formatted

---

## Next Steps After Testing

1. **Fix any bugs found** during testing
2. **Implement P0 accessibility fixes** from audit
3. **Conduct actual usability testing** with 2-3 administrators
4. **Conduct user testing** with 10-15 students
5. **Deploy to production** environment

---

**Last Updated:** 2025-11-14
**Tested By:** [Your Name]
**Version:** 1.0
