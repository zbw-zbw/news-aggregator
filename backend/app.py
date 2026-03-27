from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/categories', methods=['GET'])
def get_categories():
    predefined_categories = ['Technology', 'Health', 'Sports', 'Entertainment', 'Science']
    return jsonify({'categories': predefined_categories})

@app.route('/endpoint1', methods=['GET'])
def endpoint1():
    # Implementation of endpoint 1
    return jsonify({'message': 'This is endpoint 1'})

@app.route('/endpoint2', methods=['GET'])
def endpoint2():
    # Implementation of endpoint 2
    return jsonify({'message': 'This is endpoint 2'})

if __name__ == '__main__':
    app.run(debug=True)