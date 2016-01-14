from flask import flash
from flask import render_template
from flask import request, redirect, url_for

from blog import app
from .database import session, Entry, User
from flask.ext.login import login_user
from werkzeug.security import check_password_hash

import pdb

PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
  # Zero-indexed page
  page_index = page - 1
  
  if request.args.get('limit'):
    paginate_by = int(request.args.get('limit'))
  else:
    paginate_by = PAGINATE_BY
    
  count = session.query(Entry).count()
  
  start = page_index * paginate_by
  end = start + paginate_by
  
  total_pages = (count - 1) / paginate_by + 1
  has_next = page_index < total_pages - 1
  has_prev = page_index > 0
  
  entries = session.query(Entry)
  entries = entries.order_by(Entry.datetime.desc())
  entries = entries[start:end]
  
  return render_template("entries.html",
                          entries=entries,
                          has_next=has_next,
                          has_prev=has_prev,
                          page=page,
                          total_pages=total_pages
  )

@app.route("/entry/<int:id>")
def entry(id=1):
  count = session.query(Entry).count()
  entry = session.query(Entry).get(id)
  has_next = id < count 
  has_prev = id > 1
  return render_template("entry.html",
                          entry=entry,
                          has_next=has_next,
                          has_prev=has_prev,
                          id=id
  )

@app.route("/entry/<int:id>/edit", methods=["GET"])
def edit_get(id):
  entry = session.query(Entry).get(id)
  return render_template("edit_entry.html",
                          entry=entry
  )

@app.route("/entry/<int:id>/edit", methods=["POST"])
def edit_post(id):
  entry = session.query(Entry).get(id)
  entry.title=request.form["title"],
  entry.content=request.form["content"],
  session.commit()
  return redirect(url_for("entry", id=id))
  
@app.route("/entry/add", methods=["GET"])
def add_entry_get():
  return render_template("add_entry.html")
  
@app.route("/entry/add", methods=["POST"])
def add_entry_post():
  entry = Entry(
    title=request.form["title"],
    content=request.form["content"],
  )
  session.add(entry)
  session.commit()
  return redirect(url_for("entries"))

@app.route("/entry/<int:id>/delete", methods=["GET"])
def del_entry_confirm(id):
  entry = session.query(Entry).get(id)
  return render_template("delete.html",
                          id=id,
                          entry=entry)

@app.route("/entry/<int:id>/delete", methods=["POST"])
def check_delete_response(id):
  if request.form["delete"] == "yes":
    entry=session.query(Entry).get(id)
    session.delete(entry)
    session.commit
  return redirect(url_for("entries"))

@app.route("/login", methods=["GET"])
def login_get():
  return render_template("login.html")
  
@app.route("/login", methods=["POST"])
def login_post():
  email = request.form["email"]
  password = request.form["password"]
  user = session.query(User).filter_by(email=email).first()
  if not user or not check_password_hash(user.password, password):
    flash("Incorrect username or password", "danger")
    return redirect(url_for("login_get"))
    
  pdb.set_trace()
  
  login_user(user)
  return redirect(request.args.get('next') or url_for("entries"))
  