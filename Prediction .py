import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, classification_report

# ==========================================
# LOAD DATA
# ==========================================
a = pd.read_csv("archive (1)/Sport car price.csv")

# ==========================================
# CLEAN DATA
# ==========================================
a["Price"] = a["Price"].astype(str).str.replace(",", "", regex=True)
a["Price"] = pd.to_numeric(a["Price"])

a["Year"] = pd.to_numeric(a["Year"], errors="coerce").astype(int)
a["Horsepower"] = pd.to_numeric(a["Horsepower"], errors="coerce")
a["Torque"] = pd.to_numeric(a["Torque"], errors="coerce")
a["PH_Time"] = pd.to_numeric(a["PH_Time"], errors="coerce")

a["Car_Make"] = a["Car_Make"].astype(str)
a["Car_Model"] = a["Car_Model"].astype(str)
a["Engine_Size"] = a["Engine_Size"].astype(str)

# Fill missing values
for col in ["Year", "Horsepower", "Torque", "PH_Time", "Price"]:
    a[col] = a[col].fillna(a[col].median())

for col in ["Car_Make", "Car_Model", "Engine_Size"]:
    a[col] = a[col].fillna("Unknown")

# ==========================================
# SPLIT DATA
# ==========================================
X = a.drop("Car_Make", axis=1)
y = a["Car_Make"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ONLY categorical features
cat_features = ["Car_Model", "Engine_Size"]

# ==========================================
# MODEL TRAINING
# ==========================================
model = CatBoostClassifier(
    iterations=500,
    learning_rate=0.1,
    depth=6,
    verbose=0
)

model.fit(X_train, y_train, cat_features=cat_features)

# ==========================================
# SAVE MODEL
# ==========================================
joblib.dump(model, "car_make_model.pkl")
print("Model saved!")

# ==========================================
# LOAD MODEL
# ==========================================
loaded_model = joblib.load("car_make_model.pkl")
print("Model loaded!")

# ==========================================
# TEST ACCURACY
# ==========================================
y_pred = loaded_model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nReport:\n", classification_report(y_test, y_pred))

# ==========================================
# USER INPUT PREDICTION
# ==========================================
print("\nEnter Car Details:")

car_model = input("Car Model (e.g., 911): ")
year = int(input("Year (e.g., 2022): "))
engine_size = input("Engine Size (e.g., 3): ")
horsepower = float(input("Horsepower: "))
torque = float(input("Torque: "))
ph_time = float(input("0-100 km/h Time: "))
price = float(input("Price: "))

new_data = pd.DataFrame({
    "Car_Model": [car_model],
    "Year": [year],
    "Engine_Size": [engine_size],
    "Horsepower": [horsepower],
    "Torque": [torque],
    "PH_Time": [ph_time],
    "Price": [price]
})

prediction = loaded_model.predict(new_data)

print("\n🚗 Predicted Car Make:", prediction[0])