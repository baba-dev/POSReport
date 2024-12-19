import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="WooCommerce & POS Report Fabricator", layout='wide')

# Header Section
st.image("logo.png")
st.header("Welcome to Vitamin Point of Sale Report Fabricator")
st.text("This tool allows you to fabricate a thorough report for WooCommerce, YITH POS, Multi-Inventory, Customer Data & COGS System.")
st.subheader("", divider="rainbow")
# Helpbox
with st.expander("Helpbox", expanded=False):
    st.write("Export the following tables from your database:")
    st.markdown("""
    - [wp_wc_orders](https://vitaminphones.com/phpmyadmin/index.php?route=/table/export&db=vitaminphones_wp&table=wp_wc_orders&single_table=true)
    - [wp_wc_orders_meta](https://vitaminphones.com/phpmyadmin/index.php?route=/table/export&db=vitaminphones_wp&table=wp_wc_orders_meta&single_table=true)
    - [wp_wc_order_addresses](https://vitaminphones.com/phpmyadmin/index.php?route=/table/export&db=vitaminphones_wp&table=wp_wc_order_addresses&single_table=true)
    """)

# Raw Data Upload Section
st.subheader("Raw Data Upload Section")
st.write("Upload the three CSV files exported from your database.")

button_col1, button_col2, button_col3 = st.columns(3)

with button_col1:
    st.write("**wp_wc_orders.csv**")
    orders_file = st.file_uploader("Upload Order Main Data (wp_wc_orders)", type='csv')

with button_col2:
    st.write("**wp_wc_orders_meta.csv**")
    orders_meta_file = st.file_uploader("Upload Order Meta Data (wp_wc_orders_meta)", type='csv')

with button_col3:
    st.write("**wp_wc_order_addresses.csv**")
    orders_addr_file = st.file_uploader("Upload Order Addresses Data (wp_wc_order_addresses)", type='csv')

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

df_orders = pd.DataFrame()
df_meta = pd.DataFrame()
df_address = pd.DataFrame()

if orders_file is not None:
    df_orders = load_csv(orders_file)
if orders_meta_file is not None:
    df_meta = load_csv(orders_meta_file)
if orders_addr_file is not None:
    df_address = load_csv(orders_addr_file)

# Add a slider to control preview rows
preview_rows = st.slider("Number of rows to preview:", min_value=5, max_value=50, value=20)

st.subheader("Integrity Checks & Data Preview")
st.divider()

if not df_orders.empty and not df_meta.empty and not df_address.empty:
    preview_tabs = st.tabs(["Orders Preview", "Meta Preview", "Addresses Preview"])
    with preview_tabs[0]:
        st.write(df_orders.head(preview_rows))
    with preview_tabs[1]:
        st.write(df_meta.head(preview_rows))
    with preview_tabs[2]:
        st.write(df_address.head(preview_rows))
else:
    st.warning("Please upload all three datasets for a full preview.")

def preprocess_orders(df):
    if 'date_created_gmt' in df.columns:
        df['date_created_gmt'] = pd.to_datetime(df['date_created_gmt'], errors='coerce')
    # Convert numeric columns
    numeric_cols = ['tax_amount', 'total_amount']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def preprocess_meta(df):
    # Pivot meta data
    df_pivot = df.pivot(index='order_id', columns='meta_key', values='meta_value').reset_index()
    # Attempt numeric conversion on meta_values
    for c in df_pivot.columns:
        if c not in ['order_id']:
            df_pivot[c] = pd.to_numeric(df_pivot[c], errors='ignore')
    return df_pivot

def preprocess_address(df):
    # Pivot address by address_type
    df_pivot = df.pivot(index='order_id', columns='address_type')
    df_pivot.columns = ['_'.join(col).strip() for col in df_pivot.columns.values]
    df_pivot = df_pivot.reset_index()
    return df_pivot

