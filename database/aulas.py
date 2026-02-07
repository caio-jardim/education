# database/aulas.py
from datetime import datetime, timedelta
import pandas as pd
from .connection import conectar_planilha
from .reads import get_professores
from .utils import to_float, normalizar_id
from .dashboards import atualizar_dash_dados

# --- ADICIONADO O ARGUMENTO HORARIO ---
def registrar_aula(data, horario, id_aluno, nome_aluno, id_prof, nome_prof, mod, duracao, status, comissao_externa=None):
    sh = conectar_planilha()
    
    # Lógica de Comissão Híbrida
    # 1. Se receber valor externo (do Painel Professor), usa ele.
    # 2. Se não receber (None), calcula automaticamente (Fallback/Admin).
    
    comissao_final = 0.0
    
    if comissao_externa is not None:
        comissao_final = to_float(comissao_externa)
    else:
        # --- Cálculo Automático (Caso Admin use esta função) ---
        try:
            df_profs = get_professores()
            if not df_profs.empty:
                # Filtra o professor
                dados_prof = df_profs[df_profs['ID Professor'].astype(str) == str(id_prof)]
                if not dados_prof.empty:
                    linha = dados_prof.iloc[0]
                    
                    # Define termo de busca (Education, Online, Casa)
                    termo = "Education" if mod == "Education" else mod.split()[0]
                    
                    # Procura valor da hora
                    val_hora = 0.0
                    for k, v in linha.items():
                        if termo.lower() in k.lower():
                            val_hora = to_float(v)
                            break
                    
                    comissao_final = val_hora * to_float(duracao)
        except Exception as e:
            print(f"Erro no cálculo automático de comissão: {e}")

    ws = sh.worksheet("MOV_Aulas")
    col = ws.col_values(1)
    try: ult = int(col[-1]) if len(col) > 1 else 0
    except: ult = len(col)

    # --- INSERÇÃO COM ORDEM CORRETA (11 Colunas) ---
    # 1:ID, 2:Data, 3:Horário, 4:ID_A, 5:Nome_A, 6:ID_P, 7:Nome_P, 8:Mod, 9:Dur, 10:Status, 11:Comissão
    ws.append_row([
        ult + 1, 
        data, 
        horario, 
        id_aluno, 
        nome_aluno, 
        id_prof, 
        nome_prof, 
        mod, 
        to_float(duracao), 
        status, 
        to_float(comissao_final)
    ])
    
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