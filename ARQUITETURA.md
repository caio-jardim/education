# 🏗️ Análise Técnica & Arquitetura - Education

## 📐 Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Streamlit)                    │
│                   app.py (Entry Point)                      │
├─────────────────────────────────────────────────────────────┤
│  views/                  modules/ui/              assets/   │
│  ├─ login/              ├─ core.py                ├─ CSS    │
│  ├─ admin/              ├─ forms.py               ├─ img    │
│  ├─ professor/          ├─ alunos.py              └─ fonts  │
│  └─ estagiarios/        └─ [outros componentes]           │
├─────────────────────────────────────────────────────────────┤
│                 DATABASE LAYER (database/)                  │
│  connection.py → gspread API ←→ Google Sheets API           │
│                                                             │
│  ├─ reads.py (queries com cache)                           │
│  ├─ _writes.py (inserts/updates)                           │
│  ├─ pessoas.py (cadastro alunos/profs)                     │
│  ├─ aulas.py (lógica de aulas)                             │
│  ├─ vendas.py (faturamento)                                │
│  ├─ financeiro.py (movimentações)                          │
│  ├─ dashboards.py (agregação de dados)                     │
│  └─ utils.py (helpers)                                     │
├─────────────────────────────────────────────────────────────┤
│              DATA STORAGE (Google Sheets)                   │
│  ┌─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┐            │
│  │ CONFIG SHEETS                              │            │
│  │ • CAD_Usuarios                            │            │
│  │ • CAD_Alunos                              │            │
│  │ • CAD_Professores                         │            │
│  │ • CAD_Pacotes                             │            │
│  │ • LINK_Alunos_Professores (M2M)          │            │
│  ├─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┤            │
│  │ TRANSACTIONAL SHEETS (Movimento)         │            │
│  │ • MOV_Aulas                               │            │
│  │ • MOV_Vendas                              │            │
│  │ • MOV_Financeiro                          │            │
│  ├─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┤            │
│  │ AGGREGATION (Cache/Dashboard)            │            │
│  │ • DASH_Dados (saldo de horas por aluno)  │            │
│  │ • DASH_Alunos (rápido lookup)            │            │
│  │ • AUDIT_Log (future)                     │            │
│  └─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Dados (Exemplo: Novo Aluno)

```
┌─ USER INPUT (View)
│  └─ form_novo_aluno()
│
├─ DATA VALIDATION
│  └─ Pydantic schema (futuro)
│
├─ BUSINESS LOGIC (Module)
│  ├─ Gerar novo ID
│  ├─ Formatar telefone (55...)
│  ├─ Preparar vinculações
│  └─ Preparar venda inicial
│
├─ DATABASE WRITES
│  ├─ INSERT CAD_Alunos
│  ├─ INSERT LINK_Alunos_Professores (se múltiplos profs)
│  ├─ INSERT MOV_Vendas (se inicial)
│  ├─ INSERT MOV_Financeiro (se pago)
│  └─ UPDATE DASH_Dados
│
└─ RESPONSE
   ├─ st.success("Aluno criado!")
   ├─ st.cache_data.clear()
   └─ st.rerun()
```

---

## 🧠 Padrões de Design Utilizados

### 1. **FACTORY PATTERN** (em alguns G-Sheets)
```python
# database/connection.py
@st.cache_resource
def conectar_planilha():
    """Factory para criar conexão Google Sheets (singleton)"""
    return gspread.service_account(...).open("DB_Education")
```

### 2. **REPOSITORY PATTERN** (database/ como DAO)
```python
# database/reads.py
def get_alunos() → List[Dict]
def get_aulas() → List[Dict]
def get_vendas() → List[Dict]

# database/pessoas.py
def cadastrar_aluno(...) → int
def salvar_vinculos_do_aluno(...) → bool
```

### 3. **SERVICE LAYER** (business logic)
```python
# database/dashboards.py
def atualizar_dash_dados():
    """Coordena escrita em DASH_Dados com lógica de agregação"""
    # Não faz direto SELECT/INSERT
    # Orquestra múltiplas operações
```

### 4. **CACHE ESTRATÉGIA**
```python
@st.cache_data(ttl=60)  # TTL 60 segundos
def get_alunos():
    ...
```

### 5. **SESSION STATE** (para navegação)
```python
# Controlar qual view mostrar
st.session_state['logado'] = bool
st.session_state['usuario'] = dict
st.session_state['ver_detalhes_aluno'] = bool  # Futuro
```

