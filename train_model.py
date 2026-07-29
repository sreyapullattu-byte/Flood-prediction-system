import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

# Load dataset
data = pd.read_csv("data/train.csv")

# Select only the 6 features used in the website
X = data[[
    "MonsoonIntensity",
    "TopographyDrainage",
    "RiverManagement",
    "Deforestation",
    "Urbanization",
    "ClimateChange"
]]

# Target column
y = data["FloodProbability"]

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Create models folder
os.makedirs("models", exist_ok=True)

# Save model
joblib.dump(model, "models/flood_model.pkl")

print("✅ Model trained successfully!")
print("✅ Model saved in models/flood_model.pkl")