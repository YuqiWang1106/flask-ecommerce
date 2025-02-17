import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", os.urandom(24).hex()),
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        SQLALCHEMY_DATABASE_URI="sqlite:///northwind.db",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.before_request
    def ensure_session_id():
        # 1. Check if session_id is present in the Flask session
        # 2. If not, create one
        from flask import session
        import uuid

        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

    @app.route("/hello")
    def hello() -> str:
        return "Hello, World!"

    db.init_app(app)

    from .products import products_bp
    app.register_blueprint(products_bp)

    from . import user
    app.register_blueprint(user.bp)


    from flaskr.cart import cart_bp
    app.register_blueprint(cart_bp)

    return app

    