---

## 📊 Schema de Dados (Normalizado)

### CAD_Usuarios (Authentication)
| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| Username | TEXT | PK, UNIQUE | Login único |
| Password | TEXT | NOT NULL | ⚠️ Será HASHED |
| Nome Usuário | TEXT | NOT NULL | Exibição |
| Tipo Perfil | TEXT | NOT NULL | admin/professor/estagiario |
| ID Referência | INT | FK | Aponta para ID_Aluno ou ID_Professor |

**Índices necessários**:
```
PRIMARY KEY (Username)
INDEX (Tipo Perfil)
```

---

### CAD_Alunos (Dimensão)
| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| ID Aluno | INT | PK, AUTO | Incrementa auto |
| Nome Aluno | TEXT | NOT NULL | |
| É Responsável | TEXT | | Ex: "João Silva (pai)" |
| Telefone | TEXT | | Formato: 55XX9XXXX |
| Nascimento | DATE | | DD/MM/YYYY em célula |
| Série | TEXT | | 6º, 7º, 8º, 9º, 1EM, etc |
| Escola | TEXT | | |
| Endereço | TEXT | | Completo |
| Observações | TEXT | | Notas livre |
| Status | TEXT | | Ativo/Inativo |
| Data Cadastro | DATE | | Gerado automaticamente |

**Índices necessários**:
```
PRIMARY KEY (ID Aluno)
INDEX (Status)
INDEX (Nome Aluno) - para busca
INDEX (Escola) - para filter
```

---

### CAD_Professores (Dimensão)
| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| ID Professor | INT | PK, AUTO | |
| Nome Professor | TEXT | NOT NULL | |
| R$/h Education | FLOAT | | Valor por hora |
| R$/h Online | FLOAT | | Valor por hora |
| R$/h Casa | FLOAT | | Valor por hora |
| Status | TEXT | | Ativo/Inativo |
| Data Cadastro | DATE | | |

**Índices**:
```
PRIMARY KEY (ID Professor)
INDEX (Status)
```

---

### LINK_Alunos_Professores (Junction Table - M2M)
| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| ID Link | INT | PK, AUTO | |
| ID Aluno | INT | FK → CAD_Alunos | |
| ID Professor | INT | FK → CAD_Professores | |
| Data Vínculo | DATE | | Quando foi criado |
| Status | TEXT | | Ativo/Inativo |

**Índices**:
```
PRIMARY KEY (ID Link)
UNIQUE (ID Aluno, ID Professor, Status='Ativo')
INDEX (ID Aluno, Status)
INDEX (ID Professor, Status)
```

---

### MOV_Aulas (Transactional)
| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| ID Aula | INT | PK, AUTO | |
| Data | DATE | NOT NULL | DD/MM/YYYY |
| Horário | TIME | | HH:MM |
| ID Aluno | INT | FK | |
| Nome Aluno | TEXT | | Desnormalizado |
| ID Professor | INT | FK | |
| Nome Professor | TEXT | | Desnormalizado |
| Modalidade | TEXT | | Online/Education/Casa |
| Duração | FLOAT | | Em horas (1.5 = 1h30m) |
| Status | TEXT | | Agendada/Realizada/Cancelada |
| Comissão | FLOAT | | R$ calculado |
| Data Criação | DATE | | |

**Índices**:
```
PRIMARY KEY (ID Aula)
INDEX (Data, Status)
INDEX (ID Aluno, Status)
INDEX (ID Professor, Status)
```

---

### MOV_Vendas (Transactional)
| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| ID Venda | INT | PK, AUTO | |
| Data | DATE | NOT NULL | Contratação |
| ID Aluno | INT | FK | |
| Nome Aluno | TEXT | | Desnormalizado |
| Pacote | TEXT | | Ex: "4h", "10h" |
| Quantidade | INT | | Horas |
| Valor | FLOAT | | R$ total |
| Forma | TEXT | | Dinheiro/PIX/Cartão/Crédito |
| Data Pagamento | DATE | | Quando foi pago |
| Data Primeira Aula | DATE | | Quando 1ª aula foi realizada |
| Vencimento | DATE | | 30 dias após primeira aula |
| Status | TEXT | | Ativo/Expirado/Cancelada |

**Índices**:
```
PRIMARY KEY (ID Venda)
INDEX (Data, Status)
INDEX (ID Aluno, Status)
INDEX (Vencimento) - para alertas e relatórios
```

