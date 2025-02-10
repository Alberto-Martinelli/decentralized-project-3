# pip install flask scikit-learn pandas joblib
import json
from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
models = {
    "logistic_regression": joblib.load(os.path.join(BASE_DIR, "data", "logreg_model.pkl")),
    "random_forest": joblib.load(os.path.join(BASE_DIR, "data", "rf_model.pkl")),
    "svm": joblib.load(os.path.join(BASE_DIR, "data", "svm_model.pkl"))
}
preprocessor = joblib.load(os.path.join(BASE_DIR, "data", "preprocessor.pkl"))


try:
    with open(os.path.join(BASE_DIR, "data","model_weights.json"), "r") as f:
        weights = np.array(list(json.load(f).values()))
except FileNotFoundError:
    weights = np.array([1/3, 1/3, 1/3])  


# Initialize Flask app
app = Flask(__name__)

# ----------------------- Q1: Define model prediction function -------------------------------------
def predict_survival(model_name, features):
    """Preprocess input features and predict survival using the selected model."""
    try:
        if model_name not in models:
            return jsonify({"error": f"Model '{model_name}' not found"}), 404

        model = models[model_name]

        # Convert input features into a Pandas DataFrame with correct column names
        feature_columns = ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked']
        features_df = pd.DataFrame([features], columns=feature_columns)

        # Transform input using the same preprocessing pipeline (includes OneHotEncoder & StandardScaler)
        features_scaled = preprocessor.transform(features_df)

        # Make prediction
        prediction = model.predict(features_scaled)[0]
        survival = "Survived" if prediction == 1 else "Did not survive"

        return jsonify({
            "model": model_name,
            "input_features": features_df.to_dict(orient="records")[0],  # Convert DataFrame row to dictionary
            "prediction": survival
        })

    except ValueError as ve:
        return jsonify({"error": f"Value Error: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper function to get and validate request parameters
def get_request_features():
    """Extracts and processes query parameters from GET request."""
    try:
        pclass = request.args.get("pclass", type=int)
        sex = request.args.get("sex", type=str).lower()  # Keep as string for OneHotEncoder
        age = request.args.get("age", type=float)
        sibsp = request.args.get("sibsp", type=int)
        parch = request.args.get("parch", type=int)
        fare = request.args.get("fare", type=float)
        embarked = request.args.get("embarked", type=str).upper()  # Keep as string for OneHotEncoder

        # Check for missing values
        if None in [pclass, sex, age, sibsp, parch, fare, embarked]:
            return jsonify({"error": "Missing one or more required parameters"}), 400

        return [pclass, sex, age, sibsp, parch, fare, embarked]  # Keep categorical variables in string format

    except ValueError:
        return jsonify({"error": "Invalid input: Ensure all numerical fields contain valid numbers."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

# Define API routes for each model
@app.route('/predict/logistic_regression', methods=['GET'])
def predict_logistic_regression():
    """Predict survival using Logistic Regression."""
    features = get_request_features()
    return predict_survival("logistic_regression", features)

@app.route('/predict/random_forest', methods=['GET'])
def predict_random_forest():
    """Predict survival using Random Forest."""
    features = get_request_features()
    return predict_survival("random_forest", features)

@app.route('/predict/svm', methods=['GET'])
def predict_svm():
    """Predict survival using Support Vector Machine."""
    features = get_request_features()
    return predict_survival("svm", features)

# -------------------------- Q2: Define a route to generate a consensus prediction----------------------------------------
@app.route('/predict/consensus', methods=['GET'])
def predict_consensus():
    """Generate a consensus prediction by averaging outputs from all models."""
    try:
        features = get_request_features()
        
        # Convert features into DataFrame for preprocessing
        features_df = pd.DataFrame([features], columns=['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked'])
        features_transformed = preprocessor.transform(features_df)

        # Collect individual predictions from all models
        individual_predictions = {}
        predictions = []

        for model_name, model in models.items():
            prediction = model.predict(features_transformed)[0]
            predictions.append(int(prediction))  # Convert int64 to Python int
            individual_predictions[model_name] = "Survived" if prediction == 1 else "Did not survive"

        # Calculate consensus (average prediction)
        avg_prediction = int(round(sum(predictions) / len(predictions)))  # Convert to Python int
        survival = "Survived" if avg_prediction == 1 else "Did not survive"

        return jsonify({
            "model": "consensus",
            "input_features": {
                "pclass": features[0],
                "sex": features[1],
                "age": features[2],
                "sibsp": features[3],
                "parch": features[4],
                "fare": features[5],
                "embarked": features[6]
            },
            "individual_predictions": individual_predictions,
            "final_prediction": survival
        })

    except ValueError as ve:
        return jsonify({"error": f"Value Error: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# -------------------------- Q3: Define a route to generate a weighted consensus prediction--------------------------------
@app.route('/predict/weighted_consensus', methods=['GET'])
def predict_weighted_consensus():
    """Generate a weighted consensus prediction using dynamically adjusted model weights."""
    try:
        # Extract request parameters
        features = get_request_features()
        if features is None:
            return jsonify({"error": "Missing or invalid input parameters"}), 400

        # Convert input into a DataFrame for preprocessing
        features_df = pd.DataFrame([features], columns=['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked'])
        
        # Preprocess input features
        features_scaled = preprocessor.transform(features_df)

        # Collect individual model predictions
        individual_predictions = {
            model_name: int(model.predict(features_scaled)[0])  
            for model_name, model in models.items()
        }

        # Compute weighted consensus prediction
        model_preds = np.array(list(individual_predictions.values()))
        weighted_prediction = int(round(np.average(model_preds, weights=weights)))

        # Convert to human-readable format
        survival = "Survived" if weighted_prediction == 1 else "Did not survive"

        return jsonify({
            "model": "weighted_consensus",
            "weights": {model_name: weight for model_name, weight in zip(models.keys(), weights)},
            "input_features": {
                "pclass": features[0],
                "sex": "male" if features[1] == 1 else "female",
                "age": features[2],
                "sibsp": features[3],
                "parch": features[4],
                "fare": features[5],
                "embarked": {0: "C", 1: "Q", 2: "S"}.get(features[6], "Unknown")
            },
            "individual_predictions": individual_predictions,
            "final_prediction": survival
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)