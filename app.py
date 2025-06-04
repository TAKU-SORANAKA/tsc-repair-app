
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_session import Session
import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
import csv
import io
import chardet

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_email(to_email, code):
    from_email = "ceo@ts-c.net"
    password = os.environ.get('sachi111')
    smtp_server = "mail.ts-c.net"
    smtp_port = 587

    msg = MIMEText(f'あなたの確認コードは: {code}')
    msg['Subject'] = "【TSC　Repair Manager】ログイン確認コード"
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)

@app.route('/', methods=['GET', 'POST'])
def send_code():
    if request.method == 'POST':
        email = request.form['email']
        if not email.endswith('@ts-c.net'):
            return "社用メールアドレスのみ使用できます"
        code = generate_code()
        session['email'] = email
        session['code'] = code
        send_email(email, code)
        return redirect(url_for('verify'))
    else:
        return render_template('send_code.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        user_code = request.form['code']
        if user_code == session.get('code'):
            return redirect(url_for('menu'))
        else:
            flash('認証コードが間違っています')
            return redirect(url_for('verify'))
    return render_template('verify.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_csvs():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        results = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                raw_data = file.read()
                encoding = chardet.detect(raw_data)['encoding']
                try:
                    decoded = raw_data.decode(encoding)
                except Exception as e:
                    return f"ファイルのデコードに失敗しました: {str(e)}"
                stream = io.StringIO(decoded)
                csv_input = csv.reader(stream)
                headers = next(csv_input, None)
                for row in csv_input:
                    results.append(row)
        return render_template('results.html', results=results)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
