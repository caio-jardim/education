# 🚀 Roadmap de Próximas Alterações - Education

## 📅 Visão Geral (12-24 meses)

```
Q1 2026 (FEV-MAI)     → Core Fixes (Segurança, UX crítica)
Q2 2026 (JUN-AGO)     → Feature Expansion (Relatórios, Integrações)
Q3 2026 (SET-NOV)     → Performance & Mobile
Q4 2026 (DEZ-FEV)     → Mobile App + Offline
```

---

## 🔴 FASE 1: CRÍTICA (4 semanas) - SEGURANÇA & BUG FIX

### Sprint 1.1: SEGURANÇA (Semana 1-2)

**Prioridade**: 🚨 **CRÍTICO** - Não ir para produção sem isso

#### Tarefas
- [ ] **Task 1.1.1**: Rotar `credentials.json` (Google Cloud)
  - Criar novo Service Account
  - Atualizar Streamlit Secrets
  - Deletar credenciais antigas
  - Tempo: 2h
  
- [ ] **Task 1.1.2**: Implementar hashing de senhas com `bcrypt`
  - Instalar: `pip install bcrypt`
  - Criar função `hash_password()` em `database/utils.py`
  - Criar função `verify_password()`
  - Migrar senhas existentes em `CAD_Usuarios`
  - Tempo: 4h
  
- [ ] **Task 1.1.3**: Adicionar `.gitignore` para credenciais
  ```gitignore
  credentials.json
  .env
  .env.local
  secrets.yaml
  __pycache__/
  *.pyc
  .streamlit/secrets.toml
  ```
  - Tempo: 0.5h

- [ ] **Task 1.1.4**: Implementar middleware de autorização
  - Criar `database/auth.py` com decorador `@verificar_permissao()`
  - Adicionar em todas views críticas
  - Testar permissões
  - Tempo: 6h

**Deadline**: Em 10 dias  
**Responsável**: Dev Lead

---

### Sprint 1.2: BUG FIXES & ESTABILIDADE (Semana 2)

#### Tarefas
- [ ] **Task 1.2.1**: Corrigir cache inconsistente
  - Review e limpar lógica de cache
  - Testar: novo aluno → mostrar em list
  - Testar: aula registrada → atualizar dashboard
  - Tempo: 3h

- [ ] **Task 1.2.2**: Validação de input com Pydantic
  - Instalar: `pip install pydantic`
  - Criar schemas em `database/schemas.py`
  - Aplicar em: cadastro aluno, professor, aula, venda
  - Tempo: 5h

- [ ] **Task 1.2.3**: Normalização de dados (IDs, valores R$)
  - Review todas as comparações de ID
  - Testar saldos de alunos com IDs variados
  - Tempo: 3h

**Deadline**: Em 14 dias

---

## 🟠 FASE 2: UX CRÍTICA (2 semanas)

### Sprint 2.1: Confirmações & Feedback (Semana 3)

#### Tarefas
- [ ] **Task 2.1.1**: Adicionar confirmação 2-passos em deleções
  - Cancelar aula
  - Remover aluno-professor link
  - Tempo: 2h

- [ ] **Task 2.1.2**: Implementar loading spinners
  - Em `modules/ui/core.py`: `show_loading()`
  - Aplicar em: get_alunos(), get_aulas(), get_financeiro()
  - Tempo: 2h

- [ ] **Task 2.1.3**: Melhorar mensagens de erro
  - Revisar todas as `st.error()`
  - Criar dicionário de erros amigáveis
  - Tempo: 2h

- [ ] **Task 2.1.4**: Adicionar busca/filtro em listas grandes
  - `show_gestao_vinculos()` - adicionar search box
  - MOV_Aulas - filtro por mês, status
  - Tempo: 3h

**Deadline**: Em 21 dias

---

### Sprint 2.2: Navegação & Context (Semana 4)

#### Tarefas
- [ ] **Task 2.2.1**: Implementar breadcrumbs
  - Criar componente em `core.py`
  - Adicionar em: detalhes aluno, histórico aulas
  - Tempo: 2h

- [ ] **Task 2.2.2**: Melhorar forms com TABS
  - `form_novo_aluno()` - agrupar campos
  - `form_novo_professor()` - agrupar
  - Tempo: 3h

