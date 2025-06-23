import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import random
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import uuid

# Page configuration
st.set_page_config(
    page_title="Dragon Payout Dashboard",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B35 0%, #F7931E 50%, #FFD23F 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #FF6B35;
        margin-bottom: 1rem;
    }
    
    .status-verified { color: #22c55e; font-weight: bold; }
    .status-unverified { color: #f59e0b; font-weight: bold; }
    .status-disabled { color: #ef4444; font-weight: bold; }
    .status-in_review { color: #8b5cf6; font-weight: bold; }
    
    .sidebar-logo {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .dragon-emoji { font-size: 2rem; }
</style>
""", unsafe_allow_html=True)

# Generate demo data
@st.cache_data
def generate_demo_users(count=50):
    """Generate realistic demo user data"""
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Chris", "Lisa", "Alex", "Maria", "James", "Anna", "Robert", "Emily", "Daniel", "Jessica", "Matthew", "Ashley", "Andrew", "Amanda"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Wilson", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White"]
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "company.com", "business.org"]
    statuses = ["verified", "unverified", "in_review", "disabled"]
    payout_methods = ["ach", "paypal", "venmo", "cash_app", "intl_bank"]
    
    users = []
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"
        
        user = {
            "id": str(uuid.uuid4()),
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": {
                "country_code": "1",
                "phone_number": f"415{random.randint(1000000, 9999999)}"
            },
            "default_payout_method": random.choice(payout_methods),
            "default_payout_method_details": {
                "id": str(uuid.uuid4()),
                "platform": random.choice(payout_methods),
                "description": f"{random.choice(payout_methods).upper()} Account",
                "mask": f"****{random.randint(1000, 9999)}",
                "country": "US",
                "currency": "USD"
            },
            "wallet": {
                "amount": random.randint(0, 10000),
                "withdrawable_amount": random.randint(0, 8000),
                "credit_balance": random.randint(0, 2000)
            },
            "status": random.choice(statuses),
            "compliance": {
                "tax_id_collected": random.choice([True, False]),
                "tax_id_verification": random.choice(["verified", "unsubmitted", "pending"]),
                "address_collected": random.choice([True, False]),
                "date_of_birth_collected": random.choice([True, False]),
                "id_verified": random.choice([True, False]),
                "flagged": random.choice([True, False]),
                "flags": {
                    "ofac": random.choice([True, False]),
                    "ofac_status": random.choice(["unflagged", "flagged", "pending"])
                }
            },
            "created_date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            "metadata": {"internal_id": f"user_{random.randint(100000, 999999)}"}
        }
        users.append(user)
    
    return users

@st.cache_data
def generate_analytics_data():
    """Generate analytics data for dashboard"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # Daily signups
    daily_signups = pd.DataFrame({
        'date': dates,
        'signups': [random.randint(5, 50) for _ in range(len(dates))]
    })
    
    # Monthly revenue
    monthly_dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    monthly_revenue = pd.DataFrame({
        'month': monthly_dates,
        'revenue': [random.randint(50000, 200000) for _ in range(len(monthly_dates))]
    })
    
    # Payout method distribution
    payout_dist = pd.DataFrame({
        'method': ['ACH', 'PayPal', 'Venmo', 'Cash App', 'International Bank'],
        'count': [random.randint(100, 500) for _ in range(5)]
    })
    
    return daily_signups, monthly_revenue, payout_dist

# Load demo data
demo_users = generate_demo_users()
daily_signups, monthly_revenue, payout_dist = generate_analytics_data()

# Header
st.markdown("""
<div class="main-header">
    <h1>🐉 Dragon Payout Dashboard</h1>
    <p>Powerful user management and analytics platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🐉 Dragon Payout</div>', unsafe_allow_html=True)
    
    st.markdown("### 📊 Quick Stats")
    total_users = len(demo_users)
    verified_users = len([u for u in demo_users if u["status"] == "verified"])
    total_wallet_value = sum([u["wallet"]["amount"] for u in demo_users])
    
    st.metric("Total Users", f"{total_users:,}")
    st.metric("Verified Users", f"{verified_users:,}")
    st.metric("Total Wallet Value", f"${total_wallet_value:,}")
    
    st.markdown("---")
    st.markdown("### 🔧 Demo Mode")
    st.info("This dashboard uses simulated data for demonstration purposes.")

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analytics", "👥 Users", "➕ Create User", "🔍 User Details", "💰 Payouts"])

with tab1:
    st.header("📊 Analytics Dashboard")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Users", 
            f"{len(demo_users):,}",
            delta=f"+{random.randint(5, 25)} this week"
        )
    
    with col2:
        verified_rate = (verified_users / total_users) * 100
        st.metric(
            "Verification Rate",
            f"{verified_rate:.1f}%",
            delta=f"+{random.randint(1, 5):.1f}%"
        )
    
    with col3:
        avg_wallet = total_wallet_value / total_users
        st.metric(
            "Avg Wallet Balance",
            f"${avg_wallet:.0f}",
            delta=f"+${random.randint(10, 50)}"
        )
    
    with col4:
        active_payouts = random.randint(150, 300)
        st.metric(
            "Active Payouts",
            f"{active_payouts}",
            delta=f"+{random.randint(5, 20)}"
        )
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily User Signups")
        fig = px.line(
            daily_signups.tail(30), 
            x='date', 
            y='signups',
            title="Last 30 Days",
            color_discrete_sequence=['#FF6B35']
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Payout Methods")
        fig = px.pie(
            payout_dist, 
            values='count', 
            names='method',
            color_discrete_sequence=px.colors.sequential.Sunset
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly revenue chart
    st.subheader("💵 Monthly Revenue Trend")
    fig = px.bar(
        monthly_revenue, 
        x='month', 
        y='revenue',
        title="Revenue by Month",
        color='revenue',
        color_continuous_scale='Sunset'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("👥 User Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "verified", "unverified", "in_review", "disabled"]
        )
    
    with col2:
        payout_filter = st.selectbox(
            "Filter by Payout Method",
            options=["All", "ach", "paypal", "venmo", "cash_app", "intl_bank"]
        )
    
    with col3:
        search_term = st.text_input("🔍 Search users", placeholder="Name or email...")
    
    # Filter users
    filtered_users = demo_users.copy()
    
    if status_filter != "All":
        filtered_users = [u for u in filtered_users if u["status"] == status_filter]
    
    if payout_filter != "All":
        filtered_users = [u for u in filtered_users if u["default_payout_method"] == payout_filter]
    
    if search_term:
        search_lower = search_term.lower()
        filtered_users = [
            u for u in filtered_users 
            if search_lower in u["first_name"].lower() 
            or search_lower in u["last_name"].lower() 
            or search_lower in u["email"].lower()
        ]
    
    st.write(f"**Showing {len(filtered_users)} of {len(demo_users)} users**")
    
    # User table
    if filtered_users:
        user_data = []
        for user in filtered_users:
            status_class = f"status-{user['status'].replace(' ', '_')}"
            user_data.append({
                "👤 Name": f"{user['first_name']} {user['last_name']}",
                "📧 Email": user["email"],
                "📱 Phone": f"+{user['phone_number']['country_code']} {user['phone_number']['phone_number']}",
                "✅ Status": user["status"].title(),
                "💰 Wallet": f"${user['wallet']['amount']:,}",
                "💳 Payout": user["default_payout_method"].upper(),
                "🆔 ID": user["id"][:8] + "..."
            })
        
        df = pd.DataFrame(user_data)
        
        # Display with styling
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "✅ Status": st.column_config.TextColumn(
                    help="User verification status"
                ),
                "💰 Wallet": st.column_config.TextColumn(
                    help="Current wallet balance"
                ),
                "💳 Payout": st.column_config.TextColumn(
                    help="Default payout method"
                )
            }
        )
        
        # Bulk actions
        st.markdown("### 🔧 Bulk Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Send Newsletter", help="Send newsletter to filtered users"):
                st.success(f"Newsletter sent to {len(filtered_users)} users!")
        
        with col2:
            if st.button("💰 Process Payouts", help="Process pending payouts"):
                st.success("Payouts processed successfully!")
        
        with col3:
            if st.button("📊 Export Data", help="Export filtered data to CSV"):
                st.success("Data exported to CSV!")

with tab3:
    st.header("➕ Create New User")
    
    with st.form("create_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Personal Information")
            first_name = st.text_input("First Name *", placeholder="John")
            last_name = st.text_input("Last Name *", placeholder="Doe")
            email = st.text_input("Email *", placeholder="john.doe@example.com")
            
        with col2:
            st.subheader("📱 Contact Information")
            country_code = st.selectbox("Country Code *", options=["1", "44", "33", "49", "81"], index=0)
            phone_number = st.text_input("Phone Number *", placeholder="4155551234")
            username = st.text_input("Username", placeholder="johndoe (optional)")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("💳 Payout Preferences")
            payout_method = st.selectbox(
                "Default Payout Method",
                options=["ach", "paypal", "venmo", "cash_app", "intl_bank"],
                format_func=lambda x: x.upper()
            )
            
        with col4:
            st.subheader("📋 Additional Info")
            date_of_birth = st.date_input("Date of Birth", value=None)
            income_adjustment = st.number_input("2024 Income Adjustment", min_value=0, value=0)
        
        st.subheader("🏷️ Metadata")
        col5, col6 = st.columns(2)
        with col5:
            metadata_key = st.text_input("Metadata Key", placeholder="department")
        with col6:
            metadata_value = st.text_input("Metadata Value", placeholder="engineering")
        
        submitted = st.form_submit_button("🚀 Create User", type="primary", use_container_width=True)
        
        if submitted:
            if not all([first_name, last_name, email, phone_number]):
                st.error("❌ Please fill in all required fields")
            else:
                # Simulate user creation
                new_user_id = str(uuid.uuid4())
                
                new_user = {
                    "id": new_user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone_number": {
                        "country_code": country_code,
                        "phone_number": phone_number
                    },
                    "default_payout_method": payout_method,
                    "wallet": {
                        "amount": 0,
                        "withdrawable_amount": 0,
                        "credit_balance": 0
                    },
                    "status": "unverified",
                    "created_date": datetime.now().isoformat()
                }
                
                st.success("✅ User created successfully!")
                st.balloons()
                
                # Show created user details
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**User ID:** {new_user_id}")
                    st.info(f"**Status:** Unverified (pending verification)")
                
                with col2:
                    st.info(f"**Email:** {email}")
                    st.info(f"**Payout Method:** {payout_method.upper()}")
                
                # Store for easy access
                st.session_state.last_created_user = new_user

with tab4:
    st.header("🔍 User Details")
    
    if hasattr(st.session_state, 'last_created_user'):
        st.info(f"💡 Last created user: {st.session_state.last_created_user['first_name']} {st.session_state.last_created_user['last_name']}")
    
    # User selection
    user_options = [f"{u['first_name']} {u['last_name']} ({u['email']})" for u in demo_users]
    selected_user_display = st.selectbox("Select User", options=user_options)
    
    if selected_user_display:
        # Find selected user
        selected_index = user_options.index(selected_user_display)
        selected_user = demo_users[selected_index]
        
        # User overview cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_color = {
                "verified": "🟢",
                "unverified": "🟡", 
                "in_review": "🟣",
                "disabled": "🔴"
            }
            st.metric(
                "Status", 
                f"{status_color.get(selected_user['status'], '⚪')} {selected_user['status'].title()}"
            )
        
        with col2:
            st.metric("Wallet Balance", f"${selected_user['wallet']['amount']:,}")
        
        with col3:
            st.metric("Withdrawable", f"${selected_user['wallet']['withdrawable_amount']:,}")
        
        with col4:
            st.metric("Payout Method", selected_user['default_payout_method'].upper())
        
        # Detailed information
        tab_info, tab_compliance, tab_raw = st.tabs(["📋 Information", "🛡️ Compliance", "📄 Raw Data"])
        
        with tab_info:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👤 Personal Details")
                st.write(f"**Name:** {selected_user['first_name']} {selected_user['last_name']}")
                st.write(f"**Email:** {selected_user['email']}")
                st.write(f"**Phone:** +{selected_user['phone_number']['country_code']} {selected_user['phone_number']['phone_number']}")
                st.write(f"**User ID:** {selected_user['id']}")
            
            with col2:
                st.subheader("💰 Financial Details")
                st.write(f"**Wallet Balance:** ${selected_user['wallet']['amount']:,}")
                st.write(f"**Withdrawable:** ${selected_user['wallet']['withdrawable_amount']:,}")
                st.write(f"**Credit Balance:** ${selected_user['wallet']['credit_balance']:,}")
                st.write(f"**Payout Method:** {selected_user['default_payout_method'].upper()}")
        
        with tab_compliance:
            compliance = selected_user['compliance']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✅ Verification Status")
                st.write(f"**Tax ID Collected:** {'✅' if compliance['tax_id_collected'] else '❌'}")
                st.write(f"**Address Collected:** {'✅' if compliance['address_collected'] else '❌'}")
                st.write(f"**DOB Collected:** {'✅' if compliance['date_of_birth_collected'] else '❌'}")
                st.write(f"**ID Verified:** {'✅' if compliance['id_verified'] else '❌'}")
            
            with col2:
                st.subheader("🚩 Flags & Alerts")
                st.write(f"**Flagged:** {'⚠️ Yes' if compliance['flagged'] else '✅ No'}")
                st.write(f"**OFAC Status:** {compliance['flags']['ofac_status'].title()}")
                st.write(f"**Tax Verification:** {compliance['tax_id_verification'].title()}")
        
        with tab_raw:
            st.json(selected_user)

with tab5:
    st.header("💰 Payout Management")
    
    # Payout stats
    col1, col2, col3, col4 = st.columns(4)
    
    total_payouts = random.randint(500, 1000)
    pending_payouts = random.randint(50, 150)
    completed_today = random.randint(20, 80)
    total_amount = random.randint(500000, 2000000)
    
    with col1:
        st.metric("Total Payouts", f"{total_payouts:,}")
    
    with col2:
        st.metric("Pending", f"{pending_payouts}", delta=f"-{random.randint(5, 20)}")
    
    with col3:
        st.metric("Completed Today", f"{completed_today}")
    
    with col4:
        st.metric("Total Amount", f"${total_amount:,}")
    
    # Payout actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💸 Process Pending Payouts", type="primary", use_container_width=True):
            with st.spinner("Processing payouts..."):
                import time
                time.sleep(2)
            st.success(f"Successfully processed {pending_payouts} payouts!")
            st.balloons()
    
    with col2:
        if st.button("📊 Generate Payout Report", use_container_width=True):
            st.success("Payout report generated and sent to your email!")
    
    with col3:
        if st.button("🔍 Audit Trail", use_container_width=True):
            st.info("Opening audit trail in new window...")
    
    # Recent payouts table
    st.markdown("### 📋 Recent Payouts")
    
    # Generate sample payout data
    recent_payouts = []
    for i in range(10):
        user = random.choice(demo_users)
        recent_payouts.append({
            "ID": f"PO-{random.randint(10000, 99999)}",
            "User": f"{user['first_name']} {user['last_name']}",
            "Amount": f"${random.randint(100, 5000):,}",
            "Method": user['default_payout_method'].upper(),
            "Status": random.choice(["Completed", "Pending", "Processing"]),
            "Date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        })
    
    payout_df = pd.DataFrame(recent_payouts)
    st.dataframe(payout_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #FF6B35 0%, #F7931E 50%, #FFD23F 100%); border-radius: 10px; color: white; margin-top: 2rem;">
    <h3>🐉 Dragon Payout Dashboard</h3>
    <p>Built with ❤️ using Streamlit | Demo Version</p>
    <p><strong>Powerful • Secure • Scalable</strong></p>
</div>
""", unsafe_allow_html=True)

