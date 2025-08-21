Food Waste Management System
A Streamlit-based web application designed to manage food waste by facilitating the donation and claiming of surplus food. The app provides a dashboard for CRUD operations, data analysis, trend visualization, and provider contact management, leveraging SQLite for data storage and Plotly for interactive visualizations.
Features

CRUD Operations: Add, update, delete, and search records for providers, receivers, food listings, and claims.
Predefined Queries: Run 13 predefined SQL queries to analyze data, such as provider/receiver counts by city, most claimed food types, and expiring listings.
Trend Analysis: Visualize food quantity by type, listings by city, and expiring listings using bar charts and data tables.
Reports: Generate summary reports on total food quantity per provider, most claimed food items, and listings expiring soon.
Filtering: Filter food listings by city, provider, food type, or meal type for targeted insights.
Contacts: View provider contact details, filterable by city.
Responsive Design: Styled with custom CSS for a user-friendly interface with consistent black text and centered navigation.

Technologies Used

Python: Core programming language.
Streamlit: Web app framework for the dashboard.
Pandas: Data manipulation and CSV handling.
SQLite: In-memory database for data storage (configurable for persistent storage).
Plotly: Interactive data visualizations.
CSS: Custom styling for enhanced UI.

Installation
Follow these steps to set up and run the Food Waste Management System on your local machine:

Clone the Repository:
git clone https://github.com/your-username/food-waste-management.git
cd food-waste-management


Set Up a Python Environment:

Ensure Python 3.8 or higher is installed. You can check your Python version with:python --version


(Optional) Create and activate a virtual environment to isolate dependencies:python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate




Install Dependencies:

The project includes a requirements.txt file listing all necessary Python packages. Install them using:pip install -r requirements.txt


The requirements.txt contains:streamlit>=1.29.0
pandas>=2.0.0
plotly>=5.14.0


Note: sqlite3 is included in Python's standard library and does not require installation.


Prepare Data Files:

Place the following CSV files in the project root directory (same folder as streamlit_food_wastage_app.py):
providers_data.csv: Columns: Provider_ID, Name, Type, Address, City, Contact
receivers_data.csv: Columns: Receiver_ID, Name, Type, City, Contact
food_listings_data.csv: Columns: Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type
claims_data.csv: Columns: Claim_ID, Food_ID, Receiver_ID, Status, Timestamp


Ensure the CSV files match these schemas to avoid errors. If you don't have these files, you can create empty ones with the correct column headers or populate them with sample data.


Run the Application:

Start the Streamlit app by running:streamlit run streamlit_food_wastage_app.py


The app will open automatically in your default web browser at http://localhost:8501.



Usage

Navigation: Use the horizontal radio buttons to switch between pages: View Data & Queries, CRUD Operations, Trend Analysis, Reports, Filtering, and Contacts.
CRUD Operations: Select a table (Providers, Receivers, Food Listings, Claims) and choose an action (Add, Update, Delete, Search). Data changes are saved to the respective CSV files and SQLite database.
Queries: Run predefined SQL queries or edit them to explore data insights.
Visualizations: View bar charts and tables for trends and reports.
Filtering: Apply filters to narrow down food listings by city, provider, food type, or meal type.
Contacts: Filter provider contact details by city for easy access.

File Structure
food-waste-management/
├── streamlit_food_wastage_app.py  # Main Streamlit application
├── providers_data.csv            # Provider data
├── receivers_data.csv            # Receiver data
├── food_listings_data.csv        # Food listings data
├── claims_data.csv               # Claims data
├── requirements.txt              # Python dependencies
└── README.md                     # This file

Notes

Database: The app uses an in-memory SQLite database for demo purposes. To persist data, modify the init_connection function in streamlit_food_wastage_app.py to use a file-based database (e.g., sqlite3.connect("food_waste.db")).
CSV Files: Ensure CSV files match the specified schemas to avoid errors. Data formats (e.g., numeric IDs, date formats for Expiry_Date) must be valid.
Troubleshooting: If you encounter issues, verify package versions with pip list | grep -E "streamlit|pandas|plotly" and ensure they meet the requirements. Update packages if needed with pip install --upgrade streamlit pandas plotly.

License
This project is licensed under the MIT License. See the LICENSE file for details.
Contact
For issues or suggestions, please open an issue on GitHub or contact the repository owner.
