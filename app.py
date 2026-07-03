import streamlit as st
import pandas as pd
import joblib
import sqlite3
import base64
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
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

        /* MAIN TITLE */
        h1 {{
            color: #ffffff !important;
            text-shadow: 2px 2px 6px #000;
        }}

        /* SIDEBAR */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #111827, #1f2937);
        }}

        section[data-testid="stSidebar"] * {{
            color: white !important;
        }}

        /* BUTTONS */
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

        /* INPUT BOXES */
        input, textarea {{
            border-radius: 8px !important;
            border: 1px solid #60a5fa !important;
            background-color: rgba(255,255,255,0.85) !important;
        }}

        /* SUCCESS / WARNING */
        .stSuccess {{
            background-color: #064e3b !important;
            color: #d1fae5 !important;
        }}

        .stWarning {{
            background-color: #78350f !important;
            color: #fde68a !important;
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

        if pkl_file is not None:
            model = joblib.load(pkl_file)
            st.success("Model Loaded Successfully")

            st.subheader("📄 Upload Dataset (CSV)")
            csv_file = st.file_uploader("Upload CSV", type=["csv"])

            if csv_file is not None:

                df = pd.read_csv(csv_file)

                df["Price"] = df["Price"].astype(str).str.replace(",", "", regex=True)
                df["Price"] = pd.to_numeric(df["Price"])

                df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype(int)
                df["Horsepower"] = pd.to_numeric(df["Horsepower"], errors="coerce")
                df["Torque"] = pd.to_numeric(df["Torque"], errors="coerce")
                df["PH_Time"] = pd.to_numeric(df["PH_Time"], errors="coerce")

                df["Car_Model"] = df["Car_Model"].astype(str)
                df["Engine_Size"] = df["Engine_Size"].astype(str)
                df["Car_Make"] = df["Car_Make"].astype(str)

                X = df.drop("Car_Make", axis=1)
                y = df["Car_Make"]

                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )

                pred = model.predict(X_test)
                acc = accuracy_score(y_test, pred)

                st.success(f"📊 Accuracy: {acc*100:.2f}%")

            st.subheader("🚗 Predict Car Make")

            car_model = st.text_input("Car Model")
            year = st.text_input("Year")
            engine_size = st.text_input("Engine Size")
            horsepower = st.text_input("Horsepower")
            torque = st.text_input("Torque")
            ph_time = st.text_input("0-100 km/h Time")
            price = st.text_input("Price")

            if st.button("Predict"):

                if not all([car_model, year, engine_size, horsepower, torque, ph_time, price]):
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

    ("Which sport uses a shuttlecock?", ["Tennis", "Badminton", "Hockey", "Football"], 0),

    ("Who is known as the 'King of Football'?", ["Messi", "Ronaldo", "Pele", "Neymar"], 2),

    ("How many rings are in the Olympic logo?", ["4", "5", "6", "7"], 1),

    ("Which sport is Virat Kohli famous for?", ["Football", "Cricket", "Tennis", "Basketball"], 1),

    ("In which sport is Wimbledon famous?", ["Cricket", "Tennis", "Hockey", "Kabaddi"], 1),

    ("Which country started the Olympic Games?", ["USA", "India", "Greece", "Japan"], 2),

    ("How many points is a goal worth in football?", ["1", "2", "3", "4"], 0),

    ("Which sport uses a racket?", ["Swimming", "Badminton", "Boxing", "Running"], 1),

    ("Who is called the 'God of Cricket'?", ["MS Dhoni", "Virat Kohli", "Rohit Sharma", "Sachin Tendulkar"], 3),

    ("Which sport has NBA league?", ["Baseball", "Basketball", "Football", "Tennis"], 1),

    ("Which country is famous for sumo wrestling?", ["China", "Japan", "Korea", "Thailand"], 1),

        ("How many rings are in the Olympic logo?", ["4", "5", "6", "7"], 1),
        ]

        sarcastic_replies = [
            "Wow... confidently wrong!",
            "💀 Bro invented a new answer.",
            "chatgpt gave you the wrong answer bro..",
            "Random click ah?",
            "🐢 Even a turtle answers faster and better.",
            "😎 Confidence: 100, Accuracy: 0"
            "😂 Please borrow my brain for 2 minutes.",
        ]

        if "quiz_index" not in st.session_state:
            st.session_state.quiz_index = 0
        if "score" not in st.session_state:
            st.session_state.score = 0

        if "quiz_index" not in st.session_state:
            st.session_state.quiz_index = 0
        if "score" not in st.session_state:
            st.session_state.score = 0
        if "answered" not in st.session_state:
            st.session_state.answered = False
        if "correct_flag" not in st.session_state:
            st.session_state.correct_flag = False
        if "wrong_msg" not in st.session_state:
            st.session_state.wrong_msg = ""

        if st.session_state.quiz_index < len(questions):

            q, options, correct = questions[st.session_state.quiz_index]

            st.markdown(f"### Question {st.session_state.quiz_index + 1}: {q}")

            # OPTIONS (buttons) - stay visible until the CORRECT answer is picked
            if not st.session_state.correct_flag:

                for i, opt in enumerate(options):
                    if st.button(opt, key=f"{st.session_state.quiz_index}_{i}_{st.session_state.get('attempt', 0)}"):

                        if opt == options[correct]:
                            st.session_state.correct_flag = True
                            st.session_state.score += 1
                            st.session_state.wrong_msg = ""
                        else:
                            st.session_state.correct_flag = False
                            st.session_state.wrong_msg = random.choice(sarcastic_replies)
                            st.session_state.attempt = st.session_state.get("attempt", 0) + 1

                        st.rerun()

            # RESULT BELOW OPTIONS
            if st.session_state.correct_flag:
                st.success("✅ Correct!")

                if st.button("➡ Next Question"):
                    st.session_state.quiz_index += 1
                    st.session_state.answered = False
                    st.session_state.correct_flag = False
                    st.session_state.wrong_msg = ""
                    st.session_state.attempt = 0
                    st.rerun()

            elif st.session_state.wrong_msg:
                st.markdown(
                    f"""
                    <div style="
                        background-color:black;
                        color:darkred;
                        padding:12px;
                        border-radius:10px;
                        font-weight:bold;
                        margin-top:10px;">
                        {st.session_state.wrong_msg}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:
            st.success(f"Quiz Finished! Score: {st.session_state.score}/{len(questions)}")

            if st.button("Restart Quiz"):
                st.session_state.quiz_index = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.session_state.correct_flag = False
                st.rerun()
