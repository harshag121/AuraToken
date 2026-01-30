"""
OPD Token Allocation System - Streamlit Frontend
A beautiful, feature-rich dashboard for hospital OPD management
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from streamlit_option_menu import option_menu
import time

# Page configuration
st.set_page_config(
    page_title="OPD Token Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    h1 {
        color: #1f77b4;
    }
    h2 {
        color: #2c3e50;
    }
    .priority-high {
        color: #dc3545;
        font-weight: bold;
    }
    .priority-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .priority-low {
        color: #28a745;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper Functions
def get_status_emoji(status):
    """Get emoji for token status"""
    emoji_map = {
        "allocated": "🟢",
        "checked_in": "🔵",
        "consulting": "🟡",
        "completed": "✅",
        "cancelled": "❌",
        "no_show": "⚫"
    }
    return emoji_map.get(status, "⚪")

def get_source_emoji(source):
    """Get emoji for token source"""
    emoji_map = {
        "priority": "🔴",
        "follow_up": "🟡",
        "online": "🔵",
        "walk_in": "⚪"
    }
    return emoji_map.get(source, "⚪")

def get_priority_class(score):
    """Get CSS class for priority score"""
    if score >= 80:
        return "priority-high"
    elif score >= 40:
        return "priority-medium"
    else:
        return "priority-low"

# API Helper Functions
def api_get(endpoint):
    """Make GET request to API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.status_code}"
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def api_post(endpoint, data):
    """Make POST request to API"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=5)
        if response.status_code in [200, 201]:
            return response.json(), None
        else:
            return None, f"Error: {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def api_patch(endpoint, data):
    """Make PATCH request to API"""
    try:
        response = requests.patch(f"{API_BASE_URL}{endpoint}", json=data, timeout=5)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return None, f"Connection error: {str(e)}"

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/hospital-3.png", width=100)
    st.title("OPD Management")
    
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Token Allocation", "Queue Management", "Doctor Management", 
                 "Slot Management", "Analytics", "System Status"],
        icons=["speedometer2", "ticket-perforated", "list-task", "person-badge", 
               "calendar-week", "graph-up", "gear"],
        menu_icon="cast",
        default_index=0,
    )
    
    st.divider()
    
    # Quick Stats in Sidebar
    st.subheader("Quick Stats")
    data, error = api_get("/analytics/system/status")
    if data:
        st.metric("Active Doctors", data.get("active_doctors", 0))
        st.metric("Slots Today", data.get("total_slots_today", 0))
        st.metric("Tokens Today", data.get("total_tokens_today", 0))

# Main Content Area
if selected == "Dashboard":
    st.title("🏥 OPD Token Allocation Dashboard")
    st.markdown("### Welcome to the Hospital OPD Management System")
    
    # Fetch system status
    data, error = api_get("/analytics/system/status")
    
    if error:
        st.error(f"❌ Unable to connect to API server. Make sure it's running on http://localhost:8000")
        st.info("Start the server with: `python start.py`")
    else:
        # Top Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👨‍⚕️ Active Doctors",
                value=data.get("active_doctors", 0) if data else 0,
                delta=f"{data.get('total_doctors', 0) if data else 0} total"
            )
        
        with col2:
            st.metric(
                label="📅 Slots Today",
                value=data.get("total_slots_today", 0) if data else 0
            )
        
        with col3:
            st.metric(
                label="🎫 Tokens Today",
                value=data.get("total_tokens_today", 0) if data else 0
            )
        
        with col4:
            completed = data.get("tokens_by_status", {}).get("completed", 0) if data else 0
            total = data.get("total_tokens_today", 1) if data else 1
            completion_rate = (completed / total * 100) if total > 0 else 0
            st.metric(
                label="✅ Completion Rate",
                value=f"{completion_rate:.1f}%"
            )
        
        st.divider()
        
        # Charts Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Tokens by Status")
            status_data = data.get("tokens_by_status", {}) if data else {}
            if status_data:
                df_status = pd.DataFrame(list(status_data.items()), columns=['Status', 'Count'])
                fig = px.pie(df_status, values='Count', names='Status', 
                           color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No token data available")
        
        with col2:
            st.subheader("📈 Tokens by Source")
            source_data = data.get("tokens_by_source", {}) if data else {}
            if source_data:
                df_source = pd.DataFrame(list(source_data.items()), columns=['Source', 'Count'])
                colors = {'priority': '#dc3545', 'follow_up': '#ffc107', 
                         'online': '#0dcaf0', 'walk_in': '#6c757d'}
                fig = px.bar(df_source, x='Source', y='Count',
                           color='Source', color_discrete_map=colors)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No source data available")
        
        st.divider()
        
        # Recent Tokens
        st.subheader("🎫 Recent Tokens")
        tokens_data, error = api_get("/tokens?limit=10")
        if tokens_data and not error:
            if tokens_data:
                df_tokens = pd.DataFrame(tokens_data[:10])
                display_df = df_tokens[['token_number', 'patient_name', 'source', 'status', 'priority_score']].copy()
                display_df['source'] = display_df['source'].apply(lambda x: f"{get_source_emoji(x)} {x}")
                display_df['status'] = display_df['status'].apply(lambda x: f"{get_status_emoji(x)} {x}")
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No tokens allocated yet")

elif selected == "Token Allocation":
    st.title("🎫 Token Allocation")
    st.markdown("### Allocate new tokens to patients")
    
    # Get doctors and slots
    doctors_data, _ = api_get("/doctors?active_only=true")
    
    if doctors_data:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Patient Information")
            
            with st.form("token_allocation_form"):
                patient_name = st.text_input("Patient Name*", placeholder="John Doe")
                patient_phone = st.text_input("Phone Number*", placeholder="+1234567890")
                
                # Doctor selection
                doctor_options = {f"Dr. {d['name']} ({d['specialization']})": d['id'] 
                                for d in doctors_data}
                selected_doctor = st.selectbox("Select Doctor*", options=list(doctor_options.keys()))
                doctor_id = doctor_options[selected_doctor]
                
                # Get slots for selected doctor
                today = date.today().strftime("%Y-%m-%d")
                slots_data, _ = api_get(f"/slots?doctor_id={doctor_id}&date={today}")
                
                if slots_data:
                    slot_options = {
                        f"{s['start_time']}-{s['end_time']} (Available: {s['available_capacity']}/{s['max_capacity']})": s['id']
                        for s in slots_data if s['is_active']
                    }
                    
                    if slot_options:
                        selected_slot = st.selectbox("Select Time Slot*", options=list(slot_options.keys()))
                        slot_id = slot_options[selected_slot]
                    else:
                        st.warning("No active slots available for this doctor today")
                        slot_id = None
                else:
                    st.warning("No slots found. Please create slots first.")
                    slot_id = None
                
                # Token source
                source = st.selectbox(
                    "Token Source*",
                    options=["online", "walk_in", "priority", "follow_up"],
                    format_func=lambda x: {
                        "online": "🔵 Online Booking",
                        "walk_in": "⚪ Walk-in",
                        "priority": "🔴 Priority/VIP",
                        "follow_up": "🟡 Follow-up"
                    }[x]
                )
                
                notes = st.text_area("Notes (Optional)", placeholder="Any special instructions...")
                
                emergency = st.checkbox("🚨 Emergency Case (Override capacity limit)")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submit = st.form_submit_button("🎫 Allocate Token", type="primary")
                with col_btn2:
                    clear = st.form_submit_button("Clear Form")
                
                if submit:
                    if not patient_name or not patient_phone or not slot_id:
                        st.error("Please fill all required fields")
                    else:
                        # Prepare data
                        token_data = {
                            "patient_name": patient_name,
                            "patient_phone": patient_phone,
                            "doctor_id": doctor_id,
                            "slot_id": slot_id,
                            "source": source,
                            "notes": notes
                        }
                        
                        # Make API call
                        endpoint = f"/tokens?emergency={str(emergency).lower()}"
                        result, error = api_post(endpoint, token_data)
                        
                        if result:
                            st.success(f"✅ Token allocated successfully!")
                            st.markdown(f"""
                            <div class="success-box">
                                <h3>Token Details</h3>
                                <p><strong>Token Number:</strong> {result['token_number']}</p>
                                <p><strong>Patient:</strong> {result['patient_name']}</p>
                                <p><strong>Priority Score:</strong> {result['priority_score']}</p>
                                <p><strong>Sequence Number:</strong> {result['sequence_number']}</p>
                                <p><strong>Status:</strong> {get_status_emoji(result['status'])} {result['status']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"❌ {error}")
        
        with col2:
            st.subheader("ℹ️ Priority System")
            st.markdown("""
            **Token sources are prioritized as:**
            
            🔴 **Priority/VIP** (Weight: 10)
            - Paid patients
            - VIP cases
            - Emergency
            
            🟡 **Follow-up** (Weight: 5)
            - Return visits
            - Post-op checkups
            
            🔵 **Online** (Weight: 3)
            - Web portal
            - Mobile app
            
            ⚪ **Walk-in** (Weight: 1)
            - OPD desk
            - Same-day
            """)
            
            st.divider()
            
            st.subheader("📋 Quick Tips")
            st.info("""
            - Emergency cases can override capacity limits
            - Earlier arrivals get timing bonus
            - Queue is ordered by priority score
            - Check slot availability before allocation
            """)
    else:
        st.warning("No doctors found. Please add doctors first.")

