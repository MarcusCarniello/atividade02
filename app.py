import os
import pymysql
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/quemsomos")
def quemsomos():
    return render_template("quemsomos.html")


@app.route("/contatos")
def contatos():
    return render_template("contatos.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        email = request.form.get("email", "").strip()

        if not nome or not telefone or not email:
            flash("Preencha todos os campos.", "danger")
            return render_template("cadastro.html")

        try:
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO clientes (nome, telefone, email) VALUES (%s, %s, %s)",
                        (nome, telefone, email),
                    )
                conn.commit()
            finally:
                conn.close()
        except pymysql.MySQLError:
            flash("Erro ao salvar no banco de dados.", "danger")
            return render_template("cadastro.html")

        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for("listar"))

    return render_template("cadastro.html")


@app.route("/listar")
def listar():
    registros = []
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nome, telefone, email, data_cadastro "
                    "FROM clientes ORDER BY id DESC"
                )
                registros = cur.fetchall()
        finally:
            conn.close()
    except pymysql.MySQLError:
        flash("Erro ao consultar o banco de dados.", "danger")
    return render_template("listar.html", registros=registros)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
