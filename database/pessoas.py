import re
from .connection import conectar_planilha
from .utils import to_float, normalizar_id
from .dashboards import atualizar_dash_dados

def cadastrar_aluno(nome, responsavel, telefone, nascimento, serie, escola, endereco, obs):
    sh = conectar_planilha()
    ws = sh.worksheet("CAD_Alunos")
    
    col_ids = ws.col_values(1)
    try: ultimo = int(col_ids[-1]) if len(col_ids) > 1 else 0
    except: ultimo = len(col_ids)
    proximo_id = ultimo + 1
    
    apenas_numeros = re.sub(r'\D', '', str(telefone))
    tel_final = f"55{apenas_numeros}" if apenas_numeros and not apenas_numeros.startswith('55') else (f"+{apenas_numeros}" if apenas_numeros else "")
    
    # OBS: O ID do aluno aqui já é int (proximo_id), então salva como número
    ws.append_row([proximo_id, nome, responsavel, tel_final, nascimento, serie, escola, endereco, obs, "Ativo"])
    
    atualizar_dash_dados() 
    return proximo_id

def cadastrar_professor(nome, val_education, val_online, val_casa, create_user=False, username="", password="", perfil=""):
    sh = conectar_planilha()
    
    if create_user and username:
        try:
            ws_u = sh.worksheet("CAD_Usuarios")
            logins = ws_u.col_values(1)
            if any(u.lower() == username.lower() for u in logins):
                return False, f"O login '{username}' já está em uso!"
        except: pass

    ws_p = sh.worksheet("CAD_Professores")
    col_ids = ws_p.col_values(1)
    try: ultimo = int(col_ids[-1]) if len(col_ids) > 1 else 0
    except: ultimo = len(col_ids)
    novo_id = ultimo + 1
    
    ws_p.append_row([novo_id, nome, to_float(val_education), to_float(val_online), to_float(val_casa), "Ativo"])
    
    if create_user and username:
        try:
            try: ws_u = sh.worksheet("CAD_Usuarios")
            except: ws_u = sh.add_worksheet("CAD_Usuarios", 1000, 5)
            # Salva o ID Vinculo como inteiro
            ws_u.append_row([username, password, nome, perfil, novo_id])
        except Exception as e: return True, f"Professor criado, erro no usuário: {e}"
            
    return True, "Professor cadastrado com sucesso!"

def salvar_vinculos_do_professor(id_prof, lista_ids_alunos):
    sh = conectar_planilha()
    try: ws = sh.worksheet("LINK_Alunos_Professores")
    except: ws = sh.add_worksheet("LINK_Alunos_Professores", 1000, 3)
    
    dados = ws.get_all_records()
    id_prof_str = normalizar_id(id_prof) # String para comparar
    
    # Mantém os outros (filtra usando string para garantir match)
    novos = [L for L in dados if normalizar_id(L.get('ID Professor')) != id_prof_str]
    
    # Adiciona os novos
    for id_aluno in lista_ids_alunos:
        novos.append({
            "ID Vínculo": len(novos) + 1, 
            # --- AQUI ESTÁ A CORREÇÃO: FORÇAR INT NA HORA DE SALVAR ---
            "ID Aluno": int(normalizar_id(id_aluno)), 
            "ID Professor": int(id_prof_str)
            # ---------------------------------------------------------
        })
        
    ws.clear()
    ws.append_row(["ID Vínculo", "ID Aluno", "ID Professor"])
    if novos:
        # Garante a ordem das colunas ao salvar
        ws.append_rows([[d['ID Vínculo'], d['ID Aluno'], d['ID Professor']] for d in novos])
        
    return True, "Vínculos atualizados!"

def salvar_vinculos_do_aluno(id_aluno, lista_ids_profs):
    sh = conectar_planilha()
    try: ws = sh.worksheet("LINK_Alunos_Professores")
    except: ws = sh.add_worksheet("LINK_Alunos_Professores", 1000, 3)
    
    dados = ws.get_all_records()
    id_aluno_str = normalizar_id(id_aluno) # String para comparar
    
    # Mantém os outros
    novos = [L for L in dados if normalizar_id(L.get('ID Aluno')) != id_aluno_str]
    
    # Adiciona os novos
    for id_prof in lista_ids_profs:
        novos.append({
            "ID Vínculo": len(novos) + 1, 
            # --- AQUI ESTÁ A CORREÇÃO: FORÇAR INT NA HORA DE SALVAR ---
            "ID Aluno": int(id_aluno_str), 
            "ID Professor": int(normalizar_id(id_prof))
            # ---------------------------------------------------------
        })
        
    ws.clear()
    ws.append_row(["ID Vínculo", "ID Aluno", "ID Professor"])
    if novos:
        ws.append_rows([[d['ID Vínculo'], d['ID Aluno'], d['ID Professor']] for d in novos])
        
    return True, "Lista atualizada!"