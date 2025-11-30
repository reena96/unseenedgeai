# Progress Tracking Quick Start Guide

## What Changed?

The dashboard now displays **real historical skill data** instead of mock/dummy data.

## Key Features

- View skill trends over time for any student
- Filter by date range: Last 7/30/90 Days or All Time
- Interactive charts with hover details
- Summary statistics per skill
- Handles uneven data distribution across skills

## How to Use

### 1. Start the Backend API
```bash
cd /Users/reena/gauntletai/unseenedgeai/backend
./scripts/start-api.sh
```

### 2. Start the Dashboard
```bash
streamlit run dashboard/app_template.py
```

### 3. Access Progress Tracking
1. Open browser to http://localhost:8501
2. Login: `teacher` / `password123`
3. Click "📈 Progress Tracking" in sidebar
4. Select a student (e.g., "Noah Brooks")
5. Choose time period (default: All Time)
6. Click "📈 Load Progress"

## What You'll See

### Metrics
- **Total Assessments:** How many data points exist
- **Data Since:** Earliest assessment date
- **Skills Tracked:** How many of the 7 skills have data

### Progress Chart
- Line graph showing each skill over time
- Color-coded by skill type
- Hover to see exact date and score
- Only shows skills with data

### Summary Table
Per skill breakdown:
- Total assessments count
- Latest score
- Average score
- Min/Max scores

## Example Data

For student "Noah Brooks" (427d8809-b729-4ef6-b91e-b7d6c53ee95a):
- 83 total assessments
- Data from 2025-09-05 to 2025-11-30
- All 7 skills tracked
- Most skills have 5-17 data points each

## Troubleshooting

### "No historical assessments found"
- Student has no assessments in database
- Run: `python scripts/seed_data.py` to generate sample data
- Or create assessments via API

### "Error loading assessment data"
- Backend API not running
- Check: `curl http://localhost:8080/health`
- Start API with: `./scripts/start-api.sh`

### Chart shows "No historical data available"
- API returned empty array
- Check API directly:
  ```bash
  curl "http://localhost:8080/api/v1/assessments/{student_id}?limit=100"
  ```

## Testing

Verify functionality:
```bash
python3 test_progress_chart.py
```

Expected output:
```
✅ Successfully fetched 83 assessments
✅ Progress chart data processing successful!
✅ All tests passed!
```

## Date Range Filters

- **All Time:** Shows all historical data (no filter)
- **Last 7 Days:** Only assessments from past week
- **Last 30 Days:** Only assessments from past month
- **Last 90 Days:** Only assessments from past quarter

Filters are applied based on the `created_at` timestamp from the API.

## Skills Tracked

1. Empathy
2. Adaptability
3. Problem Solving
4. Self Regulation
5. Resilience
6. Communication
7. Collaboration

Each skill is color-coded consistently across all visualizations.

## API Endpoint Used

```
GET /api/v1/assessments/{student_id}?limit=1000
```

Returns array of assessment objects with:
- `skill_type`: Which skill was assessed
- `score`: 0.0-1.0 (displayed as 0-100%)
- `created_at`: ISO 8601 timestamp
- Plus confidence, reasoning, evidence, etc.

## Next Steps

Use the progress data to:
- Identify skill improvement trends
- Spot areas needing intervention
- Track effectiveness of teaching strategies
- Generate progress reports for parents
- Make data-driven educational decisions

---

**Quick Reference**
- Backend: http://localhost:8080
- Dashboard: http://localhost:8501
- Login: teacher/password123
- Test: `python3 test_progress_chart.py`