---

### MOV_Financeiro (Transactional - Fluxo de Caixa)
| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| ID | INT | PK, AUTO | |
| Data | DATE | NOT NULL | |
| Tipo | TEXT | | Entrada/Saída |
| Categoria | TEXT | | Venda/Salário/Aluguel/Etc |
| Descrição | TEXT | | Ex: "Pacote 10h - João" |
| Valor | FLOAT | | Sempre positivo |
| Status | TEXT | | Pago/Pendente |
| ID Aluno | INT | FK | Opcional - vínculo com aluno |
| Nome Aluno | TEXT | | Desnormalizado |
| Data Lançamento | DATE | | Quando foi criado |

**Índices**:
```
PRIMARY KEY (ID)
INDEX (Data, Tipo)
INDEX (Categoria)
INDEX (Status)
```

---

### DASH_Dados (Aggregation - Atualizado por atualizar_dash_dados())
| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| ID Aluno | INT | PK | |
| Nome Aluno | TEXT | | |
| Horas Compradas | FLOAT | | SUM(MOV_Vendas.Quantidade) |
| Horas Consumidas | FLOAT | | SUM(MOV_Aulas.Duração) WHERE Status=Realizada |
| Horas Agendadas | FLOAT | | SUM(MOV_Aulas.Duração) WHERE Status=Agendada |
| Saldo Disponível | FLOAT | | Compradas - Consumidas - Agendadas |
| Vencimento Próximo | DATE | | MIN(MOV_Vendas.Vencimento) WHERE Status=Ativo |
| Data Atualização | DATE | | Timestamp da última atualização |

**Performance Note**: Essa tabela é READ-HEAVY (dashboard, professor, admin view)  
**Update Strategy**: Atualizar apenas quando MOV_Aulas/MOV_Vendas mudam

---

### AUDIT_Log (Planejado)
| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| ID | INT | PK, AUTO | |
| Data Hora | DATETIME | NOT NULL | Timestamp completo |
| Usuario | TEXT | FK → username | Quem fez |
| Ação | TEXT | | CREATE/UPDATE/DELETE/VIEW |
| Tabela | TEXT | | Qual tabela afetada |
| Registro ID | INT | | Qual registro |
| Dados Antes | JSONTEXT | | Para recuperação |
| Dados Depois | JSONTEXT | | Novo valor |
| Status | TEXT | | Sucesso/Erro |
| IP Address | TEXT | | Para rastreabilidade |
| User Agent | TEXT | | Browser/app |

**Índices**:
```
PRIMARY KEY (ID)
INDEX (Data Hora DESC)
INDEX (Usuario, Data Hora)
INDEX (Ação)
```

---

## 🔍 Análise de Complexidade

### Operações Críticas (Order N - Linear Time)

#### GET Operações (Reads)
```python
def get_alunos():
    """
    Tempo: O(N) onde N = número de alunos
    Estratégia: Cache TTL 60s
    Expected: < 500ms (com cache)
    """
    df = pd.DataFrame(ws.get_all_records())  
    # Google Sheets API delay: ~200ms
    # Pandas processing: ~50ms
    # Cache round-trip: ~20ms
    
def get_aulas():
    """
    Tempo: O(N) onde N = número de aulas
    Expected: < 1s (com cache)
    """
    
def atualizar_dash_dados():
    """
    Tempo: O(A + V) onde A=aulas, V=vendas
    Expected: < 3s (sem cache, chamado 2x/dia)
    
    Otimização sugerida:
    - Batch read (uma chamada por sheet)
    - Pandas aggregation local (fast)
    - Batch write (append_rows vrs append_row)
    """
```

#### WRITE Operações
```python
def cadastrar_aluno(...):
    """
    Tempo: O(1) append
    Expected: < 500ms
    Operações:
    1. Gerar ID (O1)
    2. Append CAD_Alunos (600ms)
    3. Atualizar DASH_Dados (1200ms)
    Total: ~2s
    """
    
def registrar_lote_aulas(...):
    """
    Tempo: O(N) batch insert
    gspread.append_rows() é mais rápido que N*append_row()
    Expected: 50-100ms por aula em batch
    """
```

### Problemas de Escalabilidade

