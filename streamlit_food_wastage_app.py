import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os


# --- PAGE CONFIG ---
st.set_page_config(page_title="Food Waste Management", layout="wide")

# --- DB CONNECTION ---
@st.cache_resource
def init_connection():
    # In-memory for demo; switch to a file DB if you want persistence.
    return sqlite3.connect(":memory:", check_same_thread=False)

# --- LOAD CSVs INTO SQLITE (uses your exact schemas) ---
def load_data(conn):
    providers = pd.read_csv("providers_data.csv")       # Provider_ID, Name, Type, Address, City, Contact
    receivers = pd.read_csv("receivers_data.csv")       # Receiver_ID, Name, Type, City, Contact
    listings  = pd.read_csv("food_listings_data.csv")   # Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type
    claims    = pd.read_csv("claims_data.csv")          # Claim_ID, Food_ID, Receiver_ID, Status, Timestamp

    providers.to_sql("providers", conn, index=False, if_exists="replace")
    receivers.to_sql("receivers", conn, index=False, if_exists="replace")
    # IMPORTANT: name the table exactly "food_listings" so the rest of the app matches
    listings.to_sql("food_listings", conn, index=False, if_exists="replace")
    claims.to_sql("claims", conn, index=False, if_exists="replace")

# --- INIT ---
conn = init_connection()
load_data(conn)

