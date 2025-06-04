from flask import Flask, render_template, request, redirect, url_for, session
import smtplib
from email.message import EmailMessage
import os
import random
import string

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')

def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_email(to_email, code):
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.ts-c.net')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    from_email = os.environ.get('EMAIL_ADDRESS', 'ceo@ts-c.net')
    password = os.environ.get('EMAIL_PASSWORD')

    if not password:
        raise RuntimeError("EMAIL_PASSWORD is not set in environment variables.")

    try:
        msg = EmailMessage()
        msg.set_content(f'あなたの認証コードは: {code}')
        msg['Subject'] = '認証コードの送信'
        msg['From'] = from_email
        msg['To'] = to_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
    except Exception as e:
        print("メール送信エラー:", e)
        raise RuntimeError("メール送信中に予期せぬエラーが発生しました。")

@app.route('/', methods=['GET', 'POST'])
def send_code():
    if request.method == 'POST':
        email = request.form['email']
        if not email.endswith('@ts-c.net'):
            return "社用メールアドレスのみ使用できます"

        code = generate_code()
        session['code'] = code
        session['email'] = email
        send_email(email, code)
        return redirect(url_for('verify_code'))
    return render_template('send_code.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        user_code = request.form['code']
        if user_code == session.get('code'):
            return render_template('menu.html')  # 認証成功後のページ
        else:
            return "認証コードが正しくありません。"
    return render_template('verify_code.html')  # GET時

if __name__ == '__main__':
    app.run(debug=True)
