from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'ファイルが見つかりません。'
        file = request.files['file']
        if file.filename == '':
            return 'ファイル名が空です。'

        # 保存先ディレクトリを確認・作成
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(upload_dir, file.filename)
        file.save(filepath)
        return 'アップロード完了しました。'

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
