import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
# from encryption import encrypt, confirm
# from send_email import email_app, send_email
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

UPLOAD_FOLDER = '/home/ubuntu/workspace/Hmarket/project/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
          filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Session(app)


db = SQL("sqlite:///user.db")

@app.route("/")
def index():
    items=db.execute("SELECT * from")
    print(items)
    return render_template("index.html", items=items)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email= request.form.get("email")
        # token=encrypt(email)
        # verification_link= url_for('confirm_email',token=token, _external=True)
        # send_email(email)
        ##user= current_user_id (add user)
        ##user.status=False

        # if not request.form.get("username"):
        #     print ("input username")

        # elif not request.form.get("password"):
        #     return apology("must provide password", 400)

        # elif request.form.get('password') != request.form.get('confirmation'):
        #     return apology("passwords do not match", 400)

        # Result is a variable, if true, contains a username in the database identical to the inputted username
        result = db.execute("SELECT * FROM users WHERE username = :username",
                            username=request.form.get("username"))
        if result:
            print("Username already taken")

        session["user_id"] = db.execute("INSERT INTO users(username, hash) VALUES (:username, :hash)", name=request.form.get("username"),
                                        hash=generate_password_hash(request.form.get("password")))
        return redirect("/")
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
        reference_url=(url_for('s',filename=filename))
        print(reference_url)
        db.execute("INSERT INTO item(category, title, description, price, image) VALUES (:category, :title, :description, :price, :image)",
                        category= request.form.get("category"), title=request.form.get("title"),
                        description=request.form.get("description"), price=request.form.get("price"), image = reference_url)
        return redirect ("/")
    else:
        return render_template("sell.html")
# # @app.route('/<token>')
# def confirm_email(token):
#     ##user=current_user_id (do through query of SQL)
#     try:
#         email=confirm(token)
#     except:
#         print("did not work!")
#     #if (user.status=True):
#         #print("already confirmed!")
#     #else:
#         #user.status= True
#     return redirect("index.html")

##create apology template -Sam
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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            print("invalid username/passowrd")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

