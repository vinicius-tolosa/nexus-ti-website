from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configurações
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Criar pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==================== BANCO DE DADOS ====================

def get_db():
    """Conecta ao banco de dados SQLite"""
    conn = sqlite3.connect('nexusdb.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabela de administradores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Tabela de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            documento TEXT,
            cep TEXT,
            rua TEXT,
            numero TEXT,
            bairro TEXT,
            cidade TEXT,
            estado TEXT,
            complemento TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de projetos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            tipo_projeto TEXT NOT NULL,
            imagem TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Criar admin padrão se não existir
    cursor.execute('SELECT * FROM admins WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        password_hash = generate_password_hash('admin123')
        cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', ('admin', password_hash))
        conn.commit()
    
    conn.close()

# Inicializar banco na primeira execução
with app.app_context():
    init_db()

# ==================== FUNÇÕES AUXILIARES ====================

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator para verificar se o admin está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROTAS PÚBLICAS ====================

@app.route('/')
def index():
    """Página inicial"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projetos LIMIT 6')
    projetos_destaque = cursor.fetchall()
    conn.close()
    return render_template('index.html', projetos=projetos_destaque)

@app.route('/infraestrutura')
def infraestrutura():
    """Página de Infraestrutura de Redes"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projetos WHERE tipo_projeto = ?', ('Infraestrutura de Redes',))
    projetos = cursor.fetchall()
    conn.close()
    return render_template('infraestrutura.html', projetos=projetos)

@app.route('/orcamento-redes')
def orcamento_redes():
    """Redirecionamento para infraestrutura"""
    return redirect(url_for('infraestrutura'))

@app.route('/seguranca')
def seguranca():
    """Página de Segurança da Informação"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projetos WHERE tipo_projeto = ?', ('Segurança da Informação',))
    projetos = cursor.fetchall()
    conn.close()
    return render_template('seguranca.html', projetos=projetos)

@app.route('/desenvolvimento')
def desenvolvimento():
    """Página de Desenvolvimento de Software"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projetos WHERE tipo_projeto = ?', ('Desenvolvimento de Software',))
    projetos = cursor.fetchall()
    conn.close()
    return render_template('desenvolvimento.html', projetos=projetos)

@app.route('/suporte')
def suporte():
    """Página de Suporte Técnico Avançado"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projetos WHERE tipo_projeto = ?', ('Suporte Técnico Avançado',))
    projetos = cursor.fetchall()
    conn.close()
    return render_template('suporte.html', projetos=projetos)

@app.route('/cadastro-cliente', methods=['GET', 'POST'])
def cadastro_cliente():
    """Formulário e processamento de cadastro de cliente"""
    if request.method == 'POST':
        try:
            data = request.form
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO clientes 
                (nome_completo, email, telefone, documento, cep, rua, numero, 
                 bairro, cidade, estado, complemento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('nome_completo'),
                data.get('email'),
                data.get('telefone'),
                data.get('documento'),
                data.get('cep'),
                data.get('rua'),
                data.get('numero'),
                data.get('bairro'),
                data.get('cidade'),
                data.get('estado'),
                data.get('complemento')
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Cadastro realizado com sucesso!'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    return render_template('cadastro-cliente.html')

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login do administrador"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE username = ?', (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and check_password_hash(admin['password'], password):
            session['admin_logged'] = True
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error='Usuário ou senha incorretos')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    """Logout do administrador"""
    session.clear()
    return redirect(url_for('admin_login'))

# ==================== ROTAS DO PAINEL ADMINISTRATIVO ====================

@app.route('/admin')
@login_required
def admin_dashboard():
    """Dashboard administrativo"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Estatísticas
    cursor.execute('SELECT COUNT(*) as total FROM clientes')
    total_clientes = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM projetos')
    total_projetos = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM admins')
    total_admins = cursor.fetchone()['total']
    
    # Últimos clientes
    cursor.execute('SELECT * FROM clientes ORDER BY data_cadastro DESC LIMIT 5')
    ultimos_clientes = cursor.fetchall()
    
    # Todos os projetos
    cursor.execute('SELECT * FROM projetos ORDER BY data_criacao DESC')
    projetos = cursor.fetchall()
    
    # Todos os admins
    cursor.execute('SELECT id, username FROM admins')
    admins = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         total_clientes=total_clientes,
                         total_projetos=total_projetos,
                         total_admins=total_admins,
                         ultimos_clientes=ultimos_clientes,
                         projetos=projetos,
                         admins=admins)

@app.route('/admin/projeto/adicionar', methods=['POST'])
@login_required
def adicionar_projeto():
    """Adicionar novo projeto"""
    try:
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        tipo_projeto = request.form.get('tipo_projeto')
        imagem = request.files.get('imagem')
        
        nome_arquivo = None
        if imagem and allowed_file(imagem.filename):
            filename = secure_filename(imagem.filename)
            filename = f"{datetime.now().timestamp()}_{filename}"
            imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nome_arquivo = filename
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projetos (titulo, descricao, tipo_projeto, imagem)
            VALUES (?, ?, ?, ?)
        ''', (titulo, descricao, tipo_projeto, nome_arquivo))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Projeto adicionado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/admin/projeto/<int:projeto_id>/editar', methods=['POST'])
@login_required
def editar_projeto(projeto_id):
    """Editar projeto existente"""
    try:
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        tipo_projeto = request.form.get('tipo_projeto')
        imagem = request.files.get('imagem')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Buscar projeto atual
        cursor.execute('SELECT * FROM projetos WHERE id = ?', (projeto_id,))
        projeto = cursor.fetchone()
        
        nome_arquivo = projeto['imagem']
        
        # Se nova imagem foi enviada
        if imagem and allowed_file(imagem.filename):
            # Deletar imagem antiga
            if projeto['imagem']:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], projeto['imagem'])
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Salvar nova imagem
            filename = secure_filename(imagem.filename)
            filename = f"{datetime.now().timestamp()}_{filename}"
            imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nome_arquivo = filename
        
        cursor.execute('''
            UPDATE projetos 
            SET titulo = ?, descricao = ?, tipo_projeto = ?, imagem = ?
            WHERE id = ?
        ''', (titulo, descricao, tipo_projeto, nome_arquivo, projeto_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Projeto atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/admin/projeto/<int:projeto_id>/deletar', methods=['DELETE'])
@login_required
def deletar_projeto(projeto_id):
    """Deletar projeto"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Buscar projeto
        cursor.execute('SELECT * FROM projetos WHERE id = ?', (projeto_id,))
        projeto = cursor.fetchone()
        
        # Deletar imagem
        if projeto['imagem']:
            path = os.path.join(app.config['UPLOAD_FOLDER'], projeto['imagem'])
            if os.path.exists(path):
                os.remove(path)
        
        # Deletar do banco
        cursor.execute('DELETE FROM projetos WHERE id = ?', (projeto_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Projeto deletado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/admin/admin/adicionar', methods=['POST'])
@login_required
def adicionar_admin():
    """Adicionar novo administrador"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Preencha todos os campos'}), 400
        
        password_hash = generate_password_hash(password)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)',
                      (username, password_hash))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Administrador adicionado com sucesso!'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Usuário já existe'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/admin/admin/<int:admin_id>/deletar', methods=['DELETE'])
@login_required
def deletar_admin(admin_id):
    """Deletar administrador"""
    try:
        # Verificar se é o último admin
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM admins')
        
        if cursor.fetchone()['total'] <= 1:
            return jsonify({'success': False, 'message': 'Não pode deletar o último administrador'}), 400
        
        cursor.execute('DELETE FROM admins WHERE id = ?', (admin_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Administrador deletado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ==================== TRATAMENTO DE ERROS ====================

@app.errorhandler(404)
def not_found(error):
    """Página não encontrada"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Erro interno do servidor"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
