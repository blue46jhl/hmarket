import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
from encryption import encrypt, confirm
from flask_mail import Mail, Message
import re
# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

UPLOAD_FOLDER = '/home/ubuntu/workspace/Hmarket/project/static/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
          filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'hmarketinfo@gmail.com'
app.config['MAIL_PASSWORD'] = 'Hmarket123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
Session(app)


db = SQL("sqlite:///user.db")

@app.route("/")
def index():
    items=db.execute("SELECT * FROM item")
    return render_template("index.html", items=items)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result = db.execute("SELECT * FROM user WHERE username = :username",
                            username=request.form.get("username"))
        print("check")
        if result:
             flash("Username is already taken! Please try again.")
             return render_template("register.html")

        session["user_id"] = db.execute("INSERT INTO user(username, hash,status) VALUES (:username, :hash, :status)", username=request.form.get("username"),
                                        hash=generate_password_hash(request.form.get("password")), status=0)
        username=request.form.get("username")

        if not re.match(r"^[A-Za-z0-9._%+-]+@college.harvard.edu$", username):
            flash("Email Address must be a valid Harvard College email address")
            return render_template("register.html")

        password=request.form.get("password")
        if re.match(r"^([^0-9]*|[^A-Z]*)$", password):
            flash("Password must contain at least 1 uppercase letter and 1 number")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters")
            return render_template("register.html")

        confirm_password = request.form.get("confirm_password")
        if not password == confirm_password:
            flash("Passwords are not identical!")
            return render_template("register.html")

        token=encrypt(username)
        email=token
        print(token)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        msg = Message('Confirmation', sender = 'hmarketinfo@gmail.com', recipients = [username])
        msg.body = "Confirmation link: " + confirm_url
        mail.send(msg)
        print("Sent")
        return redirect(url_for("unconfirmed"))
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET","POST"])
#@login_required
def sell():
    if request.method == "POST":
        print("Check")
        file=request.files['image']
        print("Check")
        filename = secure_filename(file.filename)
        print("Check")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        reference_url=(url_for('static',filename=filename))
        print(reference_url)
        db.execute("INSERT INTO item(category, title, description, price, image,notes, seller_id) VALUES (:category, :title, :description, :price, :image, :notes, :seller_id)",
                        category= request.form.get("category"), title=request.form.get("title"),
                        description=request.form.get("description"), price=request.form.get("price"), image = reference_url, notes=request.form.get("notes"), seller_id=session["user_id"])
        return redirect ("/")
    else:
        return render_template("sell.html")


@app.route("/buy/<id>", methods=["GET", "POST"])
def buy(id):
    if request.method== "POST":
        print("check")
        buyer_email = session["user_id"]
        seller_email = db.execute("SELECT seller_id FROM item WHERE id=:id", id=id)
        print(id)
        print(buyer_email)
        print(seller_email)
    #Sends email to
        msg = Message('Confirmation', sender = 'hmarketinfo@gmail.com', recipients = [buyer_email, seller_email])
        msg.body = "An item has been bought by" + {} + "from" + {}.format(buyer_email,seller_email)
        mail.send(msg)
        return render_template("sold.html")
    else:
        item=db.execute("SELECT * FROM item where id=:id", id=id)
        return render_template("buy.html", item=item)


@app.route('/<token>')
def confirm_email(token):
    ##user=current_user_id (do through query of SQL)
    try:
        email=confirm(token)
    except:
        redirect(url_for('unconfirmed'))
    print(email)
    user = db.execute("SELECT * FROM user WHERE username = :email", email=email)
    print(user)
    #if (user.status=True):
        #print("already confirmed!")
    #else:
        #user.status= True
    user[0]["status"] = 1
    db.execute("UPDATE user SET status = :new_status", new_status = user[0]["status"])
    return redirect(url_for("login"))

@app.route('/unconfirmed')
def unconfirmed():
    # user = db.execute("SELECT * FROM user WHERE username = :email", email=email)
    # print(user)
    # if user[0]["status"]== 1:
    #     return redirect("index")
    # else:
    session.clear()
    return render_template("unconfirmed.html")

# @app.route("/confirmation")
# def confirm_sale():
#     #Get user id

#     buyer_email = db.execute("SELECT username FROM user")
#     seller_email = db.execute("SELECT seller_id FROM item")
#     #Sends email to
#     msg = Message('Confirmation', sender = 'hmarketinfo@gmail.com', recipients = ['sw7082566@gmail.com'])
#     msg.body = "An item has been bought by" + buyer_email + "from" + seller_email
#     mail.send(msg)
#     return "Sent"


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            #return apology("must provide username", 403)
            print("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            #return apology("must provide password", 403)
            print("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM user WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            print("invalid username/passowrd")

        if rows[0]["status"]==0:
            print("Confirm your status")

        # Remember which user has logged in
        session["user_id"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/books")
def books():
    items=db.execute("SELECT * from item WHERE category=:category", category="books")
    return render_template("index.html", items=items)

@app.route("/other")
def other():
    items=db.execute("SELECT * from item WHERE category=:category", category="other")
    return render_template("index.html",items=items)


@app.route("/technology")
def technology():
    items=db.execute("SELECT * from items WHERE category=:category", category="books")
    return render_template("index.html", items=items)

@app.route("/furniture")
def furniture():
    items=db.execute("SELECT * from items WHERE category=:category", category="furniture")
    return render_template("index.html", items=items)


