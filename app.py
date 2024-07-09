from flask import Flask , render_template, request,redirect,url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:gnay@localhost:5432/bdexambiblio"
app.config['SECRET_KEY'] = "b379e7f0f335ea8abb1cbcfb0ae8cf51f514bd330ff7ec2a773f10ddbef32dd7"
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
migrate = Migrate(app,db)  

login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True)
    email = db.Column(db.String(200))
    mdp = db.Column(db.String(200))
    role = db.Column(db.String(200))
    emprunts = db.relationship('Emprunt', backref='utilisateur', lazy=True)

class Livre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200))
    description = db.Column(db.String(200))
    auteur = db.Column(db.String(200))
    genre = db.Column(db.String(200))
    datepub = db.Column(db.Integer())
    status = db.Column(db.Integer())
    image = db.Column(db.String(200))
    emprunts = db.relationship('Emprunt', backref='livre', lazy=True)

class Emprunt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_livre = db.Column(db.Integer, db.ForeignKey('livre.id'), nullable=False)
    dure = db.Column(db.Integer, nullable=False)
    date_debut = db.Column(db.DateTime, default=db.func.current_timestamp())
    
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, int(user_id))

@app.route("/")
#@login_required
def index():
    livres = Livre.query.all()
    return render_template('index.html', data=livres)

@app.route("/connexion", methods=["GET","POST"])
def connexion(): 
    if request.method == 'POST':
        username = request.form.get('username')
        mdp = request.form.get('mdp')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.mdp, mdp):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Erreur de connexion")
            return redirect(url_for('connexion'))

    return render_template('connexion.html')


@app.route("/temoignage")
def temoignage():
    return render_template('temoignage.html')

@app.route("/emprunts")
def emprunts():
    livres = Livre.query.all() 
    emprunts = Emprunt.query.all()
    utilisateurs = User.query.all()
    return render_template('emprunts.html', emprunts=emprunts, livres=livres, utilisateurs=utilisateurs) 


@app.route("/details/<int:id>", methods=["GET", "POST"])
def details(id):
    livre = Livre.query.get_or_404(id)
    
    if request.method == "POST":
        try:
            dure = int(request.form.get('dure'))
            if 0 < dure <= 30:
                if livre.status == 0:
                    livre.status = 1
                    emprunt = Emprunt(id_user=current_user.id, id_livre=id, dure=dure)
                    db.session.add(emprunt)
                    db.session.commit()
                    flash("Le livre a été emprunté avec succès.", "success")
                    return redirect(url_for('emprunts'))
                else:
                    flash("Le livre n'est plus disponible.", "error")
            else:
                flash("La durée doit être entre 1 et 30 jours.", "error")
        except ValueError:
            flash("Veuillez entrer une durée valide.", "error")

    return render_template('details.html', data=livre)


@app.route("/livres", methods=["GET", "POST"])
def livres():
    livres = Livre.query.all()
    emprunts = Emprunt.query.all()
    if request.method == "POST":
        titre = request.form.get('titre')
        description = request.form.get('description')
        auteur = request.form.get('auteur')
        genre = request.form.get('genre')
        datepub = request.form.get('datepub')
        image = request.form.get('image')

        if not titre or not description or not auteur:
            flash("Tous les champs sont obligatoires !!!", "danger")
            return render_template('livres.html', livres=livres, emprunts=emprunts)

        livre = Livre(titre=titre, description=description, auteur=auteur, genre=genre, datepub=int(datepub), status=0, image=image)
        db.session.add(livre)
        db.session.commit()
        #flash("Livre ajouté")
        return redirect(url_for('livres'))

    return render_template('livres.html', livres=livres, emprunts=emprunts)



@app.route("/deconnexion")
@login_required
def deconnexion():
    logout_user()
    return redirect(url_for('connexion'))

@app.route("/inscription/<string:role>", methods=["GET","POST"])
def inscription(role):
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        mdp = request.form.get('mdp')

        if username=="" or email=="" or mdp == "":
            flash("Tous les champs sont obligatoire !!!")
            return render_template('inscription.html', role_user=role)
        
        user = User.query.filter_by(username = username).first()

        if user:
            return redirect(url_for('connexion'))
        else:
            new_user = User(username= username,email= email,mdp=generate_password_hash(mdp),role=role)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('connexion'))

    return render_template('inscription.html', role_user=role)

@app.route("/supprimer_emprunt/<int:emprunt_id>")
def supprimer_emprunt(emprunt_id):
    emprunt = Emprunt.query.get_or_404(emprunt_id)
    db.session.delete(emprunt)
    db.session.commit()
    livre = Livre.query.get_or_404(emprunt.id_livre)
    livre.status = 0
    db.session.commit()
    return redirect(url_for('emprunts'))

@app.route("/livres/supprimer/<int:livre_id>")
def supprimer_livre(livre_id):
    livre = Livre.query.get_or_404(livre_id)
    db.session.delete(livre)
    db.session.commit()
    return redirect(url_for('livres'))

@app.route("/modifier_livre/<int:livre_id>", methods=["GET", "POST"])
def modifier_livre(livre_id):
    livre = Livre.query.get_or_404(livre_id)
    
    if request.method == "POST":
        # Récupérer les données soumises depuis le formulaire
        livre.titre = request.form.get('titre')
        livre.description = request.form.get('description')
        livre.auteur = request.form.get('auteur')
        livre.genre = request.form.get('genre')
        livre.datepub = request.form.get('datepub')
        livre.image = request.form.get('image')
        db.session.commit()

        livres = Livre.query.all()
        emprunts = Emprunt.query.all()
        utilisateurs = User.query.all()
        return redirect(url_for('livres', livres=livres, emprunts=emprunts, utilisateurs=utilisateurs))
    return render_template('modifier_livre.html', livre=livre)

@app.route("/utilisateur/supprimer/<int:user_id>", methods=["POST"])
def supprimer_utilisateur(user_id):
    utilisateur = User.query.get_or_404(user_id)
    db.session.delete(utilisateur)
    db.session.commit()

    livres = Livre.query.all()
    emprunts = Emprunt.query.all()
    utilisateurs = User.query.all()
    return redirect(url_for('emprunts', livres=livres, emprunts=emprunts, utilisateurs=utilisateurs))

@app.route("/modifier_utilisateur<int:user_id>", methods=["GET", "POST"])
def modifier_utilisateur(user_id):
    utilisateur = User.query.get_or_404(user_id)
    
    if request.method == "POST":
        utilisateur.username = request.form.get('username')
        utilisateur.email = request.form.get('email')
        utilisateur.mdp = request.form.get('mdp')
        db.session.commit()
        logout_user()
        return redirect(url_for('connexion'))
    return render_template('modifier_utilisateur.html', utilisateur=utilisateur)   

@app.route('/recherche', methods=['GET', 'POST'])
def recherche():
    if request.method == 'POST':
        recherches = request.form.get('recherches')
        if recherches:
            results = Livre.query.filter(
                Livre.titre.contains(recherches) |
                Livre.auteur.contains(recherches) |
                Livre.description.contains(recherches)
            ).all()
            return render_template('recherche.html', results=results)
        else:
            return render_template('recherche.html', error="Veuillez entrer un terme de recherche.")
    return render_template('recherche.html')


if __name__== "__main__":
    app.run(debug=True)