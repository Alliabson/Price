import streamlit as st
import math
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import locale

# Configurar locale para PT-BR
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Funções de cálculo financeiro
def calcular_price(valor_financiado, taxa_juros, prazo_meses):
    i = taxa_juros / 100
    parcela = valor_financiado * (i * math.pow(1 + i, prazo_meses)) / (math.pow(1 + i, prazo_meses) - 1)
    
    parcelas = []
    saldo_devedor = valor_financiado
    
    for periodo in range(1, prazo_meses + 1):
        juros = saldo_devedor * i
        amortizacao = parcela - juros
        saldo_devedor -= amortizacao
        if saldo_devedor < 0.01:
            saldo_devedor = 0
        
        parcelas.append({
            'Período': periodo,
            'Prestação': round(parcela, 2),
            'Juros': round(juros, 2),
            'Amortização': round(amortizacao, 2),
            'Saldo Devedor': round(saldo_devedor, 2)
        })
    
    return {
        'valor_financiado': round(valor_financiado, 2),
        'taxa_juros': round(taxa_juros, 2),
        'prazo_meses': prazo_meses,
        'valor_parcela': round(parcela, 2),
        'total_pago': round(parcela * prazo_meses, 2),
        'total_juros': round(parcela * prazo_meses - valor_financiado, 2),
        'parcelas': parcelas
    }

def calcular_sac(valor_financiado, taxa_juros, prazo_meses):
    i = taxa_juros / 100
    amortizacao = valor_financiado / prazo_meses
    
    parcelas = []
    saldo_devedor = valor_financiado
    total_pago = 0
    total_juros = 0
    
    for periodo in range(1, prazo_meses + 1):
        juros = saldo_devedor * i
        parcela = amortizacao + juros
        saldo_devedor -= amortizacao
        if saldo_devedor < 0.01:
            saldo_devedor = 0
        
        total_pago += parcela
        total_juros += juros
        
        parcelas.append({
            'Período': periodo,
            'Prestação': round(parcela, 2),
            'Juros': round(juros, 2),
            'Amortização': round(amortizacao, 2),
            'Saldo Devedor': round(saldo_devedor, 2)
        })
    
    return {
        'valor_financiado': round(valor_financiado, 2),
        'taxa_juros': round(taxa_juros, 2),
        'prazo_meses': prazo_meses,
        'valor_primeira_parc': round(parcelas[0]['Prestação'], 2),
        'valor_ultima_parc': round(parcelas[-1]['Prestação'], 2),
        'total_pago': round(total_pago, 2),
        'total_juros': round(total_juros, 2),
        'parcelas': parcelas
    }

def simular_poupanca(valor, prazo_meses, taxa=0.5):
    """Simula investimento na poupança com taxa mensal (default 0.5% a.m.)"""
    montante = valor
    historico = []
    
    for mes in range(1, prazo_meses + 1):
        montante *= (1 + taxa/100)
        historico.append({
            'Mês': mes,
            'Valor': round(montante, 2),
            'Rendimento': round(montante - valor, 2)
        })
    
    return {
        'valor_inicial': valor,
        'valor_final': round(montante, 2),
        'rendimento_total': round(montante - valor, 2),
        'historico': historico
    }

def simular_imobiliario(valor, prazo_meses, taxa=0.7):
    """Simula investimento no mercado imobiliário com taxa mensal (default 0.7% a.m.)"""
    montante = valor
    historico = []
    
    for mes in range(1, prazo_meses + 1):
        montante *= (1 + taxa/100)
        historico.append({
            'Mês': mes,
            'Valor': round(montante, 2),
            'Rendimento': round(montante - valor, 2)
        })
    
    return {
        'valor_inicial': valor,
        'valor_final': round(montante, 2),
        'rendimento_total': round(montante - valor, 2),
        'historico': historico
    }

def formatar_moeda(valor):
    """Formata valores para o padrão monetário brasileiro"""
    return locale.currency(valor, grouping=True, symbol=True)

