# API Testing Guide

This guide provides example API calls for testing the OPD Token Allocation Engine.

## Setup

Start the API server:
```bash
python start.py
```

The API will be available at: `http://localhost:8000`

## Using the Interactive Documentation

**Swagger UI**: http://localhost:8000/docs
- Interactive API testing
- Try out endpoints directly in browser
- See request/response schemas

**ReDoc**: http://localhost:8000/redoc
- Beautiful API documentation
- Detailed schema information

## Example API Calls (using curl)

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "environment": "development"
}
```

### 2. Create Doctors

```bash
# Create Doctor 1
curl -X POST http://localhost:8000/api/v1/doctors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Sarah Johnson",
    "specialization": "General Medicine"
  }'

# Create Doctor 2
curl -X POST http://localhost:8000/api/v1/doctors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Rajesh Kumar",
    "specialization": "Cardiology"
  }'

# Create Doctor 3
curl -X POST http://localhost:8000/api/v1/doctors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Emily Chen",
    "specialization": "Pediatrics"
  }'
```

### 3. List Doctors

```bash
curl http://localhost:8000/api/v1/doctors
```

### 4. Create Time Slots

```bash
# Morning slot 9-10 AM for Doctor 1
curl -X POST http://localhost:8000/api/v1/slots \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "date": "2026-01-30",
    "start_time": "09:00",
    "end_time": "10:00",
    "max_capacity": 20
  }'

# Slot 10-11 AM for Doctor 1
curl -X POST http://localhost:8000/api/v1/slots \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "date": "2026-01-30",
    "start_time": "10:00",
    "end_time": "11:00",
    "max_capacity": 20
  }'
```

### 5. List Slots

```bash
# All slots
curl http://localhost:8000/api/v1/slots

# Slots for specific doctor
curl "http://localhost:8000/api/v1/slots?doctor_id=1"

# Slots for specific date
curl "http://localhost:8000/api/v1/slots?date=2026-01-30"

# Slots for doctor on specific date
curl "http://localhost:8000/api/v1/slots?doctor_id=1&date=2026-01-30"
```

### 6. Allocate Tokens

```bash
# Online booking
curl -X POST http://localhost:8000/api/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Doe",
    "patient_phone": "+1234567890",
    "doctor_id": 1,
    "slot_id": 1,
    "source": "online",
    "notes": "First consultation"
  }'

# Walk-in patient
curl -X POST http://localhost:8000/api/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Jane Smith",
    "patient_phone": "+1234567891",
    "doctor_id": 1,
    "slot_id": 1,
    "source": "walk_in"
  }'

# Priority patient
curl -X POST http://localhost:8000/api/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "VIP Patient",
    "patient_phone": "+1234567892",
    "doctor_id": 1,
    "slot_id": 1,
    "source": "priority",
    "notes": "Priority consultation"
  }'

# Follow-up patient
curl -X POST http://localhost:8000/api/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Follow-up Patient",
    "patient_phone": "+1234567893",
    "doctor_id": 1,
    "slot_id": 1,
    "source": "follow_up"
  }'
```

### 7. Emergency Insertion

```bash
curl -X POST "http://localhost:8000/api/v1/tokens?emergency=true" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Emergency Case",
    "patient_phone": "+1-EMERGENCY",
    "doctor_id": 1,
    "slot_id": 1,
    "source": "priority",
    "notes": "Chest pain - URGENT"
  }'
```

### 8. Get Token Details

```bash
# By ID
curl http://localhost:8000/api/v1/tokens/1

# By token number
curl http://localhost:8000/api/v1/tokens/number/DOC1-20260130-0001
```

### 9. List Tokens

```bash
# All tokens
curl http://localhost:8000/api/v1/tokens

# Tokens for specific doctor
curl "http://localhost:8000/api/v1/tokens?doctor_id=1"

# Tokens for specific slot
curl "http://localhost:8000/api/v1/tokens?slot_id=1"

# Tokens by status
curl "http://localhost:8000/api/v1/tokens?status_filter=allocated"
```

### 10. Update Token Status

```bash
# Check-in patient
curl -X PATCH http://localhost:8000/api/v1/tokens/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "checked_in"
  }'

# Start consultation
curl -X PATCH http://localhost:8000/api/v1/tokens/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "consulting"
  }'

# Complete consultation
curl -X PATCH http://localhost:8000/api/v1/tokens/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

### 11. Cancel Token

```bash
curl -X POST "http://localhost:8000/api/v1/tokens/2/cancel?reason=Patient%20unable%20to%20attend"
```

### 12. Mark No-Show

```bash
curl -X POST http://localhost:8000/api/v1/tokens/3/no-show
```

### 13. Reallocate Token

