import pandas as pd
from .connection import conectar_planilha
import streamlit as st

@st.cache_data(ttl=60)
def get_usuarios():
    try:
        ws = conectar_planilha().worksheet("CAD_Usuarios")
        return pd.DataFrame(ws.get_all_records())
    except: return pd.DataFrame()

@st.cache_data(ttl=60) # Alunos mudam menos, pode ser cache maior (5 min)
def get_alunos():
    try:
        ws = conectar_planilha().worksheet("CAD_Alunos")
        df = pd.DataFrame(ws.get_all_records())
        if not df.empty and 'Status' in df.columns:
            df = df[df['Status'] == 'Ativo']
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def get_professores():
    try:
        ws = conectar_planilha().worksheet("CAD_Professores")
        return pd.DataFrame(ws.get_all_records())
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def get_pacotes():
    try:
        ws = conectar_planilha().worksheet("CAD_Pacotes")
        return pd.DataFrame(ws.get_all_records())
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def get_aulas():
    try:
        ws = conectar_planilha().worksheet("MOV_Aulas")
        return pd.DataFrame(ws.get_all_records())
    except: return pd.DataFrame()

def get_vinculos():
    try:
        ws = conectar_planilha().worksheet("LINK_Alunos_Professores")
        return pd.DataFrame(ws.get_all_records())
    except: return pd.DataFrame()

# Adicione isso em database/reads.py ou __init__.py
def get_vendas():
    sh = conectar_planilha() # Ou sua função de conexão existente
    ws = sh.worksheet("MOV_Vendas")
    data = ws.get_all_records()
    return pd.DataFrame(data)

@st.cache_data(ttl=60)
def get_financeiro_geral():
    """
    Lê o MOV_Financeiro tratando R$ 1.000,00 e 0,50 corretamente.
    Evita erros de leitura de string vs float.
    """
    try:
        ws = conectar_planilha().worksheet("MOV_Financeiro")
        
        # 1. Pega tudo como TEXTO PURO (Lista de Listas)
        all_data = ws.get_all_values()
        
        if not all_data or len(all_data) < 2: 
            return pd.DataFrame()

        # 2. Monta o DataFrame
        headers = all_data[0]
        rows = all_data[1:]
        df = pd.DataFrame(rows, columns=headers)
        
        # 3. Identifica a coluna de Valor (pode ser "Valor", "Valor R$", etc)
        col_valor = None
        for c in df.columns:
            if "Valor" in c:
                col_valor = c
                break
        
        # 4. Se achou a coluna, aplica a limpeza "na marra"
        if col_valor:
            def converter_financeiro(valor):
                s = str(valor).strip()
                if s == "": return 0.0
                
                # Remove R$ e espaços invisíveis
                s = s.replace('R$', '').replace(' ', '').strip()
                
                # Lógica BR: Se tem vírgula, assume formato 1.000,00 ou 50,00
                if ',' in s:
                    s = s.replace('.', '') # Tira ponto de milhar (1.000 -> 1000)
                    s = s.replace(',', '.') # Troca vírgula por ponto (50,00 -> 50.00)
                
                try:
                    return float(s)
                except:
                    return 0.0

            df[col_valor] = df[col_valor].apply(converter_financeiro)

        return df
    except Exception as e:
        print(f"Erro ao ler financeiro: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_saldo_alunos():
    """
    Lê a aba DASH_Alunos usando get_all_values (RAW).
    Isso evita erros de versão do gspread e garante que pegamos '4,5' como texto.
    """
    try:
        ws = conectar_planilha().worksheet("DASH_Alunos")
        
        # USA GET_ALL_VALUES: Traz uma lista de listas pura. Nada de conversão automática.
        # Ex: [['ID', 'Saldo'], ['1', '4,5'], ['2', '10,0']]
        all_data = ws.get_all_values()
        
        if not all_data or len(all_data) < 2: 
            print("LOG: Dataframe DASH_Alunos vazio ou sem dados!")
            return pd.DataFrame()

        # A primeira linha é o cabeçalho
        headers = all_data[0]
        rows = all_data[1:]
        
        df = pd.DataFrame(rows, columns=headers)

        print("\n--- [DEBUG] INÍCIO LEITURA DASH_ALUNOS (VIA GET_ALL_VALUES) ---")
        
        if 'Saldo Disponível' in df.columns:
            print("1. Amostra CRUA (Texto Puro):")
            print(df['Saldo Disponível'].head(5).tolist())
        
        # --- CONVERSÃO MANUAL ---
        cols_num = ['Horas Compradas', 'Horas Consumidas', 'Horas Agendadas', 'Saldo Disponível']
        
        for col in cols_num:
            if col in df.columns:
                def converter_na_marra(valor):
                    s = str(valor).strip()
                    if s == "": return 0.0
                    
                    # Remove R$
                    s = s.replace('R$', '').strip()
                    
                    # Se tiver vírgula, assume formato BR (4,5 -> 4.5)
                    if ',' in s:
                        s = s.replace('.', '') # Remove milhar
                        s = s.replace(',', '.') # Troca vírgula por ponto
                    
                    try:
                        return float(s)
                    except:
                        return 0.0

                df[col] = df[col].apply(converter_na_marra)

        if 'Saldo Disponível' in df.columns:
            print("2. Amostra CONVERTIDA:")
            print(df['Saldo Disponível'].head(5).tolist())
            
        print("--- [DEBUG] FIM LEITURA ---\n")

        # Garante ID como string
        if 'ID Aluno' in df.columns:
            df['ID Aluno'] = df['ID Aluno'].astype(str)

        return df
    except Exception as e:
        print(f"CRITICAL ERROR no get_saldo_alunos: {e}")
        return pd.DataFrame()

# Mantive essa função caso você esteja usando em outro lugar, 
# mas ela faz a mesma coisa que a get_saldo_alunos ajustada acima.
@st.cache_data(ttl=60)
def get_dash_alunos_data():
    return get_saldo_alunos()