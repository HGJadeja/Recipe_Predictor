import pickle
import pandas as pd
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Load trained model and vectorizer
with open("model/recipe_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("model/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# Load updated dataset
df = pd.read_csv("Cleaned_Indian_Food_Dataset.csv")

# Rename relevant columns for easier access
df.rename(columns={
    "TranslatedRecipeName": "recipe_name",
    "Cleaned-Ingredients": "ingredients",
    "TranslatedInstructions": "instructions",
    "image-url": "image",
    "Veg": "veg"
}, inplace=True)

# Keep only vegetarian recipes
df = df[df["veg"] == 1]

# List of non-veg keywords
NON_VEG_ITEMS = {"chicken", "mutton", "fish", "egg", "pork", "beef", "prawn", "shrimp", "lamb", "bacon"}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    ingredients = data.get("ingredients", "").lower().strip()

    if not ingredients:
        return jsonify({"error": "❌ Please enter at least one ingredient."}), 400

    input_ingredients = {ing.strip() for ing in ingredients.split(",")}

    # Check if any non-veg ingredient is present
    if input_ingredients & NON_VEG_ITEMS:
        return jsonify({"error": "❌ Only vegetarian recipes are available!"}), 400

    # Ensure lowercase ingredients for matching
    df["ingredients"] = df["ingredients"].astype(str).str.lower()

    # Filter recipes that contain all input ingredients
    matching_recipes = df[df["ingredients"].apply(lambda x: all(ing in x for ing in input_ingredients))]

    if matching_recipes.empty:
        return jsonify({"recipes": []})

    # Convert filtered data to dictionary format
    recipes_list = matching_recipes[["recipe_name", "ingredients", "instructions", "image"]].to_dict(orient="records")

    return jsonify({"recipes": recipes_list})

if __name__ == "__main__":
    app.run(debug=True)
