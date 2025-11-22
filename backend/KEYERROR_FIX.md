# KeyError Fix: total_inference_time_ms

## Issue
```
KeyError: 'total_inference_time_ms'
File: dashboard/app_template.py, line 457
Code: assessment['total_inference_time_ms']
```

## Root Cause

The `app_template.py` dashboard was expecting the `total_inference_time_ms` field that comes from the ML inference endpoint response, but we changed it to use the assessment retrieval endpoint which doesn't include this field.

### Response Differences

**ML Inference Endpoint** (`POST /infer/{student_id}`):
```json
{
  "student_id": "uuid",
  "skills": [...],
  "total_inference_time_ms": 180.5,  ← This field
  "timestamp": "2025-11-19T12:00:00",
  "model_versions": {...}
}
```

**Assessment Retrieval Endpoint** (`GET /assessments/{student_id}`):
```json
[
  {
    "id": "uuid",
    "student_id": "uuid",
    "skill_type": "empathy",
    "score": 0.85,
    "confidence": 0.90,
    "reasoning": "...",
    "created_at": "2025-11-19T12:00:00"
  }
]
```

After our formatting in `get_student_assessment()`:
```json
{
  "student_id": "uuid",
  "skills": [...],
  "timestamp": "2025-11-19T12:00:00"
  // No total_inference_time_ms field!
}
```

## Solution

Changed the code to check if `total_inference_time_ms` exists before trying to use it, and show an alternative metric if it doesn't.

### Code Change

**File:** `dashboard/app_template.py` (lines 455-466)

**Before:**
```python
with col2:
    st.metric(
        "Inference Time", f"{assessment['total_inference_time_ms']}ms"
    )
```

**After:**
```python
with col2:
    # Only show inference time if available (from ML inference endpoint)
    if "total_inference_time_ms" in assessment:
        st.metric(
            "Inference Time", f"{assessment['total_inference_time_ms']}ms"
        )
    else:
        # Show assessment timestamp instead
        timestamp = assessment.get("timestamp", datetime.now().isoformat())
        st.metric("Assessed At", timestamp[:10] if isinstance(timestamp, str) else "Recent")
```

### Changes Made

1. **Added conditional check** for `total_inference_time_ms` field
2. **Fallback display** shows assessment timestamp instead
3. **No breaking changes** - works with both inference and assessment responses

## Verification

### Other Dashboards Checked

✅ **student_portal.py** - No references to `total_inference_time_ms`
✅ **admin_dashboard.py** - No references to `total_inference_time_ms`
✅ **app_template.py** - Fixed (this was the only occurrence)

### Fields Checked
- `total_inference_time_ms` ✅ Fixed
- `inference_time_ms` ✅ Not used anywhere
- `model_version` ✅ Not used in dashboards
- `feature_importance` ✅ Not used in dashboards

## Testing

### Expected Behavior

When using **assessment retrieval endpoint** (current setup):
- Column 2 shows: "Assessed At: 2025-11-19"
- No errors when displaying assessment metadata

When using **ML inference endpoint** (future):
- Column 2 shows: "Inference Time: 180ms"
- Displays actual inference timing

### Test Steps

1. Open app_template dashboard (will be on port 8503)
2. Select a student from dropdown
3. Click "Get Assessment" button
4. Should display:
   - Column 1: Student ID
   - Column 2: Assessed At date (not "Inference Time")
   - Column 3: Current Time
5. No KeyError should occur

## Status

✅ **Fix Applied**
- Code updated in app_template.py
- Handles both response formats gracefully
- Dashboard restarted (port 8503)

✅ **All Dashboards Checked**
- student_portal.py - No issues found
- admin_dashboard.py - No issues found
- app_template.py - Fixed

## Related Files

- **Main Fix:** `dashboard/app_template.py:455-466`
- **Previous Fix:** `dashboard/student_portal.py:133-168` (endpoint change)
- **Previous Fix:** `dashboard/app_template.py:80-115` (endpoint change)
- **Documentation:** `DASHBOARD_FIX_SUMMARY.md`
- **Documentation:** `INFERENCE_VS_ASSESSMENT_ENDPOINTS.md`

## Summary

The KeyError was caused by code expecting ML inference response format but receiving assessment retrieval response format. Fixed by checking if the field exists before accessing it and providing a sensible fallback display.

---

**Fixed:** 2025-11-19
**Status:** ✅ Resolved
**Impact:** App template dashboard now works with assessment endpoint
