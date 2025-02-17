import functools
import uuid
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # Convert username to uppercase for consistency.
        username = request.form['username'].strip().upper()
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'User ID is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            # Check if the user exists in the Customers table.
            customer = db.execute(
                'SELECT * FROM Customers WHERE CustomerID = ?',
                (username,)
            ).fetchone()

            if customer is None:
                # If no customer exists, create a new row in Customers with the CustomerID.
                db.execute(
                    'INSERT INTO Customers (CustomerID) VALUES (?)',
                    (username,)
                )
            try:
                # Insert the authentication record.
                db.execute(
                    "INSERT INTO Authentication (UserID, PasswordHash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                db.rollback()
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("user.login"))

        flash(error)

    return render_template('user/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # Convert username to uppercase so the lookup is case-insensitive.
        username = request.form['username'].strip().upper()
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = "User ID is required."
        elif not password:
            error = "Password is required."

        if error is None:
            # Look up the user by UserID (which is stored in uppercase).
            user = db.execute(
                'SELECT * FROM Authentication WHERE UserID = ?',
                (username,)
            ).fetchone()

            if user is None:
                error = "Username not found, please make sure username is correct or register."
            elif not check_password_hash(user['PasswordHash'], password):
                error = "Password incorrect, please try again or register."

        if error is None:
            # Credentials are valid.
            # Retrieve the old session ID from the Authentication table.
            old_session_id = user['SessionID']
            # Clear the current session.
            # Generate a new session ID.
            new_session_id = session['session_id']
            # Store new session info in Flask's session object.
            session['user_id'] = username

            # Compare the old and new session IDs.
            if old_session_id != new_session_id:
                # Update any Shopping_cart rows that are associated with the old session ID.
                db.execute(
                    'UPDATE Shopping_cart SET ShopperID = ? WHERE ShopperID = ?',
                    (new_session_id, old_session_id)
                )
                # Update the Authentication table with the new session ID.
                db.execute(
                    'UPDATE Authentication SET SessionID = ? WHERE UserID = ?',
                    (new_session_id, username)
                )
            db.commit()
            return redirect(url_for('products.list_products'))

        flash(error)

    return render_template('user/login.html')



@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    session_id = session.get('session_id')
    if user_id is None or session_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM Authentication WHERE UserID = ? AND SessionID = ?',
            (user_id, session_id)
        ).fetchone()


@bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        db = get_db()
        db.execute(
            'UPDATE Authentication SET SessionID = NULL WHERE UserID = ?',
            (user_id,)
        )
        db.commit()
    session.clear()
    return redirect(url_for('products.list_products'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('user.login'))
        return view(**kwargs)

    return wrapped_view
