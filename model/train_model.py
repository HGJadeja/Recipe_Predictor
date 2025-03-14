import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv("Cleaned_Indian_Food_Dataset.csv")

# Rename columns for consistency
df.rename(columns={
    "TranslatedRecipeName": "recipe_name",
    "Cleaned-Ingredients": "ingredients",
    "Veg": "veg"
}, inplace=True)

# Keep only vegetarian recipes (1 = Veg, 0 = Non-Veg)
df = df[df["veg"] == 1]

print(f"Total vegetarian recipes: {len(df)}")

# Remove recipes with only one occurrence
recipe_counts = df["recipe_name"].value_counts()
valid_recipes = recipe_counts[recipe_counts >= 2].index
df = df[df["recipe_name"].isin(valid_recipes)]

# Ensure enough samples exist
num_classes = df["recipe_name"].nunique()
min_samples = num_classes * 2  # Minimum needed (2 samples per class)

if len(df) < min_samples:
    raise ValueError(f"Dataset too small! Only {len(df)} samples for {num_classes} classes.")

# Data Preprocessing
df["ingredients"] = df["ingredients"].fillna("").str.lower().str.replace(",", " ")

# Vectorization (TF-IDF)
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(df["ingredients"])
y = df["recipe_name"]

# Adjust test_size dynamically
test_size = max(0.2, num_classes / len(df))  # Ensures test size is valid

# Split dataset into train and test sets (stratified for balance)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, stratify=y, random_state=42)

# Train Model (Random Forest)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate Model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model trained successfully! Accuracy: {accuracy:.4f}")

# Save Model & Vectorizer
with open("model/recipe_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("model/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
