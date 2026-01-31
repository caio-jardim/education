import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import re
from .connection import conectar_planilha
from .reads import get_pacotes, get_professores, get_alunos # Importe get_alunos se não estiver importando

# --- FUNÇÃO HELPER PARA LIMPAR IDs (CORREÇÃO DO PROBLEMA 1) ---
def normalizar_id(valor):
    """Transforma '1', '1.0', 1, 1.0 em string '1' puro."""
    try:
        # Tenta converter para float, depois para int, depois para str
        # Isso transforma 1.0 -> 1 -> "1"
        return str(int(float(str(valor).replace(',', '.')))).strip()
    except:
        # Se der erro (ex: texto), retorna a string limpa
        return str(valor).strip()
# -------------------------------------------------------------

def registrar_movimentacao_financeira(data, tipo, categoria, descricao, valor, status):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Financeiro")
    
    col_ids = ws.col_values(1)
    if len(col_ids) == 0: proximo_id = 1
    elif len(col_ids) == 1 and str(col_ids[0]).upper() == 'ID': proximo_id = 1
    else: proximo_id = len(col_ids)

    # 1. TRATAMENTO DE VALOR
    if isinstance(valor, (float, int)):
        val_float = float(valor)
    else:
        v_str = str(valor).strip().replace("R$", "").strip()
        if ',' in v_str:
            val_float = float(v_str.replace('.', '').replace(',', '.'))
        else:
            val_float = float(v_str)

    nova_linha = [proximo_id, data, tipo, categoria, descricao, val_float, status]
    ws.append_row(nova_linha)
    return True

def registrar_aula(data_aula, id_aluno, nome_aluno, id_prof, nome_prof, modalidade, duracao, status):
    sh = conectar_planilha()
    
    # 1. CÁLCULO DE COMISSÃO
    comissao = 0.0
    try:
        df_profs = get_professores()
        prof = df_profs[df_profs['ID Professor'].astype(str).str.strip() == str(id_prof).strip()]
        
        if not prof.empty:
            prof_data = prof.iloc[0]
            
            def get_val(termos):
                for col in prof_data.keys():
                    if any(t.lower() in col.lower() for t in termos):
                        val = prof_data[col]
                        if isinstance(val, (int, float)): return float(val)
                        s = str(val).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        return float(s) if s else 0.0
                return 0.0

            val_hora = 0.0
            if "Online" in modalidade: val_hora = get_val(["Online"])
            elif "Education" in modalidade or "Escola" in modalidade: val_hora = get_val(["Education", "Escola"])
            elif "Casa" in modalidade: val_hora = get_val(["Casa"])
            elif "Híbrido" in modalidade: val_hora = get_val(["Online"])
            
            comissao = val_hora * float(duracao)
            
    except Exception as e:
        print(f"Erro calculo comissão: {e}")
        comissao = 0.0

    # 2. SALVAR NA PLANILHA
    ws_aulas = sh.worksheet("MOV_Aulas")
    col_ids = ws_aulas.col_values(1)
    
    if len(col_ids) == 0: id_aula = 1
    elif str(col_ids[0]).upper() == 'ID AULA': id_aula = len(col_ids)
    else: id_aula = len(col_ids) + 1
    
    nova_linha = [
        id_aula, data_aula, id_aluno, nome_aluno, id_prof, nome_prof, 
        modalidade, duracao, status, comissao
    ]
    ws_aulas.append_row(nova_linha)

    # 3. TRIGGER VENCIMENTO
    if status == "Realizada":
        try:
            ws_vendas = sh.worksheet("MOV_Vendas")
            vendas = ws_vendas.get_all_records()
            if vendas:
                df_vendas = pd.DataFrame(vendas)
                for idx, row in df_vendas.iterrows():
                    # Usa normalizar_id aqui também por segurança
                    if normalizar_id(row.get('ID Aluno')) == normalizar_id(id_aluno) and str(row.get('Data Primeira Aula')) == "":
                        dt_obj = datetime.strptime(data_aula, "%d/%m/%Y")
                        vencimento_str = (dt_obj + timedelta(days=30)).strftime("%d/%m/%Y")
                        ws_vendas.update_cell(idx + 2, 10, data_aula)
                        ws_vendas.update_cell(idx + 2, 11, vencimento_str)
                        break
        except: pass
        
    atualizar_dash_dados() # Atualiza painel ao salvar aula
    return True

