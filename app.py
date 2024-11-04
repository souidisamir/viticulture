from flask import Flask, render_template, request, redirect, url_for,session, flash
import sqlite3
import hashlib
app = Flask(__name__)
app.secret_key = 'samirswidisecretkey'
# Nom de la base de données
DB_NAME = 'agriculture_db.sqlite'

# Fonction pour se connecter à la base de données
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Retourne les résultats sous forme de dictionnaire
    return conn
# Page d'accueil (redirection vers login si non connecté)
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')
def get_user_by_id(user_id):
    # Connexion à la base de données (ajustez les paramètres selon votre configuration)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chefs_exploitation WHERE id_chef = ?", (user_id,))
    user = cursor.fetchone()  # Récupérer l'utilisateur
    conn.close()
    return user
# Route pour afficher toutes les exploitations
@app.route('/login', methods=('GET', 'POST'))
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        login = request.form['login']
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        conn = get_db_connection()
        
        if login == "admin":
            admin_login = conn.execute(
                'SELECT * FROM authentification WHERE login = ? AND password = ?', 
                (login, password)
            ).fetchone()
            
            if admin_login:
                session['admin'] = admin_login['login']
                session['user_id']=admin_login['id']
                return redirect(url_for('index'))
            else:
                flash('Nom d\'utilisateur ou mot de passe incorrect.')
        
        else:
            user = conn.execute(
                'SELECT * FROM chefs_exploitation WHERE username_chef = ? AND password_chef = ?', 
                (login, password)
            ).fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user['id_chef']
                user_data = get_user_by_id(session['user_id'])
                session['admin'] = user_data['nom_chef'] + ' ' + user_data['prenom_chef']
                return redirect(url_for('index'))
            else:
                flash('Nom d\'utilisateur ou mot de passe incorrect.')

    return render_template('login.html')

# Déconnexion
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/exploitations')
def exploitations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    exploitations = conn.execute('SELECT * FROM exploitations').fetchall()
    conn.close()
    return render_template('exploitations.html', exploitations=exploitations)

# Route pour ajouter une exploitation
@app.route('/exploitations/add', methods=('GET', 'POST'))
def add_exploitation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nom = request.form['nom']
        superficie = request.form['superficie']

        conn = get_db_connection()
        conn.execute('INSERT INTO exploitations (nom_exploitation, superficie) VALUES (?, ?)', (nom, superficie))
        conn.commit()
        conn.close()
        return redirect(url_for('exploitations'))
    
    return render_template('add_exploitation.html')

# Route pour modifier une exploitation
@app.route('/exploitations/edit/<int:id>', methods=('GET', 'POST'))
def edit_exploitation(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    exploitation = conn.execute('SELECT * FROM exploitations WHERE id_exploitation = ?', (id,)).fetchone()

    if request.method == 'POST':
        nom = request.form['nom']
        superficie = request.form['superficie']
        
        conn.execute('UPDATE exploitations SET nom_exploitation = ?, superficie = ? WHERE id_exploitation = ?', (nom, superficie, id))
        conn.commit()
        conn.close()
        return redirect(url_for('exploitations'))

    return render_template('edit_exploitation.html', exploitation=exploitation)

# Route pour supprimer une exploitation
@app.route('/exploitations/delete/<int:id>')
def delete_exploitation(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM exploitations WHERE id_exploitation = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('exploitations'))

# Routes pour les autres tables (chefs_exploitation, salariés, etc.) fonctionnent de la même manière.
# Vous pouvez dupliquer le modèle utilisé pour 'exploitations' pour chaque table.



# Lister les chefs d'exploitation
@app.route('/chefs_exploitation')
def chefs_exploitation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    chefs = conn.execute('SELECT * FROM chefs_exploitation').fetchall()
    conn.close()
    return render_template('chefs_exploitation.html', chefs=chefs)

# Route pour ajouter un chef d'exploitation
@app.route('/chefs_exploitation/add', methods=('GET', 'POST'))
def add_chef_exploitation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    exploitations = conn.execute('SELECT * FROM exploitations').fetchall()  # Récupérer toutes les exploitations
    conn.close()

    if request.method == 'POST':
        username_chef=request.form['username_chef']
        nom = request.form['nom']
        prenom = request.form['prenom']
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        id_exploitation = request.form['id_exploitation']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO chefs_exploitation (username_chef,nom_chef, prenom_chef,password_chef, id_exploitation) VALUES (?,?, ?,?, ?)',
                     (username_chef,nom, prenom,password, id_exploitation))
        conn.commit()
        conn.close()
        return redirect(url_for('chefs_exploitation'))

    return render_template('add_chef_exploitation.html', exploitations=exploitations)