- [ ] **Task 2.2.3**: Quick action buttons no dashboard
  - Botões: Novo Aluno, Agendar Aula, Nova Venda, Relatório
  - Tempo: 1h

**Deadline**: Em 28 dias

---

## 🎨 FASE 3: DESIGN & RESPONSIVIDADE (3 semanas)

### Sprint 3.1: CSS & Visual (Semana 5)

#### Tarefas
- [ ] **Task 3.1.1**: Adicionar variáveis de cor para status
  ```css
  --success: #4CAF50
  --warning: #FF9800
  --danger: #F44336
  ```
  - Atualizar `assets/style.css`
  - Tempo: 1h

- [ ] **Task 3.1.2**: Implementar componentes de UI
  - Badge com status
  - Date card
  - Alert box melhorado
  - Tempo: 3h

- [ ] **Task 3.1.3**: Adicionar animações sutis
  - Hover em cards
  - Transições em modais
  - Tempo: 2h

- [ ] **Task 3.1.4**: Melhorar tipografia
  - Stdandardizar h1, h2, h3 no CSS
  - Line-height consistente
  - Tempo: 1h

**Deadline**: Em 35 dias

---

### Sprint 3.2: Responsividade & Mobile (Semana 6-7)

#### Tarefas
- [ ] **Task 3.2.1**: Media queries para mobile (<768px)
  - Sidebar colapsável
  - KPI cards em 2 colunas
  - Tabelas reduzidas
  - Tempo: 4h

- [ ] **Task 3.2.2**: Teste em dispositivos reais
  - iPhone 12, Samsung S21, iPad
  - Correção de layouts quebrados
  - Tempo: 3h

- [ ] **Task 3.2.3**: Adicionar Viewport Meta Tags
  - No Streamlit config
  - Zoom mínimo = 1
  - Tempo: 0.5h

**Deadline**: Em 49 dias

---

## 📊 FASE 4: FEATURES NOVAS (4 semanas)

### Sprint 4.1: Relatórios Avançados (Semana 8-9)

#### Tarefas
- [ ] **Task 4.1.1**: Criar seção "Relatórios" em admin
  - Receita por período
  - Top 10 alunos
  - Taxa de conversão
  - Comissões de professor
  - Tempo: 8h

- [ ] **Task 4.1.2**: Implementar export (CSV, PDF)
  - Instalar: `pip install openpyxl reportlab`
  - Funções de export em `database/reports.py`
  - Tempo: 5h

- [ ] **Task 4.1.3**: Adicionar gráficos com ECharts
  - Instalar: `pip install streamlit-echarts`
  - Gráfico de receita (linha)
  - Gráfico de aulas (pizza)
  - Tempo: 4h

**Deadline**: Em 63 dias

---

### Sprint 4.2: Integrações & Automações (Semana 10)

#### Tarefas
- [ ] **Task 4.2.1**: Integração com WhatsApp/Email
  - Notificação de aula agendada
  - Lembretes de vencimento de pacote
  - Instalar: `pip install twilio` ou `smtplib`
  - Tempo: 6h

- [ ] **Task 4.2.2**: Automação de "Primeira Aula"
  - Processar automáticamente ao confirmar
  - Enviar notificação ao professor
  - Tempo: 3h

- [ ] **Task 4.2.3**: Auditoria LOG completa
  - Criar tabela `AUDIT_Log`
  - Registrar todas as operações críticas
  - Views de auditoria
  - Tempo: 5h

**Deadline**: Em 70 dias

---

## 🔧 FASE 5: PERFORMANCE & INFRA (3 semanas)

### Sprint 5.1: Otimização (Semana 11)

#### Tarefas
- [ ] **Task 5.1.1**: Cache mais inteligente
  - Review TTL de cada função
  - Implementar cache per-user
  - Tempo: 3h

- [ ] **Task 5.1.2**: Query optimization
  - Reduzir número de chamadas ao Google Sheets
  - Batch operations onde possível
  - Monitorar tempo de resposta
  - Tempo: 4h

- [ ] **Task 5.1.3**: Database indexing
  - Adicionar "ID Aluno" em MOV_Aulas (sort descending)
  - Adicionar "Status" em CAD_Alunos
  - Tempo: 1h

**Deadline**: Em 77 dias

---

### Sprint 5.2: Deployment & Monitoring (Semana 12)

