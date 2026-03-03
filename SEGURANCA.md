# 🔐 Análise de Segurança - Education

## ⚠️ CRÍTICO: Problemas de Segurança Encontrados

### 1. **CREDENCIAIS ARMAZENADAS EM TEXTO PLANO** 🚨

**Localização**: `credentials.json` no diretório raiz  
**Severidade**: CRÍTICA  
**Impacto**: Qualquer pessoa com acesso ao repositório/servidor tem acesso a toda a base de dados

```python
# ❌ CÓDIGO VULNERÁVEL
@st.cache_resource
def conectar_planilha():
    if os.path.exists('credentials.json'):  # Arquivo exposto!
        gc = gspread.service_account(filename='credentials.json')
```

**Recomendações**:
- ✅ Usar `st.secrets` (Streamlit Cloud) ou `.env` (produção local)
- ✅ Adicionar `credentials.json` ao `.gitignore` IMEDIATAMENTE
- ✅ Usar variáveis de ambiente: `os.getenv('GOOGLE_CREDENTIALS')`
- ✅ Rotacionar credenciais Google agora mesmo (criar novo service account)

---

### 2. **SENHAS ARMAZENADAS EM TEXTO PLANO** 🚨

**Localização**: `CAD_Usuarios` (Google Sheets)  
**Severidade**: CRÍTICA  
**Impacto**: Qualquer pessoa com acesso ao sheet vê todas as senhas

```python
# ❌ VERIFICAÇÃO INSEGURA
usuario_encontrado = df_users[
    (df_users[col_user].astype(str).str.strip() == user_input) & 
    (df_users[col_pass].astype(str).str.strip() == pass_input)  # Comparação direta!
]
```

**Recomendações**:
- ✅ **Implementar hashing**: usar `bcrypt` ou `argon2`
- ✅ **Alterar tabela CAD_Usuarios**: guardar hash em vez de senha
- ✅ Exemplo de implementação:

```python
import bcrypt

# AO CADASTRAR PROFESSOR/USUÁRIO
hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
# Salvar 'hashed_password' em vez de 'password'

# AO FAZER LOGIN
if bcrypt.checkpw(password_input.encode(), hashed_password_from_db.encode()):
    # Sucesso
```

---

### 3. **SEM VALIDAÇÃO DE PERMISSÕES (AUTHORIZATION)** 🔴

**Localização**: Todos os `views/`  
**Severidade**: ALTA  
**Impacto**: Professor pode acessar dados de outro professor se mudar URL/session_state

```python
# ❌ SEM VERIFICAÇÃO
tipo_perfil = str(usuario_atual.get('Tipo Perfil', '')).lower().strip()
if tipo_perfil == 'admin':
    # Não verifica se o usuário realmente é admin em cada ação!
    # Apenas confia no session_state
```

**Recomendações**:
- ✅ Criar middleware de verificação: `@verificar_permissao('admin')`
- ✅ Validar profil em CADA operação crítica (leitura de alunos, escrita de dados)
- ✅ Exemplo:

```python
def verificar_permissao(perfil_requerido):
    def decorator(func):
        def wrapper(*args, **kwargs):
            usuario = st.session_state.get('usuario')
            if not usuario or usuario.get('Tipo Perfil').lower() != perfil_requerido.lower():
                st.error("Acesso negado!")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@verificar_permissao('admin')
def show_admin():
    ...
```

---

### 4. **SEM LOGGING/AUDITORIA** 🔴

**Localização**: Toda a aplicação  
**Severidade**: ALTA  
**Impacto**: Impossível rastrear quem fez o quê, quando e por quê

**Recomendações**:
- ✅ Criar tabela `AUDIT_Log` em Google Sheets com:
  - `ID | Data/Hora | Usuário | Ação | Detalhes | IP | Status`
