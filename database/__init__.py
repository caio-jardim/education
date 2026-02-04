# database/__init__.py

# 1. Base
from .connection import conectar_planilha
from .utils import to_float, normalizar_id

# 2. Leituras (reads.py)
# AQUI ESTAVA O ERRO: Faltava incluir get_usuarios e get_saldo_alunos na lista
from .reads import (
    get_usuarios, 
    get_alunos, 
    get_professores, 
    get_pacotes, 
    get_aulas, 
    get_vinculos, 
    get_financeiro_geral, 
    get_saldo_alunos,
    get_dash_alunos_data
)

# 3. Escritas - Financeiro
from .financeiro import registrar_movimentacao_financeira

# 4. Escritas - Dashboards
from .dashboards import atualizar_dash_dados

# 5. Escritas - Vendas
from .vendas import registrar_venda_automatica, processar_primeira_aula

# 6. Escritas - Aulas
from .aulas import (
    registrar_aula, registrar_lote_aulas, atualizar_status_aula
)

# 7. Escritas - Pessoas
from .pessoas import (
    cadastrar_aluno, cadastrar_professor, 
    salvar_vinculos_do_aluno, salvar_vinculos_do_professor
)