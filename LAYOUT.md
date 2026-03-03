# 🎨 Análise de Layout e Design - Education

## 📊 Resumo Visual

| Elemento | Status | Notas |
|----------|--------|-------|
| **Paleta de Cores** | ✅ Coerente | Off-white, Bege, Cinza escuro bem definidos |
| **Tipografia** | ✅ Boa | Poppins (titles) + Inter (body) - hierarquia clara |
| **Spacing** | ⚠️ Inconsistente | Alguns gaps irregulares, falta padding standardizado |
| **Cards/Containers** | ✅ Bom | Sombra e borda coerentes |
| **Componentes Customizados** | ✅ Bom | KPI card, header_page bem estilizados |
| **Responsividade** | 🔴 Ruim | Mobile ainda é problema (Streamlit limitation) |
| **Icons** | ⚠️ Parcial | Option-menu tem ícones, mas nem sempre consistentes |
| **Acessibilidade** | 🔴 Ruim | Sem alt-text em imagens, contrast pode falhar |

---

## 🎯 Paleta de Cores

### Cores Primárias (Definidas)
```css
--off-white:      #F5F3F0  /* Fundo principal */
--bege-primary:   #C5A065  /* CTA, highlights, borders */
--cinza-escuro:   #2C2C2C  /* Sidebar, titles */
--cinza-claro:    #E0E0E0  /* Borders, dividers */
--cinza-texto:    #757575  /* Texto secundário */
--texto-escuro:   #1A1A1A  /* Texto principal */
```

### Uso Recomendado
```
Background:    #F5F3F0 (off-white)
Text:          #1A1A1A (escuro) ou #757575 (secundário)
Highlights:    #C5A065 (bege) - calls-to-action, seleção
Sidebar:       #2C2C2C (cinza escuro) + text white
Borders:       #E0E0E0 (cinza claro)
```

### Cores de Status (Adicionar ao CSS)
```css
--success: #4CAF50  /* Verde - Sucesso, Ativo */
--warning: #FF9800  /* Laranja - Aviso, Pendente */
--danger:  #F44336  /* Vermelho - Erro, Inativo */
--info:    #2196F3  /* Azul - Informação */

/* Aplicar em toasts */
div[data-testid="stToast"]:has(svg[fill="#4CAF50"]) {
    background-color: #E8F5E9 !important;
    border-left: 4px solid #4CAF50 !important;
}
```

### Sugestão: Adicionar Light Variants
```css
/* Para hover/active states */
--bege-light:      #DFB89A  /* Hover em bege */
--cinza-light:     #F5F5F5  /* Hover em backgrounds */
--success-light:   #E8F5E9  /* BG para success toast */
```

---

## 🔤 Tipografia

### Fontes (Carregadas do Google Fonts)
```css
font-family: 'Poppins', sans-serif  /* Títulos - Bold, Modern */
font-family: 'Inter', sans-serif    /* Corpo - Legível, Clara */
```

### Hierarquia de Tamanhos (Recomendado padronizar)

| Elemento | Tamanho | Peso | Uso |
|----------|---------|------|-----|
| H1 (Page Title) | 32px | 700 | Títulos de página |
| H2 (Subheader) | 24px | 600 | Seções principais |
| H3 (Section) | 18px | 600 | Subseções |
| Label/Form | 14px | 600 | Labels de formulário |
| Body/Text | 14px | 400 | Texto principal |
| Caption/Small | 12px | 400 | Texto secundário, hints |
| KPI Value | 28px | 700 | Números em cards |

### Implementar em CSS (adicionar)
```css
/* Estilos de Tipografia Padronizados */
h1 {
    font-family: 'Poppins', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: #1A1A1A;
    margin-bottom: 20px;
}

h2 {
    font-family: 'Poppins', sans-serif;
    font-size: 24px;
    font-weight: 600;
    color: #2C2C2C;
    margin-top: 25px;
    margin-bottom: 15px;
}

h3 {
    font-family: 'Poppins', sans-serif;
    font-size: 18px;
    font-weight: 600;
    color: #2C2C2C;
    margin-top: 15px;
    margin-bottom: 10px;
}

p {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 400;
    color: #1A1A1A;
    line-height: 1.6;
}

small, .caption {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 400;
    color: #757575;
    line-height: 1.4;
}

label {
    font-family: 'Poppins', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #1A1A1A;
}
```

---

## 📏 Spacing e Layout

### Sistema de Grid (8px base)
```
8px   = 1 unit
16px  = 2 units (padding padrão)
24px  = 3 units
32px  = 4 units (gap entre sections)
48px  = 6 units
```

