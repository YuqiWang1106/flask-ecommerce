from flask import Blueprint, render_template

landing_bp = Blueprint("landing", __name__)

@landing_bp.route("/")
def home():
    """显示 Landing Page"""
    return render_template("landing.html")

