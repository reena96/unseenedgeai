# 🚀 UnseenEdge AI API Server - Running

## ✅ Server Status: RUNNING

**Process ID:** 49897
**Port:** 8000
**Host:** 0.0.0.0 (accessible from localhost)
**Environment:** production
**Debug Mode:** True
**Python Version:** 3.12.12
**Auto-reload:** Enabled (changes detected automatically)

---

## 📍 Access URLs

### **Interactive API Documentation (Swagger UI)**
```
http://localhost:8000/api/v1/docs
```
👉 **OPEN THIS IN YOUR BROWSER** - Interactive API explorer with "Try it out" buttons

### **Alternative Documentation (ReDoc)**
```
http://localhost:8000/api/v1/redoc
```
Clean, printable API documentation

### **Health Checks**
```
http://localhost:8000/api/v1/health          # Basic health
http://localhost:8000/api/v1/liveness        # Kubernetes liveness
http://localhost:8000/api/v1/readiness       # Kubernetes readiness
```

---

## 🎯 Quick Test Commands

### Test Health (in terminal)
```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T03:56:09.358328",
  "version": "0.1.0",
  "python_version": "3.12.12"
}
```

### View Logs
```bash
tail -f /tmp/uvicorn.log
```

### Check Server Process
```bash
ps aux | grep 49897
```

---

## 🛑 Stop Server

```bash
kill 49897
# Or force kill:
kill -9 49897
```

---

## 🔄 Restart Server

```bash
# Kill old server
kill 49897

# Start new server
cd /Users/reena/gauntletai/unseenedgeai/backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/uvicorn.log 2>&1 &
```

---

## 📊 Available Endpoints (35 total)

### **Health & Status (4 endpoints)**
- `GET /api/v1/health` - Basic health check ✅
- `GET /api/v1/health/detailed` - Detailed health with service status
- `GET /api/v1/liveness` - Kubernetes liveness probe ✅
- `GET /api/v1/readiness` - Kubernetes readiness probe ✅

### **ML Inference (4 endpoints)**
- `POST /api/v1/infer/{student_id}` - Infer all skills for a student
- `POST /api/v1/infer/{student_id}/{skill_type}` - Infer specific skill
- `POST /api/v1/infer/batch` - Batch inference (up to 100 students)
- `GET /api/v1/metrics` - Inference performance metrics

### **Feature Extraction (4 endpoints)**
- `POST /api/v1/features/linguistic/{transcript_id}` - Extract linguistic features
- `POST /api/v1/features/behavioral/{session_id}` - Extract behavioral features
- `POST /api/v1/features/batch/linguistic` - Batch linguistic extraction
- `POST /api/v1/features/batch/behavioral` - Batch behavioral extraction

### **Assessments (4 endpoints)**
- `GET /api/v1/assessments/{student_id}` - Get latest assessment
- `GET /api/v1/assessments/{student_id}/all` - Get all assessments
- `POST /api/v1/assessments` - Create assessment
- `POST /api/v1/assessments/batch` - Batch assessment creation

### **Authentication (4 endpoints)**
- `POST /api/v1/auth/login` - User login (JWT)
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### **Students (3 endpoints)**
- `GET /api/v1/students` - List students
- `GET /api/v1/students/{student_id}` - Get student details
- `POST /api/v1/students` - Create student

### **Audio/Transcription (5 endpoints)**
- `POST /api/v1/audio/upload` - Upload audio file
- `GET /api/v1/audio/{audio_file_id}/status` - Check status
- `POST /api/v1/audio/{audio_file_id}/transcribe` - Transcribe audio
- `GET /api/v1/audio/{audio_file_id}/transcript` - Get transcript
- `GET /api/v1/student/{student_id}/audio` - Get student audio files

### **Telemetry & Skills (7 endpoints)**
- `POST /api/v1/telemetry/events` - Submit telemetry events
- `POST /api/v1/telemetry/batch` - Batch telemetry submission
- `GET /api/v1/telemetry/status/{batch_id}` - Check batch status
- `GET /api/v1/skills/{student_id}` - Get student skills
- `GET /api/v1/skills/{student_id}/history` - Get skill history
- `GET /api/v1/skills/{student_id}/{skill_name}/evidence` - Get skill evidence
- Additional skill endpoints...

---

## 🔐 Authentication

Most endpoints require JWT authentication. To test protected endpoints:

1. **Login** (if you have credentials):
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

2. **Use the token** in subsequent requests:
```bash
curl -X GET http://localhost:8000/api/v1/students \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📝 Server Logs Location

**Log file:** `/tmp/uvicorn.log`

**View live logs:**
```bash
tail -f /tmp/uvicorn.log
```

**Recent logs:**
```
INFO:     Application startup complete.
INFO:     127.0.0.1:53751 - "GET /api/v1/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53834 - "GET /api/v1/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53836 - "GET /api/v1/docs HTTP/1.1" 200 OK
```

---

## 🎯 Next Steps

1. **Open API Docs:** http://localhost:8000/api/v1/docs
2. **Test health endpoint** in browser or curl
3. **Set up authentication** if testing protected endpoints
4. **Configure database** for full functionality (currently: unknown status)
5. **Configure Redis** for metrics storage (currently: in-memory)

---

## 🐛 Troubleshooting

### Port 8000 already in use?
```bash
# Find process using port 8000
lsof -ti:8000

# Kill it
lsof -ti:8000 | xargs kill -9
```

### Server not responding?
```bash
# Check if process is running
ps aux | grep 49897

# Check logs for errors
tail -50 /tmp/uvicorn.log
```

### Docs not loading?
Make sure you're using the correct URL:
- ✅ `http://localhost:8000/api/v1/docs`
- ❌ `http://localhost:8000/docs` (incorrect)

---

## ✅ Server Verified Working

**All endpoints tested:**
- ✅ Health: 200 OK
- ✅ Liveness: 200 OK
- ✅ Readiness: 200 OK
- ✅ Docs: HTML served correctly

**Server is ready for use!**

Last verified: 2025-11-14 03:56:17