```bash
curl -X POST http://localhost:8000/api/v1/tokens/4/reallocate \
  -H "Content-Type: application/json" \
  -d '{
    "new_slot_id": 2,
    "reason": "Doctor running behind schedule"
  }'
```

### 14. Get Slot Queue

```bash
# View priority-ordered queue for a slot
curl http://localhost:8000/api/v1/slots/1/queue
```

### 15. Analytics - Slot

```bash
curl http://localhost:8000/api/v1/analytics/slots/1
```

Response:
```json
{
  "slot_id": 1,
  "date": "2026-01-30",
  "start_time": "09:00",
  "end_time": "10:00",
  "doctor_name": "Dr. Sarah Johnson",
  "total_capacity": 20,
  "allocated_tokens": 15,
  "available_capacity": 5,
  "utilization_percentage": 75.0,
  "tokens_by_source": {
    "online": 8,
    "walk_in": 4,
    "priority": 2,
    "follow_up": 1
  }
}
```

### 16. Analytics - Doctor Day

```bash
curl http://localhost:8000/api/v1/analytics/doctors/1/day/2026-01-30
```

### 17. Analytics - System Status

```bash
curl http://localhost:8000/api/v1/analytics/system/status
```

## Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create doctor
response = requests.post(
    f"{BASE_URL}/doctors",
    json={
        "name": "Dr. Test",
        "specialization": "Testing"
    }
)
doctor = response.json()
print(f"Created doctor: {doctor['id']}")

# Create slot
response = requests.post(
    f"{BASE_URL}/slots",
    json={
        "doctor_id": doctor["id"],
        "date": "2026-01-30",
        "start_time": "09:00",
        "end_time": "10:00",
        "max_capacity": 20
    }
)
slot = response.json()

# Allocate token
response = requests.post(
    f"{BASE_URL}/tokens",
    json={
        "patient_name": "Test Patient",
        "patient_phone": "+1234567890",
        "doctor_id": doctor["id"],
        "slot_id": slot["id"],
        "source": "online"
    }
)
token = response.json()
print(f"Token allocated: {token['token_number']}")
```

## Using httpie (if installed)

```bash
# Install httpie
pip install httpie

# Create doctor
http POST localhost:8000/api/v1/doctors \
  name="Dr. Test" \
  specialization="Testing"

# Allocate token
http POST localhost:8000/api/v1/tokens \
  patient_name="John Doe" \
  patient_phone="+1234567890" \
  doctor_id:=1 \
  slot_id:=1 \
  source="online"
```

## Testing Workflow

### Complete workflow example:

```bash
# 1. Create doctors
curl -X POST http://localhost:8000/api/v1/doctors \
  -H "Content-Type: application/json" \
  -d '{"name": "Dr. Test", "specialization": "General"}'

# 2. Create slots
curl -X POST http://localhost:8000/api/v1/slots \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "date": "2026-01-30",
    "start_time": "09:00",
    "end_time": "10:00",
    "max_capacity": 5
  }'

# 3. Allocate tokens (fill slot)
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/tokens \
    -H "Content-Type: application/json" \
    -d "{
      \"patient_name\": \"Patient $i\",
      \"patient_phone\": \"+123456789$i\",
      \"doctor_id\": 1,
      \"slot_id\": 1,
      \"source\": \"online\"
    }"
done

# 4. Try to allocate when full (should fail)
curl -X POST http://localhost:8000/api/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Extra Patient",
    "patient_phone": "+1234567890",
    "doctor_id": 1,
    "slot_id": 1,
    "source": "online"
  }'

# 5. Cancel one token
curl -X POST "http://localhost:8000/api/v1/tokens/1/cancel?reason=Test"

# 6. Now allocation should work
curl -X POST http://localhost:8000/api/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "New Patient",
    "patient_phone": "+1234567890",
    "doctor_id": 1,
    "slot_id": 1,
    "source": "online"
  }'

# 7. View queue
curl http://localhost:8000/api/v1/slots/1/queue

# 8. Get analytics
curl http://localhost:8000/api/v1/analytics/slots/1
```

## Error Responses

### Slot Full
```json
{
  "detail": "Slot 1 is at maximum capacity"
}
```

### Invalid Data
```json
{
  "detail": [
    {
      "loc": ["body", "patient_phone"],
      "msg": "string does not match regex",
      "type": "value_error.str.regex"
    }
  ]
}
```

### Not Found
```json
{
  "detail": "Token not found"
}
```

## Tips

1. Use the Swagger UI at `/docs` for interactive testing
2. Token numbers follow format: `DOC{doctor_id}-{date}-{sequence}`
3. Priority order: priority > follow_up > online > walk_in
4. Emergency flag allows exceeding capacity
5. Reallocation maintains priority ordering
6. Analytics update in real-time
