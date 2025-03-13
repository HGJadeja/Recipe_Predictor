import pandas as pd

# Load dataset
df = pd.read_csv("Cleaned_Indian_Food_Dataset.csv")

df.rename(columns={
    "TranslatedRecipeName": "recipe_name",
    "Cleaned-Ingredients": "ingredients"
}, inplace=True)

# Define a list of common non-vegetarian ingredients
non_veg_items = ["chicken", "fish", "egg", "mutton", "pork", "beef", "shrimp", "crab", "prawn"]

# Function to check if a recipe is vegetarian
def is_vegetarian(ingredients):
    return not any(item in ingredients.lower() for item in non_veg_items)

# Apply the function to create the "veg" column (1 = vegetarian, 0 = non-vegetarian)
df["veg"] = df["ingredients"].astype(str).apply(is_vegetarian).astype(int)

# Save the modified dataset
df.to_csv("Cleaned_Indian_Food_Dataset.csv", index=False)

print("✅ Veg column added successfully!")
