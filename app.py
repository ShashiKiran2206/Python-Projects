from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import numpy as np
import os
from textblob import TextBlob

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file1' not in request.files or 'file2' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file1 = request.files['file1']
        file2 = request.files['file2']

        if file1.filename == '' or file2.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file1 and file2:
            file1.save(os.path.join(UPLOAD_FOLDER, "Trumpall2.csv"))
            file2.save(os.path.join(UPLOAD_FOLDER, "Bidenall2.csv"))
            flash('Dataset uploaded')

    return render_template('index.html')

@app.route('/show_head')
def show_head():
    trump_reviews = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Trumpall2.csv"))
    biden_reviews = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Bidenall2.csv"))
    return render_template('output.html', output1=trump_reviews.head().to_html(), output2=biden_reviews.head().to_html())

def find_pol(review):
    return TextBlob(review).sentiment.polarity

@app.route('/trump_polarity')
def trump_polarity():
    trump_reviews = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Trumpall2.csv"))

    # Calculate sentiment polarity and expression label for Trump reviews
    trump_reviews["Sentiment Polarity"] = trump_reviews["text"].apply(find_pol)
    trump_reviews["Expression Label"] = np.where(trump_reviews["Sentiment Polarity"] > 0, "positive", "negative")
    trump_reviews["Expression Label"][trump_reviews["Sentiment Polarity"] == 0] = "Neutral"

    return render_template('polarity_output.html', title='Trump Sentiment Polarity', output=trump_reviews.tail().to_html())

@app.route('/biden_polarity')
def biden_polarity():
    biden_reviews = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Bidenall2.csv"))

    # Calculate sentiment polarity and expression label for Biden reviews
    biden_reviews["Sentiment Polarity"] = biden_reviews["text"].apply(find_pol)
    biden_reviews["Expression Label"] = np.where(biden_reviews["Sentiment Polarity"] > 0, "positive", "negative")
    biden_reviews["Expression Label"][biden_reviews["Sentiment Polarity"] == 0] = "Neutral"

    return render_template('polarity_output.html', title='Biden Sentiment Polarity', output=biden_reviews.tail().to_html())

@app.route('/filter_neutral')
def filter_neutral():

    trump_reviews = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Trumpall2.csv"))
    biden_reviews = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Bidenall2.csv"))

    # Calculate sentiment polarity
    trump_reviews["Sentiment Polarity"] = trump_reviews["text"].apply(find_pol)
    biden_reviews["Sentiment Polarity"] = biden_reviews["text"].apply(find_pol)

    # Filter out reviews with 0 sentiment polarity for Trump
    reviews1 = trump_reviews[trump_reviews['Sentiment Polarity'] == 0.0000]
    cond1 = trump_reviews['Sentiment Polarity'].isin(reviews1['Sentiment Polarity'])
    trump_reviews.drop(trump_reviews[cond1].index, inplace=True)

    # Filter out reviews with 0 sentiment polarity for Biden
    reviews2 = biden_reviews[biden_reviews['Sentiment Polarity'] == 0.0000]
    cond2 = biden_reviews['Sentiment Polarity'].isin(reviews2['Sentiment Polarity'])
    biden_reviews.drop(biden_reviews[cond2].index, inplace=True)

    return render_template('filter_output.html', title='Filtered Reviews (No Neutral)', trump_shape=trump_reviews.shape, biden_shape=biden_reviews.shape)

