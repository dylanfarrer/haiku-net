from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import string
import nltk
from nltk.corpus import cmudict

nltk.download('cmudict')

bp = Blueprint("homepage", __name__)


@bp.route("/")
def index():
    """Renders home page."""
    page = request.args.get("page", 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
        " LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()
    return render_template("homepage/index.html", posts=posts, page=page, per_page=per_page)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Provides the create post page."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."
        elif not body:
            error = "Body is required."
        elif is_text_a_haiku(body) is False:
            error = ("Non-haiku detected! Are there 3 'lines' separated by commas, "
                    "the first being 5 syllables, the second being 7, and the third"
                    " being 5. The words must also be in English...")

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("homepage.index"))

    return render_template("homepage/create.html")


def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Given a user id and form data, attempts to update a post."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."
        elif not body:
            error = "Body is required."
        elif is_text_a_haiku(body) is False:
            error = ("Non-haiku detected! Are there 3 'lines' separated by commas, "
                    "the first being 5 syllables, the second being 7, and the third"
                    " being 5. The words must also be in English...")

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?" " WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("homepage.index"))

    return render_template("homepage/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Given a user id and form data, attempts to delete a post."""
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("homepage.index"))


def count_syllables_in_word_list(words):
    high_syllable_count = 0
    low_syllable_count = 0
    d = cmudict.dict()
    for word in words:
        if word.lower() in d:
            max_syll = max([len([y for y in x if (y[-1]).isdigit()]) for x in d[word.lower()]])
            min_syll = min([len([y for y in x if (y[-1]).isdigit()]) for x in d[word.lower()]])
            high_syllable_count += max_syll
            low_syllable_count += min_syll
            print(word.lower() + " " + str(max_syll) + " " + str(min_syll))
    
    return low_syllable_count, high_syllable_count

def remove_punctuation(strings):
    return [s for s in strings if not all(char in string.punctuation for char in s)]

def is_text_a_haiku(text):
    if text[-1] in string.punctuation:
        text = text[:-1]

    if text.count(',') != 2:
        return False

    lines = text.split(',')
    print(lines)

    if len(lines) != 3:
        return False

    lines[0] = remove_punctuation(lines[0].split())
    lines[1] = remove_punctuation(lines[1].split())
    lines[2] = remove_punctuation(lines[2].split())

    for i in range(3):
        low, high = count_syllables_in_word_list(lines[i])
        if i == 1:
            if low > 7 or high < 7:
                return False
        else:
            if low < 5 or high > 5:
                return False

    return True
