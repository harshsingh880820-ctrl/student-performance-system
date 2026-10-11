import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Training data
data = {
    "attendance": [55, 60, 65, 70, 72, 75, 78, 80, 82, 85,
                   88, 90, 92, 95, 98],
    "assignment": [50, 55, 60, 65, 68, 70, 72, 75, 78, 80,
                   83, 85, 88, 92, 96],
    "internal_marks": [45, 50, 55, 60, 62, 65, 68, 70, 73, 76,
                       80, 83, 86, 90, 95],
    "previous_marks": [48, 52, 58, 62, 65, 68, 70, 73, 76, 79,
                       82, 85, 88, 92, 96],
    "study_hours": [1, 1.5, 2, 2.5, 2.5, 3, 3, 3.5, 4, 4,
                    4.5, 5, 5.5, 6, 7],
    "performance": [45, 50, 55, 60, 63, 66, 69, 72, 75, 78,
                    81, 84, 87, 92, 96]
}

df = pd.DataFrame(data)

X = df[
    ["attendance", "assignment", "internal_marks",
     "previous_marks", "study_hours"]
]

y = df["performance"]

# Train ML model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)


def predict_performance(attendance, assignment,
                        internal_marks, previous_marks,
                        study_hours):

    input_data = pd.DataFrame([{
        "attendance": attendance,
        "assignment": assignment,
        "internal_marks": internal_marks,
        "previous_marks": previous_marks,
        "study_hours": study_hours
    }])

    prediction = model.predict(input_data)[0]

    return round(float(prediction), 2)