# UnseenEdge AI Dashboards

This directory contains three Streamlit-based dashboards for the UnseenEdge AI Skill Assessment System:

1. **Teacher Dashboard** (`app_template.py`) - For individual teachers to view their students
2. **Administrator Dashboard** (`admin_dashboard.py`) - For school-wide analytics and equity analysis
3. **Student Portal** (`student_portal.py`) - For students to view their own skills with age-appropriate design

## Quick Start

### Prerequisites

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (if not already installed)
pip install -r dashboard/requirements.txt
```

### Running the Dashboards

#### Teacher Dashboard (Port 8501)
```bash
streamlit run dashboard/app_template.py --server.port=8501
```
**Demo Credentials:**
- Username: `teacher`
- Password: `password123`

**Features:**
- Search and select individual students
- View skill assessments with gauge visualizations
- Examine evidence supporting each skill
- Read GPT-4 generated reasoning
- Class-wide overview with heatmaps
- Progress tracking over time

#### Administrator Dashboard (Port 8502)
```bash
streamlit run dashboard/admin_dashboard.py --server.port=8502
```
**Demo Credentials:**
- Username: `admin`
- Password: `admin123`

**Features:**
- School-wide skill distribution views (all 7 skills)
- Trend analysis over time (4-week, 12-week, semester views)
- Equity analysis with demographic breakdowns (gender, ethnicity, grade)
- Heatmaps showing skill levels by grade/class
- Longitudinal cohort progress tracking
- Student-level drill-down with breadcrumb navigation
- Export functionality (CSV data export, text summary reports)
- Performance optimized for 1000+ students

#### Student Portal (Port 8503)
```bash
streamlit run dashboard/student_portal.py --server.port=8503
```
**Demo Credentials:**
- Username: `student123`
- Password: `password`

**Features:**
- Student-friendly skill names (e.g., "Understanding Others" instead of "Empathy")
- Visual skill profile (radar chart and bar charts)
- Growth-oriented feedback (emphasizes improvement, not deficits)
- Achievement badges and milestones
- Historical progress view
- Optional reflection journal
- Age-appropriate language (middle school reading level)
- WCAG 2.1 AA accessibility compliance
- Mobile-responsive design
- Privacy-first (students only see their own data)

## Architecture

### API Integration

All dashboards connect to the FastAPI backend at `http://localhost:8000/api/v1` by default. Configure the URL via environment variable:

```bash
export API_URL="https://your-backend-url.com/api/v1"
```

### Skills Tracked

The system tracks 7 non-academic skills:

1. **Empathy** - Understanding and sharing feelings of others
2. **Adaptability** - Adjusting to new situations
3. **Problem Solving** - Finding solutions to challenges
4. **Self-Regulation** - Managing emotions and behaviors
5. **Resilience** - Bouncing back from setbacks
6. **Communication** - Sharing ideas effectively
7. **Collaboration** - Working well with others

### Authentication

Each dashboard uses `streamlit-authenticator` with demo credentials. In production:

1. Replace hardcoded credentials with environment variables
2. Use hashed passwords stored securely (e.g., in Google Secret Manager)
3. Integrate with school SSO/OAuth providers
4. Implement role-based access control (RBAC)

## Configuration

### Environment Variables

```bash
# API Configuration
API_URL=http://localhost:8000/api/v1

# Teacher Dashboard
DASHBOARD_USER=teacher
DASHBOARD_PASSWORD=password123
DASHBOARD_NAME=Teacher
DASHBOARD_COOKIE_KEY=change_this_secret_key

# Admin Dashboard
ADMIN_USER=admin
ADMIN_PASSWORD=admin123
ADMIN_NAME=Administrator
ADMIN_COOKIE_KEY=change_this_admin_key

# Student Portal
STUDENT_USER=student123
STUDENT_PASSWORD=password
STUDENT_NAME=Student
STUDENT_COOKIE_KEY=change_this_student_key
```

### Customization

#### Colors
Update `SKILL_COLORS` dictionary in each file to change skill visualization colors.

#### Thresholds
Modify `CONFIDENCE_THRESHOLDS` in teacher dashboard to adjust confidence level thresholds.

#### Time Periods
Edit `TIME_PERIODS` in admin dashboard to add/remove trend analysis time periods.

## Data Flow

```
┌─────────────────┐
│   Dashboards    │
│  (Streamlit)    │
└────────┬────────┘
         │
         │ HTTP Requests
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   Backend       │
└────────┬────────┘
         │
         │ SQLAlchemy
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   Database      │
└─────────────────┘
```

## Accessibility Features (Student Portal)

### WCAG 2.1 AA Compliance

- ✅ Color contrast ratios meet AA standards
- ✅ Focus indicators for keyboard navigation
- ✅ Semantic HTML structure
- ✅ ARIA labels where appropriate
- ✅ Responsive font sizes (16px minimum)
- ✅ High contrast mode support
- ✅ Mobile-responsive design

### Testing Accessibility

