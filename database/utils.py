def normalizar_id(valor):
    """Garante que ID seja string limpa de inteiro (ex: 1.0 -> '1')"""
    if isinstance(valor, (int, float)):
        return str(int(valor))
    try:
        s = str(valor).strip().replace(',', '.')
        return str(int(float(s)))
    except:
        return str(valor).strip()

def to_float(valor):
    """
    Converte para float de forma segura.
    Resolve o problema de 2.5 virar 25.
    """
    # 1. Se já é número, retorna direto
    if isinstance(valor, (int, float)):
        return float(valor)
    
    s = str(valor).strip().replace('R$', '').strip()
    if not s: return 0.0
    
    # 2. Lógica para String
    if ',' in s:
        # Formato BR (1.000,50 ou 2,5)
        # Remove ponto de milhar (1.000 -> 1000)
        s = s.replace('.', '')
        # Troca vírgula por ponto (2,5 -> 2.5)
        s = s.replace(',', '.')
    else:
        # Formato Internacional ou Python Puro (2.5 ou 1000)
        # NÃO removemos o ponto aqui, pois "2.5" é dois e meio.
        pass
        
    try:
        return float(s)
    except:
        return 0.0