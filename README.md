# 🌐 Monitor Links - NOC ITS

Sistema de monitoramento de links desenvolvido para o NOC-ITS, fornecendo monitoramento em tempo real da saúde e performance de conexões de rede críticas. O sistema coleta e analisa métricas essenciais como disponibilidade, latência, perda de pacotes e jitter, apresentando os dados através de uma interface web intuitiva.

## ✨ Funcionalidades Principais

- 🔍 **Monitoramento em Tempo Real**
  - Verificação contínua do status dos links
  - Alertas visuais para problemas de conectividade
  - Dashboard com visão geral do sistema

- 📊 **Métricas Avançadas**
  - Latência (tempo de resposta)
  - Perda de pacotes
  - Jitter (variação do atraso)
  - Status de disponibilidade

- 📱 **Interface Responsiva**
  - Design moderno e intuitivo
  - Compatível com dispositivos móveis
  - Visualização em tempo real dos dados

- 📄 **Relatórios e Logs**
  - Geração de relatórios em PDF
  - Histórico detalhado de eventos
  - Análise de tendências

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.x com Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Monitoramento**: Biblioteca `ping3` para análise de rede
- **Relatórios**: ReportLab para geração de PDFs

## ⚙️ Requisitos do Sistema

- Python 3.x
- Flask 2.3.3
- Flask-SQLAlchemy 3.1.1
- Demais dependências listadas em `requirements.txt`

## 🚀 Instalação e Execução

1. **Clone o repositório**
```bash
git clone https://github.com/jeanpassos/monitor-links.git
cd monitor-links
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Inicie o servidor**
```bash
python app.py
```

4. **Acesse a aplicação**
- Abra o navegador e acesse: `http://localhost:5000`
- Faça login com suas credenciais
- Comece a adicionar links para monitoramento

## 📁 Estrutura do Projeto

```
monitor-links/
├── app.py              # Aplicação principal
├── reset_db.py         # Utilitário de reset do banco
├── requirements.txt    # Dependências do projeto
├── instance/          
│   └── monitoring.db   # Banco de dados SQLite
├── static/            
│   ├── css/           # Estilos da aplicação
│   └── js/            # Scripts JavaScript
└── templates/         
    ├── index.html     # Página principal
    ├── logs.html      # Visualização de logs
    └── edit_link.html # Edição de links
```

## 🤝 Como Contribuir

1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas alterações (`git commit -m 'Add: nova funcionalidade'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Notas de Versão

- **v1.0.0** (Inicial)
  - Sistema base de monitoramento
  - Interface web responsiva
  - Geração de relatórios PDF
  - Histórico de logs

## 👥 Autores

- **Jean Passos** - *Desenvolvimento Inicial* - [GitHub](https://github.com/jeanpassos)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---
⌨️ com ❤️ por [Jean Passos](https://github.com/jeanpassos)