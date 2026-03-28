from flask import Flask, jsonify, request
from controller import run_drakul

app = Flask(__name__)

@app.route("/scan")
def scan():
    radius = int(request.args.get("radius", 3000))
    mode = request.args.get("mode", "paranormal")

    result = run_drakul(radius, mode)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000)