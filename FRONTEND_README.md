# 🎨 OPD Token System - Streamlit Frontend

Beautiful, feature-rich frontend for the OPD Token Allocation System!

## ✨ Features

- 📊 **Interactive Dashboard** - Real-time system overview with charts
- 🎫 **Token Allocation** - Easy patient registration and token generation
- 📋 **Queue Management** - View and manage patient queues
- 👨‍⚕️ **Doctor Management** - Add and view doctors
- 📅 **Slot Management** - Create and manage time slots
- 📈 **Analytics** - Comprehensive insights and reports
- ⚙️ **System Status** - Health monitoring and stats

## 🚀 Quick Start

### 1. Install Frontend Dependencies

```bash
pip install -r requirements-frontend.txt
```

### 2. Make Sure API is Running

First terminal:
```bash
python start.py
```

### 3. Start Frontend

Second terminal:
```bash
streamlit run frontend.py
```

The frontend will open automatically in your browser at `http://localhost:8501`

## 📸 Screenshots

### Dashboard
- Real-time metrics (doctors, slots, tokens)
- Status distribution charts
- Recent token list
- Completion rates

### Token Allocation
- Patient information form
- Doctor and slot selection
- Priority source selection
- Emergency override option
- Instant token generation

### Queue Management
- Filter by doctor
- View all queues
- Priority-ordered display
- Slot utilization stats

### Analytics
- System overview
- Doctor performance
- Utilization charts
- Status breakdowns

## 🎨 UI Features

- **Responsive Design** - Works on desktop and tablet
- **Color-Coded Priority** - Visual priority indicators
- **Status Emojis** - Easy status identification
- **Real-time Updates** - Auto-refresh capability
- **Interactive Charts** - Plotly visualizations
- **Clean Interface** - Modern, professional look

## 📋 Navigation Menu

1. **Dashboard** 🏠 - System overview
2. **Token Allocation** 🎫 - Create new tokens
3. **Queue Management** 📋 - View queues
4. **Doctor Management** 👨‍⚕️ - Manage doctors
5. **Slot Management** 📅 - Manage slots
6. **Analytics** 📊 - Reports and insights
7. **System Status** ⚙️ - Health check

## 🎯 Quick Actions

### Allocate a Token
1. Go to "Token Allocation"
2. Enter patient details
3. Select doctor and time slot
4. Choose token source (priority/online/walk-in/follow-up)
5. Click "Allocate Token"

### View Queue
1. Go to "Queue Management"
2. Select doctor (or view all)
3. Expand time slot to see queue
4. View patients in priority order

### Create Doctor
1. Go to "Doctor Management"
2. Click "Add Doctor" tab
3. Enter name and specialization
4. Submit

### Create Slot
1. Go to "Slot Management"
2. Click "Create Slot" tab
3. Select doctor, date, time, capacity
4. Submit

## 🔧 Configuration

The frontend connects to the API at:
```
http://localhost:8000/api/v1
```

If your API is running on a different port, edit `frontend.py`:
```python
API_BASE_URL = "http://localhost:YOUR_PORT/api/v1"
```

## 🎨 Color Scheme

### Priority Colors
- 🔴 **Red** - Priority/VIP (Highest)
- 🟡 **Yellow** - Follow-up (High)
- 🔵 **Blue** - Online (Medium)
- ⚪ **White** - Walk-in (Standard)

### Status Colors
- 🟢 **Green** - Allocated
- 🔵 **Blue** - Checked-in
- 🟡 **Yellow** - Consulting
- ✅ **Green** - Completed
- ❌ **Red** - Cancelled
- ⚫ **Black** - No-show

## 📊 Dashboard Metrics

### Top Row
- Active Doctors
- Slots Today
- Tokens Today
- Completion Rate

### Charts
- Token Status (Pie Chart)
- Token Source (Bar Chart)

### Recent Tokens
- Last 10 tokens allocated
- Quick status view

## 🚀 Running Both Servers

Use two terminal windows:

**Terminal 1 - API Server:**
```bash
cd c:\Users\91866\Desktop\Medoc\AuraToken
python start.py
```

**Terminal 2 - Frontend:**
```bash
cd c:\Users\91866\Desktop\Medoc\AuraToken
streamlit run frontend.py
```

Then visit:
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 💡 Tips

- Use the sidebar for quick stats
- Click on expandable sections for details
- Charts are interactive (hover for info)
- Forms validate input automatically
- Emergency checkbox for urgent cases
- Refresh page to update data

## 🔄 Auto-Refresh

The frontend automatically refreshes when:
- Forms are submitted
- Actions are completed
- Navigation changes

## 📱 Mobile Support

The interface is responsive and works on:
- Desktop (full features)
- Tablet (optimized layout)
- Mobile (basic functionality)

## 🎓 Demo Workflow

1. **Start Servers**
   ```bash
   python start.py           # Terminal 1
   streamlit run frontend.py # Terminal 2
   ```

2. **Add Doctor**
   - Dashboard → Doctor Management → Add Doctor
   - Name: "Dr. Sarah Johnson"
   - Specialization: "Cardiology"

3. **Create Slot**
   - Slot Management → Create Slot
   - Select doctor, today's date
   - Time: 09:00 - 10:00
   - Capacity: 20

4. **Allocate Token**
   - Token Allocation
   - Patient: "John Doe"
   - Phone: "+1234567890"
   - Source: Online
   - Submit

5. **View Queue**
   - Queue Management
   - See patient in queue with priority

6. **Check Analytics**
   - Analytics → View charts and stats

## 🆘 Troubleshooting

### Frontend won't start
```bash
pip install -r requirements-frontend.txt --upgrade
streamlit run frontend.py
```

### Can't connect to API
- Make sure API server is running
- Check http://localhost:8000/health
- Verify API_BASE_URL in frontend.py

### Charts not showing
```bash
pip install plotly --upgrade
```

### Slow performance
- Close unused browser tabs
- Clear browser cache
- Restart both servers

## 📦 Dependencies

- streamlit - Web framework
- requests - API calls
- pandas - Data handling
- plotly - Interactive charts
- streamlit-option-menu - Navigation
- streamlit-lottie - Animations

## 🎉 Enjoy!

You now have a beautiful, fully-functional frontend for your OPD Token Allocation System!

**Next Steps:**
- Explore all features
- Try different workflows
- Check the analytics
- Deploy to production

---

**Built with ❤️ using Streamlit**