# Check if we already have a merged_df in session state
if 'merged_df' not in st.session_state:
    # Only show "Generate Report" button if all files are available
    if (orders_file is not None) and (orders_meta_file is not None) and (orders_addr_file is not None):
        if st.button("Generate Report"):
            df_orders_clean = preprocess_orders(df_orders)
            df_meta_clean = preprocess_meta(df_meta)
            df_address_clean = preprocess_address(df_address)

            main_cols = [
                "id","status","currency","type","tax_amount","total_amount","customer_id",
                "billing_email","date_created_gmt","payment_method","payment_method_title",
                "transaction_id","customer_note"
            ]
            missing_cols = [c for c in main_cols if c not in df_orders_clean.columns]
            if missing_cols:
                st.error(f"The following required columns are missing from wp_wc_orders: {missing_cols}")
            else:
                df_orders_main = df_orders_clean[main_cols].copy()

                merged_df = pd.merge(df_orders_main, df_meta_clean, left_on='id', right_on='order_id', how='left')
                merged_df = pd.merge(merged_df, df_address_clean, left_on='id', right_on='order_id', how='left')

                # Remove redundant ID columns
                for col in ['order_id_x', 'order_id_y', 'order_id']:
                    if col in merged_df.columns and col != 'id':
                        merged_df.drop(col, axis=1, inplace=True)

                columns_to_drop = [
                    "tax_amount", "customer_id", "billing_email", "transaction_id", "_alg_wc_cog_order_item_cost",
                    "_billing_address_index", "_billing_vat", "_edit_local", "_refund_amount", "_refund_reson",
                    "_refunded_by", "_refunded_payment", "_shipping_addres_index", "_yith_pos_change",
                    "_yith_pos_gateway_bacs", "_yith_pos_gateway_cheque", "_yith_pos_gateway_yith_pos_cash_gateway",
                    "_yith_Pos_gateway_yith_pos_chip_pin_gateway", "_yith_pos_order", "id_billing", "id_shipping",
                    "first_name_shipping", "last_name_shipping", "company_billing", "company_shipping",
                    "address_1_shipping", "address_2_billing", "address_2_shipping", "city_billing", "city_shipping",
                    "state_billing", "state_shipping", "postcode_billing", "country_billing", "email_shipping",
                    "phone_shipping", "_refund_reason", "_alg_wc_cog_order_profit_percent", "_alg_wc_cog_order_cost",
                    "_edit_lock", "_shipping_address_index", "_yith_pos_gateway_yith_pos_chip_pin_gateway",
                    "address_1_billing", "postcode_shipping", "country_shipping", "type", "payment_method", "total_amount"
                ]
                merged_df.drop(columns=[c for c in columns_to_drop if c in merged_df.columns], inplace=True, errors='ignore')

                # Replace status values
                status_map = {
                    "wc-completed": "Order Complete",
                    "wc-refunded": "Order Refunded",
                    "wc-cancelled": "Order Cancelled"
                }
                if 'status' in merged_df.columns:
                    merged_df['status'] = merged_df['status'].replace(status_map)

                # Replace _yith_pos_register values
                register_map = {
                    22: "Register #1",
                    165: "Register #1",
                    23: "Register #2",
                    166: "Register #2"
                }
                if '_yith_pos_register' in merged_df.columns:
                    merged_df['_yith_pos_register'] = merged_df['_yith_pos_register'].replace(register_map)

                # Replace _yith_pos_store values
                store_map = {
                    21: "Muscat Branch",
                    164: "Sohar Branch"
                }
                if '_yith_pos_store' in merged_df.columns:
                    merged_df['_yith_pos_store'] = merged_df['_yith_pos_store'].replace(store_map)

                # Replace _yith_pos_cashier values with a default for unmapped IDs
                cashier_map = {
                    1: "Sameer Siddiqui",
                    2: "Mahmood Al Ajmi",
                    4: "Mohamed Hasir",
                    6: "Sohar Cashier #1",
                    11: "Almonther Alshibli",
                    12: "Mohamed Ajmal"
                }
                if '_yith_pos_cashier' in merged_df.columns:
                    merged_df['_yith_pos_cashier'] = merged_df['_yith_pos_cashier'].map(cashier_map)

                # Format numeric columns
                three_decimal_cols = ['_alg_wc_cog_order_items_cost', '_alg_wc_cog_order_price', '_alg_wc_cog_order_profit']
                for col in three_decimal_cols:
                    if col in merged_df.columns:
                        merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')
                        merged_df[col] = merged_df[col].apply(lambda x: f"OMR {x:.3f}" if pd.notnull(x) else x)

                if '_alg_wc_cog_order_profit_margin' in merged_df.columns:
                    merged_df['_alg_wc_cog_order_profit_margin'] = pd.to_numeric(merged_df['_alg_wc_cog_order_profit_margin'], errors='coerce')
                    merged_df['_alg_wc_cog_order_profit_margin'] = merged_df['_alg_wc_cog_order_profit_margin'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else x)

                # Rename columns as requested
                rename_map = {
                    'id': 'Order ID',
                    'status': 'Order Status',
                    'date_created_gmt': 'Order Date',
                    'payment_method_title': 'Payment Method',
                    'customer_note': 'Purchase Note',
                    '_alg_wc_cog_order_items_cost': 'Cost of Goods',
                    '_alg_wc_cog_order_price': 'Selling Price',
                    '_alg_wc_cog_order_profit': 'Profit (OMR)',
                    '_alg_wc_cog_order_profit_margin': 'Profit (%)',
                    '_yith_pos_cashier': "Cashier Name",
                    '_yith_pos_register': 'POS Register',
                    'first_name_billing': 'Customer FName',
                    'last_name_billing': 'Customer LName',
                    'email_billing': 'Customer Email',
                    '_yith_pos_store': 'POS Store',
                    'phone_billing': 'Customer Phone'
                }
                merged_df.rename(columns=rename_map, inplace=True)

                desired_order = [
                    'Order ID', 'Order Status', 'Order Date',
                    "Cashier Name", 'POS Register', 'POS Store',
                    'Cost of Goods', 'Selling Price', 'Profit (OMR)', 'Profit (%)',
                    'Customer FName', 'Customer LName', 'Customer Email',
                    'Customer Phone', 'Purchase Note'
                ]
                final_columns = [col for col in desired_order if col in merged_df.columns]
                merged_df = merged_df[final_columns]

                # Store in session state
                st.session_state["merged_df"] = merged_df
                st.session_state["df_orders_main"] = df_orders_main

