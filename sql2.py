import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, date
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Load config from YAML file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize Streamlit Authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

# Authenticate user
authenticator.login()

# Function to establish MySQL connection
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="gas_booking"
    )

# Function to fetch existing booking data
def fetch_existing_bookings(conn):
    query = "SELECT ID, Customer_Name, Customer_Phone, Customer_Address, Gas_Type, Booking_Date, Delivery_Date, Status, Admin FROM bookings"
    df = pd.read_sql(query, conn)
    return df
st.snow()

# Function to insert new booking data
def insert_booking_data(conn, name, phone, address, gas_type, booking_date, admin):
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO bookings (Customer_Name, Customer_Phone, Customer_Address, Gas_Type, Booking_Date, Admin)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (name, phone, address, gas_type, booking_date, admin))
    conn.commit()

# Ensure authentication status before accessing application
if st.session_state.get("authentication_status"):
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome {st.session_state["name"]}')

    st.title("Gas Booking Management Portal 🚚")

    conn = get_mysql_connection()
    
    existing_bookings = fetch_existing_bookings(conn)
    existing_bookings = existing_bookings.dropna(how="all")

    selected_option = st.sidebar.radio("What would you like to do?", ("Make a Booking", "View Bookings"))

    if selected_option == "Make a Booking":
        st.subheader("New Gas Booking 📝")
        st.write("Fill in the details below to make a new booking.")

        with st.form(key="booking_form"):
            name = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")
            address = st.text_area("Customer Address")
            gas_type = st.selectbox("Select Gas Type", ["LPG", "Natural Gas"])
            booking_date = st.date_input("Booking Date", min_value=date.today())

            submit_button = st.form_submit_button("Submit Booking")

            if submit_button:
                if not name or not phone or not address or not gas_type:
                    st.warning("Please fill in all mandatory fields.")
                else:
                    insert_booking_data(conn, name, phone, address, gas_type, booking_date, st.session_state["name"])
                    st.success("Booking successfully submitted!")
                    # Refresh the bookings table display
                    existing_bookings = fetch_existing_bookings(conn)

    elif selected_option == "View Bookings":
        st.subheader("Current Bookings 📅")
        if existing_bookings.empty:
            st.info("No bookings found.")
        else:
            st.dataframe(existing_bookings)

else:
    if st.session_state.get("authentication_status") == False:
        st.error('Invalid username/password')
    elif st.session_state.get("authentication_status") == None:
        st.warning('Please enter your username and password')