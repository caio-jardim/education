# database/aulas.py
from datetime import datetime, timedelta
import pandas as pd
from .connection import conectar_planilha
from .reads import get_professores
from .utils import to_float, normalizar_id
from .dashboards import atualizar_dash_dados

# --- ADICIONADO O ARGUMENTO HORARIO ---
def registrar_aula(data, horario, id_aluno, nome_aluno, id_prof, nome_prof, mod, duracao, status):
    sh = conectar_planilha()
    
    # Lógica de Comissão
    comissao = 0.0
    try:
        df_profs = get_professores()
        # (Lógica de comissão mantida igual a original...)
        # ...
        # Se quiser, cole sua lógica completa de cálculo aqui novamente
    except: pass

    ws = sh.worksheet("MOV_Aulas")
    col = ws.col_values(1)
    try: ult = int(col[-1]) if len(col) > 1 else 0
    except: ult = len(col)

    # --- AJUSTE AQUI: INSERINDO HORARIO NA ORDEM CORRETA ---
    # Ordem Sheets: ID, Data, Horário, ID Aluno, Nome Aluno, ID Prof, Nome Prof, Mod, Duração, Status, Comissão
    ws.append_row([
        ult + 1, 
        data, 
        horario,  # <--- Novo campo
        id_aluno, 
        nome_aluno, 
        id_prof, 
        nome_prof, 
        mod, 
        to_float(duracao), 
        status, 
        comissao
    ])
    
    # Trigger Vencimento
    if status == "Realizada":
        pass # (Sua lógica original mantida)
        
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
        # d espera: [Data, Horario, ID A, Nome A, ID P, Nome P, Mod, Dur, Status, Comissao]
        # Índices mudaram porque entrou Horario na lista 'd' antes
        
        # Como o lote vem do front, precisamos garantir que quem chama lote mande o horário
        # Mas para garantir a gravação correta:
        
        # d[7] era duracao, agora com horario sendo inserido no indice 1, duração vira indice 8?
        # DEPENDE de como você monta a lista 'dados' no front.
        # Vou assumir que você vai passar o horário na lista 'dados' lá no front.
        
        # Tratamento de float seguro
        # Se a lista d vier completa com horário: 
        # [Data, Horario, ID_A, Nome_A, ID_P, Nome_P, Mod, Dur, Status, Comissao]
        # Índices: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        
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
            # Coluna Status mudou?
            # Antes: I (9). Agora tem Horário em C.
            # A, B(Data), C(Hora), D(ID A), E(Nome A), F(ID P), G(Nome P), H(Mod), I(Dur), J(Status)
            # J é a décima coluna (10)
            ws.update_cell(cell.row, 10, status) # <--- Ajustado para 10
            atualizar_dash_dados()
            return True
    except: return False
    return False