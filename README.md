# Monitor Links - Sistema de Monitoramento de Links

Sistema de monitoramento de links desenvolvido para o NOC-ITS, que permite monitorar a disponibilidade, latência, perda de pacotes e jitter de múltiplos links de rede.

## Funcionalidades

- Monitoramento em tempo real de links
- Medição de latência, perda de pacotes e jitter
- Interface web intuitiva
- Geração de relatórios em PDF
- Histórico de logs detalhado
- Ativação/desativação de monitoramento por link
- Edição de configurações de links

## Requisitos

- Python 3.x
- Flask 2.3.3
- Flask-SQLAlchemy 3.1.1
- Outras dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/jeanpassos/monitor-links.git
cd monitor-links
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como Usar

1. Inicie o servidor:
```bash
python app.py
```

2. Acesse a interface web em `http://localhost:5000`

3. Adicione os links que deseja monitorar através da interface

## Estrutura do Projeto

- `app.py`: Arquivo principal da aplicação
- `templates/`: Arquivos HTML da interface web
- `static/`: Arquivos estáticos (CSS, JavaScript)
- `monitoring.db`: Banco de dados SQLite
- `reset_db.py`: Script para resetar o banco de dados

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request