#pip install flask scikit-learn pandas joblib

from flask import Flask, request, jsonify
import joblib
import numpy as np

# Load trained model and scaler
model = joblib.load("titanic_model.pkl")
scaler = joblib.load("scaler.pkl")

# Initialize Flask app
app = Flask(__name__)

@app.route('/predict', methods=['GET'])
def predict():
    try:
        # Get 'age' from request args
        age = request.args.get("age", type=float)
        
        # Validate input
        if age is None:
            return jsonify({"error": "Missing 'age' parameter"}), 400
        
        # Standardize Age using the same scaler from training
        age_scaled = scaler.transform(np.array([[age]]))
        
        # Make prediction
        prediction = model.predict(age_scaled)[0]
        survival = "Survived" if prediction == 1 else "Did not survive"
        
        # Return response as JSON
        return jsonify({
            "age": age,
            "prediction": survival
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

