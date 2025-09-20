from flask import Flask, jsonify, render_template
from kod_funkce import get_carousel_data

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spustit')
def get_data():
    tabulka = get_carousel_data()
    return jsonify(tabulka)

if __name__ == '__main__':
    app.run(debug=True)