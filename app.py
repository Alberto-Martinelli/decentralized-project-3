# pip install flask scikit-learn pandas joblib
from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd

# Load trained models and preprocessing pipeline
models = {
    "logistic_regression": joblib.load("logreg_model.pkl"),
    "random_forest": joblib.load("rf_model.pkl"),
    "svm": joblib.load("svm_model.pkl")
}
preprocessor = joblib.load("preprocessor.pkl")  # Load the preprocessing pipeline

# Initialize Flask app
app = Flask(__name__)

# Define model prediction function
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

# Define a route to generate a consensus prediction
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


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)