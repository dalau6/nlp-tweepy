from flask import Flask, request, jsonify
from twitter import download_analyze_tweets
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.route('/get_tweets', methods=['POST'])

def get_tweets():
    accounts = request.json['accounts']
    processed_tweets, sentiment_sorted, grouped_by_np = download_analyze_tweets(accounts)
    return jsonify({
        'processedTweets': processed_tweets,
        'sentimentSorted': sentiment_sorted,
        'groupedByNp': grouped_by_np
    })

if __name__ == '__main__':
    app.run(debug=True)