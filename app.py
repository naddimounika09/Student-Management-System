from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "student123"


def get_db():
    conn = sqlite3.connect("database.db")
    return conn


@app.route('/')
def home():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = username
            return redirect('/dashboard')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():

    conn = get_db()
    cursor = conn.cursor()

    search = request.args.get('search', '')

    if search:
        cursor.execute("""
        SELECT * FROM students
        WHERE name LIKE ?
        OR email LIKE ?
        OR course LIKE ?
        """,
        (
            f'%{search}%',
            f'%{search}%',
            f'%{search}%'
        ))
    else:
        cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    total_students = len(students)

    marks = [int(student[5]) for student in students] if students else [0]

    avg_marks = round(sum(marks)/len(marks), 2)
    highest_marks = max(marks)
    lowest_marks = min(marks)

    return render_template(
        'dashboard.html',
        students=students,
        total_students=total_students,
        avg_marks=avg_marks,
        highest_marks=highest_marks,
        lowest_marks=lowest_marks,
        search=search
    )


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():

    if request.method == 'POST':

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO students
        (name,email,course,attendance,marks)
        VALUES(?,?,?,?,?)
        """,
        (
            request.form['name'],
            request.form['email'],
            request.form['course'],
            request.form['attendance'],
            request.form['marks']
        ))

        conn.commit()

        return redirect('/dashboard')

    return render_template('add_student.html')


@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':

        cursor.execute("""
        UPDATE students
        SET name=?, email=?, course=?, attendance=?, marks=?
        WHERE id=?
        """,
        (
            request.form['name'],
            request.form['email'],
            request.form['course'],
            request.form['attendance'],
            request.form['marks'],
            id
        ))

        conn.commit()

        return redirect('/dashboard')

    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()

    return render_template(
        'edit_student.html',
        student=student
    )


@app.route('/delete_student/<int:id>')
def delete_student(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()

    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)