import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# -------------------------
# LOAD DATASET
# -------------------------

df = pd.read_csv("drone_dataset.csv")

# -------------------------
# FEATURES / LABELS
# -------------------------

X = df.drop("action", axis=1)
y = df["action"]

# -------------------------
# SPLIT
# -------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -------------------------
# MODEL
# -------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# -------------------------
# TRAIN
# -------------------------

model.fit(X_train, y_train)

# -------------------------
# TEST
# -------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print(f"Accuracy: {accuracy * 100:.2f}%")

# -------------------------
# SAVE MODEL
# -------------------------

joblib.dump(
    model,
    "drone_decision_model.pkl"
)

print("Model saved successfully.")