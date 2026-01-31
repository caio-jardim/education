# database/vendas.py
from .connection import conectar_planilha
from .reads import get_pacotes
from .utils import to_float
from .financeiro import registrar_movimentacao_financeira
from .dashboards import atualizar_dash_dados

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