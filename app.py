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



# import streamlit as st
# import pandas as pd
# import pickle
# import os
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.ensemble import RandomForestClassifier

# # UI Styling
# st.set_page_config(page_title="Indian Vegetarian Recipe Finder", layout="centered")

# # File Paths
# MODEL_PATH = "model/recipe_model.pkl"
# VECTORIZER_PATH = "model/vectorizer.pkl"
# DATA_PATH = "Cleaned_Indian_Food_Dataset.csv"

# # Ensure the model directory exists
# os.makedirs("model", exist_ok=True)

# # Load Dataset
# @st.cache_data
# def load_data():
#     df = pd.read_csv(DATA_PATH)
#     df.rename(columns={"TranslatedRecipeName": "recipe_name", "Cleaned-Ingredients": "ingredients",
#                        "TranslatedInstructions": "instructions", "image-url": "image", "Veg": "veg"}, inplace=True)
#     return df[df["veg"] == 1]  # Keep only vegetarian recipes

# df = load_data()

# # Train Model (if not already trained)
# @st.cache_resource
# def train_model():
#     df_filtered = df.copy()
#     df_filtered["ingredients"] = df_filtered["ingredients"].fillna("").str.lower().str.replace(",", " ")

#     vectorizer = TfidfVectorizer(stop_words="english")
#     X = vectorizer.fit_transform(df_filtered["ingredients"])
#     y = df_filtered["recipe_name"]

#     model = RandomForestClassifier(n_estimators=100, random_state=42)
#     model.fit(X, y)

#     with open(MODEL_PATH, "wb") as f:
#         pickle.dump(model, f)
#     with open(VECTORIZER_PATH, "wb") as f:
#         pickle.dump(vectorizer, f)

#     return model, vectorizer

# # Load or Train Model
# if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
#     with open(MODEL_PATH, "rb") as f:
#         model = pickle.load(f)
#     with open(VECTORIZER_PATH, "rb") as f:
#         vectorizer = pickle.load(f)
# else:
#     model, vectorizer = train_model()

# # Initialize session state
# if "recipes" not in st.session_state:
#     st.session_state.recipes = None
# if "show_more" not in st.session_state:
#     st.session_state.show_more = False


# st.markdown("""
#     <style>
#     body { font-family: 'Poppins', sans-serif; background: linear-gradient(135deg, #ffeb3b, #ff9800); text-align: center; }
#     .stTextArea, .stButton, .stMarkdown { text-align: center; }
#     .recipe-item { background: #f8f9fa; padding: 10px; border-radius: 8px; margin-top: 10px; cursor: pointer; transition: 0.3s; }
#     .recipe-item:hover { background: #e9ecef; }
#     .recipe-details { padding: 10px; background: #fff3cd; border-radius: 8px; margin-top: 10px; }
#     img { max-width: 100%; border-radius: 10px; margin-top: 10px; }
#     </style>
#     """, unsafe_allow_html=True)

# # App Title
# st.markdown("<h2 style='text-align: center; color: green;'>🍛 Indian Vegetarian Recipe Finder</h2>", unsafe_allow_html=True)
# st.markdown("<p style='text-align: center; color: gray;'>Enter ingredients to find the best recipes!</p>", unsafe_allow_html=True)

# # Input for Ingredients
# ingredients = st.text_area("Enter ingredients (comma-separated)", placeholder="e.g., potato, tomato")

# # List of non-veg keywords
# NON_VEG_ITEMS = {"chicken", "mutton", "fish", "egg", "pork", "beef", "prawn", "shrimp", "lamb", "bacon"}

# # Clear output when input is empty
# if not ingredients.strip() and st.session_state.recipes is not None:
#     st.session_state.recipes = None
#     st.rerun()

# # Prediction Function
# def predict_recipes(ingredients):
#     input_ingredients = {ing.strip().lower() for ing in ingredients.split(",")}
    
#     # Check for non-veg items
#     if input_ingredients & NON_VEG_ITEMS:
#         return "❌ Only vegetarian items are allowed!", None

#     # Filter recipes that contain *all* input ingredients
#     filtered_recipes = df[df["ingredients"].apply(lambda x: all(ing in x.lower() for ing in input_ingredients))]

#     if filtered_recipes.empty:
#         return "😕 No matching recipes found. Try different ingredients!", None


#     return None, filtered_recipes[["recipe_name", "ingredients", "instructions", "image"]].to_dict(orient="records")


# # Fetch Recipes
# if st.button("🔍 Find Recipes"):
#     if ingredients.strip():
#         input_ingredients = {ing.strip().lower() for ing in ingredients.split(",")}

#         if any(ing in NON_VEG_ITEMS for ing in input_ingredients):
#             st.error("🚫 Only vegetarian items are allowed!")
#             st.session_state.recipes = None
#         else:
#             error, recipes = predict_recipes(ingredients)
#             if error:
#                 st.error(error)
#                 st.session_state.recipes = None
#             elif recipes:
#                 st.session_state.recipes = recipes
#                 st.session_state.show_more = False
#             else:
#                 st.session_state.recipes = []
#     else:
#         st.warning("❗ Please enter at least one ingredient!")
#         st.session_state.recipes = None

# # Display Recipes
# if st.session_state.recipes:
#     recipes = st.session_state.recipes
#     num_display = 5 if not st.session_state.show_more else len(recipes)

#     st.markdown("<strong>🥗 Recommended Recipes:</strong>", unsafe_allow_html=True)
    
#     for recipe in recipes[:num_display]:
#         with st.expander(f"🥘 {recipe['recipe_name']}"):
#             st.markdown("**🛒 Ingredients:**", unsafe_allow_html=True)
#             st.markdown(f"<p style='margin-left: 20px; text-align: left;'>{', '.join(recipe['ingredients'].split(','))}</p>", unsafe_allow_html=True)

#             st.markdown("**📜 Steps:**", unsafe_allow_html=True)
#             steps_html = "<ul style='text-align: left;'>"
#             for step in recipe["instructions"].replace(". ", ".\n").split("\n"):
#                 step = step.strip()
#                 if step:
#                     steps_html += f"<li>{step}.</li>"
#             steps_html += "</ul>"

#             st.markdown(steps_html, unsafe_allow_html=True)
#             if recipe["image"]:
#                 st.image(recipe["image"], caption=recipe["recipe_name"], use_container_width=True)

#     if len(recipes) > 5 and not st.session_state.show_more:
#         if st.button("⬇️ Show More Recipes"):
#             st.session_state.show_more = True
#             st.rerun()