- ✅ Logar TODAS as operações críticas:
  - Novo aluno cadastrado
  - Aula registrada/modificada
  - Venda realizada
  - Lançamento financeiro
  - Login/logout

```python
def registrar_auditoria(acao, detalhes, status="Sucesso"):
    from datetime import datetime
    sh = conectar_planilha()
    ws = sh.worksheet("AUDIT_Log")
    usuario = st.session_state.get('usuario', {})
    
    ws.append_row([
        datetime.now().isoformat(),
        usuario.get('Username', 'ANÔNIMO'),
        acao,
        detalhes,
        status
    ])
```

---

### 5. **SEM CONTROLE DE SESSÃO (SESSION TIMEOUT)** 🔴

**Localização**: `app.py`  
**Severidade**: MÉDIA  
**Impacto**: Se alguém deixar navegador aberto, outro pode usar a sessão

**Recomendações**:
- ✅ Implementar timeout: logout automático após 1 hora
- ✅ Usar timestamp de última atividade

```python
import time

# Em app.py, após login bem-sucedido
if not hasattr(st.session_state, 'ultima_atividade'):
    st.session_state['ultima_atividade'] = time.time()

# Cada 60 segundos, verificar
if time.time() - st.session_state['ultima_atividade'] > 3600:  # 1 hora
    st.session_state['logado'] = False
    st.warning("Sua sessão expirou. Faça login novamente.")
    st.rerun()
    
# Atualizar na cada interação
st.session_state['ultima_atividade'] = time.time()
```

---

### 6. **VALIDAÇÃO DE INPUT INSUFICIENTE** 🟠

**Localização**: Todos os formulários  
**Severidade**: MÉDIA  
**Impacto**: Dados corrompidos, injection, erros

```python
# ❌ VALIDAÇÃO MÍNIMA
def cadastrar_aluno(nome, responsavel, telefone, ...):
    # Nenhuma validação de tipo, tamanho, caracteres especiais
    ws.append_row([proximo_id, nome, responsavel, ...])
```

**Recomendações**:
- ✅ Usar biblioteca `pydantic` para validação:

```python
from pydantic import BaseModel, Field, EmailStr, validator

class AlunoSchema(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    responsavel: str = Field(..., min_length=3, max_length=100)
    telefone: str = Field(..., regex=r'^\d{10,15}$')
    nascimento: str = Field(..., regex=r'^\d{2}/\d{2}/\d{4}$')
    serie: str = Field(..., min_length=1, max_length=20)
    
    @validator('telefone')
    def validar_telefone(cls, v):
        apenas_digitos = ''.join(filter(str.isdigit, v))
        if len(apenas_digitos) < 10:
            raise ValueError('Telefone inválido')
        return v
```

---

### 7. **SQL INJECTION / SHEET INJECTION** 🟡

**Localização**: `database/` - todas as escritas  
**Severidade**: BAIXA (Google Sheets é menos vulnerável, mas ainda há risco)  
**Impacto**: Dados malformados, quebra de fórmulas, XSS

```python
# ⚠️ RISCO POTENCIAL
ws.append_row([proximo_id, nome, ...])  # 'nome' não é escapado!
```

**Recomendações**:
- ✅ Escapar valores antes de salvar:

```python
def escapar_valor(valor):
    """Remove caracteres perigosos"""
    valor_str = str(valor)
    # Prefixar com apóstrofo força texto
    return f"'{valor_str}" if valor_str.startswith('=') else valor_str

# Usar
ws.append_row([proximo_id, escapar_valor(nome), ...])
```

---

### 8. **FALTA DE RATE LIMITING (FORÇA BRUTA)** 🟡

**Localização**: `views/login/page.py`  
**Severidade**: BAIXA (para sistema pequeno)  
**Impacto**: Tentativas ilimitadas de adivinhação de senha

**Recomendações**:
- ✅ Implementar rate limiting simples:

