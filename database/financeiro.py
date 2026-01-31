# database/financeiro.py
from .connection import conectar_planilha
from .utils import to_float

def registrar_movimentacao_financeira(data, tipo, categoria, descricao, valor, status):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Financeiro")
    
    col = ws.col_values(1)
    # Lógica segura de ID
    try: ult = int(col[-1]) if len(col) > 1 else 0
    except: ult = len(col)
    
    ws.append_row([ult + 1, data, tipo, categoria, descricao, valor, status])
    return True