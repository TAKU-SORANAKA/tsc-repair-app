from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import csv
import os
import smtplib
import io
from email.mime.text import MIMEText
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

SMTP_SERVER = 'mail.ts-c.net'
SMTP_PORT = 587
SENDER_EMAIL = 'ceo@ts-c.net'
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')

DATA_FILE = 'repair_cases.csv'

@app.route('/', methods=['GET', 'POST'])
def send_code():
    if request.method == 'POST':
        email = request.form['email']
        if not email.endswith('@ts-c.net'):
            flash('社用メールアドレス（@ts-c.net）のみ使用可能です')
            return redirect(url_for('send_code'))

        code = str(random.randint(100000, 999999))
        session['auth_code'] = code
        session['email'] = email

        msg = MIMEText(f'認証コードは {code} です。5分以内に入力してください。')
        msg['Subject'] = '株式会社ティーエス・コーポレーション 認証コード'
        msg['From'] = SENDER_EMAIL
        msg['To'] = email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login('ceo@ts-c.net', os.environ.get('SENDER_PASSWORD'))
            smtp.send_message(msg)

        flash('認証コードを送信しました')
        return redirect(url_for('verify_code'))

    return render_template('send_code.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        if request.form['code'] == session.get('auth_code'):
            return redirect(url_for('menu'))
        else:
            flash('認証コードが正しくありません')
    return render_template('verify.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/diagnose', methods=['POST'])
def diagnose():
    product = request.form['product']
    symptom = request.form['symptom']
    cause = "情報がありません"
    repair = "詳細な確認が必要です。"
    if "A-1712" in product and "電源" in symptom:
        cause = "電源基板の破損"
        repair = "基板交換（所要5日）"
    elif "音が出ない" in symptom:
        cause = "スピーカー断線の可能性"
        repair = "スピーカーユニット交換"
    return render_template('diagnose.html', product=product, symptom=symptom, cause=cause, repair=repair)

@app.route('/register', methods=['POST'])
def register():
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            request.form['r_product'],
            request.form['r_symptom'],
            request.form['r_cause'],
            request.form['r_repair']
        ])
    flash('登録しました')
    return redirect(url_for('menu'))

@app.route('/upload', methods=['POST'])
def upload_csvs():
    uploaded_files = request.files.getlist('files')
    count = 0
    for file in uploaded_files:
        if file.filename.endswith('.csv'):
            stream = io.StringIO(file.stream.read().decode('utf-8'))
            reader = csv.reader(stream)
            with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in reader:
                    writer.writerow(row)
                    count += 1
    flash(f'{count}件のデータをCSVから追加しました')
    return redirect(url_for('menu'))

if __name__ == '__main__':
    app.run(debug=True)