def registrar_lote_aulas(dados_aulas):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Aulas")
    
    col_ids = ws.col_values(1)
    ultimo_id = 0
    if len(col_ids) > 1:
        try: ultimo_id = int(col_ids[-1])
        except: ultimo_id = len(col_ids)
            
    linhas_para_adicionar = []
    
    for i, aula in enumerate(dados_aulas):
        novo_id = ultimo_id + 1 + i
        linha_completa = [novo_id] + aula 
        linhas_para_adicionar.append(linha_completa)
        
    ws.append_rows(linhas_para_adicionar)
    atualizar_dash_dados() # Atualiza painel ao salvar lote
    return True, f"{len(linhas_para_adicionar)} aulas agendadas com sucesso!"

def atualizar_status_aula(id_aula, novo_status):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Aulas")
    
    try:
        cell = ws.find(str(id_aula))
        if cell:
            ws.update_cell(cell.row, 9, novo_status) # Coluna 9 = Status
            
            # --- CORREÇÃO IMPORTANTE: ATUALIZA O DASHBOARD ---
            atualizar_dash_dados() 
            # -------------------------------------------------
            return True
    except:
        return False
    return False

def cadastrar_aluno(nome, responsavel, telefone, nascimento, serie, escola, endereco, obs):
    sh = conectar_planilha()
    ws = sh.worksheet("CAD_Alunos")
    proximo_id = len(ws.col_values(1))
    if proximo_id == 0: proximo_id = 1
    elif str(ws.col_values(1)[0]).upper() == 'ID ALUNO' and proximo_id == 1: proximo_id = 1 # Cabeçalho sozinho
    else: proximo_id = len(ws.col_values(1)) # Ajuste se precisar, mas len geralmente funciona
    
    # Melhoria na geração de ID se tiver cabeçalho
    try: 
        if ws.cell(1,1).value.upper() == "ID ALUNO": proximo_id = len(ws.col_values(1)) 
    except: pass

    apenas_numeros = re.sub(r'\D', '', str(telefone))
    telefone_final = f"55{apenas_numeros}" if apenas_numeros and not apenas_numeros.startswith('55') else (f"+{apenas_numeros}" if apenas_numeros else "")
    
    nova_linha = [proximo_id, nome, responsavel, telefone_final, nascimento, serie, escola, endereco, obs, "Ativo"]
    ws.append_row(nova_linha)
    
    # Não precisa atualizar dash aqui pois o aluno tem 0 horas, 
    # mas se quiser garantir que ele apareça na lista imediatamente:
    atualizar_dash_dados() 
    return proximo_id

def cadastrar_professor(nome, val_education, val_online, val_casa, create_user=False, username="", password="", perfil=""):
    # ... (Seu código original de cadastro de professor mantido igual) ...
    # Como não afeta saldo de alunos, vou resumir aqui para economizar espaço
    # (Mantenha o código que você já tem ou o que corrigimos anteriormente)
    sh = conectar_planilha()
    if create_user and username:
        try:
            ws_users = sh.worksheet("CAD_Usuarios")
            logins_existentes = ws_users.col_values(1)
            if any(u.lower() == username.lower() for u in logins_existentes):
                return False, f"ERRO: O login '{username}' já está em uso!"
        except: pass

    ws_profs = sh.worksheet("CAD_Professores")
    col_ids = ws_profs.col_values(1)
    if len(col_ids) == 0: novo_id = 1
    elif str(col_ids[0]).upper() == 'ID PROFESSOR': novo_id = len(col_ids)
    else: novo_id = len(col_ids) + 1
    
    ws_profs.append_row([novo_id, nome, val_education, val_online, val_casa, "Ativo"])
    
    if create_user and username and password:
        try:
            try: ws_users = sh.worksheet("CAD_Usuarios")
            except: ws_users = sh.add_worksheet("CAD_Usuarios", 1000, 5)
            ws_users.append_row([username, password, nome, perfil, novo_id])
        except Exception as e: return True, f"Prof criado, erro usuário: {e}"
            
    return True, "Professor cadastrado com sucesso!"

