# Rodando o projeto
- Primeiro, instale o gerenciador de pacotes do python uv: https://github.com/astral-sh/uv
- Entre no diretório do projeto e rode o comando 'uv sync' para instalar as dependências
- Inicie o kafka e a sua interface gráfica rodando 'docker compose -f ./compose.yaml up -d'
- Inicie o broker rodando 'uv run broker/main.py'
- Inicie o backend usando
    - 'cd app'
    - 'uv run fastapi dev'