import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import numpy as np  # Import numpy for random data generation

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
        background: linear-gradient(90deg, #FF6B35, #F7931E);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .payout-card {
        border: 2px solid #FF6B35;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: #f8f9fa;
    }
    
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .woo-sync-card {
        background: linear-gradient(135deg, #9F0DFF 0%, #29ABE2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Mock Dots SDK implementation for demo purposes
class MockDots:
    def __init__(self):
        self.client_id = None
        self.api_key = None
        self.configured = False
        self.demo_clients = self._generate_demo_clients(50)  # Generate demo clients

    def _generate_demo_clients(self, num_clients):
        clients = []
        for i in range(num_clients):
            clients.append({
                'id': f'client_{i+1}',
                'name': f'Demo Client {i+1}',
                'email': f'client{i+1}@example.com'
            })
        return clients
    
    def configure(self, client_id, api_key):
        self.client_id = client_id
        self.api_key = api_key
        self.configured = True
    
    class Invoice:
        @staticmethod
        def create(**kwargs):
            # Mock invoice creation
            return {
                'id': f'inv_{int(time.time())}',
                'amount': kwargs.get('amount', 0),
                'recipient': kwargs.get('recipient', ''),
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
        
        @staticmethod
        def list():
            # Mock invoice list
            return [
                {
                    'id': 'inv_001',
                    'amount': 1250.00,
                    'recipient': 'driver_001@dragondash.com',
                    'status': 'completed',
                    'created_at': (datetime.now() - timedelta(days=1)).isoformat()
                },
                {
                    'id': 'inv_002',
                    'amount': 875.50,
                    'recipient': 'driver_002@dragondash.com',
                    'status': 'pending',
                    'created_at': (datetime.now() - timedelta(hours=2)).isoformat()
                },
                {
                    'id': 'inv_003',
                    'amount': 2100.75,
                    'recipient': 'driver_003@dragondash.com',
                    'status': 'completed',
                    'created_at': (datetime.now() - timedelta(days=3)).isoformat()
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
                'created_at': datetime.now().isoformat()
            }
        
        @staticmethod
        def get_balance():
            return {
                'available': 15750.25,
                'pending': 3250.50,
                'total': 19000.75
            }

# Initialize mock Dots SDK
dots = MockDots()

# Define payout methods with themed values
payout_methods = {
    "Bank Transfer": {"icon": "🏦", "fee": 0.50, "processing_time": "1-3 business days"},
    "PayPal": {"icon": "💸", "fee": 0.75, "processing_time": "Instant"},
    "Venmo": {"icon": "📱", "fee": 0.60, "processing_time": "Instant"},
    "Cash App": {"icon": "💵", "fee": 0.65, "processing_time": "Instant"},
    "DragonPay": {"icon": "🐉", "fee": 0.25, "processing_time": "1 business day"}
}

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🐉 Dragon Dash Payout Center</h1>
        <p>Manage driver payouts and financial operations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Configuration
        with st.expander("Dots API Configuration", expanded=not dots.configured):
            if dots.configured:
                st.success("✅ API Configured Successfully!")
                st.write(f"Client ID: `{dots.client_id}`")
                st.write("API Key: `********`")  # Mask the API key
            else:
                st.warning("⚠️ API not configured. Please enter your credentials.")

            client_id = st.text_input(
                "Client ID",
                value=dots.client_id if dots.configured else "pk_dev_...",
                help="Your Dots API Client ID from Developer Dashboard",
                disabled=dots.configured
            )
            api_key = st.text_input(
                "API Key",
                value="",  # Do not display the API key if already configured
                type="password",
                help="Your Dots API Key from Developer Dashboard",
                disabled=dots.configured
            )

            if not dots.configured and st.button("Configure API"):
                if client_id and api_key:
                    dots.configure(client_id, api_key)
                    st.rerun()
                else:
                    st.error("❌ Please provide both Client ID and API Key")

            if not dots.configured:
                st.info("💡 Using demo clients. Configure API for full functionality.")

        # WooCommerce Sync
        with st.expander("WooCommerce Sync", expanded=False):
            st.markdown("""
            <div class="woo-sync-card">
                <h3>🔄 Sync with WooCommerce</h3>
                <p>Connect your WooCommerce store to automate payouts.</p>
            </div>
            """, unsafe_allow_html=True)

            woo_api_url = st.text_input("WooCommerce API URL", placeholder="https://yourstore.com/wp-json/wc/v3")
            woo_api_key = st.text_input("WooCommerce API Key", type="password")
            woo_api_secret = st.text_input("WooCommerce API Secret", type="password")

            if st.button("Connect to WooCommerce"):
                if woo_api_url and woo_api_key and woo_api_secret:
                    st.success("✅ Successfully connected to WooCommerce!")
                else:
                    st.error("❌ Please provide all WooCommerce API credentials.")
        
        # Navigation
        st.header("📊 Navigation")
        page = st.selectbox(
            "Select Page",
            ["Dashboard", "Create Payout", "Invoice Management", "Transaction History", "Analytics"]
        )
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Create Payout":
        show_create_payout()
    elif page == "Invoice Management":
        show_invoice_management()
    elif page == "Transaction History":
        show_transaction_history()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    st.header("📊 Dashboard Overview")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        st.info("Using demo clients. Configure API for full functionality.")
    
    # Balance Overview
    balance = dots.Payout.get_balance()
    
    col1, col2, col3 = st.columns(3)
    
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
    
    # Recent Activity
    st.subheader("🔄 Recent Activity")
    
    # Mock recent activity data
    recent_activity = [
        {"time": "2 hours ago", "action": "Payout Created", "amount": "$875.50", "driver": "Driver #002"},
        {"time": "1 day ago", "action": "Payout Completed", "amount": "$1,250.00", "driver": "Driver #001"},
        {"time": "2 days ago", "action": "Invoice Generated", "amount": "$2,100.75", "driver": "Driver #003"},
        {"time": "3 days ago", "action": "Payout Processing", "amount": "$650.25", "driver": "Driver #004"},
    ]
    
    for activity in recent_activity:
        st.markdown(f"""
        <div class="payout-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{activity['action']}</strong><br>
                    <small>{activity['time']} • {activity['driver']}</small>
                </div>
                <div style="text-align: right;">
                    <strong style="color: #FF6B35;">{activity['amount']}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💸 Create New Payout", use_container_width=True):
            st.session_state.page = "Create Payout"
            st.rerun()
    
    with col2:
        if st.button("📄 Generate Invoice", use_container_width=True):
            st.session_state.page = "Invoice Management"
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.page = "Analytics"
            st.rerun()

def show_create_payout():
    st.header("💸 Create New Payout")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        st.info("Using demo clients. Configure API for full functionality.")
    
    with st.form("payout_form"):
        st.subheader("Payout Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            recipient_email = st.text_input(
                "Recipient Email",
                placeholder="driver@dragondash.com"
            )
            
            payout_amount = st.number_input(
                "Payout Amount ($)",
                min_value=0.01,
                value=100.00,
                step=0.01
            )
        
        with col2:
            payout_method_name = st.selectbox(
                "Payout Method",
                options=list(payout_methods.keys())
            )
            payout_method = payout_methods[payout_method_name]

            st.write(f"**Selected Method:** {payout_method_name} {payout_method['icon']}")
            st.write(f"**Fee:** ${payout_method['fee']:.2f}")
            st.write(f"**Processing Time:** {payout_method['processing_time']}")
            
            priority = st.selectbox(
                "Priority",
                ["Standard", "Express", "Instant"]
            )
        
        description = st.text_area(
            "Description (Optional)",
            placeholder="Weekly driver payout for deliveries..."
        )
        
        # Payout schedule
        st.subheader("Schedule")
        schedule_type = st.radio(
            "When to process this payout?",
            ["Immediate", "Scheduled"]
        )
        
        scheduled_date = None
        if schedule_type == "Scheduled":
            scheduled_date = st.date_input(
                "Schedule Date",
                min_value=datetime.now().date()
            )
        
        submitted = st.form_submit_button("🚀 Create Payout", use_container_width=True)
        
        if submitted:
            if recipient_email and payout_amount > 0:
                try:
                    # Create payout using Dots SDK
                    payout = dots.Payout.create(
                        recipient=recipient_email,
                        amount=payout_amount,
                        method=payout_method_name,
                        priority=priority,
                        description=description,
                        scheduled_date=scheduled_date
                    )
                    
                    st.markdown(f"""
                    <div class="success-message">
                        <h4>✅ Payout Created Successfully!</h4>
                        <p><strong>Payout ID:</strong> {payout['id']}</p>
                        <p><strong>Amount:</strong> ${payout['amount']:,.2f}</p>
                        <p><strong>Status:</strong> {payout['status'].title()}</p>
                        <p><strong>Recipient:</strong> {payout['recipient']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        <h4>❌ Error Creating Payout</h4>
                        <p>{str(e)}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please fill in all required fields.")

def show_invoice_management():
    st.header("📄 Invoice Management")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        st.info("Using demo clients. Configure API for full functionality.")
    
    tab1, tab2 = st.tabs(["📋 View Invoices", "➕ Create Invoice"])
    
    with tab1:
        st.subheader("Recent Invoices")
        
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
                "recipient": "Recipient",
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["pending", "completed", "failed"],
                ),
                "created_at": "Created At"
            },
            use_container_width=True
        )
        
        # Invoice actions
        st.subheader("Invoice Actions")
        selected_invoice = st.selectbox(
            "Select Invoice for Actions",
            options=[inv['id'] for inv in invoices],
            format_func=lambda x: f"{x} - {next(inv['recipient'] for inv in invoices if inv['id'] == x)}"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📧 Send Reminder"):
                st.success(f"Reminder sent for invoice {selected_invoice}")
        
        with col2:
            if st.button("❌ Cancel Invoice"):
                st.warning(f"Invoice {selected_invoice} cancelled")
        
        with col3:
            if st.button("🔄 Resend Invoice"):
                st.info(f"Invoice {selected_invoice} resent")
    
    with tab2:
        st.subheader("Create New Invoice")
        
        with st.form("invoice_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                invoice_recipient = st.text_input("Recipient Email")
                invoice_amount = st.number_input("Amount ($)", min_value=0.01, value=100.00)
            
            with col2:
                due_date = st.date_input("Due Date", min_value=datetime.now().date())
                invoice_type = st.selectbox("Invoice Type", ["Driver Payout", "Vendor Payment", "Refund"])
            
            invoice_description = st.text_area("Description")
            
            if st.form_submit_button("📄 Create Invoice"):
                if invoice_recipient and invoice_amount > 0:
                    invoice = dots.Invoice.create(
                        recipient=invoice_recipient,
                        amount=invoice_amount,
                        due_date=due_date,
                        description=invoice_description,
                        type=invoice_type
                    )
                    
                    st.success(f"✅ Invoice {invoice['id']} created successfully!")
                else:
                    st.error("Please fill in all required fields.")

def show_transaction_history():
    st.header("📊 Transaction History")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        st.info("Using demo clients. Configure API for full functionality.")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now().date() - timedelta(days=30), datetime.now().date()),
            max_value=datetime.now().date()
        )
    
    with col2:
        transaction_type = st.selectbox(
            "Transaction Type",
            ["All", "Payouts", "Invoices", "Refunds"]
        )
    
    with col3:
        status_filter = st.selectbox(
            "Status",
            ["All", "Completed", "Pending", "Failed"]
        )
    
    # Mock transaction data
    transactions = [
        {
            "id": "txn_001",
            "date": "2024-01-15",
            "type": "Payout",
            "amount": -1250.00,
            "recipient": "driver_001@dragondash.com",
            "status": "Completed",
            "method": "Bank Transfer"
        },
        {
            "id": "txn_002",
            "date": "2024-01-14",
            "type": "Invoice",
            "amount": 875.50,
            "recipient": "driver_002@dragondash.com",
            "status": "Pending",
            "method": "PayPal"
        },
        {
            "id": "txn_003",
            "date": "2024-01-13",
            "type": "Payout",
            "amount": -2100.75,
            "recipient": "driver_003@dragondash.com",
            "status": "Completed",
            "method": "Venmo"
        },
        {
            "id": "txn_004",
            "date": "2024-01-12",
            "type": "Refund",
            "amount": 45.25,
            "recipient": "customer@email.com",
            "status": "Failed",
            "method": "Credit Card"
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    df['amount_display'] = df['amount'].apply(lambda x: f"${abs(x):,.2f}" + (" (Out)" if x < 0 else " (In)"))
    
    # Display transactions
    st.dataframe(
        df[['id', 'date', 'type', 'amount_display', 'recipient', 'status', 'method']],
        column_config={
            "id": "Transaction ID",
            "date": "Date",
            "type": "Type",
            "amount_display": "Amount",
            "recipient": "Recipient",
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Completed", "Pending", "Failed"],
            ),
            "method": "Method"
        },
        use_container_width=True
    )
    
    # Transaction summary
    st.subheader("📈 Summary")
    
    total_in = sum(t['amount'] for t in transactions if t['amount'] > 0)
    total_out = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))
    net_flow = total_in - total_out
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Total In", f"${total_in:,.2f}")
    
    with col2:
        st.metric("💸 Total Out", f"${total_out:,.2f}")
    
    with col3:
        st.metric("📊 Net Flow", f"${net_flow:,.2f}", delta=f"{net_flow:,.2f}")

def show_analytics():
    st.header("📊 Analytics Dashboard")
    
    if not dots.configured:
        st.warning("⚠️ Please configure your Dots API credentials in the sidebar first.")
        st.info("Using demo clients. Configure API for full functionality.")
    
    # Generate mock data for charts
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    daily_payouts = [abs(np.random.normal(1500, 300)) for _ in dates]
    daily_invoices = [abs(np.random.normal(800, 200)) for _ in dates]
    
    # Payout trends
    st.subheader("💸 Payout Trends")
    
    fig_payouts = go.Figure()
    fig_payouts.add_trace(go.Scatter(
        x=dates,
        y=daily_payouts,
        mode='lines+markers',
        name='Daily Payouts',
        line=dict(color='#FF6B35', width=3)
    ))
    
    fig_payouts.update_layout(
        title="Daily Payout Volume",
        xaxis_title="Date",
        yaxis_title="Amount ($)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_payouts, use_container_width=True)
    
    # Payment method distribution
    st.subheader("💳 Payment Method Distribution")
    
    payment_methods = ['Bank Transfer', 'PayPal', 'Venmo', 'Cash App']
    method_counts = [45, 30, 15, 10]
    
    fig_pie = px.pie(
        values=method_counts,
        names=payment_methods,
        title="Payment Methods Used",
        color_discrete_sequence=['#FF6B35', '#F7931E', '#FFB84D', '#FFC971']
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Driver performance
    st.subheader("🏆 Top Drivers by Earnings")
    
    drivers_data = {
        'Driver': ['Driver #001', 'Driver #002', 'Driver #003', 'Driver #004', 'Driver #005'],
        'Earnings': [3250.75, 2890.50, 2650.25, 2100.00, 1875.80],
        'Deliveries': [145, 132, 118, 95, 87]
    }
    
    df_drivers = pd.DataFrame(drivers_data)
    
    fig_bar = px.bar(
        df_drivers,
        x='Driver',
        y='Earnings',
        title="Top Driver Earnings This Month",
        color='Earnings',
        color_continuous_scale='Oranges'
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Key metrics
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚗 Active Drivers", "247", delta="12")
    
    with col2:
        st.metric("💰 Avg Payout", "$1,245", delta="5.2%")
    
    with col3:
        st.metric("⏱️ Avg Processing Time", "2.3 hrs", delta="-0.5 hrs")
    
    with col4:
        st.metric("✅ Success Rate", "98.7%", delta="0.3%")

if __name__ == "__main__":
    main()

