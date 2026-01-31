# database/dashboards.py
import pandas as pd
from .connection import conectar_planilha
from .reads import get_alunos
from .utils import normalizar_id, to_float

def atualizar_dash_dados():
    # sh = conectar_planilha()

    # # Lê dados RAW
    # try: df_vendas = pd.DataFrame(sh.worksheet("MOV_Vendas").get_all_records())
    # except: df_vendas = pd.DataFrame()
    # try: df_aulas = pd.DataFrame(sh.worksheet("MOV_Aulas").get_all_records())
    # except: df_aulas = pd.DataFrame()
    
    # df_alunos = get_alunos()
    # if df_alunos.empty: return False

    # # Preparação
    # df_alunos['ID_Key'] = df_alunos['ID Aluno'].apply(normalizar_id)
    
    # # --- 1. PROCESSAR VENDAS (Correção aqui) ---
    # saldo_comprado = {}
    # if not df_vendas.empty:
    #     # Procura coluna de quantidade de forma inteligente
    #     col_qtd = None
    #     possiveis_nomes = ['Quantidade', 'Qtd', 'Horas', 'Qtd Horas', 'Qtd.']
        
    #     for c in df_vendas.columns:
    #         if c in possiveis_nomes:
    #             col_qtd = c
    #             break
        
    #     # Se não achou pelo nome, tenta a coluna 5 (padrão antigo)
    #     if not col_qtd and len(df_vendas.columns) > 5:
    #         col_qtd = df_vendas.columns[5]
            
    #     if col_qtd:
    #         df_vendas['ID_Key'] = df_vendas['ID Aluno'].apply(normalizar_id)
    #         # Aplica o to_float corrigido
    #         df_vendas['Qtd_Clean'] = df_vendas[col_qtd].apply(to_float)
    #         saldo_comprado = df_vendas.groupby('ID_Key')['Qtd_Clean'].sum().to_dict()

    # # --- 2. PROCESSAR AULAS ---
    # consumido = {}
    # agendado = {}
    # if not df_aulas.empty:
    #     df_aulas['ID_Key'] = df_aulas['ID Aluno'].apply(normalizar_id)
    #     df_aulas['Dur_Clean'] = df_aulas['Duração'].apply(to_float)
        
    #     mask_real = df_aulas['Status'] == 'Realizada'
    #     mask_agen = df_aulas['Status'] == 'Agendada'
        
    #     consumido = df_aulas[mask_real].groupby('ID_Key')['Dur_Clean'].sum().to_dict()
    #     agendado = df_aulas[mask_agen].groupby('ID_Key')['Dur_Clean'].sum().to_dict()

    # # --- 3. MONTAR TABELA ---
    # dados_finais = []
    # for _, row in df_alunos.iterrows():
    #     uid = row['ID_Key']
        
    #     val_comp = float(saldo_comprado.get(uid, 0.0))
    #     val_cons = float(consumido.get(uid, 0.0))
    #     val_agen = float(agendado.get(uid, 0.0))
    #     val_saldo = val_comp - val_cons - val_agen
        
    #     dados_finais.append([
    #         str(row['ID Aluno']), 
    #         str(row['Nome Aluno']), 
    #         val_comp, 
    #         val_cons, 
    #         val_agen, 
    #         val_saldo
    #     ])

    # # 4. Salvar na aba DASH_Alunos
    # try: ws = sh.worksheet("DASH_Alunos")
    # except: ws = sh.add_worksheet("DASH_Alunos", 1000, 6)
    
    # ws.clear()
    # ws.append_row(["ID Aluno", "Nome Aluno", "Horas Compradas", "Horas Consumidas", "Horas Agendadas", "Saldo Disponível"])
    
    # if dados_finais: 
    #     ws.append_rows(dados_finais)
    
    return True