```bash
# Screen reader testing (macOS)
# Enable VoiceOver: Cmd + F5

# Keyboard navigation testing
# Use Tab, Shift+Tab, Enter, Space to navigate

# High contrast mode (Windows)
# Settings > Ease of Access > High Contrast
```

## Performance Optimization

### Caching

The teacher dashboard uses Streamlit's `@st.cache_data` decorator:
- Student list: cached for 5 minutes
- Individual assessments: cached for 1 minute

### Batch Processing

The admin dashboard supports batch assessment of up to 100 students concurrently, with optimized timeout settings.

### Database Queries

For production deployments with 1000+ students:
- Implement database indexes on `student_id`, `skill_type`, `created_at`
- Use database query pagination
- Consider implementing Redis caching layer

## Development

### Running in Development Mode

```bash
# Run with auto-reload
streamlit run dashboard/admin_dashboard.py --server.port=8502 --server.headless=false

# Debug mode
streamlit run dashboard/admin_dashboard.py --logger.level=debug
```

### Adding New Features

1. Add visualization function to appropriate section
2. Update navigation options in sidebar
3. Add new page/tab in main content area
4. Test with sample data
5. Update this README

## Deployment

### Option 1: Streamlit Cloud (Free)

1. Push code to GitHub
2. Connect repository at [share.streamlit.io](https://share.streamlit.io)
3. Configure secrets in dashboard settings
4. Deploy!

### Option 2: Google Cloud Run

See `DEPLOYMENT.md` for detailed instructions on deploying to Google Cloud Run with:
- Docker containerization
- Automatic HTTPS
- Automatic scaling
- Load balancing

### Option 3: Self-Hosted

```bash
# Install production server
pip install streamlit

# Run with production settings
streamlit run dashboard/admin_dashboard.py \
  --server.port=8502 \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false
```

## Troubleshooting

### Dashboard won't load

1. Check if backend API is running:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. Verify environment variables are set correctly

3. Check Streamlit logs for errors

### No students showing up

1. Ensure database is seeded with sample data:
   ```bash
   cd backend
   python scripts/seed_data.py
   ```

2. Check API endpoint:
   ```bash
   curl http://localhost:8000/api/v1/students
   ```

### Slow performance

1. Reduce batch size in admin dashboard (default: 100 students)
2. Implement database indexes
3. Add Redis caching layer
4. Use CDN for static assets

## Future Enhancements

### Task 27 Remaining Work
- [ ] Implement real historical data queries for trend analysis
- [ ] Add alert system for low-performing groups
- [ ] Implement PDF export functionality
- [ ] Add custom report generation interface
- [ ] Conduct usability testing with 2-3 administrators

### Task 28 Remaining Work
- [ ] Add more achievement badges and milestone detection
- [ ] Implement reflection journal data persistence
- [ ] Conduct user testing with 10-15 middle school students
- [ ] Add accessibility audit with automated tools
- [ ] Test with actual screen readers and assistive technologies

### General Improvements
- [ ] Add real-time updates with WebSockets
- [ ] Implement push notifications for new assessments
- [ ] Add data visualization download options (PNG, SVG)
- [ ] Implement advanced filtering and search
- [ ] Add comparison view (compare multiple students)
- [ ] Integrate with Learning Management Systems (LMS)
- [ ] Add internationalization (i18n) support

## Testing

### Manual Testing Checklist

#### Teacher Dashboard
- [ ] Can log in successfully
- [ ] Can view list of students
- [ ] Can view individual student assessment
- [ ] Gauge charts display correctly
- [ ] Evidence viewer shows relevant evidence
- [ ] GPT-4 reasoning displays
- [ ] Class overview heatmap works
- [ ] Logout functionality works

#### Admin Dashboard
- [ ] Can log in successfully
- [ ] School overview displays metrics
- [ ] Skill distribution bar chart shows all 7 skills
- [ ] Trend analysis generates graphs
- [ ] Equity analysis shows demographic breakdowns
- [ ] Grade heatmap displays correctly
- [ ] Student drill-down navigation works
- [ ] CSV export downloads correctly
- [ ] Summary report generates

#### Student Portal
- [ ] Can log in successfully
- [ ] Achievement badges display
- [ ] Radar chart shows all skills
- [ ] Bar chart displays correctly
- [ ] Growth feedback is positive and encouraging
- [ ] Progress timeline shows historical data
- [ ] Reflection journal accepts input
- [ ] Mobile responsive design works
- [ ] Keyboard navigation works
- [ ] High contrast mode displays correctly

### Automated Testing

```bash
# Install testing dependencies
pip install pytest pytest-streamlit selenium

# Run tests (when implemented)
pytest tests/test_dashboards.py
```

## Support

For questions or issues:
1. Check this README
2. Review `DEPLOYMENT.md` for deployment issues
3. Check the main project README
4. Create an issue on GitHub

## License

Copyright © 2025 UnseenEdge AI. All rights reserved.
