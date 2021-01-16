from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world'

@app.route('/data')
def data():
    return jsonify({'test': 50})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')