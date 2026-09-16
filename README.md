# NexusTI - Sistema Web de Gestão de Serviços de TI

Sistema web completo para empresa de prestação de serviços de TI e infraestrutura tecnológica.

## 🎯 Funcionalidades

### Área Pública
- **Homepage** - Apresentação da empresa com portfólio de serviços
- **Páginas Especializadas**
  - Infraestrutura de Redes
  - Segurança da Informação
  - Desenvolvimento de Software
  - Suporte Técnico Avançado
- **Cadastro de Clientes** - Formulário completo com validação
- **Modal de Projetos** - Visualização detalhada de cada projeto

### Painel Administrativo
- **Autenticação Segura** - Login com hash de senha
- **Dashboard** - Estatísticas e overview do sistema
- **Gerenciamento de Projetos**
  - CRUD completo
  - Upload de imagens
  - Categorização por tipo de serviço
- **Gestão de Clientes** - Visualização de cadastros
- **Gerenciamento de Administradores** - Criar/deletar usuários

## 🛠️ Tech Stack

**Backend:**
- Python 3.x
- Flask
- SQLite3
- Werkzeug (segurança)

**Frontend:**
- HTML5
- CSS3 (personalizado)
- Bootstrap 5
- Font Awesome 6.4.0
- Jinja2 Templates
- JavaScript Vanilla

## 📁 Estrutura do Projeto

```
project/
├── app.py                 # Aplicação principal Flask
├── nexusdb.db            # Banco de dados SQLite
├── requirements.txt      # Dependências Python
├── static/
│   ├── css/
│   │   └─�� style.css    # Estilos personalizados
│   ├── js/
│   │   └── main.js      # Scripts JavaScript
│   └── uploads/         # Imagens dos projetos
└── templates/
    ├── base.html            # Template base
    ├── index.html           # Homepage
    ├── infraestrutura.html  # Página infraestrutura
    ├── seguranca.html       # Página segurança
    ├── desenvolvimento.html # Página desenvolvimento
    ├── suporte.html         # Página suporte
    ├── cadastro-cliente.html# Formulário de cadastro
    ├── login.html           # Login administrativo
    ├── 404.html             # Página não encontrada
    ├── 500.html             # Erro servidor
    └── admin/
        └── dashboard.html   # Painel administrativo
```

## 🚀 Como Executar

### 1. Instalação
```bash
# Clonar repositório
git clone <url-do-repositorio>
cd nexus-ti-website

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar Aplicação
```bash
python app.py
```

A aplicação estará disponível em: `http://localhost:5000`

### 3. Credenciais Padrão
- **Usuário:** admin
- **Senha:** admin123

## 📊 Banco de Dados

### Tabelas

#### `admins`
- id (PK)
- username (UNIQUE)
- password (hashed)

#### `clientes`
- id (PK)
- nome_completo
- email
- telefone
- documento
- cep
- rua
- numero
- bairro
- cidade
- estado
- complemento
- data_cadastro

#### `projetos`
- id (PK)
- titulo
- descricao
- tipo_projeto
- imagem
- data_criacao

## 🔐 Segurança

- ✅ Hashing de senhas com Werkzeug Security
- ✅ Sessão segura com chave aleatória
- ✅ Validação de extensão de arquivo
- ✅ Proteção de rotas administrativas
- ✅ Nomes de arquivo seguros (secure_filename)

## 🎨 Personalização

### Cores Principais
- Primary: #667eea (Roxo)
- Success: #198754 (Verde)
- Danger: #dc3545 (Vermelho)
- Info: #0dcaf0 (Azul)

### Tipos de Projetos
- Infraestrutura de Redes
- Segurança da Informação
- Desenvolvimento de Software
- Suporte Técnico Avançado

## 📱 Responsividade

O sistema é totalmente responsivo e funciona em:
- Desktop
- Tablet
- Mobile

## 📝 Licença

Este projeto está disponível sob licença MIT.

## 👨‍💻 Desenvolvedor

Criado por Vinicius Tolosa

## 📞 Suporte

Para dúvidas ou sugestões, entre em contato através do formulário de cadastro no site.