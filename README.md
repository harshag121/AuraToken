# OPD Token Allocation Engine

A sophisticated, production-ready token allocation system for hospital OPD (Outpatient Department) that supports elastic capacity management, dynamic reallocation, and intelligent prioritization.

## 🎯 Project Overview

This system manages patient token allocation across multiple doctors and time slots, handling real-world complexities like:
- Multiple token sources (online booking, walk-in, priority patients, follow-ups)
- Dynamic capacity management with hard limits
- Emergency insertions and priority handling
- Cancellations, no-shows, and reallocations
- Queue management with intelligent prioritization

## 🏗️ Architecture

### Technology Stack
- **Backend Framework**: FastAPI (Python 3.8+)
- **Database**: SQLite (async with SQLAlchemy)
- **API Documentation**: OpenAPI/Swagger
- **Deployment**: Railway/Render (free tier compatible)

### Core Components

1. **Token Allocation Engine** (`app/allocation_engine.py`)
   - Priority-based allocation algorithm
   - Capacity enforcement
   - Dynamic reallocation logic
   - Emergency handling

2. **API Layer** (`app/api.py`)
   - RESTful endpoints
   - Request validation
   - Analytics endpoints

3. **Data Models** (`app/models.py`)
   - Doctor, TimeSlot, Token entities
   - Status and source enumerations

## 📋 API Design

### Base URL
```
http://localhost:8000/api/v1
```

### Core Endpoints

#### Doctor Management
```
POST   /doctors              Create new doctor
GET    /doctors              List all doctors
GET    /doctors/{id}         Get doctor details
```

#### Time Slot Management
```
POST   /slots                Create time slot
GET    /slots                List slots (filter by doctor/date)
GET    /slots/{id}           Get slot details
```

#### Token Operations
```
POST   /tokens               Allocate new token
GET    /tokens               List tokens (with filters)
GET    /tokens/{id}          Get token details
GET    /tokens/number/{num}  Get token by number

PATCH  /tokens/{id}/status   Update token status
POST   /tokens/{id}/cancel   Cancel token
POST   /tokens/{id}/reallocate  Reallocate to different slot
POST   /tokens/{id}/no-show  Mark as no-show

GET    /slots/{id}/queue     Get priority-ordered queue
```

#### Analytics
```
GET    /analytics/slots/{id}              Slot analytics
GET    /analytics/doctors/{id}/day/{date} Doctor daily analytics
GET    /analytics/system/status           System-wide status
```

### Request/Response Examples

#### Allocate Token
```bash
POST /api/v1/tokens
Content-Type: application/json

{
  "patient_name": "John Doe",
  "patient_phone": "+1234567890",
  "doctor_id": 1,
  "slot_id": 5,
  "source": "online",
  "notes": "First visit"
}
```

Response:
```json
{
  "id": 42,
  "token_number": "DOC1-20260130-0042",
  "patient_name": "John Doe",
  "patient_phone": "+1234567890",
  "doctor_id": 1,
  "slot_id": 5,
  "source": "online",
  "status": "allocated",
  "priority_score": 30,
  "sequence_number": 12,
  "allocated_at": "2026-01-30T10:30:00",
  "checked_in_at": null,
  "consultation_started_at": null,
  "completed_at": null,
  "notes": "First visit"
}
```

## 🧮 Token Allocation Algorithm

### Prioritization Logic

The system uses a multi-factor priority scoring system:

```python
Priority Score = (Source Weight × 10) + Timing Bonus

Source Weights:
- Priority Patients (Paid/VIP): 10
- Follow-up Patients: 5
- Online Booking: 3
- Walk-in: 1

Timing Bonus: max(0, 10 - current_slot_count)
```

### Queue Ordering

Tokens are ordered by:
1. **Priority Score** (descending) - Higher priority first
2. **Sequence Number** (ascending) - Earlier arrivals first
3. **Allocation Time** (ascending) - Timestamp as tiebreaker

### Capacity Enforcement

**Hard Limits**: Each slot has a `max_capacity` that cannot be exceeded except for emergency insertions with `force=true` flag.

**Flow**:
1. Check if slot has available capacity
2. If full, suggest alternative slot
3. If emergency with force flag, allow exceeding by 1
4. Otherwise, reject allocation

### Dynamic Reallocation

When conditions change (doctor delays, cancellations):

```python
async def reallocate_token(token_id, new_slot_id, reason):
    1. Validate token and new slot
    2. Verify same doctor
    3. Check new slot capacity
    4. Update capacities (decrement old, increment new)
    5. Recalculate sequence number
    6. Resequence both affected slots
```

### Emergency Insertion Strategy

```python
async def handle_emergency_insertion(request, force=False):
    if slot_full and not force:
        # Try to reallocate lowest priority walk-in
        success = reallocate_lowest_priority(slot_id)
        if not success and not force:
            raise CapacityError
    
    # Insert with maximum priority
    token = allocate_token(request)
    token.source = PRIORITY
    token.notes += "EMERGENCY INSERTION"
```

## 🔄 Edge Cases & Handling

### 1. Slot Overflow
**Scenario**: More requests than capacity  
**Handling**: 
- Reject with error message
- Suggest alternative slot
- Allow emergency override with `force=true`

### 2. Cancellations
**Scenario**: Patient cancels appointment  
**Handling**:
- Update token status to CANCELLED
- Decrement slot capacity
- Resequence remaining tokens
- Free up slot for new allocations

