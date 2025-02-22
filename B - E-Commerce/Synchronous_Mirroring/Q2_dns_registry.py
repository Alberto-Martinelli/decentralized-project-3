from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# List of available servers (Primary and Backup)
servers = [
    {"id": 1, "url": "http://localhost:3001", "active": True},  # Primary
    {"id": 2, "url": "http://localhost:3002", "active": True}   # Backup
]

@app.route('/getServer', methods=['GET'])
def get_server():
    active_server = next((s for s in servers if s["active"]), None)
    
    if active_server:
        return jsonify({
            "code": 200,
            "server": active_server["url"]
        })
    else:
        return jsonify({
            "code": 500,
            "error": "No active servers available"
        }), 500

@app.route('/updateServer', methods=['POST'])
def update_server():
    data = request.get_json()
    server_id = data.get("id")
    active_status = data.get("active")

    for server in servers:
        if server["id"] == server_id:
            server["active"] = active_status
            return jsonify({
                "message": f"Server {server_id} status updated",
                "servers": servers
            })

    return jsonify({"error": "Server not found"}), 404

if __name__ == '__main__':
    PORT = 4000  
    print(f"DNS Registry Server is running on http://localhost:{PORT}")
    app.run(port=PORT, debug=True)
