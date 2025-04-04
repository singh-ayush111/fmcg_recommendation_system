from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

products_df = pd.read_excel("new dataset.xlsx")
products_df = products_df.reset_index(drop=True)
products_df = products_df.drop_duplicates(subset=['product_name'], keep='first')
products_df = products_df.reset_index(drop=True)

#COMBINING FEATURES FOR CONTENT BASED RECOMMENDATION
products_df['combined'] = products_df['product_name'] + " " + products_df['product_type'] + " " + products_df['product_company']

#TD-IDF MODEL -> COSINE SIMILARITY
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(products_df['combined'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

#SQLLITE DB FOR SAVING RATINGS DONE DURING RECOMMENDATIONS
#NO ENTRIES ARE UPLOADED PEHLE SE
DATABASE = 'ratings.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            rating REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

#dict return hoga -> product_id , avg_rating
def get_average_ratings():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT product_id, AVG(rating) FROM ratings GROUP BY product_id")
    results = c.fetchall()
    conn.close()
    avg_ratings = {row[0]: row[1] for row in results}
    return avg_ratings

#RECOMMENDATIONS FUNCTION STARTS HERE WITH
#FIRSTLY COSINE SIMILARITY SE SORT HOGA
#
def get_recommendations(product_name, top_n=15):
    indices = products_df[products_df['product_name'].str.lower() == product_name.lower()].index
    if len(indices) == 0:
        return []  # similar nhi hai...error text
    idx = indices[0]
    
    # cos sim score niklega
    sim_scores = list(enumerate(cosine_sim[idx]))
    # khudko skip krke decreasing order me top 5 entries
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]
    
    # call avg ratings from database
    avg_ratings = get_average_ratings()
    
    recommendations = []
    for i, content_score in sim_scores:
        product = products_df.iloc[i]
        product_id = product['product_id']
        # normalized ratings nik
        if product_id in avg_ratings:
            rating_score = avg_ratings[product_id] / 5.0
        else:
            rating_score = 0
        # weighted combination of both
        combined_score = 0.7 * content_score + 0.3 * rating_score
        recommendations.append((i, combined_score))

    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)
    top_recommendations = recommendations[:top_n]
    
    # result=list of recommended products
    result = []
    for i, score in top_recommendations:
        product = products_df.iloc[i].to_dict()
        product['score'] = score
        product['avg_rating'] = avg_ratings.get(product['product_id'], None)
        result.append(product)
        
    return result

#SAARE API ENDPOINS

# HTML start krega
@app.route('/')
def index():
    return render_template('index.html')

# search suggestion ke liye 
@app.route('/products', methods=['GET'])
def products():
    products_list = products_df[['product_id', 'product_name']].drop_duplicates().to_dict(orient='records')
    return jsonify(products_list)

# Recommendation endpoint – expects a query parameter "product_name"
@app.route('/recommend', methods=['GET'])
def recommend():
    product_name = request.args.get('product_name')
    if not product_name:
        return jsonify({'error': 'No product_name provided'}), 400
    recommendations = get_recommendations(product_name)
    return jsonify(recommendations)

# Rating submission endpoint – expects JSON with a list of ratings
@app.route('/rate', methods=['POST'])
def rate():
    data = request.get_json()
    if not data or 'ratings' not in data:
        return jsonify({'error': 'No rating data provided'}), 400
    ratings = data['ratings']
    #dictionary form me rating - product_id aur ratings
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    for rating in ratings:
        product_id = rating.get('product_id')
        rating_value = rating.get('rating')
        if product_id is not None and rating_value is not None:
            c.execute("INSERT INTO ratings (product_id, rating) VALUES (?, ?)", (product_id, rating_value))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Ratings submitted successfully'})


if __name__ == '__main__':   #flask running command
    app.run(debug=True)
