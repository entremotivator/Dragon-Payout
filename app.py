import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import random
import numpy as np
from typing import Dict, List, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="Dragon Dash Payout Center",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dragon theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B35, #F7931E, #FFB84D);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(255, 107, 53, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .payout-card {
        border: 2px solid #FF6B35;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.1);
    }
    
    .client-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        transition: all 0.3s ease;
    }
    
    .client-card:hover {
        border-color: #FF6B35;
        box-shadow: 0 2px 10px rgba(255, 107, 53, 0.2);
    }
    
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .demo-badge {
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .woocommerce-section {
        background: linear-gradient(135deg, #7B68EE 0%, #9370DB 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Payout Methods with Dragon Theme
PAYOUT_METHODS = {
    "🏦 Bank Transfer": {
        "processing_time": "1-3 business days",
        "fee": "$0.50",
        "min_amount": 10.00,
        "max_amount": 10000.00,
        "dragon_bonus": "🐉 Dragon Scale Protection"
    },
    "💳 PayPal": {
        "processing_time": "Instant",
        "fee": "2.9% + $0.30",
        "min_amount": 1.00,
        "max_amount": 5000.00,
        "dragon_bonus": "🔥 Fire Speed Transfer"
    },
    "📱 Venmo": {
        "processing_time": "Instant",
        "fee": "1.75%",
        "min_amount": 0.01,
        "max_amount": 2999.99,
        "dragon_bonus": "⚡ Lightning Wings"
    },
    "💰 Cash App": {
        "processing_time": "Instant",
        "fee": "1.5%",
        "min_amount": 1.00,
        "max_amount": 2500.00,
        "dragon_bonus": "🌟 Golden Claw Rewards"
    },
    "🏧 Zelle": {
        "processing_time": "Minutes",
        "fee": "Free",
        "min_amount": 1.00,
        "max_amount": 2500.00,
        "dragon_bonus": "💎 Crystal Clear Transfer"
    },
    "🎯 Apple Pay": {
        "processing_time": "Instant",
        "fee": "1.5%",
        "min_amount": 1.00,
        "max_amount": 3000.00,
        "dragon_bonus": "🍎 Mystic Apple Power"
    },
    "🤖 Google Pay": {
        "processing_time": "Instant",
        "fee": "1.5%",
        "min_amount": 1.00,
        "max_amount": 3000.00,
        "dragon_bonus": "🔮 Digital Dragon Magic"
    },
    "💎 Crypto (Bitcoin)": {
        "processing_time": "10-60 minutes",
        "fee": "Network fees apply",
        "min_amount": 10.00,
        "max_amount": 50000.00,
        "dragon_bonus": "🚀 Cosmic Dragon Flight"
    },
    "🌟 Crypto (Ethereum)": {
        "processing_time": "2-15 minutes",
        "fee": "Gas fees apply",
        "min_amount": 5.00,
        "max_amount": 25000.00,
        "dragon_bonus": "⚡ Electric Dragon Power"
    },
    "🎪 Stripe": {
        "processing_time": "2-7 business days",
        "fee": "2.9% + $0.30",
        "min_amount": 1.00,
        "max_amount": 15000.00,
        "dragon_bonus": "🎭 Merchant Dragon Shield"
    },
    "🏪 Square": {
        "processing_time": "1-2 business days",
        "fee": "2.6% + $0.10",
        "min_amount": 1.00,
        "max_amount": 10000.00,
        "dragon_bonus": "📦 Treasure Chest Security"
    },
    "🌐 Wise (TransferWise)": {
        "processing_time": "1-2 business days",
        "fee": "0.5-2%",
        "min_amount": 1.00,
        "max_amount": 50000.00,
        "dragon_bonus": "🌍 Global Dragon Network"
    }
}

# Generate 50 Demo Clients
def generate_demo_clients() -> List[Dict]:
    """Generate 50 demo clients with realistic data"""
    first_names = ["Alex", "Jordan", "Casey", "Morgan", "Taylor", "Riley", "Avery", "Quinn", "Sage", "River",
                   "Phoenix", "Skyler", "Cameron", "Dakota", "Emery", "Finley", "Hayden", "Indigo", "Kai", "Lane",
                   "Marley", "Nova", "Ocean", "Parker", "Reese", "Rowan", "Shiloh", "Tatum", "Unity", "Vale",
                   "Wren", "Zion", "Blake", "Drew", "Ellis", "Gray", "Harper", "Jude", "Kendall", "Logan",
                   "Max", "Nico", "Onyx", "Peyton", "Remy", "Sam", "True", "Vale", "West", "Zara"]
    
    last_names = ["Dragon", "Fire", "Storm", "Swift", "Blaze", "Thunder", "Lightning", "Phoenix", "Frost", "Steel",
                  "Shadow", "Flame", "Wind", "Stone", "River", "Mountain", "Star", "Moon", "Sun", "Cloud",
                  "Wave", "Forest", "Desert", "Ocean", "Sky", "Earth", "Crystal", "Diamond", "Gold", "Silver",
                  "Copper", "Iron", "Jade", "Ruby", "Emerald", "Sapphire", "Pearl", "Coral", "Amber", "Onyx",
                  "Quartz", "Granite", "Marble", "Slate", "Flint", "Ash", "Ember", "Spark", "Glow", "Shine"]
    
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
              "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte", "San Francisco",
              "Indianapolis", "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City"]
    
    vehicle_types = ["🚗 Sedan", "🚙 SUV", "🏍️ Motorcycle", "🚲 Bicycle", "🛵 Scooter", "🚐 Van", "🚚 Truck"]
    
    clients = []
    for i in range(50):
        client = {
            "id": f"DRG{1000 + i}",
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "email": f"driver{i+1}@dragondash.com",
            "phone": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            "city": random.choice(cities),
            "vehicle": random.choice(vehicle_types),
            "rating": round(random.uniform(4.2, 5.0), 1),
            "total_deliveries": random.randint(50, 2500),
            "total_earnings": round(random.uniform(500, 15000), 2),
            "current_balance": round(random.uniform(0, 2500), 2),
            "join_date": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
            "status": random.choice(["Active", "Active", "Active", "Inactive", "Pending"]),
            "preferred_payout": random.choice(list(PAYOUT_METHODS.keys())),
            "last_payout": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
            "dragon_level": random.choice(["🥉 Bronze Dragon", "🥈 Silver Dragon", "🥇 Gold Dragon", "💎 Diamond Dragon", "🌟 Legendary Dragon"])
        }
        clients.append(client)
    
    return clients

# Mock Dots SDK implementation with enhanced features
class MockDots:
    def __init__(self):
        self.client_id = None
        self.api_key = None
        self.configured = False
        self.demo_mode = True
        self.demo_clients = generate_demo_clients()
    
    def configure(self, client_id, api_key):
        self.client_id = client_id
        self.api_key = api_key
        self.configured = True
        # Check if using demo credentials
        self.demo_mode = client_id.startswith('pk_demo_') or api_key.startswith('sk_demo_')
    
    def get_clients(self):
        if self.demo_mode:
            return self.demo_clients
        else:
            # In real implementation, this would fetch from Dots API
            return self.demo_clients[:10]  # Return fewer for real API simulation
    
    class Invoice:
        @staticmethod
        def create(**kwargs):
            return {
                'id': f'inv_{int(time.time())}',
                'amount': kwargs.get('amount', 0),
                'recipient': kwargs.get('recipient', ''),
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'payout_method': kwargs.get('payout_method', 'Bank Transfer')
            }
        
        @staticmethod
        def list():
            return [
                {
                    'id': 'inv_001',
                    'amount': 1250.00,
                    'recipient': 'driver_001@dragondash.com',
                    'status': 'completed',
                    'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
                    'payout_method': '🏦 Bank Transfer'
                },
                {
                    'id': 'inv_002',
                    'amount': 875.50,
                    'recipient': 'driver_002@dragondash.com',
                    'status': 'pending',
                    'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'payout_method': '💳 PayPal'
                },
                {
                    'id': 'inv_003',
                    'amount': 2100.75,
                    'recipient': 'driver_003@dragondash.com',
                    'status': 'completed',
                    'created_at': (datetime.now() - timedelta(days=3)).isoformat(),
                    'payout_method': '📱 Venmo'
                }
            ]
    
    class Payout:
        @staticmethod
        def create(**kwargs):
            return {
                'id': f'payout_{int(time.time())}',
                'amount': kwargs.get('amount', 0),
                'recipient': kwargs.get('recipient', ''),
                'status': 'processing',
                'created_at': datetime.now().isoformat(),
                'payout_method': kwargs.get('payout_method', 'Bank Transfer'),
                'dragon_bonus': PAYOUT_METHODS.get(kwargs.get('payout_method', '🏦 Bank Transfer'), {}).get('dragon_bonus', '')
            }
        
        @staticmethod
        def get_balance():
            return {
                'available': 15750.25,
                'pending': 3250.50,
                'total': 19000.75
            }
    
    class WooCommerce:
        @staticmethod
        def sync_orders():
            """Mock WooCommerce sync"""
            return {
                'synced_orders': random.randint(15, 45),
                'new_payouts': random.randint(5, 15),
                'total_amount': round(random.uniform(2000, 8000), 2),
                'last_sync': datetime.now().isoformat()
            }
        
        @staticmethod
        def get_connection_status():
            return {
                'connected': True,
                'store_url': 'https://dragondash-store.com',
                'last_sync': (datetime.now() - timedelta(minutes=random.randint(5, 60))).isoformat(),
                'orders_pending': random.randint(0, 12)
            }

# Initialize mock Dots SDK
dots = MockDots()

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🐉 Dragon Dash Payout Center</h1>
        <p>Advanced driver payouts and financial operations with WooCommerce integration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Configuration
        with st.expander("🔑 Dots API Configuration", expanded=not dots.configured):
            st.markdown("**Demo Credentials Available:**")
            st.code("Client ID: pk_demo_dragon_dash_2024")
            st.code("API Key: sk_demo_dragon_dash_secret_key")
            
            client_id = st.text_input(
                "Client ID", 
                value="pk_demo_dragon_dash_2024",
                help="Your Dots API Client ID from Developer Dashboard"
            )
            api_key = st.text_input(
                "API Key", 
                value="sk_demo_dragon_dash_secret_key",
                type="password",
                help="Your Dots API Key from Developer Dashboard"
            )
            
            if st.button("🔗 Configure API", use_container_width=True):
                if client_id and api_key:
                    dots.configure(client_id, api_key)
                    if dots.demo_mode:
                        st.success("✅ Demo Mode Activated!")
                        st.info("🎭 Using 50 demo clients for testing")
                    else:
                        st.success("✅ Live API Configured!")
                else:
                    st.error("❌ Please provide both Client ID and API Key")
        
        # Demo Mode Indicator
        if dots.configured and dots.demo_mode:
            st.markdown("""
            <div class="demo-badge">
                🎭 DEMO MODE ACTIVE
            </div>
            """, unsafe_allow_html=True)
        
        # WooCommerce Integration
        with st.expander("🛒 WooCommerce Integration"):
            woo_url = st.text_input("Store URL", value="https://dragondash-store.com")
            woo_key = st.text_input("Consumer Key", type="password")
            woo_secret = st.text_input("Consumer Secret", type="password")
            
            if st.button("🔗 Connect WooCommerce", use_container_width=True):
                st.success("✅ WooCommerce Connected!")
                st.info("🔄 Auto-sync enabled every 15 minutes")
        
        # Navigation
        st.header("📊 Navigation")
        page = st.selectbox(
            "Select Page",
            ["Dashboard", "Client Management", "Create Payout", "Payout Methods", "Invoice Management", "WooCommerce Sync", "Transaction History", "Analytics"]
        )
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Client Management":
        show_client_management()
    elif page == "Create Payout":
        show_create_payout()
    elif page == "Payout Methods":
        show_payout_methods()
    elif page == "Invoice Management":
        show_invoice_management()
    elif page == "WooCommerce Sync":
        show_woocommerce_sync()
    elif page == "Transaction History":
        show_transaction_history()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    st.header("📊 Dashboard Overview")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        return
    
    # Balance Overview
    balance = dots.Payout.get_balance()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Available Balance</h3>
            <h2>${balance['available']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏳ Pending Balance</h3>
            <h2>${balance['pending']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Total Balance</h3>
            <h2>${balance['total']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        client_count = len(dots.get_clients())
        st.markdown(f"""
        <div class="metric-card">
            <h3>🐉 Active Dragons</h3>
            <h2>{client_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # WooCommerce Status
    if dots.configured:
        woo_status = dots.WooCommerce.get_connection_status()
        st.markdown(f"""
        <div class="woocommerce-section">
            <h3>🛒 WooCommerce Status</h3>
            <p><strong>Store:</strong> {woo_status['store_url']}</p>
            <p><strong>Last Sync:</strong> {datetime.fromisoformat(woo_status['last_sync']).strftime('%Y-%m-%d %H:%M')}</p>
            <p><strong>Pending Orders:</strong> {woo_status['orders_pending']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent Activity
    st.subheader("🔄 Recent Activity")
    
    recent_activity = [
        {"time": "2 hours ago", "action": "Payout Created", "amount": "$875.50", "driver": "Alex Dragon", "method": "💳 PayPal"},
        {"time": "1 day ago", "action": "Payout Completed", "amount": "$1,250.00", "driver": "Jordan Fire", "method": "🏦 Bank Transfer"},
        {"time": "2 days ago", "action": "WooCommerce Sync", "amount": "$2,100.75", "driver": "System", "method": "🛒 Auto-sync"},
        {"time": "3 days ago", "action": "Payout Processing", "amount": "$650.25", "driver": "Casey Storm", "method": "📱 Venmo"},
    ]
    
    for activity in recent_activity:
        st.markdown(f"""
        <div class="payout-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{activity['action']}</strong><br>
                    <small>{activity['time']} • {activity['driver']} • {activity['method']}</small>
                </div>
                <div style="text-align: right;">
                    <strong style="color: #FF6B35;">{activity['amount']}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_client_management():
    st.header("🐉 Dragon Client Management")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        return
    
    clients = dots.get_clients()
    
    # Client Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    active_clients = len([c for c in clients if c['status'] == 'Active'])
    total_earnings = sum(c['total_earnings'] for c in clients)
    avg_rating = sum(c['rating'] for c in clients) / len(clients)
    total_deliveries = sum(c['total_deliveries'] for c in clients)
    
    with col1:
        st.metric("🟢 Active Dragons", active_clients)
    with col2:
        st.metric("💰 Total Earnings", f"${total_earnings:,.2f}")
    with col3:
        st.metric("⭐ Avg Rating", f"{avg_rating:.1f}")
    with col4:
        st.metric("📦 Total Deliveries", f"{total_deliveries:,}")
    
    # Filters
    st.subheader("🔍 Filter Dragons")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Status", ["All", "Active", "Inactive", "Pending"])
    with col2:
        city_filter = st.selectbox("City", ["All"] + list(set(c['city'] for c in clients)))
    with col3:
        dragon_level_filter = st.selectbox("Dragon Level", ["All"] + list(set(c['dragon_level'] for c in clients)))
    
    # Filter clients
    filtered_clients = clients
    if status_filter != "All":
        filtered_clients = [c for c in filtered_clients if c['status'] == status_filter]
    if city_filter != "All":
        filtered_clients = [c for c in filtered_clients if c['city'] == city_filter]
    if dragon_level_filter != "All":
        filtered_clients = [c for c in filtered_clients if c['dragon_level'] == dragon_level_filter]
    
    # Display clients
    st.subheader(f"📋 Dragon Roster ({len(filtered_clients)} dragons)")
    
    # Create DataFrame for better display
    df = pd.DataFrame(filtered_clients)
    
    # Display in a nice table
    st.dataframe(
        df[['id', 'name', 'city', 'vehicle', 'rating', 'total_deliveries', 'total_earnings', 'current_balance', 'status', 'dragon_level']],
        column_config={
            "id": "Dragon ID",
            "name": "Name",
            "city": "City",
            "vehicle": "Vehicle",
            "rating": st.column_config.NumberColumn("Rating", format="⭐ %.1f"),
            "total_deliveries": st.column_config.NumberColumn("Deliveries", format="%d 📦"),
            "total_earnings": st.column_config.NumberColumn("Total Earnings", format="$%.2f"),
            "current_balance": st.column_config.NumberColumn("Balance", format="$%.2f"),
            "status": st.column_config.SelectboxColumn("Status", options=["Active", "Inactive", "Pending"]),
            "dragon_level": "Dragon Level"
        },
        use_container_width=True,
        height=400
    )
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    
    selected_client = st.selectbox(
        "Select Dragon for Actions",
        options=[f"{c['id']} - {c['name']}" for c in filtered_clients]
    )
    
    if selected_client:
        client_id = selected_client.split(' - ')[0]
        client = next(c for c in clients if c['id'] == client_id)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💸 Create Payout"):
                st.session_state.selected_client = client
                st.session_state.page = "Create Payout"
                st.rerun()
        
        with col2:
            if st.button("📧 Send Message"):
                st.success(f"Message sent to {client['name']}")
        
        with col3:
            if st.button("📊 View Details"):
                with st.expander(f"Dragon Details: {client['name']}", expanded=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Email:** {client['email']}")
                        st.write(f"**Phone:** {client['phone']}")
                        st.write(f"**Join Date:** {client['join_date']}")
                        st.write(f"**Preferred Payout:** {client['preferred_payout']}")
                    with col_b:
                        st.write(f"**Last Payout:** {client['last_payout']}")
                        st.write(f"**Vehicle:** {client['vehicle']}")
                        st.write(f"**Dragon Level:** {client['dragon_level']}")
                        st.write(f"**Rating:** ⭐ {client['rating']}")
        
        with col4:
            if st.button("🔄 Sync Data"):
                st.info(f"Data synced for {client['name']}")

def show_payout_methods():
    st.header("💳 Dragon Payout Methods")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); padding: 1rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h3>🐉 Choose Your Dragon Power Payment Method</h3>
        <p>Each method comes with unique Dragon bonuses and magical processing speeds!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display payout methods in a grid
    cols = st.columns(2)
    
    for i, (method, details) in enumerate(PAYOUT_METHODS.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="payout-card">
                <h4>{method}</h4>
                <p><strong>⏱️ Processing:</strong> {details['processing_time']}</p>
                <p><strong>💰 Fee:</strong> {details['fee']}</p>
                <p><strong>📊 Range:</strong> ${details['min_amount']:.2f} - ${details['max_amount']:,.2f}</p>
                <p><strong>🐉 Dragon Bonus:</strong> {details['dragon_bonus']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Payout Method Comparison
    st.subheader("📊 Method Comparison")
    
    # Create comparison DataFrame
    comparison_data = []
    for method, details in PAYOUT_METHODS.items():
        comparison_data.append({
            "Method": method,
            "Processing Time": details['processing_time'],
            "Fee": details['fee'],
            "Min Amount": f"${details['min_amount']:.2f}",
            "Max Amount": f"${details['max_amount']:,.2f}",
            "Dragon Bonus": details['dragon_bonus']
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Method Usage Statistics
    st.subheader("📈 Usage Statistics")
    
    # Mock usage data
    usage_data = {
        "Method": list(PAYOUT_METHODS.keys()),
        "Usage Count": [random.randint(50, 500) for _ in PAYOUT_METHODS],
        "Total Volume": [random.randint(10000, 100000) for _ in PAYOUT_METHODS]
    }
    
    df_usage = pd.DataFrame(usage_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_usage = px.bar(
            df_usage, 
            x="Method", 
            y="Usage Count",
            title="Payment Method Usage",
            color="Usage Count",
            color_continuous_scale="Oranges"
        )
        fig_usage.update_xaxis(tickangle=45)
        st.plotly_chart(fig_usage, use_container_width=True)
    
    with col2:
        fig_volume = px.pie(
            df_usage,
            values="Total Volume",
            names="Method",
            title="Volume Distribution",
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        st.plotly_chart(fig_volume, use_container_width=True)

def show_create_payout():
    st.header("💸 Create Dragon Payout")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        return
    
    # Pre-fill if client selected from client management
    selected_client = st.session_state.get('selected_client', None)
    
    with st.form("payout_form"):
        st.subheader("🐉 Payout Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if selected_client:
                recipient_email = st.text_input(
                    "Recipient Email",
                    value=selected_client['email'],
                    disabled=True
                )
                st.info(f"Selected Dragon: {selected_client['name']} ({selected_client['dragon_level']})")
            else:
                clients = dots.get_clients()
                client_options = [f"{c['email']} - {c['name']}" for c in clients]
                selected_option = st.selectbox("Select Dragon", [""] + client_options)
                recipient_email = selected_option.split(' - ')[0] if selected_option else ""
            
            payout_amount = st.number_input(
                "Payout Amount ($)",
                min_value=0.01,
                value=selected_client['current_balance'] if selected_client else 100.00,
                step=0.01
            )
        
        with col2:
            payout_method = st.selectbox(
                "🐉 Dragon Payment Method",
                list(PAYOUT_METHODS.keys()),
                index=0 if not selected_client else list(PAYOUT_METHODS.keys()).index(selected_client.get('preferred_payout', list(PAYOUT_METHODS.keys())[0]))
            )
            
            priority = st.selectbox(
                "🔥 Dragon Priority",
                ["🐉 Standard Dragon", "⚡ Lightning Dragon", "🚀 Cosmic Dragon"]
            )
        
        # Show method details
        if payout_method:
            method_details = PAYOUT_METHODS[payout_method]
            st.info(f"**{method_details['dragon_bonus']}** | Processing: {method_details['processing_time']} | Fee: {method_details['fee']}")
        
        description = st.text_area(
            "Description (Optional)",
            placeholder="Weekly dragon payout for epic deliveries..."
        )
        
        # Payout schedule
        st.subheader("⏰ Dragon Schedule")
        schedule_type = st.radio(
            "When should the dragon receive their treasure?",
            ["🔥 Immediate Fire Breath", "📅 Scheduled Dragon Flight"]
        )
        
        scheduled_date = None
        if schedule_type == "📅 Scheduled Dragon Flight":
            scheduled_date = st.date_input(
                "Schedule Date",
                min_value=datetime.now().date()
            )
        
        submitted = st.form_submit_button("🚀 Launch Dragon Payout", use_container_width=True)
        
        if submitted:
            if recipient_email and payout_amount > 0:
                try:
                    # Validate amount against method limits
                    method_details = PAYOUT_METHODS[payout_method]
                    if payout_amount < method_details['min_amount']:
                        st.error(f"Amount too low! Minimum for {payout_method}: ${method_details['min_amount']:.2f}")
                    elif payout_amount > method_details['max_amount']:
                        st.error(f"Amount too high! Maximum for {payout_method}: ${method_details['max_amount']:,.2f}")
                    else:
                        # Create payout using Dots SDK
                        payout = dots.Payout.create(
                            recipient=recipient_email,
                            amount=payout_amount,
                            payout_method=payout_method,
                            priority=priority,
                            description=description,
                            scheduled_date=scheduled_date
                        )
                        
                        st.markdown(f"""
                        <div class="success-message">
                            <h4>🐉 Dragon Payout Launched Successfully!</h4>
                            <p><strong>Payout ID:</strong> {payout['id']}</p>
                            <p><strong>Amount:</strong> ${payout['amount']:,.2f}</p>
                            <p><strong>Status:</strong> {payout['status'].title()}</p>
                            <p><strong>Dragon Method:</strong> {payout['payout_method']}</p>
                            <p><strong>Dragon Bonus:</strong> {payout['dragon_bonus']}</p>
                            <p><strong>Recipient:</strong> {payout['recipient']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Clear selected client
                        if 'selected_client' in st.session_state:
                            del st.session_state.selected_client
                        
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        <h4>❌ Dragon Payout Failed</h4>
                        <p>{str(e)}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please fill in all required dragon fields.")

def show_woocommerce_sync():
    st.header("🛒 WooCommerce Dragon Sync")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        return
    
    # Connection Status
    woo_status = dots.WooCommerce.get_connection_status()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="woocommerce-section">
            <h3>🔗 Connection Status</h3>
            <p><strong>Status:</strong> {'🟢 Connected' if woo_status['connected'] else '🔴 Disconnected'}</p>
            <p><strong>Store URL:</strong> {woo_status['store_url']}</p>
            <p><strong>Last Sync:</strong> {datetime.fromisoformat(woo_status['last_sync']).strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📦 Pending Orders</h3>
            <h2>{woo_status['orders_pending']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Sync Actions
    st.subheader("🔄 Sync Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Manual Sync Now", use_container_width=True):
            with st.spinner("🐉 Dragon syncing with WooCommerce..."):
                time.sleep(2)  # Simulate sync time
                sync_result = dots.WooCommerce.sync_orders()
                
                st.success(f"""
                ✅ Sync Complete!
                - Orders Synced: {sync_result['synced_orders']}
                - New Payouts: {sync_result['new_payouts']}
                - Total Amount: ${sync_result['total_amount']:,.2f}
                """)
    
    with col2:
        if st.button("⚙️ Configure Auto-Sync", use_container_width=True):
            st.info("Auto-sync configured for every 15 minutes")
    
    with col3:
        if st.button("📊 View Sync History", use_container_width=True):
            st.info("Sync history feature coming soon!")
    
    # Recent Sync Activity
    st.subheader("📋 Recent WooCommerce Activity")
    
    # Mock sync history
    sync_history = [
        {
            "timestamp": datetime.now() - timedelta(minutes=15),
            "orders": 23,
            "payouts": 8,
            "amount": 1250.75,
            "status": "Success"
        },
        {
            "timestamp": datetime.now() - timedelta(hours=1),
            "orders": 18,
            "payouts": 6,
            "amount": 890.50,
            "status": "Success"
        },
        {
            "timestamp": datetime.now() - timedelta(hours=2),
            "orders": 31,
            "payouts": 12,
            "amount": 2100.25,
            "status": "Success"
        }
    ]
    
    for sync in sync_history:
        st.markdown(f"""
        <div class="payout-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>🛒 WooCommerce Sync</strong><br>
                    <small>{sync['timestamp'].strftime('%Y-%m-%d %H:%M')} • {sync['orders']} orders • {sync['payouts']} payouts</small>
                </div>
                <div style="text-align: right;">
                    <strong style="color: #FF6B35;">${sync['amount']:,.2f}</strong><br>
                    <small style="color: green;">✅ {sync['status']}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # WooCommerce Settings
    st.subheader("⚙️ WooCommerce Settings")
    
    with st.expander("🔧 Advanced Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Sync Frequency", ["Every 15 minutes", "Every 30 minutes", "Every hour", "Manual only"])
            st.selectbox("Order Status Filter", ["All", "Processing", "Completed", "On-hold"])
        
        with col2:
            st.selectbox("Auto-Payout Threshold", ["$50", "$100", "$250", "$500", "Disabled"])
            st.checkbox("Enable Dragon Notifications", value=True)
        
        if st.button("💾 Save Settings"):
            st.success("🐉 Dragon settings saved successfully!")

def show_invoice_management():
    st.header("📄 Dragon Invoice Management")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        return
    
    tab1, tab2 = st.tabs(["📋 View Dragon Invoices", "➕ Create Dragon Invoice"])
    
    with tab1:
        st.subheader("Recent Dragon Invoices")
        
        # Get invoices from Dots SDK
        invoices = dots.Invoice.list()
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(invoices)
        df['amount'] = df['amount'].apply(lambda x: f"${x:,.2f}")
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Display invoices
        st.dataframe(
            df,
            column_config={
                "id": "Invoice ID",
                "amount": "Amount",
                "recipient": "Dragon Recipient",
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["pending", "completed", "failed"],
                ),
                "created_at": "Created At",
                "payout_method": "Dragon Method"
            },
            use_container_width=True
        )
        
        # Invoice actions
        st.subheader("🐉 Dragon Invoice Actions")
        selected_invoice = st.selectbox(
            "Select Invoice for Dragon Actions",
            options=[inv['id'] for inv in invoices],
            format_func=lambda x: f"{x} - {next(inv['recipient'] for inv in invoices if inv['id'] == x)}"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📧 Send Dragon Reminder"):
                st.success(f"🐉 Dragon reminder sent for invoice {selected_invoice}")
        
        with col2:
            if st.button("❌ Cancel Dragon Invoice"):
                st.warning(f"🐉 Dragon invoice {selected_invoice} cancelled")
        
        with col3:
            if st.button("🔄 Resend Dragon Invoice"):
                st.info(f"🐉 Dragon invoice {selected_invoice} resent")
    
    with tab2:
        st.subheader("Create New Dragon Invoice")
        
        with st.form("dragon_invoice_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                clients = dots.get_clients()
                client_options = [f"{c['email']} - {c['name']}" for c in clients]
                selected_client = st.selectbox("Select Dragon", [""] + client_options)
                invoice_recipient = selected_client.split(' - ')[0] if selected_client else ""
                
                invoice_amount = st.number_input("Dragon Amount ($)", min_value=0.01, value=100.00)
            
            with col2:
                due_date = st.date_input("Dragon Due Date", min_value=datetime.now().date())
                invoice_type = st.selectbox("Dragon Invoice Type", ["Driver Payout", "Vendor Payment", "Refund", "Bonus Payment"])
                payout_method = st.selectbox("Dragon Payment Method", list(PAYOUT_METHODS.keys()))
            
            invoice_description = st.text_area("Dragon Description", placeholder="Epic dragon delivery services...")
            
            if st.form_submit_button("📄 Create Dragon Invoice"):
                if invoice_recipient and invoice_amount > 0:
                    invoice = dots.Invoice.create(
                        recipient=invoice_recipient,
                        amount=invoice_amount,
                        due_date=due_date,
                        description=invoice_description,
                        type=invoice_type,
                        payout_method=payout_method
                    )
                    
                    st.success(f"✅ Dragon Invoice {invoice['id']} created successfully!")
                else:
                    st.error("Please fill in all required dragon fields.")

def show_transaction_history():
    st.header("📊 Dragon Transaction History")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        return
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now().date() - timedelta(days=30), datetime.now().date()),
            max_value=datetime.now().date()
        )
    
    with col2:
        transaction_type = st.selectbox(
            "Transaction Type",
            ["All", "Payouts", "Invoices", "Refunds", "WooCommerce"]
        )
    
    with col3:
        status_filter = st.selectbox(
            "Status",
            ["All", "Completed", "Pending", "Failed"]
        )
    
    with col4:
        method_filter = st.selectbox(
            "Payment Method",
            ["All"] + list(PAYOUT_METHODS.keys())
        )
    
    # Mock transaction data with dragon theme
    transactions = [
        {
            "id": "txn_001",
            "date": "2024-01-15",
            "type": "Dragon Payout",
            "amount": -1250.00,
            "recipient": "Alex Dragon",
            "status": "Completed",
            "method": "🏦 Bank Transfer",
            "dragon_bonus": "🐉 Dragon Scale Protection"
        },
        {
            "id": "txn_002",
            "date": "2024-01-14",
            "type": "Dragon Invoice",
            "amount": 875.50,
            "recipient": "Jordan Fire",
            "status": "Pending",
            "method": "💳 PayPal",
            "dragon_bonus": "🔥 Fire Speed Transfer"
        },
        {
            "id": "txn_003",
            "date": "2024-01-13",
            "type": "Dragon Payout",
            "amount": -2100.75,
            "recipient": "Casey Storm",
            "status": "Completed",
            "method": "📱 Venmo",
            "dragon_bonus": "⚡ Lightning Wings"
        },
        {
            "id": "txn_004",
            "date": "2024-01-12",
            "type": "WooCommerce Sync",
            "amount": 1450.25,
            "recipient": "Auto-Sync",
            "status": "Completed",
            "method": "🛒 WooCommerce",
            "dragon_bonus": "🌐 Global Dragon Network"
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    df['amount_display'] = df['amount'].apply(lambda x: f"${abs(x):,.2f}" + (" (Out)" if x < 0 else " (In)"))
    
    # Display transactions
    st.dataframe(
        df[['id', 'date', 'type', 'amount_display', 'recipient', 'status', 'method', 'dragon_bonus']],
        column_config={
            "id": "Transaction ID",
            "date": "Date",
            "type": "Type",
            "amount_display": "Amount",
            "recipient": "Dragon Recipient",
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Completed", "Pending", "Failed"],
            ),
            "method": "Dragon Method",
            "dragon_bonus": "Dragon Bonus"
        },
        use_container_width=True
    )
    
    # Transaction summary
    st.subheader("📈 Dragon Treasury Summary")
    
    total_in = sum(t['amount'] for t in transactions if t['amount'] > 0)
    total_out = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))
    net_flow = total_in - total_out
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Dragon Treasure In", f"${total_in:,.2f}")
    
    with col2:
        st.metric("💸 Dragon Treasure Out", f"${total_out:,.2f}")
    
    with col3:
        st.metric("📊 Net Dragon Flow", f"${net_flow:,.2f}", delta=f"{net_flow:,.2f}")
    
    with col4:
        st.metric("🔥 Dragon Transactions", len(transactions))

def show_analytics():
    st.header("📊 Dragon Analytics Dashboard")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        return
    
    # Generate mock data for charts
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    daily_payouts = [abs(np.random.normal(1500, 300)) for _ in dates]
    daily_invoices = [abs(np.random.normal(800, 200)) for _ in dates]
    
    # Dragon payout trends
    st.subheader("🐉 Dragon Payout Trends")
    
    fig_payouts = go.Figure()
    fig_payouts.add_trace(go.Scatter(
        x=dates,
        y=daily_payouts,
        mode='lines+markers',
        name='Daily Dragon Payouts',
        line=dict(color='#FF6B35', width=3),
        fill='tonexty'
    ))
    
    fig_payouts.update_layout(
        title="Daily Dragon Payout Volume",
        xaxis_title="Date",
        yaxis_title="Amount ($)",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_payouts, use_container_width=True)
    
    # Dragon payment method distribution
    st.subheader("💳 Dragon Payment Method Distribution")
    
    payment_methods = list(PAYOUT_METHODS.keys())[:8]  # Top 8 methods
    method_counts = [random.randint(20, 200) for _ in payment_methods]
    
    fig_pie = px.pie(
        values=method_counts,
        names=payment_methods,
        title="Dragon Payment Methods Used",
        color_discrete_sequence=['#FF6B35', '#F7931E', '#FFB84D', '#FFC971', '#667eea', '#764ba2', '#9370DB', '#7B68EE']
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Dragon performance by level
    st.subheader("🏆 Dragon Performance by Level")
    
    dragon_levels = ["🥉 Bronze Dragon", "🥈 Silver Dragon", "🥇 Gold Dragon", "💎 Diamond Dragon", "🌟 Legendary Dragon"]
    level_earnings = [random.randint(500, 5000) for _ in dragon_levels]
    level_counts = [random.randint(5, 25) for _ in dragon_levels]
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=dragon_levels,
        y=level_earnings,
        name='Average Earnings',
        marker_color='#FF6B35'
    ))
    
    fig_bar.update_layout(
        title="Dragon Earnings by Level",
        xaxis_title="Dragon Level",
        yaxis_title="Average Earnings ($)"
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Key dragon metrics
    st.subheader("📊 Key Dragon Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🐉 Active Dragons", "247", delta="12")
    
    with col2:
        st.metric("💰 Avg Dragon Payout", "$1,245", delta="5.2%")
    
    with col3:
        st.metric("⏱️ Avg Dragon Processing", "2.3 hrs", delta="-0.5 hrs")
    
    with col4:
        st.metric("✅ Dragon Success Rate", "98.7%", delta="0.3%")
    
    # WooCommerce Integration Stats
    st.subheader("🛒 WooCommerce Dragon Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Mock WooCommerce data
        woo_dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        woo_orders = [random.randint(10, 50) for _ in woo_dates]
        
        fig_woo = go.Figure()
        fig_woo.add_trace(go.Scatter(
            x=woo_dates,
            y=woo_orders,
            mode='lines+markers',
            name='WooCommerce Orders',
            line=dict(color='#7B68EE', width=2)
        ))
        
        fig_woo.update_layout(
            title="WooCommerce Orders Synced",
            xaxis_title="Date",
            yaxis_title="Orders"
        )
        
        st.plotly_chart(fig_woo, use_container_width=True)
    
    with col2:
        # Dragon level distribution
        fig_levels = px.donut(
            values=level_counts,
            names=dragon_levels,
            title="Dragon Level Distribution",
            color_discrete_sequence=['#FFB84D', '#FFC971', '#FF6B35', '#F7931E', '#667eea']
        )
        
        st.plotly_chart(fig_levels, use_container_width=True)

if __name__ == "__main__":
    main()