# --- CSS for styling ---
st.markdown("""
    <style>
    .stRadio > div { 
        justify-content: center; 
        gap: 12px; 
    }

    /* Style the radio button labels */
    .stRadio label {
        flex: 1;
        text-align: center;
        background-color: lightblue !important;
        color: black !important;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 16px;
        cursor: pointer;
        font-family: Arial, sans-serif;  /* Set font family */
    }

    /* Style the text inside the label */
    div[role="radiogroup"] label p { 
        color: black !important; 
        font-weight: bold !important; 
        font-family: Arial, sans-serif; /* Font family */
    }

    div.stButton > button:first-child {
        background-color: lavender !important; 
        color: black !important;
        border: 1px solid #ccc !important; 
        border-radius: 8px !important;
    }

    div.stButton > button:first-child:hover { 
        background-color: lavender !important; 
        color: black !important; 
    }

    body, .stButton button { color: black; }
    .stTextInput input { color: black; }
</style>

""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>🍽️ FOOD WASTE MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Interactive dashboard with CRUD operations, data analysis, reports, and provider contacts</h4>", unsafe_allow_html=True)

# --- NAVIGATION ---
pages = ["View Data & Queries", "CRUD Operations", "Trend Analysis", "Reports", "Filtering", "Contacts"]
page = st.radio("Navigation", pages, horizontal=True, label_visibility="collapsed")

# --- PREDEFINED QUERIES (fixed column/table names) ---
queries = {
    "1. How many providers and receivers are there in each city?":
        """
        WITH pc AS (
            SELECT City, COUNT(DISTINCT Provider_ID) AS providers
            FROM providers GROUP BY City
        ),
        rc AS (
            SELECT City, COUNT(DISTINCT Receiver_ID) AS receivers
            FROM receivers GROUP BY City
        ),
        cities AS (
            SELECT City FROM providers
            UNION
            SELECT City FROM receivers
        )
        SELECT c.City,
               COALESCE(pc.providers, 0) AS providers,
               COALESCE(rc.receivers, 0) AS receivers
        FROM cities c
        LEFT JOIN pc USING (City)
        LEFT JOIN rc USING (City)
        ORDER BY c.City
        """,
    "2. Which type of food provider contributes the most (by count of listings)?":
        """
        SELECT p.Type, COUNT(*) AS listing_count
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Type
        ORDER BY listing_count DESC
        """,
    "3. Contact information of all providers (sorted by city, name)":
        "SELECT Name, City, Contact FROM providers ORDER BY City, Name",
    "4. Which receivers have claimed the most food (by claims count)?":
        """
        SELECT r.Name, COUNT(c.Claim_ID) AS total_claims
        FROM receivers r
        JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        GROUP BY r.Receiver_ID
        ORDER BY total_claims DESC
        """,
    "5. Total quantity of food available from all providers (sum of listings)":
        "SELECT SUM(Quantity) AS total_quantity FROM food_listings",
    "6. Which city (Location) has the highest number of food listings?":
        """
        SELECT Location AS City, COUNT(Food_ID) AS total_listings
        FROM food_listings
        GROUP BY Location
        ORDER BY total_listings DESC
        """,
    "7. Most commonly available food types":
        """
        SELECT Food_Type, COUNT(*) AS count
        FROM food_listings
        GROUP BY Food_Type
        ORDER BY count DESC
        """,
    "8. How many claims have been made for each food item (by Food_Name)?":
        """
        SELECT f.Food_Name, COUNT(c.Claim_ID) AS total_claims
        FROM claims c
        JOIN food_listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Food_ID
        ORDER BY total_claims DESC
        """,
    "9. Which provider has the highest number of completed claims?":
        """
        SELECT p.Name, COUNT(c.Claim_ID) AS successful_claims
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        JOIN claims c ON f.Food_ID = c.Food_ID
        WHERE c.Status = 'completed'
        GROUP BY p.Provider_ID
        ORDER BY successful_claims DESC
        """,
    "10. Percentage of claims by status":
        """
        SELECT Status,
               COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS percentage
        FROM claims
        GROUP BY Status
        """,
    "11. Average quantity claimed per receiver":
        """
        SELECT r.Name, AVG(f.Quantity) AS avg_claimed
        FROM receivers r
        JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        JOIN food_listings f ON c.Food_ID = f.Food_ID
        GROUP BY r.Receiver_ID
        ORDER BY avg_claimed DESC
        """,
    "12. Which meal type is claimed the most?":
        """
        SELECT f.Meal_Type, COUNT(c.Claim_ID) AS total_claims
        FROM claims c
        JOIN food_listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Meal_Type
        ORDER BY total_claims DESC
        """,
    "13. Total quantity donated by each provider":
        """
        SELECT p.Name, SUM(f.Quantity) AS total_donated
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Provider_ID
        ORDER BY total_donated DESC
        """
}

# --- MAIN CONTENT ---
if page == "View Data & Queries":
    st.subheader("📊 Run Predefined Queries")
    selected_query = st.selectbox("Choose a query", list(queries.keys()))
    if selected_query:
        default_sql = queries[selected_query]
        edited_sql = st.text_area("Edit and run the SQL query:", default_sql, height=200)
        if st.button("Run Query"):
            try:
                df = pd.read_sql_query(edited_sql, conn)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

elif page == "CRUD Operations":
    st.subheader("➕ Add / Update / Delete / Search Records")
    table_choice = st.selectbox("Select Table:", ["providers", "receivers", "food_listings", "claims"])

    # ---------------------- PROVIDERS ----------------------
    if table_choice == "providers":
        action = st.radio("Action:", ["Add", "Update", "Delete", "Search"], horizontal=True)

        csv_file = "providers_data.csv"

        # Load existing CSV or create empty
        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["Provider_ID", "Name", "Type", "Address", "City", "Contact"])

        if action == "Add":
            Provider_ID = st.number_input("Provider ID", min_value=1, step=1, format="%d")
            Name = st.text_input("Name", key="name") 
            Type = st.text_input("Type", key="type") 
            Address = st.text_input("Address", key="address") 
            City = st.text_input("City", key="city") 
            Contact = st.text_input("Contact", key="contact") 

            if st.button("Add Provider"):
                # get values from session_state
                name_val = st.session_state.name.strip()
                type_val = st.session_state.type.strip()
                address_val = st.session_state.address.strip()
                city_val = st.session_state.city.strip()
                contact_val = st.session_state.contact.strip()
                
                if not all([name_val, type_val, address_val, city_val, contact_val]):
                    st.warning("Please fill in all text fields!")
                elif Provider_ID in df["Provider_ID"].values:
                    st.error("Provider ID already exists! Please use a unique ID.")
                else:
                    # Create new row and append to DataFrame
                    new_row = pd.DataFrame({
                        "Provider_ID": [Provider_ID],
                        "Name": [name_val],
                        "Type": [type_val],
                        "Address": [address_val],
                        "City": [city_val],
                        "Contact": [contact_val]
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(csv_file, index=False)
                    st.success("Provider added successfully to CSV!")

        elif action == "Update":
            Provider_ID = int(st.number_input("Provider ID to Update", min_value=1, step=1, format="%d"))
            column_to_update = st.selectbox("Column", ["Name", "Type", "Address", "City", "Contact"])
            new_value = st.text_input(f"New value for {column_to_update}") or ""

            if st.button("Update Provider"):
                if Provider_ID not in df["Provider_ID"].values:
                    st.error("No record found with that Provider ID.")
                else:
                    df.loc[df["Provider_ID"] == Provider_ID, column_to_update] = new_value
                    df.to_csv(csv_file, index=False)
                    st.success(f"{column_to_update} updated successfully in CSV!")

        elif action == "Delete":
            Provider_ID = int(st.number_input("Provider ID to Delete", min_value=1, step=1, format="%d"))
            if st.button("Delete Provider"):
                if Provider_ID not in df["Provider_ID"].values:
                    st.error("No record found with that Provider ID.")
                else:
                    df = df[df["Provider_ID"] != Provider_ID]
                    df.to_csv(csv_file, index=False)
                    st.success("Provider deleted successfully from CSV!")

        elif action == "Search":
            # Reload CSV fresh for searching
            try:
                df = pd.read_csv(csv_file)
            except FileNotFoundError:
                df = pd.DataFrame(columns=["Provider_ID", "Name", "Type", "Address", "City", "Contact"])

            if df.empty:
                st.warning("No data available in Providers table.")
            else:
                search_by = st.selectbox("Search by", df.columns)
                term = st.text_input(f"Enter {search_by}")

                if st.button("Search"):
                    df = pd.read_csv(csv_file)  # Reload fresh before searching
                    results = df[df[search_by].astype(str).str.contains(term, case=False, na=False)]
                    if not results.empty:
                        st.success(f"Found {len(results)} record(s).")
                        st.dataframe(results)
                    else:
                        st.warning("No matching records found.")

    # ---------------------- RECEIVERS ----------------------
    elif table_choice == "receivers":
        action = st.radio("Action:", ["Add", "Update", "Delete", "Search"], horizontal=True)

        if action == "Add":
            Receiver_ID = int(st.number_input("Receiver ID", min_value=1, step=1, format="%d"))
            Name        = st.text_input("Name") or ""
            Type        = st.text_input("Type") or ""
            City        = st.text_input("City") or ""
            Contact     = st.text_input("Contact") or ""
            if st.button("Add Receiver"):
                try:
                    conn.execute(
                        "INSERT INTO receivers (Receiver_ID, Name, Type, City, Contact) VALUES (?, ?, ?, ?, ?)",
                        (Receiver_ID, Name, Type, City, Contact)
                    )
                    conn.commit()

                    # Save immediately
                    df = pd.read_sql_query("SELECT * FROM receivers", conn)
                    df.to_csv("receivers_data.csv", index=False)

                    st.success("Receiver added successfully and saved to CSV!")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")

        elif action == "Update":
            Receiver_ID = int(st.number_input("Receiver ID to Update", min_value=1, step=1, format="%d"))
            column_to_update = st.selectbox("Column", ["Name", "Type", "City", "Contact"])
            new_value = st.text_input(f"New value for {column_to_update}") or ""
            if st.button("Update Receiver"):
                try:
                    conn.execute(f"UPDATE receivers SET {column_to_update}=? WHERE Receiver_ID=?", (new_value, Receiver_ID))
                    conn.commit()

                    # Save immediately
                    df = pd.read_sql_query("SELECT * FROM receivers", conn)
                    df.to_csv("receivers_data.csv", index=False)

                    st.success(f"{column_to_update} updated successfully and saved to CSV!")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")

        elif action == "Delete":
            Receiver_ID = int(st.number_input("Receiver ID to Delete", min_value=1, step=1, format="%d"))
            if st.button("Delete Receiver"):
                try:
                    conn.execute("DELETE FROM receivers WHERE Receiver_ID=?", (Receiver_ID,))
                    conn.commit()

                    # Save immediately
                    df = pd.read_sql_query("SELECT * FROM receivers", conn)
                    df.to_csv("receivers_data.csv", index=False)

                    st.success("Receiver deleted successfully and saved to CSV!")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")

        elif action == "Search":
            df = pd.read_csv("receivers_data.csv")  # load CSV
            if df.empty:
                st.warning("No data available in Receivers table.")
            else:
                search_by = st.selectbox("Search by", df.columns)
                term = st.text_input(f"Enter {search_by}")
                if st.button("Search"):
                    results = df[df[search_by].astype(str).str.contains(term, case=False, na=False)]
                    st.dataframe(results if not results.empty else pd.DataFrame({"Result": ["No matching records found."]}))


    # ---------------------- FOOD LISTINGS ----------------------
    elif table_choice == "food_listings":
        action = st.radio("Action:", ["Add", "Update", "Delete", "Search"], horizontal=True)

        if action == "Add":
            Food_ID       = int(st.number_input("Food ID", min_value=1, step=1, format="%d"))
            Food_Name     = st.text_input("Food Name") or ""
            Quantity      = st.text_input("Quantity") or ""
            Expiry_Date   = st.text_input("Expiry Date") or ""
            Provider_ID   = int(st.number_input("Provider ID", min_value=1, step=1, format="%d"))
            Provider_Type = st.text_input("Provider Type") or ""
            Location      = st.text_input("Location") or ""
            Food_Type     = st.text_input("Food Type") or ""
            Meal_Type     = st.text_input("Meal Type") or ""
            if st.button("Add Food Listing"):
                try:
                    conn.execute(
                        """INSERT INTO food_listings
                        (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                    )
                    conn.commit()

                    # Save immediately
                    df = pd.read_sql_query("SELECT * FROM food_listings", conn)
                    df.to_csv("food_listings_data.csv", index=False)

                    st.success("Food Listing added successfully and saved to CSV!")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")

        elif action == "Update":
            Food_ID = int(st.number_input("Food ID to Update", min_value=1, step=1, format="%d"))
            column_to_update = st.selectbox("Column", ["Food_Name", "Quantity", "Expiry_Date", "Provider_ID", "Provider_Type", "Location", "Food_Type", "Meal_Type"])
            new_value = st.text_input(f"New value for {column_to_update}") or ""
            if st.button("Update Food Listing"):
                try:
                    conn.execute(f"UPDATE food_listings SET {column_to_update}=? WHERE Food_ID=?", (new_value, Food_ID))
                    conn.commit()

                    # Save immediately
                    df = pd.read_sql_query("SELECT * FROM food_listings", conn)
                    df.to_csv("food_listings_data.csv", index=False)

                    st.success(f"{column_to_update} updated successfully and saved to CSV!")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")

        elif action == "Delete":
            Food_ID = int(st.number_input("Food ID to Delete", min_value=1, step=1, format="%d"))
            if st.button("Delete Food Listing"):
                try:
                    conn.execute("DELETE FROM food_listings WHERE Food_ID=?", (Food_ID,))
                    conn.commit()

                    # Save immediately
                    df = pd.read_sql_query("SELECT * FROM food_listings", conn)
                    df.to_csv("food_listings_data.csv", index=False)

                    st.success("Food Listing deleted successfully and saved to CSV!")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")

        elif action == "Search":
            df = pd.read_csv("food_listings_data.csv")
            if df.empty:
                st.warning("No data available in Food Listings table.")
            else:
                search_by = st.selectbox("Search by", df.columns)
                term = st.text_input(f"Enter {search_by}")
                if st.button("Search"):
                    results = df[df[search_by].astype(str).str.contains(term, case=False, na=False)]
                    st.dataframe(results if not results.empty else pd.DataFrame({"Result": ["No matching records found."]}))


    # ---------------------- CLAIMS ----------------------
    elif table_choice == "claims":
        action = st.radio("Action:", ["Add", "Update", "Delete", "Search"], horizontal=True)

        if action == "Add":
            Claim_ID    = int(st.number_input("Claim ID", min_value=1, step=1, format="%d"))
            Food_ID     = int(st.number_input("Food ID", min_value=1, step=1, format="%d"))
            Receiver_ID = int(st.number_input("Receiver ID", min_value=1, step=1, format="%d"))
            Status      = st.text_input("Status") or ""
            Timestamp   = st.text_input("Timestamp") or ""
            if st.button("Add Claim"):
                try:
                    conn.execute(
                        "INSERT INTO claims (Claim_ID, Food_ID, Receiver_ID, Status, Timestamp) VALUES (?, ?, ?, ?, ?)",
                        (Claim_ID, Food_ID, Receiver_ID, Status, Timestamp)
                    )
                    conn.commit()

                    # Save immediately
                    df = pd.read_sql_query("SELECT * FROM claims", conn)
                    df.to_csv("claims_data.csv", index=False)

                    st.success("Claim added successfully and saved to CSV!")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")

        elif action == "Update":
            Claim_ID = int(st.number_input("Claim ID to Update", min_value=1, step=1, format="%d"))
            column_to_update = st.selectbox("Column", ["Food_ID", "Receiver_ID", "Status", "Timestamp"])
            new_value = st.text_input(f"New value for {column_to_update}") or ""
            if st.button("Update Claim"):
                try:
                    conn.execute(f"UPDATE claims SET {column_to_update}=? WHERE Claim_ID=?", (new_value, Claim_ID))
                    conn.commit()

                    # Save immediately
                    df = pd.read_sql_query("SELECT * FROM claims", conn)
                    df.to_csv("claims_data.csv", index=False)

                    st.success(f"{column_to_update} updated successfully and saved to CSV!")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")

        elif action == "Delete":
            Claim_ID = int(st.number_input("Claim ID to Delete", min_value=1, step=1, format="%d"))
            if st.button("Delete Claim"):
                try:
                    conn.execute("DELETE FROM claims WHERE Claim_ID=?", (Claim_ID,))
                    conn.commit()

                    # Save immediately
                    df = pd.read_sql_query("SELECT * FROM claims", conn)
                    df.to_csv("claims_data.csv", index=False)

                    st.success("Claim deleted successfully and saved to CSV!")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")

        elif action == "Search":
            df = pd.read_csv("claims_data.csv")
            if df.empty:
                st.warning("No data available in Claims table.")
            else:
                search_by = st.selectbox("Search by", df.columns)
                term = st.text_input(f"Enter {search_by}")
                if st.button("Search"):
                    results = df[df[search_by].astype(str).str.contains(term, case=False, na=False)]
                    st.dataframe(results if not results.empty else pd.DataFrame({"Result": ["No matching records found."]}))

# ----------------------------
# 3. Trend Analysis
# ----------------------------
elif page == "Trend Analysis":  # <-- fixed page key to match the nav
    st.subheader("📈 Food Wastage Trends")

    st.write("**Food Quantity by Food Type:**")
    df = pd.read_sql_query("""
        SELECT Food_Type, SUM(Quantity) AS total_quantity
        FROM food_listings
        GROUP BY Food_Type
    """, conn)
    if not df.empty:
        st.bar_chart(df.set_index("Food_Type"))

    st.write("**Listings by City (Location):**")
    df_city = pd.read_sql_query("""
        SELECT Location AS City, COUNT(Food_ID) AS total_listings
        FROM food_listings
        GROUP BY Location
    """, conn)
    if not df_city.empty:
        st.bar_chart(df_city.set_index("City"))

    st.write("**Listings Expiring Soon (Next 3 Days):**")
    df_expiry = pd.read_sql_query(
        "SELECT * FROM food_listings WHERE date(Expiry_Date) <= date('now','+3 day')", conn
    )
    st.dataframe(df_expiry)

    # --- Listings Expiring Soon ---
    st.write("**Listings Expiring in Next 3 Days:**")
    df3 = pd.read_sql_query("SELECT * FROM food_listings", conn)

    # Convert Expiry_Date to datetime
    df3["Expiry_Date"] = pd.to_datetime(df3["Expiry_Date"], errors="coerce")

    # Filter for next 3 days
    df3_expiring = df3[df3["Expiry_Date"] <= (pd.Timestamp.now() + pd.Timedelta(days=3))]

    # Sort by Expiry_Date ascending (earliest first)
    df3_expiring = df3_expiring.sort_values(by="Expiry_Date", ascending=True)

    st.dataframe(df3_expiring, use_container_width=True)

# ----------------------------
# 4. Reports
# ----------------------------
elif page == "Reports":
    st.subheader("📄 Summary Reports")

    # --- Total Food Quantity per Provider ---
    st.write("**Total Food Quantity per Provider:**")
    df1 = pd.read_sql_query("""
        SELECT p.Name, SUM(f.Quantity) AS total_quantity
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Provider_ID
    """, conn)
    st.dataframe(df1, use_container_width=True)
    if not df1.empty:
        fig1 = px.bar(df1, x="Name", y="total_quantity", title="Food Quantity per Provider")
        st.plotly_chart(fig1, use_container_width=True)

    # --- Most Claimed Food Items ---
    st.write("**Most Claimed Food Items:**")
    df2 = pd.read_sql_query("""
        SELECT f.Food_Name, COUNT(c.Claim_ID) AS total_claims
        FROM claims c
        JOIN food_listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Food_ID
        ORDER BY total_claims DESC
    """, conn)
    st.dataframe(df2, use_container_width=True)
    if not df2.empty:
        fig2 = px.bar(df2, x="Food_Name", y="total_claims", title="Most Claimed Food Items")
        st.plotly_chart(fig2, use_container_width=True)

    # --- Listings Expiring Soon ---
    st.write("**Listings Expiring in Next 3 Days:**")
    df3 = pd.read_sql_query("SELECT * FROM food_listings", conn)

    # Convert Expiry_Date to datetime
    df3["Expiry_Date"] = pd.to_datetime(df3["Expiry_Date"], errors="coerce")

    # Filter for next 3 days
    df3_expiring = df3[df3["Expiry_Date"] <= (pd.Timestamp.now() + pd.Timedelta(days=3))]

    # Sort by Expiry_Date ascending (earliest first)
    df3_expiring = df3_expiring.sort_values(by="Expiry_Date", ascending=True)

    st.dataframe(df3_expiring, use_container_width=True)

# ----------------------------
# 5. Filtering
# ----------------------------
elif page == "Filtering":
    st.subheader("🔎 Filter Data")

    # --- CSS for black font ---
    st.markdown("""
        <style>
            .stSelectbox div[data-baseweb="select"] > div {
                color: white !important;
            }
            .stDataFrame div {
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Distinct filter values
    city_list      = pd.read_sql_query("SELECT DISTINCT City FROM providers", conn)["City"].dropna().tolist()
    city_list.insert(0, "All Cities")
    
    provider_list  = pd.read_sql_query("SELECT DISTINCT Name FROM providers", conn)["Name"].dropna().tolist()
    provider_list.insert(0, "All Providers")
    
    food_type_list = pd.read_sql_query("SELECT DISTINCT Food_Type FROM food_listings", conn)["Food_Type"].dropna().tolist()
    food_type_list.insert(0, "All Food Types")
    
    meal_type_list = pd.read_sql_query("SELECT DISTINCT Meal_Type FROM food_listings", conn)["Meal_Type"].dropna().tolist()
    meal_type_list.insert(0, "All Meal Types")

    # Dropdown filters
    selected_city     = st.selectbox("City", city_list)
    selected_provider = st.selectbox("Provider", provider_list)
    selected_food     = st.selectbox("Food Type", food_type_list)
    selected_meal     = st.selectbox("Meal Type", meal_type_list)

    # Build query dynamically based on "All" selections
    query = """
        SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, f.Provider_ID, f.Provider_Type,
               f.Location, f.Food_Type, f.Meal_Type,
               p.Name AS Provider_Name, p.City
        FROM food_listings f
        JOIN providers p ON f.Provider_ID = p.Provider_ID
        WHERE 1=1
    """
    params = []

    if selected_city != "All Cities":
        query += " AND f.Location = ?"
        params.append(selected_city)

    if selected_food != "All Food Types":
        query += " AND f.Food_Type = ?"
        params.append(selected_food)

    if selected_meal != "All Meal Types":
        query += " AND f.Meal_Type = ?"
        params.append(selected_meal)

    if selected_provider != "All Providers":
        query += " AND p.Name = ?"
        params.append(selected_provider)

    query += " ORDER BY f.Expiry_Date"

    # Fetch filtered data
    df_filtered = pd.read_sql_query(query, conn, params=params)
    st.dataframe(df_filtered, use_container_width=True)

# ----------------------------
# 6. Contacts
# ----------------------------

elif page == "Contacts":
    st.subheader("📞 Provider Contact Details")

    # --- City Dropdown ---
    city_list = pd.read_sql_query("SELECT DISTINCT City FROM providers", conn)["City"].dropna().tolist()
    city_list = ["All Cities"] + city_list
    selected_city = st.selectbox("Select City", city_list, index=0)

    # --- Query Providers ---
    query = "SELECT Name AS Provider_Name, City, Contact FROM providers WHERE 1=1"
    params = []
    if selected_city != "All Cities":
        query += " AND City = ?"
        params.append(selected_city)

    df_contacts = pd.read_sql_query(query, conn, params=params)

    # --- Display Table ---
    st.dataframe(df_contacts, use_container_width=True)



