from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World!"

if __name__ == '__main__':
    PORT = 3001
    print(f"Server is running on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
