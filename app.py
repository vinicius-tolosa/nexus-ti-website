from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import uuid

app = Flask(__name__)
# Keep sessions valid across Render restarts. Configure SECRET_KEY in Render.
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-change-this-secret-key')

# SQLite only persists on Render when DATA_DIR points to a mounted Persistent Disk.
# Set DATA_DIR=/var/data in Render and mount a disk at /var/data.
DATA_DIR = os.environ.get('DATA_DIR', '/var/data')
try:
    os.makedirs(DATA_DIR, exist_ok=True)
    test_file = os.path.join(DATA_DIR, '.write-test')
    with open(test_file, 'a', encoding='utf-8'):
        pass
    os.remove(test_file)
except (OSError, IOError):
    DATA_DIR = os.path.join(app.root_path, 'instance')
    os.makedirs(DATA_DIR, exist_ok=True)

DB_NAME = os.path.join(DATA_DIR, 'nexus_ti.db')
# Keep uploads below static/ so the existing templates continue to serve them.
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            documento TEXT NOT NULL,
            cep TEXT NOT NULL,
            rua TEXT NOT NULL,
            numero TEXT NOT NULL,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            complemento TEXT,
            tipo_servico TEXT DEFAULT 'Geral',
            descricao TEXT,
            status TEXT DEFAULT 'Pendente'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            tipo_projeto TEXT NOT NULL,
            imagem TEXT,
            imagem2 TEXT,
            imagem3 TEXT,
            imagem4 TEXT,
            sketchup_link TEXT
        )
    ''')

    for col in ['tipo_servico', 'descricao', 'status']:
        try:
            cursor.execute(f"ALTER TABLE clientes ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass

    for col in ['imagem', 'imagem2', 'imagem3', 'imagem4', 'sketchup_link']:
        try:
            cursor.execute(f"ALTER TABLE projetos ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass

    cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("admin123")
        cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ("admin", hashed_pw))

    conn.commit()
    conn.close()


init_db()

# --- ROTAS PÚBLICAS DO SITE ---

@app.route('/')
def index():
    # The homepage must receive the projects; otherwise {% for projeto in projetos %}
    # renders nothing even when the INSERT succeeded.
    conn = get_db_connection()
    projetos = conn.execute("SELECT * FROM projetos ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('index.html', projetos=projetos)


@app.route('/infraestrutura')
def servico_infraestrutura():
    conn = get_db_connection()
    projetos = conn.execute("SELECT * FROM projetos WHERE tipo_projeto = 'Infraestrutura de Redes'").fetchall()
    conn.close()
    return render_template('infraestrutura.html', projetos=projetos)


@app.route('/seguranca')
def servico_seguranca():
    conn = get_db_connection()
    projetos = conn.execute("SELECT * FROM projetos WHERE tipo_projeto = 'Segurança da Informação'").fetchall()
    conn.close()
    return render_template('seguranca.html', projetos=projetos)


@app.route('/desenvolvimento')
def servico_desenvolvimento():
    conn = get_db_connection()
    projetos = conn.execute("SELECT * FROM projetos WHERE tipo_projeto = 'Desenvolvimento de Software'").fetchall()
    conn.close()
    return render_template('desenvolvimento.html', projetos=projetos)


@app.route('/suporte')
def servico_suporte():
    conn = get_db_connection()
    projetos = conn.execute("SELECT * FROM projetos WHERE tipo_projeto = 'Suporte Técnico Avançado'").fetchall()
    conn.close()
    return render_template('suporte.html', projetos=projetos)


@app.route('/projeto/<int:id>')
def detalhe_projeto(id):
    conn = get_db_connection()
    projeto = conn.execute("SELECT * FROM projetos WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not projeto:
        abort(404)
    return render_template('detalhe_projeto.html', projeto=projeto)


# --- ROTAS DE SOLICITAÇÃO E CADASTRO ---

@app.route('/cadastro-cliente', methods=['GET', 'POST'])
def cadastro_cliente():
    if request.method == 'POST':
        campos = ['nome_completo', 'email', 'telefone', 'documento', 'cep', 'rua', 'numero', 'bairro', 'cidade', 'estado']
        dados = {campo: request.form.get(campo) for campo in campos}
        complemento = request.form.get('complemento', '')
        tipo_servico = request.form.get('tipo_servico', 'Geral')
        descricao = request.form.get('descricao', '')
        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO clientes (nome_completo, email, telefone, documento, cep, rua, numero,
                bairro, complemento, cidade, estado, tipo_servico, descricao, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pendente')
            ''', tuple(dados[campo] for campo in campos) + (complemento, tipo_servico, descricao))
            conn.commit()
            conn.close()
            return jsonify({"success": True, "message": "Solicitação cadastrada com sucesso!"}), 200
        except Exception as e:
            return jsonify({"success": False, "message": f"Erro no banco de dados: {str(e)}"}), 500

    return render_template('cadastro_cliente.html', servico_selecionado=request.args.get('servico', 'Geral'))


@app.route('/solicitar-servico')
def solicitar_servico():
    return render_template('solicitar_servico.html', servico=request.args.get('servico', 'Serviço Personalizado'))


