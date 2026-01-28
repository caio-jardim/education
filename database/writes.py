import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import re
from .connection import conectar_planilha
from .reads import get_pacotes # Importa leitura de pacotes para usar na venda

# Em database/writes.py

def registrar_movimentacao_financeira(data, tipo, categoria, descricao, valor, status):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Financeiro")
    
    col_ids = ws.col_values(1)
    if len(col_ids) == 0: proximo_id = 1
    elif len(col_ids) == 1 and str(col_ids[0]).upper() == 'ID': proximo_id = 1
    else: proximo_id = len(col_ids)

    # 1. TRATAMENTO DE VALOR
    # Convertemos para float (número real)
    if isinstance(valor, (float, int)):
        val_float = float(valor)
    else:
        v_str = str(valor).strip().replace("R$", "").strip()
        if ',' in v_str:
            val_float = float(v_str.replace('.', '').replace(',', '.'))
        else:
            val_float = float(v_str)

    # 2. SALVAMENTO (MUDANÇA AQUI!)
    # Mandamos o NÚMERO (val_float) e não a STRING ("100,00").
    # O Google Sheets vai receber 100.0 e tratar como número corretamente.
    
    nova_linha = [proximo_id, data, tipo, categoria, descricao, val_float, status]
    
    ws.append_row(nova_linha)
    return True

def registrar_aula(data_aula, id_aluno, nome_aluno, id_prof, nome_prof, modalidade, duracao, obs):
    sh = conectar_planilha()
    ws_aulas = sh.worksheet("MOV_Aulas")
    rows_count = len(ws_aulas.col_values(1))
    id_aula = rows_count if rows_count > 0 else 1 
    
    nova_linha = [id_aula, data_aula, id_aluno, nome_aluno, id_prof, nome_prof, modalidade, str(duracao).replace('.', ','), "Realizada", ""]
    ws_aulas.append_row(nova_linha)

    # Trigger Vencimento
    try:
        ws_vendas = sh.worksheet("MOV_Vendas")
        vendas = ws_vendas.get_all_records()
        if vendas:
            df_vendas = pd.DataFrame(vendas)
            for idx, row in df_vendas.iterrows():
                r_id_aluno = str(row.get('ID Aluno', ''))
                r_dt_prim = str(row.get('Data Primeira Aula', ''))
                if r_id_aluno == str(id_aluno) and r_dt_prim == "":
                    linha_sheet = idx + 2 
                    dt_obj = datetime.strptime(data_aula, "%d/%m/%Y")
                    vencimento_obj = dt_obj + timedelta(days=30)
                    vencimento_str = vencimento_obj.strftime("%d/%m/%Y")
                    ws_vendas.update_cell(linha_sheet, 10, data_aula)
                    ws_vendas.update_cell(linha_sheet, 11, vencimento_str)
                    break
    except Exception as e:
        st.error(f"Erro trigger vencimento: {e}")
    return True

def cadastrar_aluno(nome, responsavel, telefone, nascimento, serie, escola, endereco, obs):
    sh = conectar_planilha()
    ws = sh.worksheet("CAD_Alunos")
    proximo_id = len(ws.col_values(1))
    if proximo_id == 0: proximo_id = 1
    
    apenas_numeros = re.sub(r'\D', '', str(telefone))
    telefone_final = f"55{apenas_numeros}" if apenas_numeros and not apenas_numeros.startswith('55') else (f"+{apenas_numeros}" if apenas_numeros else "")
    
    nova_linha = [proximo_id, nome, responsavel, telefone_final, nascimento, serie, escola, endereco, obs, "Ativo"]
    ws.append_row(nova_linha)
    return proximo_id

def cadastrar_professor(nome, val_education, val_online, val_casa):
    sh = conectar_planilha()
    ws = sh.worksheet("CAD_Professores")
    proximo_id = len(ws.col_values(1))
    nova_linha = [proximo_id, nome, str(val_education).replace('.', ','), str(val_online).replace('.', ','), str(val_casa).replace('.', ','), "Ativo"]
    ws.append_row(nova_linha)
    return True

def salvar_vinculos_professor(id_aluno, lista_ids_professores):
    sh = conectar_planilha()
    try: ws = sh.worksheet("LINK_Alunos_Professores")
    except: 
        ws = sh.add_worksheet("LINK_Alunos_Professores", 1000, 3)
        ws.append_row(["ID Vínculo", "ID Aluno", "ID Professor"])
        
    todos_dados = ws.get_all_records()
    novos_dados = [linha for linha in todos_dados if str(linha.get('ID Aluno')) != str(id_aluno)]
    for id_prof in lista_ids_professores:
        novos_dados.append({"ID Vínculo": len(novos_dados) + 1, "ID Aluno": id_aluno, "ID Professor": id_prof})
        
    ws.clear()
    ws.append_row(["ID Vínculo", "ID Aluno", "ID Professor"])
    if novos_dados:
        # Garante a ordem correta das colunas
        dados_salvar = [[d.get('ID Vínculo'), d.get('ID Aluno'), d.get('ID Professor')] for d in novos_dados]
        ws.append_rows(dados_salvar)
    return True

def registrar_venda_automatica(id_aluno, nome_aluno, qtd_horas, forma_pagamento, data_contratacao, data_pagamento):
    sh = conectar_planilha()
    df_pacotes = get_pacotes() # Importado de reads.py
    
    valor_hora_encontrado = 0
    nome_pacote_gerado = f"Personalizado {qtd_horas}h"
    
    for index, row in df_pacotes.iterrows():
        try:
            val_h = float(str(row.get('Valor Hora', 0)).replace(',', '.'))
            qtd_min = float(row.get('Quantidade Mínima', 0))
            qtd_max = float(row.get('Quantidade Máxima', 999))
            nome_real = row.get('Nome Pacote', 'Pacote')
            if qtd_min <= qtd_horas <= qtd_max:
                valor_hora_encontrado = val_h
                nome_pacote_gerado = f"{nome_real} ({qtd_horas}h)"
                break
        except: continue
    
    if valor_hora_encontrado == 0:
        return False, "Erro: Qtd de horas não se encaixa em nenhum pacote cadastrado."

    valor_total = valor_hora_encontrado * qtd_horas
    
    status = "Pago" if data_pagamento else "Pendente"
    dt_pag_final = data_pagamento if data_pagamento else ""

    ws = sh.worksheet("MOV_Vendas")
    proximo_id = len(ws.col_values(1))
    
    nova_linha = [proximo_id, data_contratacao, id_aluno, nome_aluno, nome_pacote_gerado, qtd_horas, str(valor_total).replace('.', ','), forma_pagamento, dt_pag_final, "", "", status]
    ws.append_row(nova_linha)
    
    if status == "Pago":
        # Chama a função de registro financeiro (está no mesmo arquivo, chamada direta)
        registrar_movimentacao_financeira(dt_pag_final, "Entrada", "Venda de Pacote", f"Venda: {nome_pacote_gerado} - {nome_aluno}", valor_total, "Pago")
        return True, f"Venda realizada e Financeiro registrado! Total: R$ {valor_total:.2f}"
    
    return True, f"Venda registrada (Pendente). Total: R$ {valor_total:.2f}"