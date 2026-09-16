from flask import Flask, render_template, redirect, request, flash, url_for
import fdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chavesecreta'

host = "localhost"
database = r'C:\Users\Aluno\Downloads\BANCO (1) (1)\BANCO.FDB'
user = 'sysdba'
password = 'sysdba'

con = fdb.connect(host=host, database=database, user=user, password=password)


@app.route("/")
def index():
    cursor = con.cursor()
    cursor.execute("""SELECT ID_LIVRO, NOME, AUTOR, DATAPUBLICACAO FROM LIVRO
                   ORDER BY NOME""")
    livros = cursor.fetchall()
    cursor.close()
    return render_template('livros.html', livros=livros)


@app.route('/novo')
def novo():
    return render_template('novo.html')


@app.route('/criar', methods=['POST'])
def criar():
    nome = request.form['nome']
    autor = request.form['autor']
    ano = request.form['ano']
    cursor = con.cursor()
    try:
        cursor.execute("SELECT 1 FROM LIVRO WHERE NOME = ?", (nome,))
        if cursor.fetchone():
            flash('Erro ao cadastrar o livro. Ele já existe.')
            return redirect(url_for('novo'))

        cursor.execute("""
            INSERT INTO LIVRO (NOME, AUTOR, DATAPUBLICACAO)
            VALUES (?, ?, ?)
        """, (nome, autor, ano))
        con.commit()
        flash('Livro cadastrado com sucesso.')

    except Exception as e:
        flash(f'Ocorreu um erro ao cadastrar -> {e}')
        con.rollback()
    finally:
        cursor.close()

    return redirect(url_for('index'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()
    try:
        if request.method == 'POST':
            nome = request.form['nome']
            autor = request.form['autor']
            ano = request.form['ano']

            cursor.execute("""
                UPDATE LIVRO
                SET NOME = ?, AUTOR = ?, DATAPUBLICACAO = ?
                WHERE ID_LIVRO = ?
            """, (nome, autor, ano, id))
            con.commit()
            flash('Livro atualizado com sucesso.')
            return redirect(url_for('index'))

        cursor.execute("""
            SELECT ID_LIVRO, NOME, AUTOR, DATAPUBLICACAO
            FROM LIVRO
            WHERE ID_LIVRO = ?
        """, (id,))
        livro = cursor.fetchone()

        if not livro:
            flash('Livro não encontrado.')
            return redirect(url_for('index'))

        return render_template('editar.html', livro=livro)

    except Exception as e:
        con.rollback()
        flash(f'Ocorreu um erro ao editar -> {e}')
        return redirect(url_for('index'))
    finally:
        cursor.close()


@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    cursor = con.cursor()
    try:
        cursor.execute("DELETE FROM LIVRO WHERE ID_LIVRO = ?", (id,))
        con.commit()
        flash('Livro deletado com sucesso.')
    except Exception as e:
        con.rollback()
        flash(f'Erro ao deletar o livro -> {e}')
    finally:
        cursor.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