# Modifier un chef d'exploitation
@app.route('/chefs_exploitation/edit/<int:id>', methods=('GET', 'POST'))
def edit_chef_exploitation(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    chef = conn.execute('SELECT * FROM chefs_exploitation WHERE id_chef = ?', (id,)).fetchone()
    exploitations = conn.execute('SELECT * FROM exploitations').fetchall()  # Récupérer toutes les exploitations
    conn.close()

    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        id_exploitation = request.form['id_exploitation']
        
        conn = get_db_connection()
        conn.execute('UPDATE chefs_exploitation SET nom_chef = ?, prenom_chef = ?, id_exploitation = ? WHERE id_chef = ?',
                     (nom, prenom, id_exploitation, id))
        conn.commit()
        conn.close()
        return redirect(url_for('chefs_exploitation'))

    return render_template('edit_chef_exploitation.html', chef=chef, exploitations=exploitations)

# Supprimer un chef d'exploitation
@app.route('/chefs_exploitation/delete/<int:id>', methods=('POST',))
def delete_chef_exploitation(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM chefs_exploitation WHERE id_chef = ?', (id,))
    conn.commit()
    conn.close()
    #flash('Chef d\'exploitation supprimé avec succès.')
    return redirect(url_for('chefs_exploitation'))


# salarié
@app.route('/salaries')
def salaries():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    salaries = conn.execute('SELECT * FROM salaries inner join exploitations on exploitations.id_exploitation=salaries.id_exploitation').fetchall()
    conn.close()
    
    return render_template('salaries.html', salaries=salaries)
# Route pour ajouter un salarié
@app.route('/salaries/add_salarie', methods=('GET', 'POST'))
def add_salarie():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    exploitations = conn.execute('SELECT * FROM exploitations').fetchall()  # Récupérer toutes les exploitations
    conn.close()    
    if request.method == 'POST':
        identifiant = request.form['identifiant']
        nom = request.form['nom']
        prenom = request.form['prenom']
        date_embauche = request.form['date_embauche']
        id_exploitation=request.form['id_exploitation']
        # Ouverture de la connexion
        conn = get_db_connection()
        
        # Vérification si le salarié existe déjà
        verif = conn.execute('SELECT * FROM salaries WHERE identifiant_sal = ?', (identifiant, )).fetchone()
        
        if verif:
            flash('Salarié déjà existe.', 'error')
            conn.close()  # Fermer la connexion après la vérification
            return render_template('add_salarie.html', exploitations=exploitations)
        else:
            # Insertion du salarié dans la base de données
            conn.execute(
                'INSERT INTO salaries (identifiant_sal, nom_salarie, prenom_salarie, date_embauche,id_exploitation) VALUES (?, ?, ?, ?,?)',
                (identifiant, nom, prenom, date_embauche,id_exploitation)
            )
            conn.commit()  # Enregistrer les modifications dans la base de données
            flash('Salarié ajouté avec succès.', 'success')
            conn.close()  # Fermer la connexion après l'insertion
            
            return redirect(url_for('add_salarie'))  # Redirection vers la même page après l'insertion
    
    return render_template('add_salarie.html', exploitations=exploitations)

    

@app.route('/salaries/edit/<int:id>', methods=('GET', 'POST'))
def edit_salarie(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Récupérer le salarié et les exploitations en utilisant une seule connexion
    salarie = conn.execute('SELECT * FROM salaries WHERE id_salarie = ?', (id,)).fetchone()
    exploitations = conn.execute('SELECT * FROM exploitations').fetchall()  # Récupérer toutes les exploitations
    
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        date_embauche = request.form['date_embauche']
        id_exploitation = request.form['id_exploitation']
        
        # Mettre à jour les informations du salarié
        conn.execute(
            'UPDATE salaries SET nom_salarie = ?, prenom_salarie = ?, date_embauche = ?, id_exploitation = ? WHERE id_salarie = ?',
            (nom, prenom, date_embauche, id_exploitation, id)
        )
        conn.commit()  # Confirmer les changements
        
        # Fermer la connexion après toutes les opérations
        conn.close()
        
        return redirect(url_for('salaries'))

    # Fermer la connexion après toutes les opérations de récupération si pas de mise à jour
    conn.close()
    flash('Salarié modifié avec succès.')
    return render_template('edit_salarie.html', salarie=salarie, exploitations=exploitations)

# Route pour supprimer une salarie

@app.route('/salaries/delete/<int:id>', methods=('POST',) )
def delete_salarie(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM salaries WHERE id_salarie = ?', (id,))
    conn.commit()
    conn.close()
    flash('Salarié supprimé avec succès.')
    return redirect(url_for('salaries'))



if __name__ == '__main__':
    app.run(debug=True)