@app.route('/drop_random')
def drop_random():
    trump_reviews = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Trumpall2.csv"))
    biden_reviews = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Bidenall2.csv"))

    # Calculate sentiment polfarity for both Trump and Biden datasets
    trump_reviews["Sentiment Polarity"] = trump_reviews["text"].apply(find_pol)
    biden_reviews["Sentiment Polarity"] = biden_reviews["text"].apply(find_pol)

    # Create the 'Expression Label' column based on polarity
    trump_reviews["Expression Label"] = np.where(trump_reviews["Sentiment Polarity"] > 0, "positive", "negative")
    trump_reviews["Expression Label"][trump_reviews["Sentiment Polarity"] == 0] = "Neutral"

    biden_reviews["Expression Label"] = np.where(biden_reviews["Sentiment Polarity"] > 0, "positive", "negative")
    biden_reviews["Expression Label"][biden_reviews["Sentiment Polarity"] == 0] = "Neutral"

    # Drop random rows from Trump reviews
    np.random.seed(10)
    remove_n_trump = 324
    drop_indices_trump = np.random.choice(trump_reviews.index, remove_n_trump, replace=False)
    df_subset_trump = trump_reviews.drop(drop_indices_trump)

    # Drop random rows from Biden reviews
    np.random.seed(10)
    remove_n_biden = 31
    drop_indices_biden = np.random.choice(biden_reviews.index, remove_n_biden, replace=False)
    df_subset_biden = biden_reviews.drop(drop_indices_biden)

    # Group by 'Expression Label' and count the occurrences
    count_trump = df_subset_trump.groupby('Expression Label').count()
    count_biden = df_subset_biden.groupby('Expression Label').count()

    # Calculate percentages for Trump reviews
    negative_per_trump = (count_trump['Sentiment Polarity'][0] / len(df_subset_trump)) * 100
    positive_per_trump = (count_trump['Sentiment Polarity'][1] / len(df_subset_trump)) * 100

    return render_template('random_drop_output.html',
                           title='Random Row Drop Results',
                           trump_shape=df_subset_trump.shape,
                           biden_shape=df_subset_biden.shape,
                           count_trump=count_trump.to_html(),
                           count_biden=count_biden.to_html(),
                           negative_per_trump=negative_per_trump,
                           positive_per_trump=positive_per_trump)


import plotly.graph_objects as go
@app.route('/sentiment_comparison')
def sentiment_comparison():
    trump_reviews = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Trumpall2.csv"))
    biden_reviews = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Bidenall2.csv"))

    # Calculate sentiment polarity and expression label for both Trump and Biden
    trump_reviews["Sentiment Polarity"] = trump_reviews["text"].apply(find_pol)
    biden_reviews["Sentiment Polarity"] = biden_reviews["text"].apply(find_pol)

    # Create the 'Expression Label' column based on polarity
    trump_reviews["Expression Label"] = np.where(trump_reviews["Sentiment Polarity"] > 0, "positive", "negative")
    trump_reviews["Expression Label"][trump_reviews["Sentiment Polarity"] == 0] = "Neutral"

    biden_reviews["Expression Label"] = np.where(biden_reviews["Sentiment Polarity"] > 0, "positive", "negative")
    biden_reviews["Expression Label"][biden_reviews["Sentiment Polarity"] == 0] = "Neutral"

    # Group by 'Expression Label' and count the occurrences
    count_trump = trump_reviews.groupby('Expression Label').count()
    count_biden = biden_reviews.groupby('Expression Label').count()

    # Calculate percentages for Trump reviews
    negative_per1 = (count_trump['Sentiment Polarity'].get('negative', 0) / len(trump_reviews)) * 100
    positive_per1 = (count_trump['Sentiment Polarity'].get('positive', 0) / len(trump_reviews)) * 100

    # Calculate percentages for Biden reviews
    negative_per2 = (count_biden['Sentiment Polarity'].get('negative', 0) / len(biden_reviews)) * 100
    positive_per2 = (count_biden['Sentiment Polarity'].get('positive', 0) / len(biden_reviews)) * 100

    # Politicians and sentiment lists
    Politicians = ['Joe Biden','Donald Trump']
    lis_pos = [positive_per1, positive_per2]
    lis_neg = [negative_per1, negative_per2]

    # Create the figure using Plotly
    fig = go.Figure(data=[
        go.Bar(name='Positive', x=Politicians, y=lis_pos),
        go.Bar(name='Negative', x=Politicians, y=lis_neg)
    ])

    # Update the layout
    fig.update_layout(barmode='group', title="Sentiment Comparison of Joe Biden and Donald Trump")

    # Save the figure as an HTML file
    plot_path = os.path.join(UPLOAD_FOLDER, "sentiment_comparison.html")
    fig.write_html(plot_path)

    return render_template('sentiment_comparison_output.html', plot_url=plot_path)


if __name__ == '__main__':
    app.run(debug=True)
