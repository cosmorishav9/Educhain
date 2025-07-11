from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_migrate import Migrate
from io import BytesIO
from reportlab.pdfgen import canvas
from sqlalchemy import desc

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rishavmitra187@gmail.com'
app.config['MAIL_PASSWORD'] = 'kpda gysq xsob lhln'

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    wallet = db.Column(db.String(200), nullable=False, default="not_assigned")
    certificates = db.relationship('Certificate', backref='user', lazy=True)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    issue_date = db.Column(db.String(100), nullable=False)
    cert_id = db.Column(db.String(100), nullable=False, unique=True)
    dob = db.Column(db.String(100), nullable=False)
    class_10_marks = db.Column(db.String(20), nullable=False)
    class_12_marks = db.Column(db.String(20), nullable=False)
    stream = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.String(10), nullable=False)

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        if not name or not email:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash(f'Email {email} is already registered!', 'danger')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()

        try:
            msg = Message(
                subject='Welcome to EduChain',
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = f"""
Hi {name},

You have successfully signed up on EduChain!

Now, head over to the "Issue Certificate" page on our website to provide your educational credentials.

Best regards,  
EduChain Team
"""
            mail.send(msg)
            flash(f'Confirmation email sent to {email}!', 'success')
        except Exception as e:
            flash(f'Error sending confirmation email: {str(e)}', 'danger')

        return redirect(url_for('registration_success', name=name))

    return render_template('register.html')

@app.route('/registration_success')
def registration_success():
    name = request.args.get('name')
    return render_template('registration_success.html', name=name)

@app.route('/issue', methods=['GET', 'POST'])
def issue_certificate():
    if request.method == 'POST':
        form_data = request.form

        required_fields = ['name', 'email', 'course', 'issue_date', 'dob', 
                           'class_10_marks', 'class_12_marks', 'stream', 'cgpa']
        if not all(form_data.get(field) for field in required_fields):
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('issue_certificate'))

        user = User.query.filter_by(email=form_data['email']).first()
        if not user:
            flash('User with the given email not found.', 'danger')
            return redirect(url_for('issue_certificate'))

        cert_id = f"{form_data['name'].replace(' ', '_')}_{form_data['course'].replace(' ', '_')}_{form_data['issue_date'].replace('-', '')}"

        new_cert = Certificate(
            user_id=user.id,
            course=form_data['course'],
            issue_date=form_data['issue_date'],
            cert_id=cert_id,
            dob=form_data['dob'],
            class_10_marks=form_data['class_10_marks'],
            class_12_marks=form_data['class_12_marks'],
            stream=form_data['stream'],
            cgpa=form_data['cgpa']
        )
        db.session.add(new_cert)
        db.session.commit()

        flash(f'Certificate issued for {form_data["name"]} (ID: {cert_id})', 'success')
        return redirect(url_for('certificate_issued', name=form_data["name"], cert_id=cert_id))

    return render_template('issue_certificate.html')

@app.route('/certificate_issued')
def certificate_issued():
    name = request.args.get('name')
    cert_id = request.args.get('cert_id')
    return render_template('certificate_issued.html', name=name, cert_id=cert_id)

@app.route('/verify', methods=['GET', 'POST'])
def verify_certificate():
    if request.method == 'POST':
        cert_id = request.form['cert_id']
        certificate = Certificate.query.filter_by(cert_id=cert_id).first()

        if certificate:
            return render_template('certificate_verified.html',
                                   message=f"Certificate ID '{cert_id}' verified successfully.",
                                   status='success',
                                   certificate=certificate)
        else:
            return render_template('certificate_verified.html',
                                   message=f"Certificate ID '{cert_id}' not found.",
                                   status='failure',
                                   certificate=None)

    return render_template('verify_certificate.html')

@app.route('/download_certificate/<cert_id>')
def download_certificate(cert_id):
    certificate = Certificate.query.filter_by(cert_id=cert_id).first()
    if not certificate:
        flash('Certificate not found.', 'danger')
        return redirect(url_for('verify_certificate'))

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Certificate ID: {certificate.cert_id}")
    p.drawString(100, 780, f"Name: {certificate.user.name}")
    p.drawString(100, 760, f"Course: {certificate.course}")
    p.drawString(100, 740, f"Issue Date: {certificate.issue_date}")
    p.drawString(100, 720, f"DOB: {certificate.dob}")
    p.drawString(100, 700, f"Class 10 Marks: {certificate.class_10_marks}")
    p.drawString(100, 680, f"Class 12 Marks: {certificate.class_12_marks}")
    p.drawString(100, 660, f"Stream: {certificate.stream}")
    p.drawString(100, 640, f"CGPA: {certificate.cgpa}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{cert_id}.pdf", mimetype='application/pdf')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('view_certificates'))
        else:
            flash('Invalid admin credentials', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/view_certificates', methods=['GET'])
def view_certificates():
    email_query = request.args.get('email')

    if email_query:
        user = User.query.filter_by(email=email_query).first()
        if user:
            certificates = Certificate.query.filter_by(user_id=user.id).order_by(desc(Certificate.issue_date)).all()
        else:
            certificates = []
    else:
        certificates = Certificate.query.order_by(desc(Certificate.issue_date)).all()

    return render_template('view_certificates.html', certificates=certificates)

# Informational Pages Routes
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/how_it_works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)


#from web3 import Web3

# Connect to Ethereum node (make sure the Ethereum node is running or use Infura for a remote node)
"""
w3 = Web3(Web3.HTTPProvider('https://rinkeby.infura.io/v3/YOUR_INFURA_PROJECT_ID'))

# Replace with your contract's address and ABI (Application Binary Interface)
contract_address = 'YOUR_CONTRACT_ADDRESS'
contract_abi = [
    # Copy your contract ABI here
]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Issuing a certificate (on the blockchain)

@app.route('/issue_certificate_on_blockchain', methods=['POST'])
def issue_certificate_on_blockchain():
    name = request.form['name']
    course = request.form['course']
    issue_date = request.form['issue_date']
    cert_id = f"{name.replace(' ', '_')}_{course.replace(' ', '_')}_{issue_date.replace('-', '')}"

    # Interact with the smart contract to issue the certificate
    account = 'YOUR_WALLET_ADDRESS'
    private_key = 'YOUR_PRIVATE_KEY'

    # Build the transaction
    txn = contract.functions.issueCertificate(cert_id, name, course, issue_date).buildTransaction({
        'chainId': 4,  # Rinkeby Testnet chain ID
        'gas': 2000000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': w3.eth.getTransactionCount(account),
    })

    # Sign the transaction
    signed_txn = w3.eth.account.signTransaction(txn, private_key)

    # Send the transaction
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    return f"Certificate Issued! Transaction Hash: {txn_hash.hex()}"

# Verifying a certificate (from the blockchain)
@app.route('/verify_certificate_on_blockchain', methods=['POST'])
def verify_certificate_on_blockchain():
    cert_id = request.form['cert_id']

    # Call the smart contract to get certificate details
    result = contract.functions.verifyCertificate(cert_id).call()
    if result:
        cert_details = {
            "cert_id": result[0],
            "name": result[1],
            "course": result[2],
            "issue_date": result[3]
        }
        return render_template('certificate_verified.html', certificate=cert_details)
    else:
        flash('Certificate not found.', 'danger')
        return redirect(url_for('verify_certificate'))
"""