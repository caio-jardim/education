# database/financeiro.py
import pandas as pd
from .connection import conectar_planilha
from .utils import to_float # Mantido o import caso precise no futuro

def get_financeiro_geral():
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Financeiro")
    data = ws.get_all_records()
    return pd.DataFrame(data)

# Função ajustada mantendo a lógica original de ID e Valor
def registrar_movimentacao_financeira(data, tipo, categoria, descricao, valor, status, id_aluno="", nome_aluno=""):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Financeiro")
    
    col = ws.col_values(1)
    
    # Lógica segura de ID (EXATAMENTE COMO VOCÊ PEDIU)
    try: ult = int(col[-1]) if len(col) > 1 else 0
    except: ult = len(col)
    
    # Adicionamos id_aluno e nome_aluno no final da lista
    # Ordem: ID, Data, Tipo, Categoria, Descrição, Valor, Status, ID Aluno, Nome Aluno
    ws.append_row([
        ult + 1, 
        data, 
        tipo, 
        categoria, 
        descricao, 
        valor, 
        status, 
        id_aluno, 
        nome_aluno
    ])
    
    return True