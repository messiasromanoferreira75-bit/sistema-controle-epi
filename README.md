# Sistema de Controle de EPI

Aplicação web simples para cadastrar setores, funcionários e EPIs, acompanhar estoque e registrar entregas. O backend usa FastAPI e Supabase; a interface está em HTML, CSS e JavaScript puros.

## Configuração no Windows (Python 3.13)

No PowerShell, na pasta do projeto:

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite `backend/.env` e preencha `SUPABASE_URL` e `SUPABASE_KEY`. Use no backend a chave `secret` do Supabase, mantenha-a apenas no `.env` local e nunca a coloque no frontend ou no Git.

No painel do Supabase, abra **SQL Editor**, cole e execute `database/projeto_EPIs.sql`. O script ativa RLS nas cinco tabelas. O acesso de backend com chave `secret` ignora RLS; para clientes com chaves públicas, crie políticas RLS adequadas antes de liberar acesso.

Com o ambiente ativo e dentro de `backend`:

```powershell
uvicorn app:app --reload
```

Abra `frontend/index.html` no navegador. A API fica em `http://localhost:8000`.

## Chave exposta anteriormente

Como o `.env` foi incluído no histórico Git, considere a chave antiga comprometida. No Supabase, acesse **Project Settings → API Keys** e crie uma nova chave `secret` (ou, se a antiga for a chave legada `service_role`, substitua-a por uma nova `secret`). Atualize `SUPABASE_KEY` no `backend/.env` local, reinicie o servidor e confirme que o sistema funciona; só então revogue/exclua a chave comprometida nessa mesma tela. Não publique a chave nova. Remover o arquivo do estado atual não apaga cópias existentes do histórico; se necessário, reescreva o histórico Git e coordene isso com quem clonou o repositório.

## Automação

Na raiz, execute `iniciar.bat`. Ele cria o ambiente virtual se necessário, instala as dependências e inicia o servidor.

