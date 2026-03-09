import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

os.makedirs('ai_models', exist_ok=True)
np.random.seed(42)
n = 1500

delivery_days     = np.random.randint(1, 60, n)
price_volatility  = np.random.uniform(0, 1, n)
past_delays       = np.random.randint(0, 10, n)
distance_km       = np.random.randint(100, 5000, n)
defect_rate       = np.random.uniform(0, 0.2, n)

risk_score = (
    (delivery_days > 30).astype(int) +
    (price_volatility > 0.65).astype(int) +
    (past_delays > 4).astype(int) +
    (distance_km > 2500).astype(int) +
    (defect_rate > 0.1).astype(int)
)

risk_label = np.where(risk_score >= 3, 'high', np.where(risk_score >= 1, 'medium', 'low'))

df = pd.DataFrame({
    'delivery_days':    delivery_days,
    'price_volatility': price_volatility,
    'past_delays':      past_delays,
    'distance_km':      distance_km,
    'defect_rate':      defect_rate,
    'risk':             risk_label
})

df.to_csv('ai_models/supply_dataset.csv', index=False)
print(f"Supply dataset: {len(df)} rows")
print(df['risk'].value_counts())

le = LabelEncoder()
df['risk_encoded'] = le.fit_transform(df['risk'])

X = df[['delivery_days', 'price_volatility', 'past_delays', 'distance_km', 'defect_rate']]
y = df['risk_encoded']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = GradientBoostingClassifier(n_estimators=150, max_depth=4, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
print(classification_report(y_test, y_pred, target_names=le.classes_))

joblib.dump(model, 'ai_models/supply_model.pkl')
joblib.dump(le,    'ai_models/supply_label_encoder.pkl')
print("Saved: ai_models/supply_model.pkl ✅")
print("Saved: ai_models/supply_label_encoder.pkl ✅")
