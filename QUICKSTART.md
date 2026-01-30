# 🚀 Quick Start Guide

## Installation & Setup (2 minutes)

```bash
# 1. Navigate to project
cd c:\Users\91866\Desktop\Medoc\AuraToken

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the server
python start.py
```

**Server will run at**: http://localhost:8000

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Run Simulation

```bash
# In a new terminal (keep server running)
python simulation.py --run
```

## Quick Test

### 1. Create a Doctor
```bash
curl -X POST http://localhost:8000/api/v1/doctors \
  -H "Content-Type: application/json" \
  -d '{"name": "Dr. John", "specialization": "General"}'
```

### 2. Create a Time Slot
```bash
curl -X POST http://localhost:8000/api/v1/slots \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "date": "2026-01-30",
    "start_time": "09:00",
    "end_time": "10:00",
    "max_capacity": 20
  }'
```

### 3. Allocate a Token
```bash
curl -X POST http://localhost:8000/api/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Doe",
    "patient_phone": "+1234567890",
    "doctor_id": 1,
    "slot_id": 1,
    "source": "online"
  }'
```

### 4. View System Status
```bash
curl http://localhost:8000/api/v1/analytics/system/status
```

## Project Structure

```
AuraToken/
├── app/
│   ├── main.py              # FastAPI app
│   ├── api.py               # API endpoints
│   ├── allocation_engine.py # Core algorithm
│   ├── models.py            # Database models
│   ├── schemas.py           # API schemas
│   ├── database.py          # DB config
│   └── config.py            # Settings
├── simulation.py            # Demo simulation
├── start.py                 # Quick start script
├── requirements.txt         # Dependencies
├── README.md                # Full documentation
├── API_TESTING.md          # API examples
└── DEPLOYMENT.md           # Deploy guide
```

## Key Features

✅ **Multi-source token allocation** (online, walk-in, priority, follow-up)  
✅ **Priority-based queueing** with intelligent scoring  
✅ **Dynamic capacity management** with hard limits  
✅ **Emergency insertions** with overflow handling  
✅ **Cancellation & no-show** management  
✅ **Dynamic reallocation** for delays  
✅ **Comprehensive analytics** and reporting  

## Token Sources (Priority Order)

1. **Priority** (Paid/VIP) - Weight: 10
2. **Follow-up** - Weight: 5
3. **Online** - Weight: 3
4. **Walk-in** - Weight: 1

## Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/doctors` | Create doctor |
| POST | `/api/v1/slots` | Create time slot |
| POST | `/api/v1/tokens` | Allocate token |
| GET | `/api/v1/tokens` | List tokens |
| POST | `/api/v1/tokens/{id}/cancel` | Cancel token |
| POST | `/api/v1/tokens/{id}/reallocate` | Reallocate token |
| GET | `/api/v1/slots/{id}/queue` | Get queue |
| GET | `/api/v1/analytics/system/status` | System stats |

## Deployment (Free Options)

### Railway (Recommended)
```bash
# Push to GitHub, then:
1. Go to railway.app
2. New Project → Deploy from GitHub
3. Select repository
4. Done!
```

### Render
```bash
1. Go to render.com
2. New Web Service
3. Connect GitHub repo
4. Build: pip install -r requirements.txt
5. Start: python -m app.main
```

### Fly.io
```bash
fly launch
fly deploy
```

## Environment Variables

```env
DATABASE_URL=sqlite+aiosqlite:///./opd_tokens.db
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
```

## Common Tasks

### View all doctors
```bash
curl http://localhost:8000/api/v1/doctors
```

### View today's slots
```bash
curl "http://localhost:8000/api/v1/slots?date=2026-01-30"
```

### Get slot queue (priority order)
```bash
curl http://localhost:8000/api/v1/slots/1/queue
```

### Cancel token
```bash
curl -X POST "http://localhost:8000/api/v1/tokens/1/cancel?reason=Patient%20request"
```

### Emergency insertion
```bash
curl -X POST "http://localhost:8000/api/v1/tokens?emergency=true" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Emergency",
    "patient_phone": "+1-EMERGENCY",
    "doctor_id": 1,
    "slot_id": 1,
    "source": "priority"
  }'
```

## Troubleshooting

### Port already in use
```bash
# Find and kill process on port 8000
netstat -ano | findstr :8000  # Windows
lsof -ti:8000 | xargs kill    # Mac/Linux
```

### Database locked
```bash
# Delete database and restart
rm opd_tokens.db
python -m app.main
```

### Module not found
```bash
# Ensure virtual environment is activated
venv\Scripts\activate
pip install -r requirements.txt
```

## Need Help?

- 📖 Full docs: `README.md`
- 🧪 API examples: `API_TESTING.md`
- 🚀 Deploy guide: `DEPLOYMENT.md`
- 🌐 Interactive docs: http://localhost:8000/docs

## Next Steps

1. ✅ Start server: `python start.py`
2. ✅ Visit docs: http://localhost:8000/docs
3. ✅ Run simulation: `python simulation.py --run`
4. ✅ Deploy: See `DEPLOYMENT.md`

---

**Happy coding! 🏥**
