from flask import Flask, render_template, request, jsonify
from inference import get_recommendations

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    author_name = data.get('author')
    recommendations = get_recommendations(author_name)
    return jsonify({'recommendations': recommendations})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
