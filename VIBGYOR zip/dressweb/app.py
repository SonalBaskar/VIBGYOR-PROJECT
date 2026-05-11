from flask import Flask, render_template, request, redirect, jsonify, url_for, session
import os
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = "secret123"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

history_data = []
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id='CLIENT_ID',
    client_secret='CLIENT_SECRET_KEY',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# 🔹 1. LANDING PAGE
@app.route("/")
def index():
    return render_template("index.html")

# 🔹 2. SIGNUP / LOGIN PAGE
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        session["user"] = {"email": email}
        return redirect("/myhome")

    return render_template("signup.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        session["user"] = {"email": email}
        return redirect("/myhome")

    
    return render_template("login.html")

# 🔹 3. GOOGLE LOGIN
@app.route("/login/google")
def login_google():
    return google.authorize_redirect(
        url_for('google_callback', _external=True),
        prompt='select_account'   # ✅ FORCE account selection
    )

# 🔹 4. GOOGLE CALLBACK
@app.route("/login/google/callback")
def google_callback():
    token = google.authorize_access_token()
    resp = google.get('https://www.googleapis.com/oauth2/v3/userinfo')
    user = resp.json()

    session["user"] = user
    return redirect("/myhome")

# 🔹 5. MAIN HOME PAGE
@app.route("/myhome")
def myhome():
    user = session.get("user")
    if user:
        return render_template("myhome.html", user=user)
    return redirect("/")

# 🔹 6. OTHER PAGES (PROTECTED)
@app.route("/wardrobe")
def wardrobe():
    if "user" not in session:
        return redirect("/")
    return render_template("wardrobe.html")

@app.route("/social")
def social():
    if "user" not in session:
        return redirect("/")
    return render_template("social.html")

@app.route("/color")
def color():
    if "user" not in session:
        return redirect("/")
    return render_template("color.html")

@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/")
    return render_template("history.html")

@app.route("/outfit")
def outfit():
    if "user" not in session:
        return redirect("/")
    return render_template("outfit.html")

# 🔹 LOGOUT (optional but useful)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
 
@app.route('/upload', methods=['POST'])
def upload():

    file = request.files['image']
    category = request.form['category']

    filepath = os.path.join(
        app.config['UPLOAD_FOLDER'],
        file.filename
    )

    file.save(filepath)

    return jsonify({
        "path": filepath,
        "category": category
    })
@app.route('/recommend', methods=['POST'])
def recommend():

    data = request.json

    occasion = data['occasion']
    style = data['style']
    color = data['color']

    result = {
        "occasion": occasion,
        "style": style,
        "color": color,
        "recommended": "Luxury Fusion Outfit"
    }

    history_data.append(result)

    return jsonify(result)

@app.route('/history-data')
def history_data_route():

    return jsonify(history_data)
if __name__ == "__main__":
    app.run(debug=True)