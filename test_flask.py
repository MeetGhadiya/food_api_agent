from flask import Flask
app = Flask(__name__)

@app.route('/test')
def test():
    return {'message': 'Flask is working!'}

if __name__ == '__main__':
    print("Starting simple Flask test...")
    app.run(host='127.0.0.1', port=5001, debug=False)
