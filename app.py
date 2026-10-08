from flask import Flask, render_template,request ,redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    connection = sqlite3.connect("database.db")
    return connection

def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE  if not exists words (
            id INTEGER PRIMARY KEY,
            word TEXT,
            note TEXT
        )
    """)
    connection.commit()
    connection.close()



# Define a route for the home page
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/add", methods=["POST"])
def add_word():
    word = request.form["word"].strip()
    note = request.form["note"].strip()

    # إذا الكلمة فارغة أو فراغات بس، ارجع للصفحة الرئيسية بدون حفظ
    if not word:
        return redirect("/")

    connection = get_db_connection()

    connection.execute(
        "INSERT INTO words (word, note) VALUES (?, ?)",
        (word, note)
    )

    connection.commit()
    connection.close()

    return redirect("/words")
@app.route("/words")
def words():
    page = request.args.get("page", 1, type=int)

    connection = get_db_connection()
    words = connection.execute("SELECT * FROM words").fetchall()
    connection.close()

    if words:
        if page < 1 or page > len(words):
            page = 1

        word = words[page - 1]
    else:
        word = None

    return render_template(
        "words.html",
        word=word,
        page=page,
        total_pages=len(words)
    )

@app.route("/delete/<int:word_id>", methods=["POST"])
def delete_word(word_id):
    connection=get_db_connection()
    connection.execute("DELETE FROM words WHERE id = ?", (word_id,))
    connection.commit()
    connection.close()
    return redirect("/words")
@app.route("/search")
def search():
    query = request.args.get("q", "")

    connection = get_db_connection()

    words = connection.execute(
        "SELECT * FROM words WHERE word LIKE ?",
        (f"%{query}%",)
    ).fetchall()

    connection.close()
    return render_template("search.html", words=words, query=query)
@app.route("/edit/<int:word_id>", methods=["GET", "POST"])
def edit_word(word_id):
    connection = get_db_connection()

    if request.method == "POST":
        word = request.form["word"].strip()
        note = request.form["note"].strip()

        # إذا الكلمة فارغة أو فراغات بس، ارجع لصفحة التعديل بدون حفظ
        if not word:
            return redirect(f"/edit/{word_id}")

        connection.execute(
            "UPDATE words SET word = ?, note = ? WHERE id = ?",
            (word, note, word_id)
        )

        connection.commit()
        connection.close()

        return redirect("/words")

    word = connection.execute(
        "SELECT * FROM words WHERE id = ?",
        (word_id,)
    ).fetchone()

    connection.close()

    return render_template("edit.html", word=word)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)