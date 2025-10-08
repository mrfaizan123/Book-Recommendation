from flask import Flask, render_template, request, jsonify, session
import pickle
import pandas as pd
import numpy as np
import gzip


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Load your data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(gzip.open('book.pkl.gz', 'rb'))
similarity_scores = pickle.load(open('similarity.pkl', 'rb'))

# Convert numpy types to Python native types for JSON serialization
def convert_to_python_types(df):
    """Convert numpy types to Python native types"""
    result = []
    for i in range(len(df)):
        item = {
            'Book-Title': str(df.iloc[i]['Book-Title']),
            'Book-Author': str(df.iloc[i]['Book-Author']),
            'Image-URL-M': str(df.iloc[i]['Image-URL-M']),
            'Num-Ratings': int(df.iloc[i]['Num-Ratings']),
            'Avg-Ratings': float(df.iloc[i]['Avg-Ratings'])
        }
        # Add genres if they exist
        if 'Genres' in df.columns:
            item['Genres'] = str(df.iloc[i]['Genres'])
        result.append(item)
    return result

@app.route('/')
def index():
    # Convert to Python native types
    popular_data = convert_to_python_types(popular_df)

    return render_template('index.html',
                           book_name=[item['Book-Title'] for item in popular_data],
                           author=[item['Book-Author'] for item in popular_data],
                           image=[item['Image-URL-M'] for item in popular_data],
                           votes=[item['Num-Ratings'] for item in popular_data],
                           rating=[item['Avg-Ratings'] for item in popular_data],
                           genres=[item.get('Genres', 'Fiction') for item in popular_data]
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    try:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

            data.append(item)

        return render_template('recommend.html', data=data)
    except IndexError:
        return render_template('recommend.html', error="Book not found. Please try another title.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

