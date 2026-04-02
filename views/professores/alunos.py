import streamlit as st
import pandas as pd
import database as db
from datetime import datetime
from dateutil.relativedelta import relativedelta
from modules.ui.core import header_page, kpi_card

def show_page_alunos(id_prof_logado, nome_prof):
    header_page("Meus Alunos", f"Painel de {nome_prof}")
    
    try:
        # --- 1. CARREGAMENTO DE DADOS ---
        # Carrega Alunos (para a contagem)
        df_alunos = db.get_saldo_alunos() 
        
        # Carrega Aulas (para calcular comissão)
        df_aulas = db.get_aulas()
        
        # Carrega Vínculos (para filtrar alunos)
        try: df_links = db.get_vinculos()
        except: df_links = None

        # --- 2. LÓGICA DE ALUNOS (Filtragem) ---
        df_meus_alunos = df_alunos
        if df_links is not None and not df_links.empty:
            df_links = df_links.rename(columns={'ID Professor': 'id_prof_link', 'ID Aluno': 'id_aluno_link'})
            vinculos_prof = df_links[df_links['id_prof_link'].astype(str) == str(id_prof_logado)]
            ids_meus_alunos = vinculos_prof['id_aluno_link'].astype(str).tolist()
            
            col_id_aluno_cad = 'ID Aluno' if 'ID Aluno' in df_alunos.columns else 'id_aluno'
            if col_id_aluno_cad in df_alunos.columns:
                df_meus_alunos = df_alunos[df_alunos[col_id_aluno_cad].astype(str).isin(ids_meus_alunos)]
        
        # --- 3. LÓGICA DE COMISSÃO ---
        comissao_mes = 0.00
        
        # --- FILTRO DE MÊS (Novo) ---
        st.markdown("### 📊 Análise de Comissão")
        
        # Gera lista de meses a partir de janeiro de 2026 até o mês atual
        hoje = datetime.now()
        inicio = datetime(2026, 1, 1)
        meses_disponiveis = []
        
        # Calcula quantos meses há entre janeiro/2026 e hoje
        meses_total = (hoje.year - inicio.year) * 12 + (hoje.month - inicio.month) + 1
        
        for i in range(meses_total):
            data_filtro = inicio + relativedelta(months=i)
            # Formato mais legível
            mes_ano_display = data_filtro.strftime("%B de %Y").replace("January", "Janeiro").replace("February", "Fevereiro").replace("March", "Março").replace("April", "Abril").replace("May", "Maio").replace("June", "Junho").replace("July", "Julho").replace("August", "Agosto").replace("September", "Setembro").replace("October", "Outubro").replace("November", "Novembro").replace("December", "Dezembro")
            meses_disponiveis.append((mes_ano_display, data_filtro))
        
        # Selectbox com opção de escolher o mês
        col_mes, col_vazio = st.columns([2, 4])
        with col_mes:
            mes_selecionado_display = st.selectbox(
                "Selecione o mês para consultar comissão:",
                options=[m[0] for m in meses_disponiveis],
                index=len(meses_disponiveis) - 1  # Por padrão, seleciona o mês atual
            )
        
        # Encontra o objeto datetime correspondente ao mês selecionado
        mes_escolhido = next((m[1] for m in meses_disponiveis if m[0] == mes_selecionado_display), hoje)
        
        if not df_aulas.empty:
            # Filtra pelo Professor Logado
            col_id_prof_aula = next((c for c in df_aulas.columns if 'id' in c.lower() and 'prof' in c.lower()), None)
            
            if col_id_prof_aula:
                # Filtra aulas do professor
                minhas_aulas = df_aulas[df_aulas[col_id_prof_aula].astype(str) == str(id_prof_logado)].copy()
                
                if not minhas_aulas.empty:
                    # Converte data para datetime
                    if 'Data' in minhas_aulas.columns:
                        minhas_aulas['Data_Dt'] = pd.to_datetime(minhas_aulas['Data'], format="%d/%m/%Y", errors='coerce')
                        
                        # Filtra Mês e Ano Selecionados (ao invés de usar "hoje")
                        aulas_mes = minhas_aulas[
                            (minhas_aulas['Data_Dt'].dt.month == mes_escolhido.month) & 
                            (minhas_aulas['Data_Dt'].dt.year == mes_escolhido.year)
                        ]
                        
                        # Calcula a soma da comissão
                        col_comissao = next((c for c in aulas_mes.columns if 'comiss' in c.lower()), None)
                        
                        if col_comissao:
                            # Limpeza segura de R$ 50,00 -> 50.00
                            def limpar_valor(v):
                                try:
                                    s = str(v).replace('R$', '').replace('.', '').replace(',', '.').strip()
                                    return float(s)
                                except: return 0.0
                            
                            aulas_mes['Comissao_Clean'] = aulas_mes[col_comissao].apply(limpar_valor)
                            
                            # Soma apenas aulas REALIZADAS
                            if 'Status' in aulas_mes.columns:
                                aulas_mes = aulas_mes[aulas_mes['Status'] == 'Realizada']
                            
                            comissao_mes = aulas_mes['Comissao_Clean'].sum()

        # --- 4. EXIBIÇÃO DOS KPIS (Cards Apenas) ---
        c1, c2 = st.columns(2)
        
        with c1:
            kpi_card("Meus Alunos", str(len(df_meus_alunos)), "icon_alunos.png")
            
        with c2:
            # Formatação bonita em R$
            kpi_card("Minha Comissão (Mês)", f"R$ {comissao_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "icon_money.png")

        # FIM DO ARQUIVO (Tabela removida conforme solicitado)
            
    except Exception as e:
        st.error(f"Erro ao carregar painel: {e}")