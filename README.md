# fmcg_recommendation_system
FMCG Product Recommendation System
Overview
This project is a product recommendation system for middlemen in the FMCG sector. It uses content-based and collaborative filtering to suggest similar or better-performing products based on user input. Ratings are based on factors like profitability, demand, availability, and customer preference.

🚀 Features
Recommends top 5 similar products using hybrid filtering

Accepts ratings for recommendations and updates the model accordingly

Handles duplicate entries in the product dataset

Intelligent fallback to content-based filtering when collaborative data is insufficient

🛠 Tech Stack
Backend: Flask (Python)

Frontend: HTML/CSS

Database: SQLite (local) / Cloud (for deployment)

ML: Scikit-learn, Pandas, NumPy

Project Structure:

├── app.py                        # Main Flask app
├── templates/ index.html         # HTML templates
├── static/ style.css,script.js   # CSS and assets
├── products_data.xlsx            # Product dataset
├── ratings.db                    # User ratings database
├── utils/                        # Recommendation logic
├── requirements.txt              # Python dependencies
└── README.md                     # This file