@app.route('/salvar-solicitacao', methods=['POST'])
def salvar_solicitacao():
    tipo_servico = request.form.get('tipo_servico', 'Geral')
    campos = ['nome_completo', 'email', 'telefone', 'documento', 'cep', 'rua', 'numero', 'bairro', 'cidade', 'estado']
    dados = {campo: request.form.get(campo) for campo in campos}
    complemento = request.form.get('complemento', '')
    descricao = request.form.get('descricao', '')
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO clientes (nome_completo, email, telefone, documento, cep, rua, numero,
            bairro, complemento, cidade, estado, tipo_servico, descricao, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pendente')
        ''', tuple(dados[campo] for campo in campos) + (complemento, tipo_servico, descricao))
        conn.commit()
        conn.close()
        flash(f"Sua solicitação para '{tipo_servico}' foi enviada com sucesso! Entraremos em contato em breve.", "success")
    except Exception:
        flash("Ocorreu um erro ao enviar sua solicitação. Tente novamente.", "danger")
    return redirect(url_for('index'))


# --- ROTAS DO PAINEL ADMINISTRATIVO ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        conn.close()
        if admin and check_password_hash(admin['password'], password):
            session['admin_logged'] = True
            session['admin_user'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        flash("Usuário ou senha incorretos!", "danger")
    return render_template('admin_login.html')


@app.route('/login')
def login():
    return redirect(url_for('admin_login'))


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    solicitacoes = conn.execute("SELECT * FROM clientes ORDER BY id DESC").fetchall()
    projetos = conn.execute("SELECT * FROM projetos ORDER BY id DESC").fetchall()
    admins = conn.execute("SELECT id, username FROM admins").fetchall()
    conn.close()
    return render_template('admin_dashboard.html', solicitacoes=solicitacoes, projetos=projetos, admins=admins)


@app.route('/admin/solicitacao/status/<int:id>', methods=['POST'])
def atualizar_status_solicitacao(id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    conn.execute("UPDATE clientes SET status = ? WHERE id = ?", (request.form.get('status'), id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/solicitacao/atualizar/<int:id>', methods=['POST'])
def atualizar_solicitacao(id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    conn.execute("UPDATE clientes SET status = ?, tipo_servico = ? WHERE id = ?", (request.form.get('status'), request.form.get('tipo_servico'), id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/solicitacao/excluir/<int:id>', methods=['POST'])
def excluir_solicitacao(id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    conn.execute("DELETE FROM clientes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/projeto/salvar', methods=['POST'])
def salvar_projeto():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))

    projeto_id = request.form.get('projeto_id')
    titulo = request.form.get('titulo', '').strip()
    descricao = request.form.get('descricao', '').strip()
    tipo_projeto = request.form.get('tipo_projeto', '').strip()
    sketchup_link = request.form.get('sketchup_link', '').strip()
    if not titulo or not descricao or not tipo_projeto:
        flash('Preencha título, descrição e tipo do projeto.', 'danger')
        return redirect(url_for('admin_dashboard'))

    filenames = {campo: None for campo in ['imagem', 'imagem2', 'imagem3', 'imagem4']}
    try:
        for campo in filenames:
            file = request.files.get(campo)
            if file and file.filename:
                if not allowed_file(file.filename):
                    flash(f'Formato de imagem inválido no campo {campo}.', 'danger')
                    return redirect(url_for('admin_dashboard'))
                # Avoid overwriting another project's image when filenames repeat.
                extension = file.filename.rsplit('.', 1)[1].lower()
                filename = f'{uuid.uuid4().hex}.{extension}'
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filenames[campo] = filename

        conn = get_db_connection()
        if projeto_id:
            projeto_atual = conn.execute("SELECT * FROM projetos WHERE id = ?", (projeto_id,)).fetchone()
            if not projeto_atual:
                conn.close()
                flash('Projeto não encontrado.', 'danger')
                return redirect(url_for('admin_dashboard'))
            valores = [filenames['imagem'] or projeto_atual['imagem'], filenames['imagem2'] or projeto_atual['imagem2'], filenames['imagem3'] or projeto_atual['imagem3'], filenames['imagem4'] or projeto_atual['imagem4']]
            conn.execute('''UPDATE projetos SET titulo = ?, descricao = ?, tipo_projeto = ?, imagem = ?, imagem2 = ?, imagem3 = ?, imagem4 = ?, sketchup_link = ? WHERE id = ?''', (titulo, descricao, tipo_projeto, *valores, sketchup_link, projeto_id))
        else:
            conn.execute('''INSERT INTO projetos (titulo, descricao, tipo_projeto, imagem, imagem2, imagem3, imagem4, sketchup_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (titulo, descricao, tipo_projeto, filenames['imagem'], filenames['imagem2'], filenames['imagem3'], filenames['imagem4'], sketchup_link))
        conn.commit()
        conn.close()
        flash('Projeto salvo com sucesso.', 'success')
    except Exception as error:
        app.logger.exception('Erro ao salvar projeto')
        flash(f'Não foi possível salvar o projeto: {error}', 'danger')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/projeto/excluir/<int:id>', methods=['POST'])
def excluir_projeto(id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    projeto = conn.execute("SELECT * FROM projetos WHERE id = ?", (id,)).fetchone()
    conn.execute("DELETE FROM projetos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    if projeto:
        for campo in ['imagem', 'imagem2', 'imagem3', 'imagem4']:
            if projeto[campo]:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], projeto[campo]))
                except OSError:
                    pass
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/usuario/salvar', methods=['POST'])
def salvar_admin():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    username = request.form.get('novo_username')
    password = request.form.get('novo_password')
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (username, generate_password_hash(password)))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/orcamento-redes')
def orcamento_redes():
    return render_template('infraestrutura.html')


if __name__ == '__main__':
    app.run(debug=True)