#### Tarefas
- [ ] **Task 5.2.1**: Setup em Streamlit Cloud
  - Conectar repositório GitHub
  - Configurar secrets
  - Deploy automático
  - Tempo: 3h

- [ ] **Task 5.2.2**: Implementar logging
  - Instalar: `pip install python-json-logger`
  - Logs de erro em arquivo + Sheets
  - Tempo: 2h

- [ ] **Task 5.2.3**: Alertas de erro crítico
  - Email ao admin se conexão falhar
  - Slack webhook para alerts
  - Tempo: 2h

**Deadline**: Em 84 dias

---

## 📱 FASE 6: MOBILE & OFFLINE (6 semanas) - Q2 2026

### Sprint 6.1: PWA Preparation (Semana 13-14)

#### Tarefas
- [ ] **Task 6.1.1**: Preparar manifest.json
  - PWA icons
  - Metadata
  - Themes
  - Tempo: 2h

- [ ] **Task 6.1.2**: Service Worker básico
  - Cache estratégia
  - Fallback offline
  - Tempo: 4h

- [ ] **Task 6.1.3**: Instalável no home screen
  - Testar em iOS + Android
  - Tempo: 2h

**Deadline**: Em 98 dias

---

### Sprint 6.2: Offline Mode (Semana 15-16)

#### Tarefas
- [ ] **Task 6.2.1**: LocalStorage para dados críticos
  - Cache de alunos, aulas, professor
  - Sincronizar quando online
  - Tempo: 6h

- [ ] **Task 6.2.2**: Formulários offline-first
  - Salvar draft antes de enviar
  - Queue de síncrono
  - Tempo: 4h

- [ ] **Task 6.2.3**: Indicador de conexão
  - Online/offline status
  - Alert ao tentar ação offline
  - Tempo: 2h

**Deadline**: Em 112 dias

---

## 🎓 FASE 7: FEATURES EDUCACIONAIS (4 semanas) - Q3 2026

### Sprint 7.1: Professor Features

#### Tarefas
- [ ] **Task 7.1.1**: Plano de aula por aluno
  - Notas após aula
  - Frequência
  - Progresso
  - Tempo: 8h

- [ ] **Task 7.1.2**: Questionário/Quiz integrado
  - Criar questões
  - Avaliar aluno
  - Histórico de respostas
  - Tempo: 10h

**Deadline**: Em 140 dias

---

### Sprint 7.2: Student & Parent Portal

#### Tarefas
- [ ] **Task 7.2.1**: Portal do aluno
  - Ver próximas aulas
  - Saldo de horas
  - Notas e progresso
  - Tempo: 6h

- [ ] **Task 7.2.2**: Portal do responsável
  - Relatório de filho
  - Controle de pagamentos
  - Comunicados
  - Tempo: 6h

**Deadline**: Em 154 dias

---

## 📋 FASE 8: SCALE (Ongoing) - Q4 2026

### Sprint 8.1: Multi-Location

#### Tarefas
- [ ] **Task 8.1.1**: Suportar múltiplas unidades
  - Seletor de filial
  - Dados isolados por branch
  - Tempo: 10h

- [ ] **Task 8.1.2**: RLS (Row-Level Security)
  - Professor só vê seus alunos
  - Admin filial só vê sua unidade
  - Tempo: 8h

**Deadline**: Em 182 dias

---

### Sprint 8.2: Integração com Externos

#### Tarefas
- [ ] **Task 8.2.1**: API pública
  - Endpoints para integrações
  - OAuth2
  - Rate limiting
  - Tempo: 12h

- [ ] **Task 8.2.2**: Webhooks
  - Notificar 3ºs quando aluno se cadastra
  - CRM integrações
  - Tempo: 8h

**Deadline**: Em 210 dias

---

## 📊 ESTIMATIVAS TOTAIS

| Fase | Semanas | Dev Hours | Tester Hours | Total |
|------|---------|-----------|--------------|-------|
| 1: Core | 4 | 32 | 8 | 40 |
| 2: UX | 2 | 20 | 5 | 25 |
| 3: Design | 3 | 28 | 8 | 36 |
| 4: Features | 4 | 48 | 12 | 60 |
| 5: Perf | 3 | 24 | 8 | 32 |
| 6: Mobile | 6 | 52 | 16 | 68 |
| 7: Edu | 4 | 40 | 12 | 52 |
| 8: Scale | ∞ | ?  | ? | ? |
| **TOTAL** | **26** | **244h** | **69h** | **313h** |

