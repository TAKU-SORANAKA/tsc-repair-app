from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_session import Session
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/', methods=['GET', 'POST'])
def send_code():
    if request.method == 'POST':
        email = request.form['email']

        # ドメインチェックを追加
        if not email.endswith('@ts-c.net'):
            flash('社内メールアドレス（@ts-c.net）をご利用ください。')
            return render_template('send_code.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_csvs():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            try:
                raw_data = file.read()
                try:
                    decoded = raw_data.decode('utf-8')
                except UnicodeDecodeError:
                    decoded = raw_data.decode('shift_jis')
            except Exception as e:
                flash('ファイルの読み込みに失敗しました。')
                return redirect(url_for('upload_csvs'))
        flash('アップロード成功')
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
