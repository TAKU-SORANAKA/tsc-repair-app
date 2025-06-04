
import os
import csv
import io
import random
import string
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_session import Session

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# 環境変数からメール設定を取得
SMTP_SERVER = 'mail.ts-c.net'
SMTP_PORT = 587
SENDER_EMAIL = 'ceo@ts-c.net'
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')

DATA_FILE = 'data.csv'

@app.route('/', methods=['GET', 'POST'])
def send_code():
    if request.method == 'POST':
        else:return render_template('send_code.html')
        email = request.form['email']
        if not email.endswith('@ts-c.net'):
            return "社用メールアドレスのみ使用できます"

        code = ''.join(random.choices(string.digits, k=6))
        session['auth_code'] = code
        session['email'] = email

        msg = EmailMessage()
        msg['Subject'] = '認証コード'
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg.set_content(f'あなたの認証コードは: {code}')

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(msg)
        except Exception as e:
            print(f"[MAIL ERROR] {e}")
            return "メール送信に失敗しました"

        return redirect('/verify')
    return render_template('send_code.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        code = request.form['code']
        if code == session.get('auth_code'):
            session['authenticated'] = True
            return redirect('/menu')
        else:
            flash('認証コードが間違っています。')
    return render_template('verify.html')


@app.route('/menu')
def menu():
    if not session.get('authenticated'):
        return redirect('/')
    return render_template('menu.html')


@app.route('/diagnose', methods=['GET', 'POST'])
def diagnose():
    if not session.get('authenticated'):
        return redirect('/')
    result = None
    if request.method == 'POST':
        product = request.form['product']
        symptom = request.form['symptom']
        with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['製品名'] == product and row['症状'] == symptom:
                    result = row['原因']
                    break
    return render_template('diagnose.html', result=result)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not session.get('authenticated'):
        return redirect('/')
    if request.method == 'POST':
        product = request.form['product']
        symptom = request.form['symptom']
        cause = request.form['cause']
        action = request.form['action']
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([product, symptom, cause, action])
        flash('登録が完了しました。')
    return render_template('register.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_csvs():
    if not session.get('authenticated'):
        return redirect('/')
    if request.method == 'POST':
        files = request.files.getlist('csv_files')
        for file in files:
            raw_data = file.stream.read()
            try:
                decoded = raw_data.decode('utf-8')
            except UnicodeDecodeError:
                decoded = raw_data.decode('shift_jis')
            stream = io.StringIO(decoded)
            reader = csv.reader(stream)
            next(reader, None)
            with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in reader:
                    writer.writerow(row)
        flash('CSVファイルのアップロードが完了しました。')
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
