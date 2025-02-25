import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskr.db import get_db, initialize_northwind

db = SQLAlchemy()

def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    db_path = "northwind.db" 

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", os.urandom(24).hex()),
        DATABASE=db_path if test_config is None else test_config["DATABASE"],  # ✅ 确保数据库可被 `pytest` 覆盖
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        initialize_northwind()  # ✅ 在应用启动时检查 `northwind.db`


    @app.before_request
    def ensure_session_id():
        # 1. Check if session_id is present in the Flask session
        # 2. If not, create one
        from flask import session
        import secrets

        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(16)

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

    from flaskr.orders import orders_bp
    app.register_blueprint(orders_bp)

    from flaskr.landing import landing_bp
    app.register_blueprint(landing_bp)

    from flaskr.checkout import checkout_bp
    app.register_blueprint(checkout_bp)

    return app