elif selected == "Queue Management":
    st.title("📋 Queue Management")
    st.markdown("### View and manage patient queues")
    
    # Get today's slots
    today = date.today().strftime("%Y-%m-%d")
    slots_data, _ = api_get(f"/slots?date={today}")
    
    if slots_data:
        # Doctor filter
        doctors_data, _ = api_get("/doctors?active_only=true")
        if doctors_data:
            doctor_options = ["All Doctors"] + [f"Dr. {d['name']}" for d in doctors_data]
            selected_doctor_filter = st.selectbox("Filter by Doctor", doctor_options)
            
            st.divider()
            
            # Display queues for each slot
            for slot in slots_data:
                if selected_doctor_filter != "All Doctors":
                    doctor = next((d for d in doctors_data if d['id'] == slot['doctor_id']), None)
                    if doctor and f"Dr. {doctor['name']}" != selected_doctor_filter:
                        continue
                
                # Get doctor info
                doctor_info, _ = api_get(f"/doctors/{slot['doctor_id']}")
                
                with st.expander(
                    f"🕐 {slot['start_time']}-{slot['end_time']} | "
                    f"👨‍⚕️ Dr. {doctor_info['name'] if doctor_info else 'Unknown'} | "
                    f"📊 {slot['current_count']}/{slot['max_capacity']} | "
                    f"{'🔴 FULL' if slot['is_full'] else '🟢 Available'}",
                    expanded=False
                ):
                    # Get queue for this slot
                    queue_data, _ = api_get(f"/slots/{slot['id']}/queue")
                    
                    if queue_data:
                        st.markdown(f"**{len(queue_data)} patients in queue**")
                        
                        # Display queue
                        for idx, token in enumerate(queue_data, 1):
                            col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
                            
                            with col1:
                                st.markdown(f"**#{idx}**")
                            with col2:
                                st.markdown(f"{get_source_emoji(token['source'])} **{token['patient_name']}**")
                            with col3:
                                st.markdown(f"Token: `{token['token_number']}`")
                            with col4:
                                st.markdown(f"{get_status_emoji(token['status'])} {token['status']}")
                            with col5:
                                priority_class = get_priority_class(token['priority_score'])
                                st.markdown(f"<span class='{priority_class}'>Priority: {token['priority_score']}</span>", 
                                          unsafe_allow_html=True)
                    else:
                        st.info("No patients in queue")
                    
                    # Slot analytics
                    analytics, _ = api_get(f"/analytics/slots/{slot['id']}")
                    if analytics:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Utilization", f"{analytics['utilization_percentage']:.1f}%")
                        with col2:
                            st.metric("Allocated", analytics['allocated_tokens'])
                        with col3:
                            st.metric("Available", analytics['available_capacity'])
    else:
        st.info("No slots found for today. Create slots in Slot Management.")

