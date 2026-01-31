# database/aulas.py
from datetime import datetime, timedelta
import pandas as pd
from .connection import conectar_planilha
from .reads import get_professores
from .utils import to_float, normalizar_id
from .dashboards import atualizar_dash_dados

def registrar_aula(data, id_aluno, nome_aluno, id_prof, nome_prof, mod, duracao, status):
    sh = conectar_planilha()
    
    # Lógica de Comissão (Resumida para caber)
    comissao = 0.0
    try:
        df_profs = get_professores()
        # ... (Sua lógica de comissão usando to_float e normalizar_id aqui) ...
        # Se quiser posso colar a lógica completa aqui
    except: pass

    ws = sh.worksheet("MOV_Aulas")
    col = ws.col_values(1)
    try: ult = int(col[-1]) if len(col) > 1 else 0
    except: ult = len(col)

    ws.append_row([ult + 1, data, id_aluno, nome_aluno, id_prof, nome_prof, mod, to_float(duracao), status, comissao])
    
    # Trigger Vencimento (Se Realizada)
    if status == "Realizada":
        # ... (Sua lógica de trigger de vencimento) ...
        pass
        
    atualizar_dash_dados()
    return True

def registrar_lote_aulas(dados):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Aulas")
    col = ws.col_values(1)
    try: ult = int(col[-1]) if len(col) > 1 else 0
    except: ult = len(col)
    
    final = []
    for i, d in enumerate(dados):
        d[7] = to_float(d[7]) # Duracao
        d[9] = to_float(d[9]) # Comissao
        final.append([ult + 1 + i] + d)
        
    ws.append_rows(final)
    atualizar_dash_dados()
    return True, f"{len(final)} salvas."

def atualizar_status_aula(id_aula, status):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Aulas")
    try:
        cell = ws.find(str(id_aula))
        if cell:
            ws.update_cell(cell.row, 9, status)
            atualizar_dash_dados()
            return True
    except: return False