from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("user", __name__)


@bp.route("/view/<username>")
@login_required
def view(username=None):
    """Endpoint to view a user's profile -- to be implemented and tested further.
    """
    if username is None:
        return redirect(url_for("homepage.index"))
    db = get_db()
    user = db.execute(
        "SELECT username " "FROM user WHERE username = ?", (username,)
    ).fetchone()

    if not user:
        flash("No such user")
        return redirect(url_for("homepage.index"))

    print(user["username"])
    return render_template("user/view.html", user=user)
