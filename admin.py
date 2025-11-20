import os
import streamlit as st
import database  # Import database functions
import pandas as pd

st.title("Admin Panel - Plant Disease Detection")

if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False
if "admin_username" not in st.session_state:
    st.session_state["admin_username"] = None

admin_exists = database.admin_collection.count_documents({}) > 0

if st.session_state["admin_logged_in"]:
    admin_mode = st.sidebar.selectbox("Select Page", ["Dashboard", "Manage Users", "View Logs", "Manage Supplements", "View Orders"])
else:
    if admin_exists:
        admin_mode = st.sidebar.selectbox("Select Page", ["Admin Login"])
    else:
        admin_mode = st.sidebar.selectbox("Select Page", ["Register Admin", "Admin Login"])

if admin_mode == "Register Admin":
    st.header("Register Admin")
    new_admin_username = st.text_input("New Admin Username")
    new_admin_password = st.text_input("New Admin Password", type="password")

    if st.button("Register Admin"):
        if new_admin_username and new_admin_password:
            result = database.register_admin(new_admin_username, new_admin_password)
            if result == "Admin registration successful!":
                st.success(result)
                st.experimental_rerun()
            else:
                st.error(result)
        else:
            st.warning("Please fill in all fields.")

if admin_mode == "Admin Login":
    st.header("Admin Login")
    admin_username = st.text_input("Admin Username", key="admin_username_input")
    admin_password = st.text_input("Admin Password", type="password", key="admin_password_input")

    if st.button("Login as Admin"):
        if database.login_admin(admin_username, admin_password):
            st.session_state['admin_logged_in'] = True
            st.session_state['admin_username'] = admin_username
            st.success("Admin Login Successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid Admin Credentials")

if st.session_state["admin_logged_in"]:
    if st.sidebar.button("Logout"):
        st.session_state["admin_logged_in"] = False
        st.session_state["admin_username"] = None
        st.experimental_rerun()

    if admin_mode == "Dashboard":
        st.header(f"Welcome, {st.session_state['admin_username']}!")
        st.subheader("Admin Dashboard")
        st.write("📊 Here you can manage users, view orders, and monitor system analytics.")

    elif admin_mode == "Manage Users":
        st.header("Manage Users")
        users = database.users_collection.find({}, {"_id": 0, "username": 1})
        users_list = list(users)

        if users_list:
            df = pd.DataFrame(users_list)
            st.dataframe(df)
            selected_user = st.selectbox("Select a user to remove:", [user["username"] for user in users_list])

            if st.button("Delete User"):
                database.users_collection.delete_one({"username": selected_user})
                st.success(f"User '{selected_user}' has been deleted.")
                st.experimental_rerun()
        else:
            st.info("No registered users found.")

    elif admin_mode == "View Logs":
        st.header("User Prediction Logs")
        logs = database.prediction_logs.find({}, {"_id": 0, "username": 1, "image_name": 1, "disease_name": 1})
        logs_list = list(logs)

        if logs_list:
            df = pd.DataFrame(logs_list)
            st.dataframe(df)
        else:
            st.info("No prediction logs found.")

    elif admin_mode == "Manage Supplements":
        st.header("Manage Supplements")
        supplement_name = st.text_input("Supplement Name")
        supplement_description = st.text_area("Description")
        supplement_price = st.number_input("Price", min_value=0.0, step=0.1)
        supplement_image = st.file_uploader("Upload Supplement Image", type=["jpg", "jpeg", "png"])

        if st.button("Add Supplement"):
            if supplement_name and supplement_description and supplement_price > 0:
                image_url = None
                if supplement_image:
                    upload_folder = "uploads"
                    os.makedirs(upload_folder, exist_ok=True)
                    image_path = os.path.join(upload_folder, supplement_image.name)
                    with open(image_path, "wb") as f:
                        f.write(supplement_image.read())
                    image_url = image_path

                database.add_supplement(supplement_name, supplement_description, supplement_price, image_url)
                st.success(f"Supplement '{supplement_name}' added successfully!")
            else:
                st.error("Please fill in all fields with valid values.")

        st.subheader("Existing Supplements")
        supplements = list(database.get_all_supplements())
        if supplements:
            df = pd.DataFrame(supplements)
            st.dataframe(df)

            selected_supplement = st.selectbox("Select a supplement to delete:", [supp["name"] for supp in supplements])
            if st.button("Delete Supplement"):
                database.delete_supplement(selected_supplement)
                st.success(f"Supplement '{selected_supplement}' deleted successfully!")
                st.experimental_rerun()
        else:
            st.info("No supplements available.")


    elif admin_mode == "View Orders":
        st.header("User Orders")
        orders = database.get_all_orders()
        if orders:
            orders_data = []
            for order in orders:
                for item in order["items"]:
                    orders_data.append({
                        "Username": order["username"],
                        "Supplement Name": item["supplement_name"],
                        "Quantity": item["quantity"],
                        "Price": item["price"],
                        "Total Price": order.get("total_price", 0.0),
                        "Order Date": order["order_date"].strftime('%Y-%m-%d %H:%M:%S')
                    })
            df = pd.DataFrame(orders_data)
            st.dataframe(df)
        else:
            st.info("No orders found.")

