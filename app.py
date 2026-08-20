from flask import Flask, render_template, request, jsonify
from backend.main import inisialisasi_sistem, proses_login

app = Flask(__name__)

# Bangun database pas server nyala
inisialisasi_sistem()

# Rute buat nampilin file HTML
@app.route("/")
def index():
    return render_template("index.html")

# Rute API yang dipanggil sama JavaScript dari HTML
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    # Manggil fungsi otak Python lo
    hasil = proses_login(username, password)
    return jsonify(hasil)

if __name__ == "__main__":
    # Jalanin server di jaringan lokal biar bisa dibuka di HP
    app.run(host="0.0.0.0", port=5000, debug=True)