| Limite | Valor | Impacto |
|--------|-------|--------|
| Aulas/ano | 1000 | ✅ OK (<1s) |
| Aulas/ano | 10000 | ⚠️ Lento (>2s) |
| Aulas/ano | 100000 | 🔴 MUITO LENTO (>5s) |
| Alunos | 500 | ✅ OK |
| Alunos | 1000 | ✅ OK (com cache) |
| Alunos | 5000 | ⚠️ Dashboard lento |
| Alunos | 10000+ | 🔴 Precisa BD diferente |

---

## 📈 Plano de Migração (DB Progressão)

### Fase 1: Google Sheets (ATUAL)
```
Vantagens:
✅ Zero infra
✅ Familiar
✅ Até 5M células (~50k alunos)
✅ Backup automático

Desvantagens:
❌ Rate limiting (API)
❌ Sem transações
❌ Relatórios lentos
❌ Caro em escala

Limite recomendado: 500 alunos ativos
```

### Fase 2: PostgreSQL + Sheets (Sincronização)
```
Estratégia:
- PostgreSQL como "source of truth"
- Sheets como interface/dashboard leitura
- Sincronização bidirecional (Python script)
- Melhor performance, mantém familiaridade

Setup:
1. Criar DB PostgreSQL (Supabase/Railway gratuito)
2. Replicar schema
3. Criar sync worker (cada 15min)
4. Migrar views para usar PG direto
5. Deprecar Google Sheets após 6 meses

Custo: ~$10-20/mês
Esforço: ~100h de dev
```

### Fase 3: Full PostgreSQL (Futuro)
```
Timeline: 2027+
Descontinuar Google Sheets
Usar Sheets APENAS para backup
Relatórios em BI tool (Metabase/PowerBI)

Custo: ~$30-50/mês
Performance: 100x melhor
```

---

## 🔗 Integração de APIs (Futuro)

### WhatsApp Integration (Twilio)
```python
# Notificar aluno de aula agendada
from twilio.rest import Client

def enviar_notificacao_aula(telefone_aluno, data_aula, professor):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=f"+{telefone_aluno}",
        from_="+5511988776655",
        body=f"Olá! Você tem aula agendada em {data_aula} com {professor}. Confirme sua presença."
    )
```

### Email Integration (SMTP)
```python
import smtplib
from email.mime.text import MIMEText

def enviar_relatorio_vencimento(email_responsavel, dias_faltantes):
    msg = MIMEText(f"Seu pacote de horas vence em {dias_faltantes} dias!")
    msg['Subject'] = 'Alerta: Pacote vencendo'
    msg['From'] = 'suporte@education.com.br'
    msg['To'] = email_responsavel
    
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(user, password)
    smtp.send_message(msg)
```

### Slack/Discord Alerts
```python
# Alerta para admin quando há erro
import requests

def alert_admin(message):
    requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": f"🚨 {message}"}
    )
```

---

## 🧪 Strategy de Testing (Planejado)

### Unit Tests
```python
# tests/test_utils.py
def test_to_float():
    assert to_float("4,5") == 4.5
    assert to_float("1.000,00") == 1000.0
    assert to_float(10) == 10.0

def test_normalizar_id():
    assert normalizar_id(1) == "1"
    assert normalizar_id(1.0) == "1"
    assert normalizar_id("1") == "1"
```

### Integration Tests
```python
# tests/test_database.py
def test_cadastrar_aluno():
    id_novo = cadastrar_aluno("João", "Maria", "11987654321", ...)
    assert id_novo > 0
    
    # Verificar que foi criado
    df = get_alunos()
    assert df[df['ID Aluno'] == id_novo].shape[0] == 1

def test_registrar_aula_atualiza_dashboard():
    registrar_aula(..., id_aluno=123)
    
    df_dash = get_saldo_alunos()
    aluno = df_dash[df_dash['ID Aluno'] == 123]
    assert aluno['Horas Agendadas'].values[0] > 0
```

### E2E Tests (Selenium/Playwright)
```python
# tests/e2e_login.py
def test_login_admin():
    browser.get("http://localhost:8501")
    
    username_field = browser.find_element("Name", "user_input")
    username_field.send_keys("admin")
    
    password_field = browser.find_element("Name", "password_field")
    password_field.send_keys("senha123")
    
    login_btn = browser.find_element("XPath", "//button[contains(text(), 'Acessar')]")
    login_btn.click()
    
    # Verificar redirecionamento
    assert "Dashboard" in browser.page_source
```

---

## 🚀 Otimizações Possíveis

