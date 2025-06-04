from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os

app = Flask(__name__)
app.secret_key = 'secret-key'

DATA_FILE = 'data.csv'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        if not email.endswith('@ts-c.net'):
            return "社用メールアドレスのみ使用できます"
        session['authenticated'] = True
        return redirect(url_for('menu'))
    return render_template('send_code.html')

@app.route('/menu')
def menu():
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('menu.html')

@app.route('/diagnose', methods=['GET', 'POST'])
def diagnose():
    diagnosis = ''
    if request.method == 'POST':
        product = request.form['product']
        symptom = request.form['symptom']
        with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['product'] == product and row['symptom'] == symptom:
                    diagnosis = row['cause']
                    break
    return render_template('diagnose.html', diagnosis=diagnosis)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        product = request.form['product']
        symptom = request.form['symptom']
        cause = request.form['cause']
        solution = request.form['solution']
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['product', 'symptom', 'cause', 'solution'])
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow({'product': product, 'symptom': symptom, 'cause': cause, 'solution': solution})
        return redirect(url_for('menu'))
    return render_template('register.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist('csv_files')
        for file in files:
            if file and file.filename.endswith('.csv'):
                file.save(os.path.join('uploads', file.filename))
        return redirect(url_for('menu'))
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