def gerar_pdf(resultado, sistema):
    """Gera PDF com o detalhamento das parcelas"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Cabeçalho
    pdf.cell(200, 10, txt="Detalhamento do Financiamento", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Sistema: {sistema}", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1, align='C')
    pdf.ln(10)
    
    # Informações gerais
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Resumo do Financiamento", ln=1)
    pdf.set_font("Arial", size=10)
    
    pdf.cell(100, 8, txt=f"Valor financiado: {formatar_moeda(resultado['valor_financiado'])}", ln=1)
    pdf.cell(100, 8, txt=f"Taxa de juros: {resultado['taxa_juros']}% ao mês", ln=1)
    pdf.cell(100, 8, txt=f"Prazo: {resultado['prazo_meses']} meses", ln=1)
    
    if sistema == "Price":
        pdf.cell(100, 8, txt=f"Valor da parcela: {formatar_moeda(resultado['valor_parcela'])}", ln=1)
    else:
        pdf.cell(100, 8, txt=f"1ª Parcela: {formatar_moeda(resultado['valor_primeira_parc'])}", ln=1)
        pdf.cell(100, 8, txt=f"Última Parcela: {formatar_moeda(resultado['valor_ultima_parc'])}", ln=1)
    
    pdf.cell(100, 8, txt=f"Total pago: {formatar_moeda(resultado['total_pago'])}", ln=1)
    pdf.cell(100, 8, txt=f"Total de juros: {formatar_moeda(resultado['total_juros'])}", ln=1)
    pdf.ln(10)
    
    # Tabela de parcelas
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detalhamento das Parcelas", ln=1)
    pdf.set_font("Arial", 'B', 10)
    
    # Cabeçalho da tabela
    col_widths = [20, 30, 30, 30, 40]
    headers = ["Período", "Prestação", "Juros", "Amortização", "Saldo Devedor"]
    
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, txt=header, border=1)
    pdf.ln()
    
    # Dados da tabela
    pdf.set_font("Arial", size=8)
    for parcela in resultado['parcelas']:
        pdf.cell(col_widths[0], 8, txt=str(parcela['Período']), border=1)
        pdf.cell(col_widths[1], 8, txt=formatar_moeda(parcela['Prestação']), border=1)
        pdf.cell(col_widths[2], 8, txt=formatar_moeda(parcela['Juros']), border=1)
        pdf.cell(col_widths[3], 8, txt=formatar_moeda(parcela['Amortização']), border=1)
        pdf.cell(col_widths[4], 8, txt=formatar_moeda(parcela['Saldo Devedor']), border=1)
        pdf.ln()
    
    # Salvar PDF
    pdf_filename = f"financiamento_{sistema}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(pdf_filename)
    
    return pdf_filename

# Configuração da página
st.set_page_config(page_title="Calculadora Financeira", page_icon="💰", layout="wide")

# Título do aplicativo
st.title("💰 Calculadora Financeira Avançada")

# Abas para diferentes funcionalidades
tab1, tab2, tab3 = st.tabs(["Cálculo", "Comparativo", "Investimentos"])

with tab1:
    st.header("Cálculo de Financiamento")
    
    # Formulário de entrada
    col1, col2, col3 = st.columns(3)
    with col1:
        valor_financiado = st.number_input("Valor a Financiar (R$):", min_value=0.0, step=1000.0, value=100000.0)
    with col2:
        taxa_juros = st.number_input("Taxa de Juros (% ao mês):", min_value=0.0, step=0.1, value=1.5)
    with col3:
        prazo_meses = st.number_input("Prazo (em meses):", min_value=1, step=1, value=36)
    
    sistema = st.selectbox("Sistema de Amortização:", ["Price (Parcelas fixas)", "SAC (Amortização constante)"])
    
    if st.button("Calcular Financiamento"):
        if "Price" in sistema:
            resultado = calcular_price(valor_financiado, taxa_juros, prazo_meses)
            sistema_nome = "Price"
        else:
            resultado = calcular_sac(valor_financiado, taxa_juros, prazo_meses)
            sistema_nome = "SAC"
        
        # Exibir resumo
        st.subheader(f"Resumo do Financiamento - Sistema {sistema_nome}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Valor Financiado", formatar_moeda(resultado['valor_financiado']))
        col2.metric("Taxa de Juros", f"{resultado['taxa_juros']}% a.m.")
        col3.metric("Prazo", f"{resultado['prazo_meses']} meses")
        
        if sistema_nome == "Price":
            col1, col2, col3 = st.columns(3)
            col1.metric("Valor da Parcela", formatar_moeda(resultado['valor_parcela']))
            col2.metric("Total Pago", formatar_moeda(resultado['total_pago']))
            col3.metric("Total de Juros", formatar_moeda(resultado['total_juros']))
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("1ª Parcela", formatar_moeda(resultado['valor_primeira_parc']))
            col2.metric("Última Parcela", formatar_moeda(resultado['valor_ultima_parc']))
            col3.metric("Total Pago", formatar_moeda(resultado['total_pago']))
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Juros", formatar_moeda(resultado['total_juros']))
        
        # Exibir tabela de parcelas
        st.subheader("Detalhamento das Parcelas")
        df = pd.DataFrame(resultado['parcelas'])
        st.dataframe(df.style.format({
            'Prestação': lambda x: formatar_moeda(x),
            'Juros': lambda x: formatar_moeda(x),
            'Amortização': lambda x: formatar_moeda(x),
            'Saldo Devedor': lambda x: formatar_moeda(x)
        }), hide_index=True, use_container_width=True)
        
        # Gráfico de evolução
        st.subheader("Evolução do Financiamento")
        fig = px.line(df, x='Período', y=['Prestação', 'Juros', 'Amortização'],
                      title=f"Evolução das Parcelas - Sistema {sistema_nome}",
                      labels={'value': 'Valor (R$)', 'variable': 'Componente'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Botão para exportar PDF
        if st.button("Exportar para PDF"):
            pdf_filename = gerar_pdf(resultado, sistema_nome)
            with open(pdf_filename, "rb") as pdf_file:
                st.download_button(
                    label="Baixar PDF",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )

with tab2:
    st.header("Comparativo Price vs SAC")
    
    # Formulário de entrada
    col1, col2, col3 = st.columns(3)
    with col1:
        valor_comp = st.number_input("Valor a Financiar (R$):", min_value=0.0, step=1000.0, value=100000.0, key="valor_comp")
    with col2:
        taxa_comp = st.number_input("Taxa de Juros (% ao mês):", min_value=0.0, step=0.1, value=1.5, key="taxa_comp")
    with col3:
        prazo_comp = st.number_input("Prazo (em meses):", min_value=1, step=1, value=36, key="prazo_comp")
    
    if st.button("Comparar Sistemas", key="comparar"):
        resultado_price = calcular_price(valor_comp, taxa_comp, prazo_comp)
        resultado_sac = calcular_sac(valor_comp, taxa_comp, prazo_comp)
        
        diff_juros = resultado_price['total_juros'] - resultado_sac['total_juros']
        percentual_diff = round(diff_juros / resultado_sac['total_juros'] * 100, 2)
        
        # Exibir comparativo
        st.subheader("Comparativo entre Sistemas")
        
        # Métricas comparativas
        col1, col2, col3 = st.columns(3)
        col1.metric("Valor Financiado", formatar_moeda(resultado_price['valor_financiado']))
        col2.metric("Taxa de Juros", f"{resultado_price['taxa_juros']}% a.m.")
        col3.metric("Prazo", f"{resultado_price['prazo_meses']} meses")
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("1ª Parcela (Price)", formatar_moeda(resultado_price['valor_parcela']))
        col2.metric("1ª Parcela (SAC)", formatar_moeda(resultado_sac['valor_primeira_parc']))
        col3.metric("Diferença", formatar_moeda(resultado_price['valor_parcela'] - resultado_sac['valor_primeira_parc']))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Última Parcela (Price)", formatar_moeda(resultado_price['valor_parcela']))
        col2.metric("Última Parcela (SAC)", formatar_moeda(resultado_sac['valor_ultima_parc']))
        col3.metric("Diferença", formatar_moeda(resultado_price['valor_parcela'] - resultado_sac['valor_ultima_parc']))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Pago (Price)", formatar_moeda(resultado_price['total_pago']))
        col2.metric("Total Pago (SAC)", formatar_moeda(resultado_sac['total_pago']))
        col3.metric("Diferença", formatar_moeda(resultado_price['total_pago'] - resultado_sac['total_pago']))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Juros (Price)", formatar_moeda(resultado_price['total_juros']))
        col2.metric("Total Juros (SAC)", formatar_moeda(resultado_sac['total_juros']))
        col3.metric("Diferença", f"{formatar_moeda(diff_juros)} ({percentual_diff}%)")
        
        # Gráfico comparativo de parcelas
        st.subheader("Evolução das Parcelas")
        
        # Preparar dados para o gráfico
        df_price = pd.DataFrame(resultado_price['parcelas'])
        df_sac = pd.DataFrame(resultado_sac['parcelas'])
        
        # Juntar os dados
        df_comparativo = pd.DataFrame({
            'Período': df_price['Período'],
            'Price': df_price['Prestação'],
            'SAC': df_sac['Prestação']
        })
        
        # Exibir gráfico
        fig = px.line(df_comparativo, x='Período', y=['Price', 'SAC'],
                     title="Comparação de Parcelas - Price vs SAC",
                     labels={'value': 'Valor da Parcela (R$)', 'variable': 'Sistema'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise
        st.subheader("Análise")
        st.write("""
        - **Sistema Price**: Oferece parcelas fixas ao longo de todo o financiamento, o que facilita o planejamento financeiro.
        - **Sistema SAC**: Inicia com parcelas maiores que vão diminuindo ao longo do tempo, o que pode ser vantajoso a longo prazo.
        """)
        st.success(f"No sistema SAC, você pagará menos juros no total ({percentual_diff}% menos) em comparação com o sistema Price.")
        st.info("A escolha entre os sistemas depende da sua capacidade de pagamento inicial e de suas prioridades financeiras.")

with tab3:
    st.header("Comparativo com Investimentos")
    st.write("Simulação do que aconteceria se o valor das parcelas fosse investido")
    
    # Formulário de entrada
    col1, col2, col3 = st.columns(3)
    with col1:
        valor_invest = st.number_input("Valor Disponível (R$):", min_value=0.0, step=1000.0, value=100000.0, key="valor_invest")
    with col2:
        prazo_invest = st.number_input("Prazo (em meses):", min_value=1, step=1, value=36, key="prazo_invest")
    with col3:
        taxa_poupanca = st.number_input("Taxa Poupança (% a.m.):", min_value=0.0, step=0.01, value=0.5, key="taxa_poup")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        taxa_imobiliario = st.number_input("Taxa Imobiliário (% a.m.):", min_value=0.0, step=0.01, value=0.7, key="taxa_imob")
    
    if st.button("Simular Investimentos"):
        # Simular investimentos
        res_poupanca = simular_poupanca(valor_invest, prazo_invest, taxa_poupanca)
        res_imobiliario = simular_imobiliario(valor_invest, prazo_invest, taxa_imobiliario)
        
        # Exibir resultados
        st.subheader("Resultados dos Investimentos")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Poupança - Valor Final", formatar_moeda(res_poupanca['valor_final']))
            st.metric("Poupança - Rendimento Total", formatar_moeda(res_poupanca['rendimento_total']))
            
            # Gráfico da poupança
            df_poup = pd.DataFrame(res_poupanca['historico'])
            fig_poup = px.line(df_poup, x='Mês', y='Valor', 
                             title="Evolução do Investimento na Poupança")
            st.plotly_chart(fig_poup, use_container_width=True)
        
        with col2:
            st.metric("Mercado Imobiliário - Valor Final", formatar_moeda(res_imobiliario['valor_final']))
            st.metric("Mercado Imobiliário - Rendimento Total", formatar_moeda(res_imobiliario['rendimento_total']))
            
            # Gráfico do imobiliário
            df_imob = pd.DataFrame(res_imobiliario['historico'])
            fig_imob = px.line(df_imob, x='Mês', y='Valor', 
                             title="Evolução do Investimento no Mercado Imobiliário",
                             color_discrete_sequence=['orange'])
            st.plotly_chart(fig_imob, use_container_width=True)
        
        # Comparativo entre investimentos
        st.subheader("Comparativo entre Investimentos")
        
        df_comparativo = pd.DataFrame({
            'Mês': df_poup['Mês'],
            'Poupança': df_poup['Valor'],
            'Mercado Imobiliário': df_imob['Valor']
        })
        
        fig_comp = px.line(df_comparativo, x='Mês', y=['Poupança', 'Mercado Imobiliário'],
                          title="Comparação entre Investimentos",
                          labels={'value': 'Valor (R$)', 'variable': 'Tipo de Investimento'})
        st.plotly_chart(fig_comp, use_container_width=True)

# Rodapé
st.divider()
st.caption("Calculadora Financeira Avançada - Desenvolvida com Streamlit")
