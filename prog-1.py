import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Load data
data = pd.read_csv("info0.csv")

# Features and target
X = data[['Hours']]
y = data['Marks']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = LinearRegression()
model.fit(X_train, y_train)

# Prediction
pred = model.predict(X_test)

# Accuracy (R2 Score)
print("R2 Score (Model Accuracy):", r2_score(y_test, pred))

# Graph
plt.scatter(X, y)
plt.plot(X, model.predict(X), color='red')
plt.xlabel("Hours")
plt.ylabel("Marks")
plt.title("Study Hours vs Marks")
plt.show()

# User Input
hours = float(input("Enter study hours: "))
result = model.predict([[hours]])
print("Predicted marks:", result[0])