### 3. No-Shows
**Scenario**: Patient doesn't arrive  
**Handling**:
- Mark token as NO_SHOW
- Free up capacity
- Track for analytics

### 4. Doctor Delays
**Scenario**: Doctor running behind schedule  
**Handling**:
- Reallocate waiting patients to next slot
- Maintain priority ordering
- Update all affected sequences

### 5. Multiple Emergency Insertions
**Scenario**: Several emergencies in short time  
**Handling**:
- Allow override with force flag
- Reallocate lower priority patients
- Track overflow for capacity planning

### 6. Concurrent Allocation Requests
**Scenario**: Race condition on last slot  
**Handling**:
- Database transaction isolation
- Optimistic locking
- Atomic capacity updates

## ⚠️ Failure Handling

### Database Failures
```python
try:
    await db.commit()
except Exception:
    await db.rollback()
    raise HTTPException(500, "Database error")
```

### Validation Failures
```python
if not slot.is_active:
    raise ValueError("Slot is inactive")

if slot.is_full:
    raise ValueError("Slot at maximum capacity")
```

### Network Failures
- Retry logic with exponential backoff
- Circuit breaker pattern for external services
- Graceful degradation

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
cd c:\Users\91866\Desktop\Medoc\AuraToken
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment**
```bash
cp .env.example .env
# Edit .env if needed
```

5. **Run the application**
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Running the Simulation

The project includes a comprehensive simulation of a full OPD day with 3 doctors.

```bash
# Make sure the API is running first
python -m app.main

# In another terminal, run simulation
python simulation.py --run
```

The simulation demonstrates:
- ✅ 3 doctors with different specializations
- ✅ 8 time slots per doctor (9 AM - 5 PM)
- ✅ 300+ token allocations from all sources
- ✅ Realistic cancellation rates (10%)
- ✅ No-show simulation (5%)
- ✅ Emergency insertions
- ✅ Dynamic reallocation
- ✅ Comprehensive analytics

## 📊 Sample Output

```
=== OPD DAY SIMULATION ANALYTICS ===

📊 SYSTEM OVERVIEW
  Total Doctors: 3
  Active Doctors: 3
  Total Slots Today: 24
  Total Tokens Today: 320

  Tokens by Status:
    - allocated: 245
    - cancelled: 32
    - no_show: 16
    - completed: 27

  Tokens by Source:
    - online: 128
    - walk_in: 96
    - priority: 48
    - follow_up: 48

📋 DOCTOR-WISE PERFORMANCE

🏥 Dr. Sarah Johnson
  Total Slots: 8
  Total Capacity: 135
  Allocated Tokens: 108
  Utilization: 80.0%

🏥 Dr. Rajesh Kumar
  Total Slots: 8
  Total Capacity: 135
  Allocated Tokens: 105
  Utilization: 77.8%
```

## 🌐 Deployment

### Free Deployment Options

#### Option 1: Railway

1. **Create account**: https://railway.app
2. **Install Railway CLI**
```bash
npm i -g @railway/cli
railway login
```

3. **Deploy**
```bash
railway init
railway up
```

#### Option 2: Render

1. **Create account**: https://render.com
2. **Connect GitHub repository**
3. **Create Web Service**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m app.main`

#### Option 3: Fly.io

1. **Install flyctl**: https://fly.io/docs/hands-on/install-flyctl/
2. **Deploy**
```bash
fly launch
fly deploy
```

### Environment Variables for Production

```env
DATABASE_URL=postgresql://... (use managed DB)
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
```

## 📁 Project Structure

```
AuraToken/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database setup
│   ├── models.py                # SQLAlchemy models
│   ├── schemas.py               # Pydantic schemas
│   ├── api.py                   # API endpoints
│   └── allocation_engine.py     # Core allocation logic
├── simulation.py                # OPD day simulation
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
├── .gitignore
└── README.md                    # This file
```

## 🔐 Security Considerations

- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration for production
- Rate limiting (add for production)
- Authentication/Authorization (add JWT for production)

## 🎓 Design Trade-offs

### 1. SQLite vs PostgreSQL
**Choice**: SQLite for development, PostgreSQL for production  
**Rationale**: Easy setup, async support, free hosting options

### 2. Synchronous vs Asynchronous
**Choice**: Async with SQLAlchemy + asyncio  
**Rationale**: Better scalability, non-blocking I/O

### 3. Hard Capacity Limits
**Choice**: Enforce strict limits with emergency override  
**Rationale**: Prevents overcrowding while allowing critical cases

### 4. Priority Scoring vs FIFO
**Choice**: Multi-factor priority scoring  
**Rationale**: Fair queue management respecting medical priorities

### 5. Resequencing After Changes
**Choice**: Auto-resequence on cancellation/reallocation  
**Rationale**: Maintains accurate queue order

## 🧩 Extension Ideas

- **SMS Notifications**: Notify patients of token allocation
- **Real-time Dashboard**: WebSocket-based live updates
- **Queue Display**: Digital display board integration
- **Multi-language Support**: i18n for patient-facing features
- **Payment Integration**: For priority token purchases
- **Reports**: PDF generation for daily/weekly analytics

## 📞 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review this README
3. Check the simulation for usage examples

## 📄 License

This project is created for the OPD Token Allocation Engine assignment.

---

**Built with ❤️ using FastAPI**
