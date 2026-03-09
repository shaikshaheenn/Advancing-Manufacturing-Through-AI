import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

os.makedirs('ai_models', exist_ok=True)

np.random.seed(42)
n = 2000

temperature    = np.random.normal(75, 15, n)
vibration      = np.random.normal(0.5, 0.2, n)
pressure       = np.random.normal(100, 20, n)
runtime_hours  = np.random.uniform(0, 5000, n)

failure = (
    (temperature > 95) |
    (vibration > 0.85) |
    ((runtime_hours > 4000) & (temperature > 80))
).astype(int)

noise_mask = np.random.rand(n) < 0.05
failure[noise_mask] = 1 - failure[noise_mask]

df = pd.DataFrame({
    'temperature':    temperature,
    'vibration':      vibration,
    'pressure':       pressure,
    'runtime_hours':  runtime_hours,
    'failure':        failure
})

df.to_csv('ai_models/maintenance_dataset.csv', index=False)
print(f"Dataset: {len(df)} rows | Failures: {failure.sum()} ({failure.mean()*100:.1f}%)")

X = df[['temperature', 'vibration', 'pressure', 'runtime_hours']]
y = df['failure']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
print(classification_report(y_test, y_pred))

joblib.dump(model, 'ai_models/maintenance_model.pkl')
print("Saved: ai_models/maintenance_model.pkl ✅")
