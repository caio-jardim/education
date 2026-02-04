# database/vendas.py
from .connection import conectar_planilha
from .reads import get_pacotes
from .utils import to_float
from .financeiro import registrar_movimentacao_financeira
from .dashboards import atualizar_dash_dados
from datetime import datetime, timedelta

def registrar_venda_automatica(id_aluno, nome_aluno, qtd, forma, dt_contrato, dt_pag, valor_manual=None):
    sh = conectar_planilha()
    
    qtd_float = to_float(qtd)
    total = 0.0
    nome_pct = ""
    
    # Lógica de Preço
    if isinstance(valor_manual, (int, float)) and valor_manual > 0:
        total = float(valor_manual)
        nome_pct = f"Personalizado ({qtd_float}h)"
    else:
        df_pct = get_pacotes()
        nome_pct = f"Avulso {qtd_float}h"
        for _, row in df_pct.iterrows():
            try:
                if to_float(row['Quantidade Mínima']) <= qtd_float <= to_float(row.get('Quantidade Máxima', 999)):
                    total = to_float(row['Valor Hora']) * qtd_float
                    nome_pct = f"{row['Nome Pacote']} ({qtd_float}h)"
                    break
            except: continue
    
    # Salvar Venda
    ws = sh.worksheet("MOV_Vendas")
    col = ws.col_values(1)
    try: ult = int(col[-1]) if len(col) > 1 else 0
    except: ult = len(col)
    
    status = "Pago" if dt_pag else "Pendente"
    ws.append_row([ult + 1, dt_contrato, id_aluno, nome_aluno, nome_pct, qtd_float, total, forma, dt_pag, "", "", status])
    
    if status == "Pago":
        registrar_movimentacao_financeira(dt_pag, "Entrada", "Venda Pacote", f"Venda {nome_pct}", total, "Pago")
    
    atualizar_dash_dados() # Chama a atualização isolada
    return True, f"Venda R$ {total:,.2f}"

def processar_primeira_aula(id_aluno, data_aula_dt):
    """
    Atualiza MOV_Vendas com a Data da Primeira Aula e Vencimento.
    """
    print(f"\n>>> [DEBUG VENDAS] Iniciando proc. para Aluno ID: {id_aluno}")
    
    try:
        sh = conectar_planilha()
        ws = sh.worksheet("MOV_Vendas")
        all_values = ws.get_all_values()
        
        if not all_values: return False, "Planilha vazia."
        
        header = [h.strip().lower() for h in all_values[0]] # Cabeçalho minúsculo e sem espaços
        dados = all_values[1:]
        
        # 1. Localizar índices das colunas (Independente de maiúscula/minúscula)
        try:
            # Procura coluna que contenha "id" e "aluno"
            idx_id = next(i for i, h in enumerate(header) if "id" in h and "aluno" in h)
            
            # Procura coluna que contenha "primeira" e "aula"
            idx_dt_prim = next(i for i, h in enumerate(header) if "primeira" in h and "aula" in h)
            
            # Procura coluna que contenha "vencimento"
            idx_venc = next(i for i, h in enumerate(header) if "vencimento" in h)
            
            print(f">>> [DEBUG VENDAS] Colunas encontradas: ID={idx_id}, Prim={idx_dt_prim}, Venc={idx_venc}")
        except StopIteration:
            print(">>> [ERRO VENDAS] Colunas não encontradas no cabeçalho.")
            return False, "Erro: Verifique os nomes das colunas na planilha MOV_Vendas."

        # 2. Varrer de baixo para cima (última venda primeiro)
        id_busca = str(id_aluno).strip()
        
        for i in range(len(dados) - 1, -1, -1):
            row = dados[i]
            
            # Limpa o ID da linha (tira .0 se vier do excel)
            id_row = str(row[idx_id]).strip().replace(".0", "")
            dt_prim_atual = str(row[idx_dt_prim]).strip()
            
            if id_row == id_busca:
                # Se achou o aluno e a data está vazia
                if dt_prim_atual == "":
                    print(f">>> [DEBUG VENDAS] Venda encontrada na linha {i+2}. Atualizando...")
                    
                    # Cálculos
                    dt_inicio = data_aula_dt.strftime("%d/%m/%Y")
                    dt_fim = (data_aula_dt + timedelta(days=30)).strftime("%d/%m/%Y")
                    
                    # Atualiza (row + 2 porque i começa em 0 e tem header)
                    ws.update_cell(i + 2, idx_dt_prim + 1, dt_inicio)
                    ws.update_cell(i + 2, idx_venc + 1, dt_fim)
                    
                    return True, f"Pacote ativado! Vencimento: {dt_fim}"
        
        print(">>> [DEBUG VENDAS] Nenhuma venda pendente encontrada.")
        return False, "Nenhum pacote pendente encontrado para este aluno."

    except Exception as e:
        print(f">>> [ERRO CRÍTICO VENDAS]: {e}")
        return False, f"Erro sistema: {e}"
    