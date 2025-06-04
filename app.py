from flask import Flask, request, render_template
import os
import random
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = os.urandom(24)

def send_email(to_email, code):
    smtp_server = 'mail.ts-c.net'
    smtp_port = 587
    from_email = 'ceo@ts-c.net'
    password = os.environ.get('EMAIL_PASSWORD')

    if not password:
        raise RuntimeError("EMAIL_PASSWORD is not set in environment variables.")

    subject = '認証コードのお知らせ'
    body = f'以下の認証コードを入力してください：\n\n{code}'

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)

    except Exception as e:
        print(f"メール送信エラー: {e}")
        raise RuntimeError("メール送信中に予期せぬエラーが発生しました。")

@app.route('/', methods=['GET', 'POST'])
def send_code():
    if request.method == 'POST':
        email = request.form['email']
        if not email.endswith('@ts-c.net'):
            return "社用メールアドレス（@ts-c.net）のみ使用できます。"

        code = str(random.randint(100000, 999999))
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
            return redirect(url_for('menu'))
        else:
            flash('認証コードが間違っています。')
    return render_template('verify.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

if __name__ == '__main__':
    app.run(debug=True)
