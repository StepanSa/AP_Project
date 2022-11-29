from flask import Flask
from wsgiref.simple_server import make_server
from flask_jwt_extended import JWTManager
from blueprint import api_blueprint

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

app.register_blueprint(api_blueprint, url_prefix="")

if __name__ == "__main__":
    app.run(debug=True)


# with make_server('', 5000, app) as server:
#     app.register_blueprint(api_blueprint, url_prefix="/api/v1")
#     server.serve_forever()


# curl -v -XGET http://localhost:5000/api/v1/hello-world