def salvar_vinculos_do_professor(id_prof, lista_ids_alunos):
    # ... (Seu código original mantido) ...
    sh = conectar_planilha()
    try: ws = sh.worksheet("LINK_Alunos_Professores")
    except: ws = sh.add_worksheet("LINK_Alunos_Professores", 1000, 3)
    todos_dados = ws.get_all_records()
    novos_dados = [linha for linha in todos_dados if str(linha.get('ID Professor')) != str(id_prof)]
    for id_aluno in lista_ids_alunos:
        novos_dados.append({"ID Vínculo": len(novos_dados) + 1, "ID Aluno": id_aluno, "ID Professor": id_prof})
    ws.clear()
    ws.append_row(["ID Vínculo", "ID Aluno", "ID Professor"])
    if novos_dados:
        ws.append_rows([[d.get('ID Vínculo'), d.get('ID Aluno'), d.get('ID Professor')] for d in novos_dados])
    return True, f"Vínculos atualizados!"

def salvar_vinculos_do_aluno(id_aluno, lista_ids_profs):
    # ... (Seu código original mantido) ...
    sh = conectar_planilha()
    try: ws = sh.worksheet("LINK_Alunos_Professores")
    except: ws = sh.add_worksheet("LINK_Alunos_Professores", 1000, 3)
    todos_dados = ws.get_all_records()
    novos_dados = [linha for linha in todos_dados if str(linha.get('ID Aluno')) != str(id_aluno)]
    for id_prof in lista_ids_profs:
        novos_dados.append({"ID Vínculo": len(novos_dados) + 1, "ID Aluno": id_aluno, "ID Professor": id_prof})
    ws.clear()
    ws.append_row(["ID Vínculo", "ID Aluno", "ID Professor"])
    if novos_dados:
        ws.append_rows([[d.get('ID Vínculo'), d.get('ID Aluno'), d.get('ID Professor')] for d in novos_dados])
    return True, "Lista atualizada!"

def registrar_venda_automatica(id_aluno, nome_aluno, qtd, forma, dt_contrato, dt_pag, valor_manual=None):
    sh = conectar_planilha()
    
    total = 0.0
    nome_pct = ""
    
    if valor_manual is not None and float(valor_manual) > 0:
        total = float(valor_manual)
        nome_pct = f"Personalizado ({qtd}h)"
    else:
        df_pct = get_pacotes()
        val_h = 0
        nome_pct = f"Avulso {qtd}h"
        for _, row in df_pct.iterrows():
            try:
                r_val = row.get('Valor Hora', 0)
                if isinstance(r_val, str): r_val = float(r_val.replace('R$', '').replace('.', '').replace(',', '.').strip())
                qtd_min = float(row.get('Quantidade Mínima', 0))
                qtd_max = float(row.get('Quantidade Máxima', 999))
                if qtd_min <= float(qtd) <= qtd_max:
                    val_h = float(r_val)
                    nome_pct = f"{row.get('Nome Pacote', 'Pacote')} ({qtd}h)"
                    break
            except: continue
        if val_h == 0: return False, "Nenhum pacote compatível."
        total = val_h * float(qtd)
    
    status = "Pago" if dt_pag else "Pendente"
    ws = sh.worksheet("MOV_Vendas")
    col_ids = ws.col_values(1)
    pid = len(col_ids) if len(col_ids) > 0 and str(col_ids[0]).upper() != 'ID VENDA' else (len(col_ids) if len(col_ids) > 1 else 1)
    if len(col_ids) == 0: pid = 1
    
    ws.append_row([pid, dt_contrato, id_aluno, nome_aluno, nome_pct, str(qtd).replace('.', ','), total, forma, dt_pag, "", "", status])
    
    if status == "Pago":
        registrar_movimentacao_financeira(dt_pag, "Entrada", "Venda Pacote", f"Venda {nome_pct}", total, "Pago")
    
    # --- CORREÇÃO IMPORTANTE: FORA DO IF ---
    # Agora atualiza o saldo mesmo se a venda for "Pendente"
    atualizar_dash_dados()
    # ---------------------------------------
    
    return True, f"Venda registrada! Valor: R$ {total:,.2f}"