### Padding Recomendado
```css
/* Containers principais */
.main-content {
    padding: 24px;  /* 3 units */
}

/* Cards */
.card {
    padding: 20px;  /* Ligeiramente menos que 24px para cards */
}

/* Sidebar */
[data-testid="stSidebar"] {
    padding: 16px;  /* 2 units */
}

/* Form elements */
.form-group {
    margin-bottom: 16px;  /* 2 units */
}
```

### Gaps entre elementos
```css
/* Espaço entre seções */
.section {
    margin-bottom: 32px;  /* 4 units */
}

/* Espaço entre itens em list */
.list-item {
    margin-bottom: 12px;  /* 1.5 units */
}

/* Espaço entre colunas */
[data-testid="stHorizontalBlock"] {
    gap: 16px !important;  /* 2 units */
}
```

---

## 🎨 Componentes Customizados

### 1. KPI Card (ATUAL - BOM)
```css
.kpi-card {
    background-color: #FFFFFF;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    border-top: 4px solid #C5A065;
    text-align: left;
    height: 100%;
    position: relative;
}

.kpi-title {
    color: #757575;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.kpi-value {
    color: #1A1A1A;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
}

.kpi-icon-img {
    width: 40px;
    height: 40px;
    margin-bottom: 12px;
    opacity: 0.8;
}
```

### 2. Sugerir novo: Data Card (Para mostrar datas)
```css
.date-card {
    background-color: #F5F3F0;
    border-left: 4px solid #C5A065;
    padding: 12px 16px;
    border-radius: 4px;
    font-size: 14px;
    color: #1A1A1A;
}
```

### 3. Badge (Para status)
```css
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.badge-success {
    background-color: #E8F5E9;
    color: #4CAF50;
    border: 1px solid #4CAF50;
}

.badge-warning {
    background-color: #FFF3E0;
    color: #FF9800;
    border: 1px solid #FF9800;
}

.badge-danger {
    background-color: #FFEBEE;
    color: #F44336;
    border: 1px solid #F44336;
}
```

### 4. Alert Box (Melhorar alert de Streamlit)
```css
div[data-testid="stAlert"] {
    background-color: #F5F3F0 !important;
    border-left: 4px solid #C5A065 !important;
    border-radius: 4px !important;
    padding: 12px 16px !important;
}

div[data-testid="stAlert"][class*="error"] {
    border-left-color: #F44336 !important;
    background-color: #FFEBEE !important;
}

div[data-testid="stAlert"][class*="success"] {
    border-left-color: #4CAF50 !important;
    background-color: #E8F5E9 !important;
}
```

---

## 📱 Problemas de Responsividade

### Problema 1: Sidebar em Mobile
**Situação**: Sidebar ocupa 30% da tela mesmo no mobile  
**Impacto**: Conteúdo fica muito estreito

**Solução CSS** (adicionar):
```css
/* Mobile First */
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        width: 100% !important;
        position: absolute;
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    [data-testid="stSidebar"].open {
        transform: translateX(0);
        z-index: 999;
    }
    
    .block-container {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
}
```

### Problema 2: Tabelas não se adaptam
**Solução**: Usar columns responsivas

```python
# ✅ Adaptar colunas baseado em tela
import streamlit as st

screen_width = 1920  # Streamlit não expõe isso nativamente, usar JS
is_mobile = screen_width < 768

if is_mobile:
    st.dataframe(df[['ID', 'Nome']])  # Mostrar só importantes
else:
    st.dataframe(df)  # Mostrar tudo
```

### Problema 3: KPI Cards quebram em mobile
**Solução**: Usar `st.columns` com números adaptativos

```python
# ✅ Adaptar coluna de KPIs
n_cols = 2 if is_mobile else 4
cols = st.columns(n_cols)

for idx, (titulo, valor, icone) in enumerate(kpis):
    with cols[idx % n_cols]:
        kpi_card(titulo, valor, icone)
```

---

## 🎨 Melhorias Visuais Sugeridas

### 1. Adicionar Animações Sutis
```css
/* Hover em cards */
.card {
    transition: all 0.2s ease;
}

.card:hover {
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

/* Hover em botões */
button {
    transition: all 0.2s ease;
}

button:hover {
    background-color: #C5A065 !important;
    transform: scale(1.02);
}
```

### 2. Implementar Gradient Subtle
```css
/* Background com gradiente suave */
body {
    background: linear-gradient(135deg, #F5F3F0 0%, #FAF9F7 100%);
}

/* Cards com gradiente sutil */
.kpi-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #FAFAF8 100%);
}
```