```python
import json
from datetime import datetime, timedelta

def verificar_rate_limit(username, max_tentativas=5, janela_minutos=15):
    """Bloqueia após N tentativas em M minutos"""
    limites_file = "login_attempts.json"  # Ou guardar em Sheets
    
    try:
        with open(limites_file, 'r') as f:
            limites = json.load(f)
    except: limites = {}
    
    agora = datetime.now()
    chave = f"{username}_{agora.strftime('%Y%m%d%H%M')[:11]}"  # Janela de tempo
    
    limites[chave] = limites.get(chave, 0) + 1
    
    if limites[chave] > max_tentativas:
        st.error("⚠️ Muitas tentativas. Tente novamente em 15 minutos.")
        return False
    
    with open(limites_file, 'w') as f:
        json.dump(limites, f)
    
    return True
```

---

### 9. **SEM HTTPS (EM PRODUÇÃO)** 🔴

**Localização**: Hospedagem  
**Severidade**: CRÍTICA (em produção)  
**Impacto**: Credenciais transmitidas em texto plano

**Recomendações**:
- ✅ Deploy APENAS em Streamlit Cloud (tem HTTPS automático)
- ✅ Se self-hosted: usar Nginx com SSL/TLS
- ✅ Nunca expor HTTP em produção

---

### 10. **SEM PROTEÇÃO CONTRA CSRF** 🟡

**Localização**: Formulários (forms)  
**Severidade**: BAIXA (Streamlit mitiga naturalmente)  
**Impacto**: Requisições não autorizadas de terceiros

**Detalhes**: Streamlit tem proteção nativa, mas bom documentar

---

## ✅ CHECKLIST DE SEGURANÇA - Ordem de Prioridade

### 🔴 CRÍTICO (Fazer HOJE)
- [ ] Rotar `credentials.json` (criar novo service account Google)
- [ ] Adicionar `credentials.json` ao `.gitignore`
- [ ] Implementar hashing de senhas com `bcrypt`
- [ ] Iniciar migração de senhas em texto plano

### 🟠 ALTO (Esta semana)
- [ ] Implementar middleware de autorização (`@verificar_permissao`)
- [ ] Criar tabela `AUDIT_Log` e logar operações críticas
- [ ] Implementar validação de input com `pydantic`
- [ ] Adicionar session timeout (1 hora)

### 🟡 MÉDIO (Próximas 2 semanas)
- [ ] Escapar valores antes de salvar em sheets
- [ ] Implementar rate limiting para login
- [ ] Adicionar verificação de HTTPS em produção
- [ ] Documentação de segurança para equipe

### 🟢 BAIXO (Backlog)
- [ ] Criptografar dados sensíveis em repouso (Google Sheets)
- [ ] 2FA (autenticação de dois fatores)
- [ ] SSO (Single Sign-On) integrado

---

## 🛡️ Variáveis de Ambiente Recomendadas

Criar `.env.example`:
```
GOOGLE_SHEETS_ID=abc123...
GOOGLE_CREDENTIALS_JSON=/path/to/credentials.json
SECRET_KEY=gerado_com_secrets_generate_key()
DEBUG=False
LOG_LEVEL=INFO
ALLOWED_HOSTS=app.education.com.br
SESSION_TIMEOUT_MINUTES=60
```

---

## 📋 Fluxo de Credenciais Seguro (NOVO)

```
┌─ Streamlit Cloud Secrets
│  └─ GOOGLE_SERVICE_ACCOUNT (JSON)
│
├─ Variáveis de Ambiente (.env)
│  └─ Não commitar no Git
│
└─ Local Development
   └─ credentials.json em .gitignore
```

---

## 🚀 Próximos Passos

1. **Semana 1**: Resolver credenciais + hashing de senhas
2. **Semana 2**: Auditoria + autorização
3. **Semana 3**: Validação de input
4. **Semana 4**: Testes de segurança

**Recomendação**: Contratar audit de segurança externo antes de produção