def atualizar_dash_dados():
    sh = conectar_planilha()
    
    # 1. Carregar dados
    df_alunos = get_alunos()
    try: df_vendas = pd.DataFrame(sh.worksheet("MOV_Vendas").get_all_records())
    except: df_vendas = pd.DataFrame()
    try: df_aulas = pd.DataFrame(sh.worksheet("MOV_Aulas").get_all_records())
    except: df_aulas = pd.DataFrame()

    if df_alunos.empty: return False
    
    # --- CORREÇÃO IMPORTANTE: NORMALIZAÇÃO DE IDs ---
    # Garante que 1 == 1.0 == "1"
    df_alunos['ID Aluno'] = df_alunos['ID Aluno'].apply(normalizar_id)
    
    # 2. VENDAS
    saldo_comprado = pd.Series(dtype=float)
    if not df_vendas.empty:
        col_qtd = 'Quantidade' if 'Quantidade' in df_vendas.columns else ('Qtd' if 'Qtd' in df_vendas.columns else df_vendas.columns[5]) # Tenta achar coluna 6
        
        # Garante ID normalizado
        df_vendas['ID Aluno'] = df_vendas['ID Aluno'].apply(normalizar_id)
        
        def clean_float(x):
            try: return float(str(x).replace(',', '.'))
            except: return 0.0
        df_vendas['qtd_float'] = df_vendas[col_qtd].apply(clean_float)
        
        # Agrupa usando a coluna normalizada
        saldo_comprado = df_vendas.groupby('ID Aluno')['qtd_float'].sum()

    # 3. AULAS
    horas_consumidas = pd.Series(dtype=float)
    horas_agendadas = pd.Series(dtype=float)
    
    if not df_aulas.empty:
        def clean_duracao(x):
            try: return float(str(x).replace(',', '.'))
            except: return 0.0
        
        df_aulas['dur_float'] = df_aulas['Duração'].apply(clean_duracao)
        df_aulas['ID Aluno'] = df_aulas['ID Aluno'].apply(normalizar_id) # Normaliza ID
        
        mask_realizada = df_aulas['Status'] == 'Realizada'
        mask_agendada = df_aulas['Status'] == 'Agendada'
        
        horas_consumidas = df_aulas[mask_realizada].groupby('ID Aluno')['dur_float'].sum()
        horas_agendadas = df_aulas[mask_agendada].groupby('ID Aluno')['dur_float'].sum()

    # 4. TABELA FINAL
    dados_finais = []
    
    for _, row in df_alunos.iterrows():
        uid = str(row['ID Aluno']) # Já foi normalizado acima
        nome = row['Nome Aluno']
        
        tot_comprado = saldo_comprado.get(uid, 0.0)
        tot_consumido = horas_consumidas.get(uid, 0.0)
        tot_agendado = horas_agendadas.get(uid, 0.0)
        
        saldo_disp = tot_comprado - tot_consumido - tot_agendado
        
        dados_finais.append([uid, nome, tot_comprado, tot_consumido, tot_agendado, saldo_disp])
        
    try: ws_dash = sh.worksheet("DASH_Dados")
    except: ws_dash = sh.add_worksheet("DASH_Dados", 1000, 6)
        
    ws_dash.clear()
    header = ["ID Aluno", "Nome Aluno", "Horas Compradas", "Horas Consumidas", "Horas Agendadas", "Saldo Disponível"]
    ws_dash.append_row(header)
    if dados_finais: ws_dash.append_rows(dados_finais)
        
    return True