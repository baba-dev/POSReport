### Overview

The WooCommerce & POS Report Fabricator is a powerful and user-friendly Streamlit application designed to seamlessly integrate and analyze data from WooCommerce, YITH POS, Multi-Inventory, Customer Data, and COGS systems. This tool empowers business owners, analysts, and managers to generate comprehensive reports, visualize key performance indicators (KPIs), and gain actionable insights into their sales, profits, and operational efficiency.

### Features
Data Integration:

Upload and merge CSV files from WooCommerce (wp_wc_orders.csv), YITH POS (wp_wc_orders_meta.csv), and Order Addresses (wp_wc_order_addresses.csv).
Automatic preprocessing and cleaning of data for accurate analysis.
Interactive Data Preview:

Preview uploaded datasets with adjustable row counts.
Integrity checks to ensure all necessary data is available.
Comprehensive Reporting:

Generate reports with summary statistics across multiple timeframes:
Last 30 Days
Last 6 Months
Last 1 Year
All Time
Detailed breakdowns by Store, Register, and Cashier within expandable sections for each timeframe.
Visualizations:

Order Status Distribution: Visualize the distribution of order statuses.
Monthly Sales Trend: Track sales performance over time.
Cashier-wise Performance: Assess performance based on profit contributions.
Store-wise Performance: Evaluate sales across different store locations.
Data Export:

Download the combined and processed data as a CSV file for external analysis or record-keeping.
Responsive UI:

Clean and organized 2x2 grid layout for summary statistics.
Expanders to manage detailed data views without cluttering the interface.
Pagination for efficient navigation through large datasets.

### Usage
Upload Data:

Navigate to the Raw Data Upload Section.
Upload the three required CSV files:
wp_wc_orders.csv
wp_wc_orders_meta.csv
wp_wc_order_addresses.csv
Preview Data:

Use the slider to adjust the number of rows displayed in the data previews.
Verify the integrity and structure of your data.
Generate Report:

Click on the Generate Report button.
The application will process and merge the data, replacing mapped values with readable labels.
View Summary Statistics:

Explore the Summary Statistics section organized in a 2x2 grid:
Last 30 Days
Last 6 Months
Last 1 Year
All Time
Expand each section to view detailed breakdowns by Store, Register, and Cashier.
Analyze Visualizations:

Review various charts showcasing order status distributions, sales trends, and performance metrics.
Download Data:

Use the Download Combined CSV button to export the processed data for further analysis or record-keeping.
