// suggestio drop list
document.addEventListener("DOMContentLoaded", function() {
    fetch('/products')
        .then(response => response.json())
        .then(data => {
            const datalist = document.getElementById("productSuggestions");
            data.forEach(product => {
                const option = document.createElement("option");
                option.value = product.product_name;
                datalist.appendChild(option);
            });
        })
        .catch(error => console.error("Error loading products:", error));
});

// When the "Get Recommendations" button is clicked, read the search field value
document.getElementById("recommendBtn").addEventListener("click", function(){
    const productName = document.getElementById("productInput").value;
    if (!productName) {
        alert("Please enter a product name");
        return;
    }
    // Call the backend recommendation endpoint using the searched product name
    fetch(`/recommend?product_name=${encodeURIComponent(productName)}`)
        .then(response => response.json())
        .then(data => {
            displayRecommendations(data);
        })
        .catch(error => {
            console.error("Error fetching recommendations:", error);
        });
});

// display recommendations
function displayRecommendations(recommendations) {
    const container = document.getElementById("recommendationsContainer");
    container.innerHTML = "";
    if (recommendations.length === 0) {
        container.innerHTML = "<p>No recommendations found.</p>";
        return;
    }
    
    recommendations.forEach(rec => {
        const recDiv = document.createElement("div");
        recDiv.className = "recommendation";
        recDiv.innerHTML = `
            <p><strong>Product Name:</strong> ${rec.product_name}</p>
            <p><strong>Product Type:</strong> ${rec.product_type}</p>
            <p><strong>Product Company:</strong> ${rec.product_company}</p>
            <p><strong>Score:</strong> ${rec.score.toFixed(2)}</p>
            <p><strong>Average Rating:</strong> ${rec.avg_rating ? rec.avg_rating.toFixed(1) : "No ratings"}</p>
            <div class="rating-section">
                <label for="rating_${rec.product_id}">Rate this product (1-5): </label>
                <input type="number" id="rating_${rec.product_id}" min="1" max="5">
            </div>
        `;
        container.appendChild(recDiv);
    });
    
    // submit ratings wala button
    const submitBtn = document.createElement("button");
    submitBtn.textContent = "Submit Ratings";
    submitBtn.classList.add("btn"); 
    submitBtn.addEventListener("click", submitRatings);
    container.appendChild(submitBtn);
}

// ratings sentto backend
function submitRatings() {
    const ratings = [];
    const inputs = document.querySelectorAll("[id^='rating_']");
    inputs.forEach(input => {
        const product_id = input.id.replace("rating_", "");
        const ratingValue = parseFloat(input.value);
        if (ratingValue >= 1 && ratingValue <= 5) {
            ratings.push({product_id, rating: ratingValue});
        }
    });
    
    if (ratings.length === 0) {
        alert("Please provide at least one rating (1-5) before submitting.");
        return;
    }
    
    fetch('/rate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ratings })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error("Error submitting ratings:", error);
    });
}
