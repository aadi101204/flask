import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from blogsite.database.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        elif not email:
            error = "Email is required"

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user(email,username,password) VALUES (?,?,?)",
                    (email, username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User:{username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)
    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute("SELECT *FROM user WHERE email=?", (email,)).fetchone()

        if user is None:
            error='No user with this email'
        elif not check_password_hash(user['password'],password):
            error= f'Incorrect password for {user["email"]}'        

        if error is None:
            session.clear()
            session['user_id']=user['id']
            return redirect(url_for('index'))
        
        flash(error)
    return render_template('auth/login.html')
        