import streamlit as st
import database  # Import database functions
import tensorflow as tf
import numpy as np
from database import place_order

st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-size: 16px;
        padding: 10px;
        margin-top: 10px;
    }
    .stTextInput>div>div>input {
        padding: 10px;
        font-size: 16px;
        border-radius: 5px;
    }
    .header {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: #4CAF50;
    }
    .subtext {
        text-align: center;
        color: #777;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Plant Disease Detection")

# Authentication System
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


# Adjust Sidebar Menu Based on Login Status
if st.session_state["logged_in"]:
    app_mode = st.sidebar.selectbox("🔹 Select Page", ["🏠 Home", "📌 About", "🔍 Disease Recognition", "🛂 Supplements","🛒 Cart", "📜 Order History"])
else:
    app_mode = st.sidebar.selectbox("🔹 Select Page", ["🔑 Login", "📝 Register"])



# Order History Page
if app_mode == "📜 Order History":
    st.header("📜 Your Order History")
    username = st.session_state.get("username")

    if username:
        orders = database.get_user_orders(username)
        if orders:
            for order in orders:
                st.write(f"**Order Date:** {order['order_date'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Total Price:** ₹{order['total_price']}")
                st.write("**Items:**")
                for item in order['items']:
                    st.write(f"- {item['supplement_name']} (Quantity: {item['quantity']}, Price: ₹{item['price']})")
                st.write("---")
        else:
            st.info("No orders found.")
    else:
        st.error("Please log in to view your order history.")




# Register Page
if app_mode == "📝 Register":
    st.markdown('<p class="header">Create an Account</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtext">Join us and start detecting plant diseases easily!</p>', unsafe_allow_html=True)

    new_user = st.text_input("👤 Username", key="register_username")
    new_password = st.text_input("🔒 Password", type="password", key="register_password")

    if st.button("🚀 Register", help="Click to create your account"):
        message = database.register_user(new_user, new_password)
        st.success(message)



# Login Page
elif app_mode == "🔑 Login":
    st.markdown('<p class="header">Welcome Back!</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtext">Log in to continue detecting plant diseases.</p>', unsafe_allow_html=True)

    username = st.text_input("👤 Username", key="login_username")
    password = st.text_input("🔒 Password", type="password", key="login_password")

    if st.button("✅ Login", help="Click to access your account"):
        if database.login_user(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success("✅ Login Successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid Credentials. Please try again.")

# Cart Management
if app_mode == "🛒 Cart":
    st.header("🛒 Your Cart")
    username = st.session_state.get("username")

    if username:
        cart_items = database.view_cart(username)
        if cart_items:
            for item in cart_items:
                st.write(f"**{item['supplement_name']}** - ₹{item['price']} x {item['quantity']}")
            total_price = sum(item['price'] * item['quantity'] for item in cart_items)
            st.write(f"### 🧾 Total: ₹{total_price}")
            
            # Purchase button and order placement
            if st.button("🛍 Purchase"):
                order_message = database.place_order(username)
                st.success(order_message)
        else:
            st.info("Your cart is empty.")
    else:
        st.error("Please log in to view your cart.")



# Supplements Page
elif st.session_state["logged_in"] and app_mode == "🛂 Supplements":
    st.header("🛂 Plant Care Supplements")

    # Initialize session state for cart
    if "carts" not in st.session_state:
        st.session_state["carts"] = []

    supplements = database.get_all_supplements()

    if supplements:
        for supplement in supplements:
            st.subheader(supplement.get('name', 'Unknown Supplement'))
            image_url = supplement.get('image_url')
            if image_url and image_url != 'None':
                st.image(image_url, caption=supplement['name'], width=300)
            st.write(f"💰 **Price:** ₹{supplement.get('price', 'N/A')}")
            st.write(f"📜 **Description:** {supplement.get('description', 'No Description Available')}")

            if st.button(f"Add to Cart - {supplement['name']}"):
                database.add_to_cart(st.session_state["username"], supplement['name'], 1)
                st.success(f"Added {supplement['name']} to your cart!")



    else:
        st.info("No supplements available. Check back later!")




# Home Page
if st.session_state["logged_in"] and app_mode == "🏠 Home":
    st.header("🌿 PLANT DISEASE RECOGNITION SYSTEM")
    st.image("home_page.jpeg", use_column_width=True)
    st.markdown("""
Welcome to the Plant Disease Recognition System! 🌿🔍

Our mission is to help in identifying plant diseases efficiently. Upload an image of a plant, and our system will analyze it to detect any signs of diseases. Together, let's protect our crops and ensure a healthier harvest!

**How It Works:**
1. **Upload Image:** Go to the **Disease Recognition** page and upload an image of a plant with suspected diseases.
2. **Analysis:** Our system will process the image using advanced algorithms to identify potential diseases.
3. **Results:** View the results and recommendations for further action.

**Why Choose Us?**
- **Accuracy:** Our system utilizes state-of-the-art machine learning techniques for accurate disease detection.
- **User-Friendly:** Simple and intuitive interface for seamless user experience.
- **Fast and Efficient:** Receive results in seconds, allowing for quick decision-making.

**Get Started:**
Click on the **Disease Recognition** page in the sidebar to upload an image and experience the power of our Plant Disease Recognition System!

**About Us:**
Learn more about the project, our team, and our goals on the **About** page.
""", unsafe_allow_html=True)


#About Project
elif(app_mode=="📌 About"):
    st.header("About")
    st.markdown("""
                #### About Dataset
                This dataset is recreated using offline augmentation from the original dataset.The original dataset can be found on this github repo.
                This dataset consists of about 87K rgb images of healthy and diseased crop leaves which is categorized into 38 different classes.The total dataset is divided into 80/20 ratio of training and validation set preserving the directory structure.
                A new directory containing 33 test images is created later for prediction purpose.
                #### Content
                1. train (70295 images)
                2. test (33 images)
                3. validation (17572 images)

                """)



elif app_mode == "🔍 Disease Recognition":
    st.header("🌱 Disease Recognition")
    test_image = st.file_uploader("📷 Upload an Image:")

    if test_image:
        st.image(test_image, caption="Uploaded Image", use_column_width=True)

        if test_image and st.button("🔬 Predict"):

            def model_prediction(test_image):
                model = tf.keras.models.load_model("trained_model.keras")
                image = tf.keras.preprocessing.image.load_img(test_image, target_size=(128, 128))
                input_arr = tf.keras.preprocessing.image.img_to_array(image)
                input_arr = np.array([input_arr])  # Convert single image to batch
                prediction = model.predict(input_arr)
                return np.argmax(prediction)

            result_index = model_prediction(test_image)
            class_name = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
                'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 
                'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 
                'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 
                'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 
                'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot',
                'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 
                'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 
                'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew', 
                'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot', 
                'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 
                'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 
                'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
                'Tomato___healthy']
            
            solutions = {
                'Apple___Apple_scab': "Apply fungicides and remove infected leaves.",
                'Apple___Black_rot': "Prune and destroy infected branches; use copper-based sprays.",
                'Apple___Cedar_apple_rust': "Use fungicides and plant disease-resistant varieties.",
                'Corn_(maize)___Common_rust_': "Apply fungicides and practice crop rotation.",
                'Tomato___Late_blight': "Remove infected plants and use copper fungicides."
            }

            disease_name = class_name[result_index]
            st.success(f"✅ Model predicts: **{disease_name}**")

            # Show Solution
            solution = solutions.get(disease_name, "No specific solution available. Please consult an expert.")
            st.info(f"📝 Recommended Solution: {solution}")

            # Save Prediction Log in MongoDB
            username = st.session_state.get("username", "Guest")
            database.save_prediction(username, test_image.name, disease_name)

# Logout Button (Persistent)
if st.session_state["logged_in"] and st.sidebar.button("🚪 Logout"):
    st.session_state["logged_in"] = False
    st.session_state.pop("username", None)
    st.experimental_rerun()


elif app_mode == "none of the above":
    st.error("Login and register first")