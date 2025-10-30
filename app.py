from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3, os, time, hashlib, secrets, string
from blockchain import Blockchain

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')
blockchain = Blockchain()
DB_FILE = "database.db"

# ----------------- Security Functions -----------------
def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest(), salt

def verify_password(password, hashed_password, salt):
    """Verify password against hash"""
    return hashlib.sha256((password + salt).encode()).hexdigest() == hashed_password

def generate_anonymous_token():
    """Generate a secure anonymous token"""
    return "ANON_" + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))

def generate_coin_id():
    """Generate a unique coin id"""
    return "COIN_" + secrets.token_hex(8).upper()

def migrate_database():
    """Migrate existing database to new schema"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        # Check if we need to migrate existing voters
        c.execute("SELECT voter_id, password FROM voters WHERE salt IS NULL LIMIT 1")
        old_voters = c.fetchall()
        
        if old_voters:
            print("🔄 Migrating existing voters to new security schema...")
            for voter_id, old_password in old_voters:
                # Generate new salt and hash for old passwords
                hashed_pwd, salt = hash_password(old_password)
                anonymous_token = generate_anonymous_token()
                
                c.execute("UPDATE voters SET password=?, salt=?, anonymous_token=? WHERE voter_id=?", 
                         (hashed_pwd, salt, anonymous_token, voter_id))
            
            print("✅ Database migration completed!")
        
        conn.commit()
    except Exception as e:
        print(f"Migration note: {e}")
    finally:
        conn.close()

# ----------------- DB Setup -----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create voters table with new schema
    c.execute("""CREATE TABLE IF NOT EXISTS voters(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    voter_id TEXT UNIQUE,
                    name TEXT,
                    password TEXT,
                    salt TEXT,
                    anonymous_token TEXT UNIQUE,
                    has_voted INTEGER DEFAULT 0,
                    mobile TEXT,
                    aadhaar_hash TEXT,
                    aadhaar_last4 TEXT,
                    aadhaar_verified INTEGER DEFAULT 0)""")
    
    # Add new columns to existing voters table if they don't exist
    try:
        c.execute("ALTER TABLE voters ADD COLUMN salt TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        c.execute("ALTER TABLE voters ADD COLUMN anonymous_token TEXT UNIQUE")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        c.execute("ALTER TABLE voters ADD COLUMN has_voted INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # New columns for Aadhaar + mobile
    try:
        c.execute("ALTER TABLE voters ADD COLUMN mobile TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE voters ADD COLUMN aadhaar_hash TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE voters ADD COLUMN aadhaar_last4 TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE voters ADD COLUMN aadhaar_verified INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    # Create admin table
    c.execute("""CREATE TABLE IF NOT EXISTS admin(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)""")
    
    # Create votes table with new schema
    c.execute("""CREATE TABLE IF NOT EXISTS votes(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anonymous_token TEXT,
                    candidate TEXT,
                    timestamp TEXT)""")
    
    # Update existing votes table if it has old schema
    try:
        c.execute("ALTER TABLE votes ADD COLUMN anonymous_token TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        c.execute("ALTER TABLE votes ADD COLUMN timestamp TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create coins table (one coin per voter, spent when voting)
    c.execute("""CREATE TABLE IF NOT EXISTS coins(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_id TEXT UNIQUE,
                    voter_id TEXT,
                    spent INTEGER DEFAULT 0,
                    spent_to TEXT,
                    spent_at TEXT)""")
    # Backfill: mint a coin for any voter lacking one
    try:
        c.execute("""
            SELECT v.voter_id FROM voters v
            LEFT JOIN coins c2 ON c2.voter_id = v.voter_id
            WHERE c2.voter_id IS NULL
        """)
        missing = [row[0] for row in c.fetchall()]
        for vid in missing:
            c.execute("INSERT OR IGNORE INTO coins(coin_id, voter_id, spent) VALUES (?,?,0)", (generate_coin_id(), vid))
        conn.commit()
    except Exception:
        pass
    
    # Migrate existing data if needed
    try:
        c.execute("SELECT voter_id FROM voters WHERE anonymous_token IS NULL LIMIT 1")
        if c.fetchone():
            # Generate anonymous tokens for existing voters
            c.execute("SELECT voter_id FROM voters WHERE anonymous_token IS NULL")
            existing_voters = c.fetchall()
            for voter in existing_voters:
                token = generate_anonymous_token()
                c.execute("UPDATE voters SET anonymous_token=? WHERE voter_id=?", (token, voter[0]))
    except sqlite3.OperationalError:
        pass  # No existing data to migrate
    
    conn.commit()
    
    # Create default admin (change password in production)
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    c.execute("INSERT OR IGNORE INTO admin(username,password) VALUES (?,?)", ("admin", admin_password))
    conn.commit()
    
    # Backfill existing rows to not block old users: set aadhaar_verified=1 if NULL
    try:
        c.execute("UPDATE voters SET aadhaar_verified=1 WHERE aadhaar_verified IS NULL")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()

# ----------------- Routes -----------------
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (user,pwd))
        admin = c.fetchone()
        conn.close()
        if admin:
            session['admin'] = user
            return redirect(url_for('admin_dashboard'))
        flash("Invalid admin credentials.")
    return render_template("login.html", role="Admin")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    # Tally votes directly from the blockchain ledger to keep graph in sync with ledger
    tally = {}
    for blk in blockchain.chain[1:]:  # skip genesis block at index 0
        data = blk.get('data', {})
        cand = data.get('vote')
        if not cand:
            continue
        tally[cand] = tally.get(cand, 0) + 1
    labels = list(tally.keys())
    counts = [tally[lbl] for lbl in labels]
    valid_chain = blockchain.is_valid()
    active_validator = session.get('validator_id')
    validators = blockchain.get_validator_ids()

    # Find winner
    winner = "No votes yet"
    if counts:
        winner = labels[counts.index(max(counts))]

    return render_template("admin_dashboard.html",
                           labels=labels, counts=counts,
                           valid_chain=valid_chain,
                           chain=blockchain.chain,
                           winner=winner,
                           active_validator=active_validator,
                           validators=validators,
                           validators_full=blockchain.get_validators_full(),
                           threshold=getattr(blockchain, 'threshold', 1))

@app.route('/validator', methods=['GET', 'POST'])
def validator_login():
    if request.method == 'POST':
        vid = request.form.get('validator_id')
        if vid and vid in blockchain.get_validator_ids():
            session['validator_id'] = vid
            flash(f"Logged in as validator: {vid}")
            return redirect(url_for('admin_dashboard'))
        flash('Invalid validator selection.')
    return render_template('validator.html', validators_full=blockchain.get_validators_full())

@app.route('/validator/logout')
def validator_logout():
    session.pop('validator_id', None)
    flash('Validator logged out.')
    return redirect(url_for('admin_dashboard'))

@app.route('/validator/sign_latest', methods=['POST'])
def validator_sign_latest():
    vid = session.get('validator_id')
    if not vid:
        flash('Please log in as a validator first.')
        return redirect(url_for('validator_login'))
    ok = blockchain.add_signature_latest(vid)
    if ok:
        flash('Signature added to latest block (local simulation).')
    else:
        flash('Failed to add signature.')
    return redirect(url_for('admin_dashboard'))

@app.route('/validator/sign_all', methods=['POST'])
def validator_sign_all():
    vid = session.get('validator_id')
    if not vid:
        flash('Please log in as a validator first.')
        return redirect(url_for('validator_login'))
    n = blockchain.add_signature_all(vid)
    flash(f'Added {n} signatures for validator {vid}.')
    return redirect(url_for('admin_dashboard'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        voter_id = request.form['voter_id']
        pwd = request.form['password']
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Hash password and generate anonymous token
            hashed_pwd, salt = hash_password(pwd)
            anonymous_token = generate_anonymous_token()
            
            # Insert user; skip mobile/OTP and mark verified by default
            c.execute("INSERT INTO voters(voter_id,name,password,salt,anonymous_token,aadhaar_verified) VALUES (?,?,?,?,?,1)",
                      (voter_id, name, hashed_pwd, salt, anonymous_token))
            # Mint one coin for the voter
            coin_id = generate_coin_id()
            c.execute("INSERT INTO coins(coin_id, voter_id, spent) VALUES (?,?,0)", (coin_id, voter_id))
            conn.commit()
            conn.close()
            flash("Registration successful. You can now log in.")
            return redirect(url_for('voter_login'))
        except sqlite3.IntegrityError:
            flash("Voter ID already registered.")
        except Exception as e:
            flash(f"Registration failed: {str(e)}")
    return render_template("register.html")

@app.route('/voter', methods=['GET','POST'])
def voter_login():
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        pwd = request.form['password']
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT voter_id, password, salt, anonymous_token, has_voted FROM voters WHERE voter_id=?", (voter_id,))
        user = c.fetchone()
        conn.close()
        
        if user and verify_password(pwd, user[1], user[2]):
            session['voter_id'] = voter_id
            session['anonymous_token'] = user[3]
            return redirect(url_for('vote'))
        else:
            flash("Invalid credentials.")
    return render_template("login.html", role="Voter")

@app.route('/vote', methods=['GET','POST'])
def vote():
    if 'voter_id' not in session:
        return redirect(url_for('voter_login'))
    
    voter_id = session['voter_id']
    anonymous_token = session.get('anonymous_token')
    
    if request.method == 'POST':
        candidate = request.form['candidate']
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Check if already voted
        c.execute("SELECT has_voted FROM voters WHERE voter_id= ?", (voter_id,))
        voter_status = c.fetchone()
        
        if voter_status and voter_status[0] == 1:
            flash("You have already voted.")
        else:
            # Fetch an unspent coin for this voter
            c.execute("SELECT coin_id FROM coins WHERE voter_id= ? AND spent=0 LIMIT 1", (voter_id,))
            coin_row = c.fetchone()
            if not coin_row:
                conn.close()
                flash("No available voting coin found for this voter.")
                return render_template("vote.html")
            coin_id = coin_row[0]

            # Record vote with anonymous token
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO votes(anonymous_token,candidate,timestamp) VALUES (?,?,?)",
                      (anonymous_token, candidate, timestamp))
            
            # Mark voter as having voted
            c.execute("UPDATE voters SET has_voted=1 WHERE voter_id= ?", (voter_id,))

            # Spend the coin
            c.execute("UPDATE coins SET spent=1, spent_to= ?, spent_at= ? WHERE coin_id= ?", (candidate, timestamp, coin_id))
            
            conn.commit()
            conn.close()
            
            # Add to blockchain with anonymous token
            blockchain.add_block({"anonymous_token": anonymous_token, "vote": candidate, "coin_id": coin_id})
            flash("Vote recorded successfully! Your vote is anonymous and secure.")
            return redirect(url_for('vote'))
        conn.close()
    return render_template("vote.html")

if __name__ == "__main__":
    init_db()
    migrate_database()
    app.run(debug=True)