# If merged_df is in session state, display it and show stats
if "merged_df" in st.session_state:
    merged_df = st.session_state["merged_df"]
    df_orders_main = st.session_state["df_orders_main"]

    # Convert Order Date to datetime properly
    # Assuming format "dd-mm-yyyy HH:MM"
    merged_df['Order Date'] = pd.to_datetime(merged_df['Order Date'], format="%d-%m-%Y %H:%M", errors='coerce')

    # Pagination
    rows_per_page = 10
    total_rows = len(merged_df)
    total_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page > 0 else 0)
    page_num = st.number_input("Page number", min_value=1, max_value=max(total_pages, 1), value=1)
    start = (page_num - 1) * rows_per_page
    end = start + rows_per_page
    page_data = merged_df.iloc[start:end]

    def alternate_row_colors(row):
        return ['background-color: #f9f9f9' if row.name % 2 else 'background-color: #ffffff' for _ in row]

    styled = (
        page_data.style
        .apply(alternate_row_colors, axis=1)
        .set_table_styles([
            {'selector': 'th',
             'props': [('background-color', '#4F81BD'),
                       ('color', 'black'),
                       ('font-weight', 'bold'),
                       ('text-align', 'center')]}
        ], overwrite=False)
        .set_properties(**{'color':'black'})
        .hide(axis='index')
    )

    st.markdown(styled.to_html(), unsafe_allow_html=True)

    # Download button
    csv_buffer = io.StringIO()
    merged_df.drop(columns=['Profit (OMR)_num', 'Selling Price_num'], errors='ignore').to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download Combined CSV",
        data=csv_buffer.getvalue(),
        file_name="combined_woocommerce_data.csv",
        mime="text/csv"
    )


    # Helper functions to strip "OMR " from numeric fields
    def omr_to_float(val):
        if isinstance(val, str) and val.startswith("OMR"):
            return float(val.replace("OMR", "").strip())
        return pd.to_numeric(val, errors='coerce')

    merged_df['Profit (OMR)_num'] = merged_df['Profit (OMR)'].apply(omr_to_float)
    merged_df['Selling Price_num'] = merged_df['Selling Price'].apply(omr_to_float)

    now = pd.Timestamp.now()
    last_30_days = now - pd.Timedelta(days=30)
    last_6_months = now - pd.DateOffset(months=6)
    last_1_year = now - pd.DateOffset(years=1)

    def compute_stats(df):
        total_orders = df['Order ID'].nunique()
        total_sales = df['Selling Price_num'].sum()
        total_profit = df['Profit (OMR)_num'].sum()
        cancellations = df['Order Status'].isin(['Order Cancelled', 'Order Refunded']).sum()

        # Detailed summaries
        store_summary = df.groupby('POS Store').agg(
            Number_of_Orders=('Order ID', 'nunique'),
            Total_Sales=('Selling Price_num', 'sum'),
            Total_Profit=('Profit (OMR)_num', 'sum'),
            Cancellations=('Order Status', lambda x: x.isin(['Order Cancelled', 'Order Refunded']).sum())
        ).to_dict('index') if 'POS Store' in df.columns else {}

        register_summary = df.groupby('POS Register').agg(
            Number_of_Orders=('Order ID', 'nunique'),
            Total_Sales=('Selling Price_num', 'sum'),
            Total_Profit=('Profit (OMR)_num', 'sum'),
            Cancellations=('Order Status', lambda x: x.isin(['Order Cancelled', 'Order Refunded']).sum())
        ).to_dict('index') if 'POS Register' in df.columns else {}

        cashier_summary = df.groupby("Cashier Name").agg(
            Number_of_Orders=('Order ID', 'nunique'),
            Total_Sales=('Selling Price_num', 'sum'),
            Total_Profit=('Profit (OMR)_num', 'sum'),
            Cancellations=('Order Status', lambda x: x.isin(['Order Cancelled', 'Order Refunded']).sum())
        ).to_dict('index') if "Cashier Name" in df.columns else {}

        return {
            'orders': total_orders,
            'sales': total_sales,
            'profit': total_profit,
            'cancellations': cancellations,
            'store_summary': store_summary,
            'register_summary': register_summary,
            'cashier_summary': cashier_summary
        }

    # Filtered DataFrames
    df_30d = merged_df[merged_df['Order Date'] >= last_30_days]
    df_6m = merged_df[merged_df['Order Date'] >= last_6_months]
    df_1y = merged_df[merged_df['Order Date'] >= last_1_year]
    df_all = merged_df.copy()

    stats_30d = compute_stats(df_30d)
    stats_6m = compute_stats(df_6m)
    stats_1y = compute_stats(df_1y)
    stats_all = compute_stats(df_all)

    # Summary Statistics Section (Updated with 2x2 Grid and Expanders)
    st.subheader("Summary Statistics", divider="rainbow")

    # Define the time periods and their corresponding stats
    time_periods = {
        "Last 30 Days": stats_30d,
        "Last 6 Months": stats_6m,
        "Last 1 Year": stats_1y,
        "All Time": stats_all
    }

    # Create a 2x2 grid layout
    with st.container():
        # First Row
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            period = "Last 30 Days"
            stats = time_periods[period]
            st.subheader(period, divider="rainbow")
            i1, i2 = st.columns(2)
            with i1:
                st.write(f"**Number of Orders:** {stats['orders']}")
                st.write(f"**Total Sales (OMR):** {stats['sales']:.3f}")
            with i2:
                st.write(f"**Total Profit (OMR):** {stats['profit']:.3f}")
                st.write(f"**Cancellations/Refunds:** {stats['cancellations']}")

            # Expanders for Detailed Breakdown
            with st.expander("Detailed Breakdown"):
                # Breakdown by Store
                if stats['store_summary']:
                    st.write("#### By Store:")
                    store_data = {
                        "Store": list(stats['store_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['store_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['store_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['store_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['store_summary'].values()]
                    }
                    df_store = pd.DataFrame(store_data)
                    st.write(df_store)

                # Breakdown by Register
                if stats['register_summary']:
                    st.write("#### By Register:")
                    register_data = {
                        "Register": list(stats['register_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['register_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['register_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['register_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['register_summary'].values()]
                    }
                    df_register = pd.DataFrame(register_data)
                    st.write(df_register)

                # Breakdown by Cashier
                if stats['cashier_summary']:
                    st.write("#### By Cashier:")
                    cashier_data = {
                        "Cashier": list(stats['cashier_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['cashier_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['cashier_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['cashier_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['cashier_summary'].values()]
                    }
                    # Ensure all lists are of the same length
                    if len(set(len(lst) for lst in cashier_data.values())) == 1:
                        df_cashier = pd.DataFrame(cashier_data)
                        st.write(df_cashier)
                    else:
                        st.error("Mismatch in lengths of cashier summary data.")

        with row1_col2:
            period = "Last 6 Months"
            stats = time_periods[period]
            st.subheader(period, divider="rainbow")
            i1, i2 = st.columns(2)
            with i1:            
                st.write(f"**Number of Orders:** {stats['orders']}")
                st.write(f"**Total Sales (OMR):** {stats['sales']:.3f}")
            with i2:
                st.write(f"**Total Profit (OMR):** {stats['profit']:.3f}")
                st.write(f"**Cancellations/Refunds:** {stats['cancellations']}")

            # Expanders for Detailed Breakdown
            with st.expander("Detailed Breakdown"):
                # Breakdown by Store
                if stats['store_summary']:
                    st.write("#### By Store:")
                    store_data = {
                        "Store": list(stats['store_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['store_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['store_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['store_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['store_summary'].values()]
                    }
                    df_store = pd.DataFrame(store_data)
                    st.write(df_store)

                # Breakdown by Register
                if stats['register_summary']:
                    st.write("#### By Register:")
                    register_data = {
                        "Register": list(stats['register_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['register_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['register_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['register_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['register_summary'].values()]
                    }
                    df_register = pd.DataFrame(register_data)
                    st.write(df_register)

                # Breakdown by Cashier
                if stats['cashier_summary']:
                    st.write("#### By Cashier:")
                    cashier_data = {
                        "Cashier": list(stats['cashier_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['cashier_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['cashier_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['cashier_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['cashier_summary'].values()]
                    }
                    # Ensure all lists are of the same length
                    if len(set(len(lst) for lst in cashier_data.values())) == 1:
                        df_cashier = pd.DataFrame(cashier_data)
                        st.write(df_cashier)
                    else:
                        st.error("Mismatch in lengths of cashier summary data.")

        # Second Row
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            period = "Last 1 Year"
            stats = time_periods[period]
            st.subheader(period, divider="rainbow")
            i1, i2 = st.columns(2)
            with i1:            
                st.write(f"**Number of Orders:** {stats['orders']}")
                st.write(f"**Total Sales (OMR):** {stats['sales']:.3f}")
            with i2:
                st.write(f"**Total Profit (OMR):** {stats['profit']:.3f}")
                st.write(f"**Cancellations/Refunds:** {stats['cancellations']}")

            # Expanders for Detailed Breakdown
            with st.expander("Detailed Breakdown"):
                # Breakdown by Store
                if stats['store_summary']:
                    st.write("#### By Store:")
                    store_data = {
                        "Store": list(stats['store_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['store_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['store_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['store_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['store_summary'].values()]
                    }
                    df_store = pd.DataFrame(store_data)
                    st.write(df_store)

                # Breakdown by Register
                if stats['register_summary']:
                    st.write("#### By Register:")
                    register_data = {
                        "Register": list(stats['register_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['register_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['register_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['register_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['register_summary'].values()]
                    }
                    df_register = pd.DataFrame(register_data)
                    st.write(df_register)

                # Breakdown by Cashier
                if stats['cashier_summary']:
                    st.write("#### By Cashier:")
                    cashier_data = {
                        "Cashier": list(stats['cashier_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['cashier_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['cashier_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['cashier_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['cashier_summary'].values()]
                    }
                    # Ensure all lists are of the same length
                    if len(set(len(lst) for lst in cashier_data.values())) == 1:
                        df_cashier = pd.DataFrame(cashier_data)
                        st.write(df_cashier)
                    else:
                        st.error("Mismatch in lengths of cashier summary data.")

        with row2_col2:
            period = "All Time"
            stats = time_periods[period]
            st.subheader(period, divider="rainbow")
            i1, i2 = st.columns(2)
            with i1:
                st.write(f"**Number of Orders:** {stats['orders']}")
                st.write(f"**Total Sales (OMR):** {stats['sales']:.3f}")
            with i2:
                st.write(f"**Total Profit (OMR):** {stats['profit']:.3f}")
                st.write(f"**Cancellations/Refunds:** {stats['cancellations']}")

            # Expanders for Detailed Breakdown
            with st.expander("Detailed Breakdown"):
                # Breakdown by Store
                if stats['store_summary']:
                    st.write("#### By Store:")
                    store_data = {
                        "Store": list(stats['store_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['store_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['store_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['store_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['store_summary'].values()]
                    }
                    df_store = pd.DataFrame(store_data)
                    st.write(df_store)

                # Breakdown by Register
                if stats['register_summary']:
                    st.write("#### By Register:")
                    register_data = {
                        "Register": list(stats['register_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['register_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['register_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['register_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['register_summary'].values()]
                    }
                    df_register = pd.DataFrame(register_data)
                    st.write(df_register)

                # Breakdown by Cashier
                if stats['cashier_summary']:
                    st.write("#### By Cashier:")
                    cashier_data = {
                        "Cashier": list(stats['cashier_summary'].keys()),
                        "Number of Orders": [v['Number_of_Orders'] for v in stats['cashier_summary'].values()],
                        "Total Sales (OMR)": [f"{v['Total_Sales']:.3f}" for v in stats['cashier_summary'].values()],
                        "Total Profit (OMR)": [f"{v['Total_Profit']:.3f}" for v in stats['cashier_summary'].values()],
                        "Cancellations": [v['Cancellations'] for v in stats['cashier_summary'].values()]
                    }
                    # Ensure all lists are of the same length
                    if len(set(len(lst) for lst in cashier_data.values())) == 1:
                        df_cashier = pd.DataFrame(cashier_data)
                        st.write(df_cashier)
                    else:
                        st.error("Mismatch in lengths of cashier summary data.")

    # Separator for clarity
    st.markdown("---")

    # ---- Additional KPIs and Visualizations ----
    st.subheader("Key Performance Indicators & Visualizations", divider="rainbow")

    vis1, vis2 = st.columns(2)
    with vis1:
        # Order Status Distribution
        if 'Order Status' in merged_df.columns:
            st.write("### Order Status Distribution (All Time)")
            status_counts = merged_df['Order Status'].value_counts()
            st.bar_chart(status_counts)
        
        # Cashier-wise Performance
        st.write("### Cashier Wise Performance Profit/All Time")
        if "Cashier Name" in merged_df.columns:
            cashier_perf = (
                merged_df.groupby("Cashier Name")['Profit (OMR)_num'].sum().sort_values(ascending=False)
            )
            st.bar_chart(cashier_perf)


    with vis2:

        # Sales over Month
        st.write("### Monthly Sales Trend")
        if 'Order Date' in merged_df.columns:
            monthly_sales = (
                merged_df.groupby(merged_df['Order Date'].dt.to_period('M'))['Selling Price_num'].sum()
                .rename("Total Sales")
                .reset_index()
            )
            monthly_sales['Order Date'] = monthly_sales['Order Date'].dt.to_timestamp()
            st.line_chart(monthly_sales.set_index('Order Date')['Total Sales'])

        # Store-wise Performance
        st.write("### Store Wise Performance (By Total Sales/All Time)")
        if 'POS Store' in merged_df.columns:
            store_perf = (
                merged_df.groupby('POS Store')['Selling Price_num'].sum().sort_values(ascending=False)
            )
            st.bar_chart(store_perf)