import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import re
from .connection import conectar_planilha
from .reads import get_pacotes, get_professores # Importa leitura de pacotes para usar na venda

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

def registrar_aula(data_aula, id_aluno, nome_aluno, id_prof, nome_prof, modalidade, duracao, status):
    sh = conectar_planilha()
    
    # 1. CÁLCULO DE COMISSÃO SIMPLIFICADO
    comissao = 0.0
    try:
        df_profs = get_professores()
        # Filtra professor pelo ID (converte para string para garantir comparação correta)
        prof = df_profs[df_profs['ID Professor'].astype(str).str.strip() == str(id_prof).strip()]
        
        if not prof.empty:
            prof_data = prof.iloc[0]
            
            # Função para buscar valor ignorando maiúsculas/minúsculas no nome da coluna
            def get_val(termos):
                for col in prof_data.keys():
                    if any(t.lower() in col.lower() for t in termos):
                        # Pega o valor cru (pode ser int, float ou str '20,00')
                        val = prof_data[col]
                        
                        # Se for número direto, retorna float
                        if isinstance(val, (int, float)): 
                            return float(val)
                        
                        # Se for string (ex: 'R$ 20,00' ou '20,00')
                        s = str(val).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        return float(s) if s else 0.0
                return 0.0

            # Seleciona o valor da hora baseado na modalidade
            val_hora = 0.0
            if "Online" in modalidade: 
                val_hora = get_val(["Online"])
            elif "Education" in modalidade or "Escola" in modalidade: 
                val_hora = get_val(["Education", "Escola"])
            elif "Casa" in modalidade: 
                val_hora = get_val(["Casa"])
            elif "Híbrido" in modalidade:
                val_hora = get_val(["Online"]) # Assume valor online para híbrido (ajuste se precisar)
            
            # Cálculo Final
            comissao = val_hora * float(duracao)
            
    except Exception as e:
        print(f"Erro calculo comissão: {e}")
        comissao = 0.0

    # 2. SALVAR NA PLANILHA
    ws_aulas = sh.worksheet("MOV_Aulas")
    col_ids = ws_aulas.col_values(1)
    
    # Lógica simples de ID
    if len(col_ids) == 0: id_aula = 1
    elif str(col_ids[0]).upper() == 'ID AULA': id_aula = len(col_ids)
    else: id_aula = len(col_ids) + 1
    
    # Prepara a linha (Envia COMISSÃO como número puro, o Sheets formata)
    nova_linha = [
        id_aula, 
        data_aula, 
        id_aluno, 
        nome_aluno, 
        id_prof, 
        nome_prof, 
        modalidade, 
        duracao,
        status, 
        comissao # Envia float puro (ex: 40.0). O Sheets Brasil entende e põe vírgula.
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
                    if str(row.get('ID Aluno')) == str(id_aluno) and str(row.get('Data Primeira Aula')) == "":
                        dt_obj = datetime.strptime(data_aula, "%d/%m/%Y")
                        vencimento_str = (dt_obj + timedelta(days=30)).strftime("%d/%m/%Y")
                        ws_vendas.update_cell(idx + 2, 10, data_aula)
                        ws_vendas.update_cell(idx + 2, 11, vencimento_str)
                        break
        except: pass
        
    return True

# Função Extra para Atualizar Status (Para o botão de cancelar/realizar)
def atualizar_status_aula(id_aula, novo_status):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Aulas")
    
    try:
        cell = ws.find(str(id_aula)) # Procura o ID na planilha
        if cell:
            # Coluna I é a 9ª coluna (Status)
            ws.update_cell(cell.row, 9, novo_status)
            return True
    except:
        return False
    return False

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

def cadastrar_professor(nome, val_education, val_online, val_casa, create_user=False, username="", password="", perfil=""):
    sh = conectar_planilha()
    
    # --- 1. VALIDAÇÃO DE USUÁRIO DUPLICADO (SEGURANÇA) ---
    if create_user and username:
        try:
            ws_users = sh.worksheet("CAD_Usuarios")
            
            # Pega lista de logins existentes (Coluna A / 1ª coluna)
            logins_existentes = ws_users.col_values(1)
            
            # Pega lista de nomes de usuários existentes (Coluna C / 3ª coluna) - Opcional, mas bom evitar homônimos exatos
            # nomes_existentes = ws_users.col_values(3) 

            # Verifica se o Login já existe (ignora maiúsculas/minúsculas para segurança)
            if any(u.lower() == username.lower() for u in logins_existentes):
                return False, f"ERRO: O login '{username}' já está em uso! Escolha outro."
            
        except Exception as e:
            return False, f"Erro técnico na validação: {e}"

    # --- 2. SALVAR PROFESSOR ---
    ws_profs = sh.worksheet("CAD_Professores")
    col_ids = ws_profs.col_values(1)
    
    # ID Sequencial Seguro
    if len(col_ids) == 0: novo_id = 1
    elif str(col_ids[0]).upper() == 'ID PROFESSOR': novo_id = len(col_ids)
    else: novo_id = len(col_ids) + 1
    
    # Salva Professor (Valores puramente float)
    nova_linha_prof = [novo_id, nome, val_education, val_online, val_casa, "Ativo"]
    ws_profs.append_row(nova_linha_prof)
    
    # --- 3. SALVAR USUÁRIO ---
    if create_user and username and password:
        try:
            # Garante que a aba existe (se não existir, o except acima pegou, mas aqui cria)
            try: ws_users = sh.worksheet("CAD_Usuarios")
            except: 
                ws_users = sh.add_worksheet("CAD_Usuarios", 1000, 5)
                ws_users.append_row(["Username", "Password", "Nome Usuário", "Tipo Perfil", "ID Vinculo"])
            
            # Colunas: Username, Password, Nome Usuário, Tipo Perfil, ID Vinculo
            nova_linha_user = [username, password, nome, perfil, novo_id]
            ws_users.append_row(nova_linha_user)
            
            return True, f"Professor '{nome}' e Usuário '{username}' criados com sucesso!"
            
        except Exception as e:
            return True, f"Professor cadastrado, mas erro ao criar usuário: {e}"
            
    return True, "Professor cadastrado com sucesso!"

# ... (Mantenha todo o resto do arquivo igual) ...

def salvar_vinculos_do_professor(id_prof, lista_ids_alunos):
    sh = conectar_planilha()
    try: 
        ws = sh.worksheet("LINK_Alunos_Professores")
    except: 
        # Cria a aba se não existir
        ws = sh.add_worksheet("LINK_Alunos_Professores", 1000, 3)
        ws.append_row(["ID Vínculo", "ID Aluno", "ID Professor"])
        
    # 1. Lê todos os vínculos existentes
    todos_dados = ws.get_all_records()
    
    # 2. Mantém na lista APENAS os vínculos de OUTROS professores
    # (Ou seja, removemos tudo que for desse id_prof para recriar do zero)
    novos_dados = [linha for linha in todos_dados if str(linha.get('ID Professor')) != str(id_prof)]
    
    # 3. Adiciona os novos vínculos selecionados
    for id_aluno in lista_ids_alunos:
        novos_dados.append({
            "ID Vínculo": len(novos_dados) + 1, 
            "ID Aluno": id_aluno, 
            "ID Professor": id_prof
        })
        
    # 4. Reescreve a planilha (Limpa e Salva tudo de novo para garantir ordem)
    ws.clear()
    ws.append_row(["ID Vínculo", "ID Aluno", "ID Professor"])
    
    if novos_dados:
        # Prepara lista de listas para salvar rápido
        linhas_salvar = [[d.get('ID Vínculo'), d.get('ID Aluno'), d.get('ID Professor')] for d in novos_dados]
        ws.append_rows(linhas_salvar)
        
    return True, f"Vínculos atualizados! Professor agora atende {len(lista_ids_alunos)} alunos."

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
    
    nova_linha = [proximo_id, data_contratacao, id_aluno, nome_aluno, nome_pacote_gerado, qtd_horas, valor_total, forma_pagamento, dt_pag_final, "", "", status]
    ws.append_row(nova_linha)
    
    if status == "Pago":
        # Chama a função de registro financeiro (está no mesmo arquivo, chamada direta)
        registrar_movimentacao_financeira(dt_pag_final, "Entrada", "Venda de Pacote", f"Venda: {nome_pacote_gerado} - {nome_aluno}", valor_total, "Pago")
        return True, f"Venda realizada e Financeiro registrado! Total: R$ {valor_total:.2f}"
    
    return True, f"Venda registrada (Pendente). Total: R$ {valor_total:.2f}"

def salvar_vinculos_do_aluno(id_aluno, lista_ids_profs):
    sh = conectar_planilha()
    try: 
        ws = sh.worksheet("LINK_Alunos_Professores")
    except: 
        ws = sh.add_worksheet("LINK_Alunos_Professores", 1000, 3)
        ws.append_row(["ID Vínculo", "ID Aluno", "ID Professor"])
        
    # 1. Lê todos os dados atuais
    todos_dados = ws.get_all_records()
    
    # 2. Mantém apenas os dados de OUTROS alunos (remove tudo desse aluno específico)
    novos_dados = [linha for linha in todos_dados if str(linha.get('ID Aluno')) != str(id_aluno)]
    
    # 3. Adiciona os novos professores vinculados
    for id_prof in lista_ids_profs:
        novos_dados.append({
            "ID Vínculo": len(novos_dados) + 1, 
            "ID Aluno": id_aluno, 
            "ID Professor": id_prof
        })
        
    # 4. Reescreve a planilha
    ws.clear()
    ws.append_row(["ID Vínculo", "ID Aluno", "ID Professor"])
    
    if novos_dados:
        # Prepara lista para escrita rápida
        linhas_salvar = [[d.get('ID Vínculo'), d.get('ID Aluno'), d.get('ID Professor')] for d in novos_dados]
        ws.append_rows(linhas_salvar)
        
    return True, "Lista de professores do aluno atualizada com sucesso!"