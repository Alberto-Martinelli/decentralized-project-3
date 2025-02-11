from flask import Flask, jsonify

app = Flask(__name__)

# Hello World server's address 
SERVER_URL = "localhost:3001"

@app.route('/getServer', methods=['GET'])
def get_server():
    return jsonify({
        "code": 200,
        "server": SERVER_URL
    })

if __name__ == '__main__':
    PORT = 4000  
    print(f"DNS Registry Server is running on http://localhost:{PORT}")
    app.run(port=PORT, debug=True)
