import streamlit as st
import pandas as pd
import joblib
import sqlite3
import base64
import random

# ==========================
# BACKGROUND IMAGE
# ==========================
def set_bg():
    with open("wallpaper.jpg", "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        h1 {{
            color: #ffffff !important;
            text-shadow: 2px 2px 6px #000;
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #111827, #1f2937);
        }}

        section[data-testid="stSidebar"] * {{
            color: white !important;
        }}

        .stButton > button {{
            background: linear-gradient(90deg, #4f46e5, #06b6d4);
            color: white;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            border: none;
            font-weight: bold;
        }}

        .stButton > button:hover {{
            transform: scale(1.03);
            background: linear-gradient(90deg, #06b6d4, #4f46e5);
        }}

        input, textarea {{
            border-radius: 8px !important;
            border: 1px solid #60a5fa !important;
            background-color: rgba(255,255,255,0.85) !important;
        }}
        </style>
    """, unsafe_allow_html=True)

set_bg()

st.markdown(
    "<h1 style='text-align:center;'>🚗 Car Make Prediction System</h1>",
    unsafe_allow_html=True
)

# ==========================
# DATABASE
# ==========================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()

def register_user(username, password):
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Car Prediction"

# ==========================
# LOGIN / REGISTER
# ==========================
if not st.session_state.logged_in:

    st.sidebar.title("Menu")
    menu = st.sidebar.selectbox("Choose", ["Login", "Register"])

    if menu == "Register":
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Register"):
            if register_user(user, pw):
                st.success("Registered Successfully")
            else:
                st.error("User already exists")

    if menu == "Login":
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(user, pw):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Login")

# ==========================
# DASHBOARD
# ==========================
else:

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.title("Navigation")

    if st.sidebar.button("🚗 Car Prediction"):
        st.session_state.page = "Car Prediction"

    if st.sidebar.button("🏆 Sports Quiz"):
        st.session_state.page = "Sports Quiz"

    # ==========================
    # CAR PREDICTION PAGE
    # ==========================
    if st.session_state.page == "Car Prediction":

        st.subheader("🧠 Upload Pickle file (.pkl)")
        pkl_file = st.file_uploader("Upload Pickle Model", type=["pkl"])

        model = None
        accuracy = None

        if pkl_file is not None:
            data = joblib.load(pkl_file)

            if isinstance(data, dict):
                model = data.get("model")
                accuracy = data.get("accuracy")
            else:
                model = data

            st.success("Model Loaded Successfully")

            if accuracy is not None:
                st.success(f"📊 Model Accuracy: {accuracy*100:.2f}%")
            else:
                st.warning("⚠ Accuracy not stored in model")

        # ================= INPUT =================
        st.subheader("🚗 Predict Car Make")

        car_model = st.text_input("Car Model")
        year = st.text_input("Year")
        engine_size = st.text_input("Engine Size")
        horsepower = st.text_input("Horsepower")
        torque = st.text_input("Torque")
        ph_time = st.text_input("0-100 km/h Time")
        price = st.text_input("Price")

        if st.button("Predict"):

            if not model:
                st.error("Please upload model first")

            elif not all([car_model, year, engine_size, horsepower, torque, ph_time, price]):
                st.error("Please fill all fields")

            else:
                try:
                    input_df = pd.DataFrame([{
                        "Car_Model": car_model,
                        "Year": int(year),
                        "Engine_Size": engine_size,
                        "Horsepower": float(horsepower),
                        "Torque": float(torque),
                        "PH_Time": float(ph_time),
                        "Price": float(price)
                    }])

                    prediction = model.predict(input_df)
                    st.success(f"🚗 Predicted Car Make: {prediction[0]}")

                except Exception as e:
                    st.error(f"Prediction Error: {e}")

    # ==========================
    # SPORTS QUIZ
    # ==========================
    elif st.session_state.page == "Sports Quiz":

        st.title("🏆 Sports Quiz")

        questions = [
            ("Which country won the FIFA World Cup 2022?", ["Brazil", "Argentina", "France", "Germany"], 1),
            ("How many players are there in a cricket team?", ["9", "10", "11", "12"], 2),
            ("Which sport uses a shuttlecock?", ["Tennis", "Badminton", "Hockey", "Football"], 1),
            ("Who is known as the 'King of Football'?", ["Messi", "Ronaldo", "Pele", "Neymar"], 2),
            ("How many rings are in the Olympic logo?", ["4", "5", "6", "7"], 1),
            ("Which sport is Virat Kohli famous for?", ["Football", "Cricket", "Tennis", "Basketball"], 1),
            ("In which sport is Wimbledon famous?", ["Cricket", "Tennis", "Hockey", "Kabaddi"], 1),
            ("Which country started the Olympic Games?", ["USA", "India", "Greece", "Japan"], 2),
            ("How many points is a goal worth in football?", ["1", "2", "3", "4"], 0),
            ("Which sport uses a racket?", ["Swimming", "Badminton", "Boxing", "Running"], 1),
        ]

        sarcastic_replies = [
            "Wow... confidently wrong!",
            "💀 Bro invented a new answer.",
            "ChatGPT is disappointed.",
            "Random click ah?",
            "🐢 Even a turtle answers better.",
            "😎 Confidence 100, Accuracy 0",
            "😂 Please borrow my brain for 2 minutes."
        ]

        if "quiz_index" not in st.session_state:
            st.session_state.quiz_index = 0
        if "score" not in st.session_state:
            st.session_state.score = 0
        if "correct_flag" not in st.session_state:
            st.session_state.correct_flag = False
        if "wrong_msg" not in st.session_state:
            st.session_state.wrong_msg = ""

        if st.session_state.quiz_index < len(questions):

            q, options, correct = questions[st.session_state.quiz_index]

            st.markdown(f"### Question {st.session_state.quiz_index + 1}: {q}")

            if not st.session_state.correct_flag:

                for i, opt in enumerate(options):
                    if st.button(opt, key=f"{st.session_state.quiz_index}_{i}"):

                        if i == correct:
                            st.session_state.correct_flag = True
                            st.session_state.score += 1
                            st.session_state.wrong_msg = ""
                        else:
                            st.session_state.wrong_msg = random.choice(sarcastic_replies)

                        st.rerun()

            if st.session_state.correct_flag:
                st.success("✅ Correct!")

                if st.button("➡ Next Question"):
                    st.session_state.quiz_index += 1
                    st.session_state.correct_flag = False
                    st.session_state.wrong_msg = ""
                    st.rerun()

            elif st.session_state.wrong_msg:
                st.error(st.session_state.wrong_msg)

        else:
            st.success(f"Quiz Finished! Score: {st.session_state.score}/{len(questions)}")

            if st.button("Restart Quiz"):
                st.session_state.quiz_index = 0
                st.session_state.score = 0
                st.session_state.correct_flag = False
                st.rerun()
