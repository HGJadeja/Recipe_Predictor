import streamlit as st
import requests
import json

# Streamlit UI Configuration
st.set_page_config(page_title="Indian Vegetarian Recipe Finder", layout="centered")


# Initialize session state for handling "Show More"
if "show_more" not in st.session_state:
    st.session_state.show_more = False  # Initially set to False

# Custom CSS for UI Styling
st.markdown(
    """
    <style>
    body {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #ffeb3b, #ff9800);
        text-align: center;
    }
    .stTextArea, .stButton, .stMarkdown {
        text-align: center;
    }
    .recipe-item {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin-top: 10px;
        cursor: pointer;
        transition: 0.3s;
    }
    .recipe-item:hover {
        background: #e9ecef;
    }
    .recipe-details {
        padding: 10px;
        background: #fff3cd;
        border-radius: 8px;
        margin-top: 10px;
    }
    img {
        max-width: 100%;
        border-radius: 10px;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# App Title
st.markdown("<h2 style='text-align: center; color: green;'>🍛 Indian Vegetarian Recipe Finder</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Enter ingredients to find the best recipes!</p>", unsafe_allow_html=True)

# Initialize session state for recipes
if "recipes" not in st.session_state:
    st.session_state.recipes = None

# Input for Ingredients
ingredients = st.text_area("Enter ingredients (comma-separated)", placeholder="e.g., potato, tomato")

# List of non-veg keywords
non_veg_items = {"chicken", "mutton", "fish", "egg", "pork", "beef", "prawn", "shrimp", "lamb", "bacon"}

# Clear output when input is empty
if not ingredients.strip() and st.session_state.recipes is not None:
    st.session_state.recipes = None
    st.rerun() 

# Button to fetch recipes
if st.button("🔍 Find Recipes"):
    if ingredients.strip():
        input_ingredients = {ing.strip().lower() for ing in ingredients.split(",")}

        # Check for non-veg items
        if any(ing in non_veg_items for ing in input_ingredients):
            st.error("🚫 Only vegetarian items are allowed!")
            st.session_state.recipes = None  # Clear previous results
        else:
            # Call Flask API 
            response = requests.post("http://127.0.0.1:5000/predict", json={"ingredients": ingredients})
            
            if response.status_code == 200:
                data = response.json()
                if data["recipes"]:
                    st.session_state.recipes = data["recipes"]  # Store recipes in session state
                    st.session_state.show_more = False 
                else:
                    st.session_state.recipes = []  # No recipes found
            else:
                st.error("⚠️ Error fetching recipes. Please try again later.")
                st.session_state.recipes = None  # Clear output on error
    else:
        st.warning("❗ Please enter at least one ingredient!")
        st.session_state.recipes = None  # Clear output if empty


# **Display Recipes (if available)**
if "recipes" in st.session_state and st.session_state.recipes:
    recipes = st.session_state.recipes
    num_display = 5 if not st.session_state.show_more else len(recipes)

    st.markdown("<strong>🥗 Recommended Recipes:</strong>", unsafe_allow_html=True)
    
    for i, recipe in enumerate(recipes[:num_display]):
        with st.expander(f"🥘 {recipe['recipe_name']}"):
            # Ingredients Section (Properly aligned in a single row)
            st.markdown("**🛒 Ingredients:**", unsafe_allow_html=True)
            st.markdown(f"<p style='margin-left: 20px; text-align: left;'>{', '.join(recipe['ingredients'].split(','))}</p>", unsafe_allow_html=True)

            # Steps Section (Ensuring Proper Bullet Points & Left Alignment)
            st.markdown("**📜 Steps:**", unsafe_allow_html=True)
            steps = recipe["instructions"].replace(". ", ".\n").split("\n")   

            # Using HTML for proper formatting
            steps_html = "<ul style='text-align: left;'>"
            for step in steps:
                step = step.strip()
                if step:  # Ensure the step is not empty
                    steps_html += f"<li>{step}.</li>"  # Re-add the period at the end
            steps_html += "</ul>"

            st.markdown(steps_html, unsafe_allow_html=True)

            # Display Image (if available)
            if recipe["image"]:
                st.image(recipe["image"], caption=recipe["recipe_name"], use_container_width=True)

    # **Show "Show More" button if recipes are more than 5**
    if len(recipes) > 5 and not st.session_state.show_more:
        if st.button("⬇️ Show More Recipes"):
            st.session_state.show_more = True
            st.rerun()