### 3. Mejorar Sombras (Depth)
```css
/* Sombra base (padrão) */
.shadow-sm {
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* Sombra média */
.shadow-md {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Sombra grande (modals) */
.shadow-lg {
    box-shadow: 0 12px 24px rgba(0,0,0,0.12);
}
```

---

## 📋 Implementação de Dark Mode (Futuro)

```css
/* Modo escuro - adicionar em style.css */
@media (prefers-color-scheme: dark) {
    html, body {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
    }
    
    div[data-baseweb="input"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #2C2C2C !important;
        border-color: #3C3C3C !important;
        color: #FFFFFF !important;
    }
    
    .card {
        background-color: #2C2C2C !important;
        border-color: #3C3C3C !important;
    }
    
    .kpi-card {
        background-color: #2C2C2C !important;
        color: #FFFFFF !important;
    }
}

/* Toggle do usuário */
if st.sidebar.toggle("🌙 Dark Mode"):
    st.session_state['dark_mode'] = True
```

---

## ♿ Acessibilidade

### Problemas Encontrados
1. ❌ Imagens sem `alt-text`
2. ❌ Contrast ratio em alguns textos < 4.5:1
3. ❌ Sem labels em inputs
4. ❌ Sem suporte a screen readers
5. ❌ Sem skip links

### Melhorias (adicionar ao CSS)
```css
/* Skip link (para screen readers) */
a.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: #C5A065;
    color: white;
    padding: 8px;
    z-index: 100;
}

a.skip-link:focus {
    top: 0;
}

/* Focus visible para teclado */
button:focus-visible,
input:focus-visible,
select:focus-visible {
    outline: 3px solid #C5A065;
    outline-offset: 2px;
}

/* Aumentar tamanho mínimo de touch targets */
button, a, input[type="checkbox"], input[type="radio"] {
    min-height: 44px;
    min-width: 44px;
}
```

### Adicionar Alt-text em código
```python
# ❌ ATUAL
st.image("assets/logo.png")

# ✅ MELHORADO
st.image("assets/logo.png", caption="Logo Education", use_container_width=True)

# ✅ COM HTML ALT
st.markdown(
    '<img src="assets/logo.png" alt="Logo da empresa Education">',
    unsafe_allow_html=True
)
```

---

## 📊 Grid System Recomendado

### Layout Padrão (Admin)
```
┌─────────────────────────────┐
│   HEADER (info do usuário)  │
├──────────────┬──────────────┤
│   SIDEBAR    │   CONTENT    │
│   (20%)      │   (80%)      │
│              │              │
│              ├──────────────┤
│              │  FOOTER      │
└──────────────┴──────────────┘
```

### Content Layout
```
┌──────────────────────────────┐
│  [←] Título | Ações Rápidas  │
├──────────────────────────────┤
│  [KPI 1] [KPI 2] [KPI 3] [4] │
├──────────────────────────────┤
│         Tabela/Dados         │
├──────────────────────────────┤
│         Formulário           │
└──────────────────────────────┘
```

---

## ✅ CHECKLIST de Design

### 🔴 CRÍTICO
- [ ] Ajustar responsividade para mobile (media queries)
- [ ] Adicionar alt-text em todas imagens
- [ ] Verificar contrast ratio (WCAG AA: 4.5:1)
- [ ] Adicionar labels explícitos em forms

### 🟠 ALTO
- [ ] Implantar sistema de cores para status (verde/amarelo/vermelho)
- [ ] Padronizar spacing (system 8px)
- [ ] Adicionar animações sutis
- [ ] Melhorar feedback visual em buttons

### 🟡 MÉDIO
- [ ] Implementar Dark Mode
- [ ] Adicionar badges para status
- [ ] Melhorar sombras (depth)
- [ ] Review tipografia em mobile

### 🟢 BAIXO
- [ ] Adicionar gradientes
- [ ] Ícones customizados
- [ ] Fonte customizada (Google Fonts custom)

---

## 📦 Arquivos a Atualizar

### `assets/style.css` - Adicionar
```css
/* Seção 5: Tipografia Padronizada */
/* Seção 6: Spacing System */
/* Seção 7: Componentes Adicionais (Badge, Date Card) */
/* Seção 8: Modo Escuro */
/* Seção 9: Acessibilidade */
/* Seção 10: Responsividade Mobile */
```

### `modules/ui/core.py` - Adicionar
```python
def badge(texto, tipo="info"):
    """Renderiza badge com status"""
    
def date_card(data, titulo=""):
    """Card para datas importantes"""
    
def responsive_columns(items, cols_desktop=4, cols_mobile=2):
    """Colunas que se adaptam ao tamanho"""
```