### 1. Batch Operations
```python
# ❌ LENTO: N operações individuais
for aluno in alunos:
    ws.append_row([aluno])  # N * 600ms

# ✅ RÁPIDO: Uma operação batch
rows = [[aluno] for aluno in alunos]
ws.append_rows(rows)  # 1x 800ms para N
```

### 2. Lazy Loading
```python
# ✅ Carregar só o que vê (paginação)
def get_alunos_paginated(page=1, per_page=20):
    df = get_alunos()  # Ainda carrega tudo
    start = (page - 1) * per_page
    return df.iloc[start:start+per_page]

# Mostrar paginação
import streamlit.components.v1 as components
```

### 3. Índices em Google Sheets
```python
# Google Sheets não tem índices nativos, mas podemos:
# 1. Guardar "ID Aluno" na coluna A para sort rápido
# 2. Usar FILTER() em worksheet
# 3. Criar views (sheets) com dados pré-filtrados
```

### 4. Redis Cache (Futuro)
```python
import redis

@st.cache_resource
def get_redis():
    return redis.Redis(host='localhost', port=6379)

def get_alunos():
    r = get_redis()
    cached = r.get('alunos')
    
    if cached:
        return json.loads(cached)
    
    df = pd.DataFrame(ws.get_all_records())
    r.setex('alunos', 60, df.to_json())  # Cache 60s
    return df
```

---

## 📊 Métricas de Saúde (Observability)

### Indicadores a Monitorar
```python
# 1. API Call Count (Google Sheets)
api_calls_daily = 0  # Target: < 100

# 2. Response Time
response_time_p95 = 2.5  # seconds, Target: < 3s

# 3. Error Rate
error_rate = 0.01  # Target: < 0.1%

# 4. Cache Hit Rate
cache_hit_rate = 0.85  # Target: > 0.8

# 5. Data Consistency
inconsistent_records = 0  # Target: 0
```

### Log Estruturado
```python
import logging
import json

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger.error("Erro ao conectar", extra={
    "function": "conectar_planilha",
    "error_type": "ConnectionError",
    "duration_ms": 1250
})
```

---

## 🔒 Segurança em Camadas

### Layer 1: Autenticação
```
┌─ Username/Password (com hash bcrypt)
├─ Session token (com TTL)
└─ Rate limiting (max 5 tentativas/15min)
```

### Layer 2: Autorização
```
┌─ Role-based access (admin, professor, estagiario)
├─ Row-level security (professor vê seus alunos)
├─ Auditoria de acesso (AUDIT_Log)
└─ Permissões granulares (edit_aluno, delete_aula, etc)
```

### Layer 3: Network
```
┌─ HTTPS only (Streamlit Cloud)
├─ No credential in code (use env vars)
├─ No hardcoding secrets
└─ Firewall/WAF (future)
```

### Layer 4: Data
```
┌─ Encryption at rest (future - Google Sheets encryption)
├─ Backup diário
├─ Backup geográfico distribuído
└─ GDPR compliance (dados pessoais)
```

---

## 📞 Referências Técnicas

### Documentação
- Streamlit Docs: https://docs.streamlit.io
- gspread Docs: https://docs.gspread.org
- Google Sheets API: https://developers.google.com/sheets/api
- Pandas: https://pandas.pydata.org/docs

### Librarys recomendadas para adicionar
```
# Validation
pydantic==2.0

# Password hashing
bcrypt==4.0

# Database (future)
sqlalchemy==2.0
psycopg2==2.9  # PostgreSQL driver

# Testing
pytest==7.4
pytest-mock==3.11

# Monitoring
python-json-logger==2.0.7
sentry-sdk==1.32

# API (future)
fastapi==0.104
uvicorn==0.24
```

---

## 🎯 Decisões Técnicas Recomendadas

| Decisão | Opção Recomendada | Razão |
|---------|------------------|-------|
| **DB** | PG em 6 meses | Escalabilidade > custo |
| **Auth** | OAuth Google | Segurança + facilidade |
| **Logging** | CloudWatch/DataDog | Centralizado + análises |
| **API Gateway** | Kong/Tyk (futuro) | Rate limiting + versioning |
| **Cache** | Redis | Rápido + distributed |
| **Search** | Elasticsearch | Full-text + filtering |
| **Queue** | Celery + RabbitMQ | Async jobs + notifications |

---

**Última Atualização**: 24 de Fevereiro de 2026  
**Versão**: 1.0  
**Status**: 🟡 Parcialmente implementado