**= ~1.5 dev + 1 tester em 6 meses (até Q3 2026)**

---

## 🧠 Decisões Técnicas Pendentes

### A. Framework Frontend
```
OPÇÃO A: Manter Streamlit + Android app wrapper
  ✅ Manter backend Python
  ❌ Mobile UX ruim
  
OPÇÃO B: React Native + Node backend
  ✅ Melhor UX mobile
  ❌ Reescrever tudo
  
OPÇÃO C: Flutter + Python backend
  ✅ Ótima performance
  ❌ Learning curve
  
→ RECOMENDAÇÃO: Opção A (custo-benefício), com PWA
```

### B. Banco de Dados
```
OPÇÃO A: Manter Google Sheets
  ✅ Zero infra
  ❌ Sem transações, lento, caro em escala
  
OPÇÃO B: PostgreSQL
  ✅ Robusto, rápido
  ❌ DevOps, backup, maintenance
  
OPÇÃO C: Firebase/Realtime DB
  ✅ Real-time, escalável
  ❌ Lock-in Google
  
→ RECOMENDAÇÃO: BDD híbrido - PostgreSQL + Google Sheets em sync
```

### C. Autenticação
```
OPÇÃO A: Sistema próprio (atual)
  ❌ Inseguro, manutenção
  
OPÇÃO B: Google OAuth
  ✅ Seguro, integração
  ❌ Exige Gmail
  
OPÇÃO C: Auth0 / Supabase Auth
  ✅ Enterprise grade
  ❌ Custo
  
→ RECOMENDAÇÃO: Migrar para Google OAuth + backup local
```

---

## ✅ CHECKLIST: Priorizar por Impact × Effort

### Fazer AGORA (High Impact, Low Effort)
- [x] Segurança de credenciais
- [x] Hashing de senhas
- [x] Loading spinners
- [x] Confirmações em deleções
- [x] Busca em listas

### Fazer em 2 semanas (High Impact, Medium Effort)
- [ ] Auditoria LOG
- [ ] Formulários com TABS
- [ ] Breadcrumbs
- [ ] Export CSV/PDF
- [ ] Mobile responsividade básica

### Fazer em 1 mês (High Impact, High Effort)
- [ ] Relatórios avançados
- [ ] Integrações WhatsApp/Email
- [ ] Dashboard customizável por usuário
- [ ] App PWA

### Nice to Have (Low Priority)
- [ ] Dark mode
- [ ] Atalhos de teclado
- [ ] Reação em emoji (gamification)
- [ ] Analytics avançado

---

## 🎯 Critérios de Sucesso

### Sprint 1 (Segurança)
- ✅ Zero credenciais em código/git
- ✅ Senhas com bcrypt
- ✅ Teste de força bruta falha
- ✅ Audit log funcional

### Sprint 2-3 (UX)
- ✅ 0 cliques acidentais (confirmação)
- ✅ TTL de carregamento < 2s (com spinner)
- ✅ Mobile score > 80 (PageSpeed)
- ✅ Feedback score > 4/5 (usuários)

### Sprint 4-5 (Features & Performance)
- ✅ Relatórios gerando < 5s
- ✅ Dashboard carregando < 3s
- ✅ 99% uptime
- ✅ Suporte a 10k+ registros

### Sprint 6-7 (Mobile & Edu)
- ✅ PWA instalável
- ✅ Funciona offline (modo read)
- ✅ Portal aluno com 80% adoption
- ✅ NPS > 70

---

## 📞 Contatos & Responsáveis

| Fase | Responsável | Backup | Deadline |
|------|-------------|--------|----------|
| 1: Core | Dev Lead | TBD | 28/02 |
| 2: UX | UX Designer | Dev | 14/03 |
| 3: Design | Design Lead | Dev | 28/03 |
| 4: Features | Dev Senior | Dev | 25/04 |
| 5: Perf | DevOps | Dev | 16/05 |
| 6: Mobile | Dev Mobile | Dev Web | 27/06 |
| 7: Edu | Subject Matter Expert | Dev | 25/07 |

---

**Última Atualização**: 24 de Fevereiro de 2026  
**Status**: 🟢 Pronto para Sprint 1  
**Próxima Review**: 04 de Março de 2026
