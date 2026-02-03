# Arquivo: views/__init__.py

# Importa as funções principais das pastas novas
from .login import show_login
from .professores import show_professor
from .admin import show_admin

# Se você ainda tiver o arquivo 'estagiarios.py' antigo solto, mantenha:
# from .estagiarios import show_estag_view