elif selected == "Doctor Management":
    st.title("👨‍⚕️ Doctor Management")
    
    tab1, tab2 = st.tabs(["📋 All Doctors", "➕ Add Doctor"])
    
    with tab1:
        st.subheader("All Doctors")
        doctors_data, error = api_get("/doctors")
        
        if doctors_data:
            for doctor in doctors_data:
                with st.expander(
                    f"Dr. {doctor['name']} - {doctor['specialization']} "
                    f"{'🟢 Active' if doctor['is_active'] else '🔴 Inactive'}"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ID:** {doctor['id']}")
                        st.write(f"**Name:** Dr. {doctor['name']}")
                    with col2:
                        st.write(f"**Specialization:** {doctor['specialization']}")
                        st.write(f"**Status:** {'Active' if doctor['is_active'] else 'Inactive'}")
                    
                    # Get today's analytics
                    today = date.today().strftime("%Y-%m-%d")
                    analytics, _ = api_get(f"/analytics/doctors/{doctor['id']}/day/{today}")
                    
                    if analytics:
                        st.divider()
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Slots Today", analytics['total_slots'])
                        with col2:
                            st.metric("Allocated", analytics['total_allocated'])
                        with col3:
                            st.metric("Completed", analytics['total_completed'])
                        with col4:
                            st.metric("Utilization", f"{analytics['average_utilization']:.1f}%")
        else:
            st.info("No doctors found")
    
    with tab2:
        st.subheader("Add New Doctor")
        
        with st.form("add_doctor_form"):
            name = st.text_input("Doctor Name*", placeholder="Sarah Johnson")
            specialization = st.text_input("Specialization*", placeholder="Cardiology")
            
            submitted = st.form_submit_button("➕ Add Doctor", type="primary")
            
            if submitted:
                if name and specialization:
                    doctor_data = {
                        "name": name,
                        "specialization": specialization
                    }
                    result, error = api_post("/doctors", doctor_data)
                    
                    if result:
                        st.success(f"✅ Dr. {result['name']} added successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
                else:
                    st.error("Please fill all required fields")

elif selected == "Slot Management":
    st.title("📅 Slot Management")
    
    tab1, tab2 = st.tabs(["📋 All Slots", "➕ Create Slot"])
    
    with tab1:
        st.subheader("All Time Slots")
        
        # Date filter
        selected_date = st.date_input("Select Date", value=date.today())
        date_str = selected_date.strftime("%Y-%m-%d")
        
        slots_data, _ = api_get(f"/slots?date={date_str}")
        
        if slots_data:
            # Group by doctor
            doctors_data, _ = api_get("/doctors")
            
            for doctor in (doctors_data or []):
                doctor_slots = [s for s in slots_data if s['doctor_id'] == doctor['id']]
                
                if doctor_slots:
                    st.markdown(f"### 👨‍⚕️ Dr. {doctor['name']} ({doctor['specialization']})")
                    
                    for slot in doctor_slots:
                        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                        
                        with col1:
                            st.write(f"🕐 **{slot['start_time']} - {slot['end_time']}**")
                        with col2:
                            st.write(f"📊 {slot['current_count']}/{slot['max_capacity']}")
                        with col3:
                            utilization = (slot['current_count'] / slot['max_capacity'] * 100) if slot['max_capacity'] > 0 else 0
                            st.write(f"📈 {utilization:.0f}% utilized")
                        with col4:
                            st.write(f"{'🟢 Available' if not slot['is_full'] else '🔴 Full'}")
                        with col5:
                            if slot['is_active']:
                                st.write("✅")
                            else:
                                st.write("❌")
                    
                    st.divider()
        else:
            st.info(f"No slots found for {date_str}")
    
    with tab2:
        st.subheader("Create New Slot")
        
        doctors_data, _ = api_get("/doctors?active_only=true")
        
        if doctors_data:
            with st.form("create_slot_form"):
                # Doctor selection
                doctor_options = {f"Dr. {d['name']} ({d['specialization']})": d['id'] 
                                for d in doctors_data}
                selected_doctor = st.selectbox("Select Doctor*", options=list(doctor_options.keys()))
                doctor_id = doctor_options[selected_doctor]
                
                # Date and time
                slot_date = st.date_input("Date*", value=date.today())
                
                col1, col2 = st.columns(2)
                with col1:
                    start_time = st.time_input("Start Time*", value=None)
                with col2:
                    end_time = st.time_input("End Time*", value=None)
                
                max_capacity = st.number_input("Maximum Capacity*", min_value=1, max_value=100, value=20)
                
                submitted = st.form_submit_button("📅 Create Slot", type="primary")
                
                if submitted:
                    if start_time and end_time:
                        slot_data = {
                            "doctor_id": doctor_id,
                            "date": slot_date.strftime("%Y-%m-%d"),
                            "start_time": start_time.strftime("%H:%M"),
                            "end_time": end_time.strftime("%H:%M"),
                            "max_capacity": max_capacity
                        }
                        
                        result, error = api_post("/slots", slot_data)
                        
                        if result:
                            st.success("✅ Slot created successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {error}")
                    else:
                        st.error("Please select start and end times")
        else:
            st.warning("No doctors available. Please add doctors first.")

elif selected == "Analytics":
    st.title("📊 Analytics Dashboard")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=date.today())
    with col2:
        end_date = st.date_input("To", value=date.today())
    
    today = date.today().strftime("%Y-%m-%d")
    
    # System Overview
    st.subheader("System Overview")
    data, _ = api_get("/analytics/system/status")
    
    if data:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Doctors", data.get("total_doctors", 0))
        with col2:
            st.metric("Active Doctors", data.get("active_doctors", 0))
        with col3:
            st.metric("Slots Today", data.get("total_slots_today", 0))
        with col4:
            st.metric("Tokens Today", data.get("total_tokens_today", 0))
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Token Status Distribution")
            status_data = data.get("tokens_by_status", {})
            if status_data:
                fig = go.Figure(data=[go.Pie(
                    labels=list(status_data.keys()),
                    values=list(status_data.values()),
                    hole=.3
                )])
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Token Source Distribution")
            source_data = data.get("tokens_by_source", {})
            if source_data:
                fig = px.bar(
                    x=list(source_data.keys()),
                    y=list(source_data.values()),
                    labels={'x': 'Source', 'y': 'Count'}
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Doctor-wise analytics
        st.subheader("Doctor Performance Today")
        
        doctors_data, _ = api_get("/doctors?active_only=true")
        
        if doctors_data:
            doctor_analytics = []
            
            for doctor in doctors_data:
                analytics, _ = api_get(f"/analytics/doctors/{doctor['id']}/day/{today}")
                if analytics:
                    doctor_analytics.append(analytics)
            
            if doctor_analytics:
                df = pd.DataFrame(doctor_analytics)
                
                # Display as table
                display_df = df[['doctor_name', 'total_slots', 'total_allocated', 
                               'total_completed', 'total_cancelled', 'average_utilization']].copy()
                display_df.columns = ['Doctor', 'Slots', 'Allocated', 'Completed', 'Cancelled', 'Utilization %']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Utilization chart
                st.subheader("Doctor Utilization Comparison")
                fig = px.bar(
                    df, 
                    x='doctor_name', 
                    y='average_utilization',
                    labels={'doctor_name': 'Doctor', 'average_utilization': 'Utilization %'},
                    color='average_utilization',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)

elif selected == "System Status":
    st.title("⚙️ System Status")
    
    # API Health Check
    st.subheader("API Server Status")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API Server is running")
            st.json(response.json())
        else:
            st.error("❌ API Server returned an error")
    except:
        st.error("❌ Cannot connect to API server")
        st.info("Make sure the server is running on http://localhost:8000")
        st.code("python start.py", language="bash")
    
    st.divider()
    
    # System Information
    st.subheader("System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**API Endpoints**")
        st.code("""
        Base URL: http://localhost:8000/api/v1
        
        Doctors: /doctors
        Slots: /slots
        Tokens: /tokens
        Analytics: /analytics
        """)
    
    with col2:
        st.markdown("**Documentation**")
        st.markdown("- [API Docs](http://localhost:8000/docs)")
        st.markdown("- [ReDoc](http://localhost:8000/redoc)")
        st.markdown("- [Health Check](http://localhost:8000/health)")
    
    st.divider()
    
    # Database Stats
    st.subheader("Database Statistics")
    data, _ = api_get("/analytics/system/status")
    
    if data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Doctors", data.get("total_doctors", 0))
        with col2:
            today_slots = data.get("total_slots_today", 0)
            st.metric("Slots (Today)", today_slots)
        with col3:
            today_tokens = data.get("total_tokens_today", 0)
            st.metric("Tokens (Today)", today_tokens)
        
        # Detailed breakdown
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Token Status Breakdown**")
            status_data = data.get("tokens_by_status", {})
            for status, count in status_data.items():
                st.write(f"{get_status_emoji(status)} {status.capitalize()}: {count}")
        
        with col2:
            st.markdown("**Token Source Breakdown**")
            source_data = data.get("tokens_by_source", {})
            for source, count in source_data.items():
                st.write(f"{get_source_emoji(source)} {source.capitalize()}: {count}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🏥 OPD Token Allocation System | Built with Streamlit & FastAPI</p>
        <p>For support, check the documentation or contact IT support</p>
    </div>
    """,
    unsafe_allow_html=True
)
