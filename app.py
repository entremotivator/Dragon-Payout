import streamlit as st
import requests
import json
import base64
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Dots.dev API Manager",
    page_icon="🔵",
    layout="wide"
)

st.title("🔵 Dots.dev API Manager")
st.markdown("Manage users and operations through the Dots.dev API")

# Sidebar for API credentials
with st.sidebar:
    st.header("🔐 API Configuration")
    
    username = st.text_input("Username", type="password")
    password = st.text_input("Password", type="password")
    
    if username and password:
        # Create base64 encoded auth string
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        st.success("✅ Credentials configured")
    else:
        st.warning("⚠️ Please enter API credentials")
        encoded_credentials = None

# Helper function to make API requests
def make_api_request(method, endpoint, data=None, params=None):
    if not encoded_credentials:
        st.error("Please configure API credentials in the sidebar")
        return None
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json'
    }
    
    url = f"https://api.dots.dev/api/v2{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        if hasattr(e.response, 'text'):
            st.error(f"Response: {e.response.text}")
        return None

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📋 List Users", "➕ Create User", "🔍 User Details"])

with tab1:
    st.header("List All Users")
    
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "verified", "unverified", "in_review", "disabled"],
            index=0
        )
        
        limit = st.number_input("Limit", min_value=1, max_value=100, value=10)
    
    with col2:
        starting_after = st.text_input("Starting After (User ID)", help="For pagination")
        ending_before = st.text_input("Ending Before (User ID)", help="For pagination")
    
    if st.button("🔄 Fetch Users", type="primary"):
        params = {"limit": limit}
        
        if status_filter != "All":
            params["status"] = status_filter
        if starting_after:
            params["starting_after"] = starting_after
        if ending_before:
            params["ending_before"] = ending_before
        
        with st.spinner("Fetching users..."):
            response = make_api_request("GET", "/users", params=params)
        
        if response:
            users = response.get("data", [])
            has_more = response.get("has_more", False)
            
            st.success(f"✅ Found {len(users)} users")
            
            if has_more:
                st.info("ℹ️ More users available - use pagination parameters")
            
            if users:
                # Create a simplified view for the table
                user_data = []
                for user in users:
                    user_data.append({
                        "ID": user.get("id", ""),
                        "Name": f"{user.get('first_name', '')} {user.get('last_name', '')}",
                        "Email": user.get("email", ""),
                        "Status": user.get("status", ""),
                        "Wallet Amount": user.get("wallet", {}).get("amount", 0),
                        "Payout Method": user.get("default_payout_method", "")
                    })
                
                df = pd.DataFrame(user_data)
                st.dataframe(df, use_container_width=True)
                
                # Show detailed view for selected user
                if st.checkbox("Show detailed user data"):
                    selected_user_id = st.selectbox(
                        "Select user for details",
                        options=[user["ID"] for user in user_data],
                        format_func=lambda x: f"{next(u['Name'] for u in user_data if u['ID'] == x)} ({x[:8]}...)"
                    )
                    
                    selected_user = next((u for u in users if u["id"] == selected_user_id), None)
                    if selected_user:
                        st.json(selected_user)

with tab2:
    st.header("Create New User")
    
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", help="Required")
            last_name = st.text_input("Last Name *", help="Required")
            email = st.text_input("Email *", help="Required")
            
        with col2:
            country_code = st.text_input("Country Code *", value="1", help="e.g., 1 for US")
            phone_number = st.text_input("Phone Number *", help="e.g., 4157223331")
            username = st.text_input("Username", help="Optional, 1-50 characters")
        
        date_of_birth = st.date_input("Date of Birth", value=None, help="Optional")
        
        income_adjustment = st.number_input(
            "1099 Adjustment 2024", 
            min_value=0, 
            value=0, 
            help="Income paid outside Dots platform in 2024"
        )
        
        st.subheader("Metadata")
        metadata_key = st.text_input("Metadata Key", help="Optional")
        metadata_value = st.text_input("Metadata Value", help="Optional")
        
        submitted = st.form_submit_button("🚀 Create User", type="primary")
        
        if submitted:
            # Validate required fields
            if not all([first_name, last_name, email, country_code, phone_number]):
                st.error("❌ Please fill in all required fields")
            else:
                # Prepare payload
                payload = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "country_code": country_code,
                    "phone_number": phone_number
                }
                
                if username:
                    payload["username"] = username
                
                if date_of_birth:
                    payload["date_of_birth"] = date_of_birth.isoformat()
                
                if income_adjustment > 0:
                    payload["1099_adjustment_2024"] = income_adjustment
                
                if metadata_key and metadata_value:
                    payload["metadata"] = {metadata_key: metadata_value}
                
                with st.spinner("Creating user..."):
                    response = make_api_request("POST", "/users", data=payload)
                
                if response:
                    st.success("✅ User created successfully!")
                    st.json(response)
                    
                    # Store user ID for easy access
                    if "id" in response:
                        st.session_state.last_created_user_id = response["id"]

with tab3:
    st.header("User Details")
    
    if hasattr(st.session_state, 'last_created_user_id'):
        st.info(f"💡 Last created user ID: {st.session_state.last_created_user_id}")
    
    user_id = st.text_input("Enter User ID", help="Enter a user ID to fetch details")
    
    if user_id and st.button("🔍 Get User Details"):
        with st.spinner("Fetching user details..."):
            response = make_api_request("GET", f"/users/{user_id}")
        
        if response:
            st.success("✅ User found!")
            
            # Display key information in a nice format
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", response.get("status", "Unknown"))
                st.metric("Wallet Amount", f"${response.get('wallet', {}).get('amount', 0)}")
            
            with col2:
                st.metric("Payout Method", response.get("default_payout_method", "None"))
                st.metric("Withdrawable", f"${response.get('wallet', {}).get('withdrawable_amount', 0)}")
            
            with col3:
                compliance = response.get("compliance", {})
                st.metric("Tax ID Collected", "✅" if compliance.get("tax_id_collected") else "❌")
                st.metric("ID Verified", "✅" if compliance.get("id_verified") else "❌")
            
            # Full JSON response
            with st.expander("📄 Full User Data"):
                st.json(response)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and the Dots.dev API")

# Add some styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .stMetric > label {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    .stSuccess, .stInfo, .stWarning, .stError {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

