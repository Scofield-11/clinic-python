from flask import Flask
from routes.auth import auth_bp
from routes.benh_nhan import benh_nhan_bp
from routes.bac_si import bac_si_bp
from routes.public import public_bp
app = Flask(__name__)
app.secret_key = "06081983"
app.register_blueprint(auth_bp)
app.register_blueprint(benh_nhan_bp)
app.register_blueprint(bac_si_bp)
app.register_blueprint(public_bp)

if __name__ == "__main__":
    app.run(debug=True)