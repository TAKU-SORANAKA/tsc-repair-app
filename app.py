import os
import smtplib
import random
from flask import Flask, render_template, request, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)

def send_email(to_email, code):
    from_email = "ceo@ts-c.net"
    password = os.environ.get("EMAIL_PASSWORD")
    smtp_server = "smtp.ts-c.net"  # ← 実際のSMTPサーバー名に適宜修正してください
    smtp_port = 587

    if not password:
        raise RuntimeError("EMAIL_PASSWORD is not set in environment variables.")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(from_email, password)

            subject = "認証コードのお知らせ"
            body = f"認証コードは {code} です。"
            msg = f"Subject: {subject}\n\n{body}"

            server.sendmail(from_email, to_email, msg)
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP認証エラー: {e}")
        raise RuntimeError("メールサーバの認証に失敗しました。")
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
