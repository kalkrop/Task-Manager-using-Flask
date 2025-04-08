import pytest
from app import app  # Ajuste o import conforme o nome do arquivo principal

# Configuração do cliente de teste
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'  # Chave para testes
    with app.test_client() as client:
        yield client

# Teste para verificar se a página de login é acessível sem autenticação
def test_login_page_accessible(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data  # Verifica se a página contém o formulário

# Teste para autenticação bem-sucedida
def test_successful_login(client, mocker):
    # Mock do bcrypt para simular senha correta
    mocker.patch('bcrypt.checkpw', return_value=True)
    response = client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 302  # Redireciona para a página inicial
    assert 'user' in session  # Verifica se a sessão foi criada

# Teste para falha na autenticação
def test_failed_login(client, mocker):
    # Mock do bcrypt para simular senha incorreta
    mocker.patch('bcrypt.checkpw', return_value=False)
    response = client.post('/login', data={'username': 'testuser', 'password': 'wrongpass'})
    assert response.status_code == 200  # Permanece na página de login
    assert b"Login falhou" in response.data

# Teste para acesso não autorizado sem login
def test_unauthorized_access(client):
    response = client.get('/')
    assert response.status_code == 302  # Redireciona para login
    assert '/login' in response.headers['Location']

# Teste para criação de tarefa
def test_create_task(client, mocker):
    # Simula login
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
    response = client.post('/', data={'task': 'Nova tarefa de teste'})
    assert response.status_code == 200
    assert b"Nova tarefa de teste" in response.data  # Verifica se a tarefa aparece

# Teste para pesquisa de tarefas
def test_search_tasks(client, mocker):
    # Simula login e tarefas existentes
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
    # Mock para simular a lista de tarefas
    mocker.patch('app.tasks', ['Tarefa 1', 'Tarefa de teste', 'Outra tarefa'])
    response = client.post('/search', data={'keyword': 'teste'})
    assert response.status_code == 200
    assert b"Tarefa de teste" in response.data
    assert b"Tarefa 1" not in response.data  # Apenas resultados relevantes

# Teste para logout
def test_logout(client):
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
    response = client.get('/logout')
    assert response.status_code == 302  # Redireciona para login
    with client.session_transaction() as sess:
        assert 'user' not in sess  # Verifica se a sessão foi destruída

# Teste para logs via syslog (mockado)
def test_syslog_logging(client, mocker):
    mock_logger = mocker.patch('logging.handlers.SysLogHandler')
    response = client.post('/login', data={'username': 'testuser', 'password': 'wrongpass'})
    mock_logger.return_value.warning.assert_called_once_with('Falha na autenticação: testuser')