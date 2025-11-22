# MASS - Quick Start Guide

## 🚀 Starting the System

### Option 1: Start Everything at Once (Recommended)

```bash
# From the project root directory
./start_all.sh
```

This will start:
- ✅ Backend API Server (Port 8080)
- ✅ Teacher Dashboard (Port 8501)
- ✅ Admin Dashboard (Port 8502)
- ✅ Student Portal (Port 8503)

### Option 2: Start Services Individually

#### Backend API Only
```bash
cd backend
./start_server.sh dev    # Development mode with auto-reload
# OR
./start_server.sh prod   # Production mode (4 workers, no reload)
```

#### Individual Dashboards
```bash
cd backend
source venv/bin/activate

# Teacher Dashboard
streamlit run dashboard/app_template.py --server.port=8501

# Admin Dashboard
streamlit run dashboard/admin_dashboard.py --server.port=8502

# Student Portal
streamlit run dashboard/student_portal.py --server.port=8503
```

---

## 🛑 Stopping the System

```bash
# Stop all services
./stop_all.sh

# OR stop individual services
cd backend
./stop_server.sh
```

---

## 🌐 Access Points

Once started, access the system at:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Backend API** | http://localhost:8080 | N/A |
| **API Documentation** | http://localhost:8080/docs | N/A |
| **Teacher Dashboard** | http://localhost:8501 | `teacher` / `password123` |
| **Admin Dashboard** | http://localhost:8502 | `admin` / `admin123` |
| **Student Portal** | http://localhost:8503 | `student123` / `password` |

---

## 📊 What's Available

### Data Population Status
- ✅ **50 Students** across grades 6-8
- ✅ **2,150+ Skill Assessments** (7 skills per student)
- ✅ **1,966 Classroom Transcripts** with realistic dialogue
- ✅ **2,150+ Evidence Items** (linguistic + behavioral)
- ✅ **AI-Generated Reasoning** for every assessment
- ✅ **Personalized Recommendations** for skill development

### Skills Tracked
1. **Empathy** - Understanding others' perspectives
2. **Adaptability** - Adjusting to new situations
3. **Problem Solving** - Finding solutions to challenges
4. **Self-Regulation** - Managing emotions and behaviors
5. **Resilience** - Bouncing back from setbacks
6. **Communication** - Sharing ideas effectively
7. **Collaboration** - Working well with others

---

## 🎯 Quick Testing

### Test the Backend API
```bash
# Health check
curl http://localhost:8080/api/v1/health

# Get all students
curl http://localhost:8080/api/v1/students | jq '.[0:3]'

# Get assessments for first student
STUDENT_ID=$(curl -s http://localhost:8080/api/v1/students | jq -r '.[0].id')
curl "http://localhost:8080/api/v1/assessments/$STUDENT_ID" | jq '.[0]'
```

### Test the Dashboards
1. Open http://localhost:8501 in your browser
2. Login with `teacher` / `password123`
3. Select a student from the dropdown
4. View their skill assessments with evidence and AI reasoning

---

## 📝 Logs

View real-time logs:

```bash
# Backend API
tail -f /tmp/mass_api.log

# Teacher Dashboard
tail -f /tmp/mass_teacher.log

# Admin Dashboard
tail -f /tmp/mass_admin.log

# Student Portal
tail -f /tmp/mass_student.log
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find and kill process on port 8080
lsof -ti:8080 | xargs kill

# Or use stop_all.sh to clean up
./stop_all.sh
```

### Database Connection Issues
```bash
# Check if PostgreSQL is running
psql $DATABASE_URL -c "SELECT 1;"

# Check .env file
cat backend/.env | grep DATABASE_URL
```

### Virtual Environment Issues
```bash
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8080/docs (when server is running)
- **Dashboard README**: `backend/dashboard/README.md`
- **Project PRD**: `.taskmaster/docs/prd.txt`

---

## 🎉 Next Steps

1. **Explore the Dashboards**: Try all three interfaces
2. **Review the Evidence**: Click on skills to see supporting evidence
3. **Test the Admin Features**: Use demographic filters and exports
4. **Check the Student Portal**: See the age-appropriate, growth-focused design
5. **API Integration**: Use the REST API to build additional features

---

**Need Help?** Check the main README or open an issue on GitHub.
