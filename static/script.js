document.getElementById("ingredients").addEventListener("input", function () {
    let outputDiv = document.getElementById("output");
    if (this.value.trim() === "") {
        outputDiv.innerHTML = ""; // Clear output when input is empty
    }
});

function getRecipe() {
    let ingredients = document.getElementById("ingredients").value.trim();
    let outputDiv = document.getElementById("output");

    if (ingredients === "") {
        alert("❗ Please enter at least one ingredient!");
        outputDiv.innerHTML = "";
        return;
    }

    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients: ingredients })
    })
    .then(response => response.json())
    .then(data => {
        outputDiv.innerHTML = "";

        if (data.recipes && data.recipes.length > 0) {
            outputDiv.innerHTML = "<strong>🥗 Recommended Recipes:</strong><br>";

            let recipesToShow = 3;  // Initially show 3 recipes
            let allRecipes = data.recipes;
            let displayedRecipes = allRecipes.slice(0, recipesToShow);

            displayedRecipes.forEach((recipe, index) => {
                let recipeElement = document.createElement("div");
                recipeElement.className = "recipe-item";
                recipeElement.innerHTML = `
                    <p>
                        <a href="#" onclick="showSteps(
                            '${encodeURIComponent(recipe.recipe_name)}', 
                            '${encodeURIComponent(recipe.ingredients)}', 
                            '${encodeURIComponent(recipe.instructions)}', 
                            '${encodeURIComponent(recipe.image)}',
                            event
                        )">${recipe.recipe_name} 🥘</a>
                    </p>
                `;
                outputDiv.appendChild(recipeElement);
            });

            // If more than 3 recipes exist, add "Show More" button
            if (allRecipes.length > recipesToShow) {
                let moreButton = document.createElement("button");
                moreButton.className = "btn btn-link text-primary";
                moreButton.innerText = "Show More...";
                moreButton.onclick = function () {
                    this.remove(); // Remove the button once clicked
                    allRecipes.slice(recipesToShow).forEach((recipe) => {
                        let recipeElement = document.createElement("div");
                        recipeElement.className = "recipe-item";
                        recipeElement.innerHTML = `
                            <p>
                                <a href="#" onclick="showSteps(
                                    '${encodeURIComponent(recipe.recipe_name)}', 
                                    '${encodeURIComponent(recipe.ingredients)}', 
                                    '${encodeURIComponent(recipe.instructions)}', 
                                    '${encodeURIComponent(recipe.image)}',
                                    event
                                )">${recipe.recipe_name} 🥘</a>
                            </p>
                        `;
                        outputDiv.appendChild(recipeElement);
                    });
                };
                outputDiv.appendChild(moreButton);
            }
        } else {
            outputDiv.innerHTML = "<p class='text-danger'>❌ No vegetarian recipes found.</p>";
        }
    })
    .catch(error => {
        outputDiv.innerHTML = "⚠️ Error fetching recipes.";
        console.error("Error:", error);
    });
}


function showSteps(name, ingredients, steps, image, event) {
    document.querySelectorAll(".recipe-details").forEach(el => el.remove());

    let formattedSteps = decodeURIComponent(steps)
        .replace(/\.\s+/g, ".|")
        .split("|")
        .filter(sentence => sentence.trim() !== '')
        .map(sentence => `<li>${sentence.trim()}</li>`)
        .join('');

    let detailsDiv = document.createElement("div");
    detailsDiv.className = "recipe-details";
    detailsDiv.innerHTML = `
        <p><strong style="color: orange;">🍽️ Recipe Name:</strong> ${decodeURIComponent(name)}</p>
        <p><strong style="color: green;">🛒 Ingredients:</strong> ${decodeURIComponent(ingredients)}</p>
        <p><strong style="color: blue;">📜 Steps:</strong></p>
        <ul>${formattedSteps}</ul>
        <div style="text-align: center; margin-top: 10px;">
            <img src="${decodeURIComponent(image)}" alt="${decodeURIComponent(name)}">
        </div>
    `;

    event.target.closest(".recipe-item").appendChild(detailsDiv);
}





