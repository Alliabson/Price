import streamlit as st
import math
import pandas as pd
from datetime import datetime
import locale
import logging

# --- Configuração inicial de logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Calculadora Financeira", page_icon="💰", layout="wide")

# --- Configuração robusta do locale com cache ---
@st.cache_resource
def configure_locale():
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        logger.info("Locale configurado para pt_BR.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')
            logger.info("Locale configurado para pt_BR")
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
                logger.info("Locale configurado para Portuguese_Brazil.1252")
            except locale.Error:
                try:
                    locale.setlocale(locale.LC_ALL, '')
                    logger.info("Locale configurado para padrão do sistema")
                except locale.Error:
                    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
                    logger.warning("Configuração de locale específica não disponível. Usando padrão internacional.")

configure_locale()

# Função para formatar moeda com fallback robusto
def formatar_moeda(valor):
    try:
        return locale.currency(valor, grouping=True, symbol=True)
    except:
        try:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return f"R$ {valor:.2f}"

# --- Funções de Cálculo Financeiro ---
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

# --- Funções para Visualização ---
def mostrar_evolucao_financiamento(df, sistema_nome):
    st.subheader(f"Evolução - Sistema {sistema_nome}")
    
    # Configuração de cores
    cores = {
        'Prestação': '#1f77b4',  # Azul
        'Juros': '#ff7f0e',      # Laranja
        'Amortização': '#2ca02c', # Verde
        'Saldo Devedor': '#9467bd' # Roxo
    }
    
    # Gráfico de componentes da parcela
    st.line_chart(
        df.set_index('Período')[['Prestação', 'Juros', 'Amortização']],
        color=[cores['Prestação'], cores['Juros'], cores['Amortização']]
    )
    
    # Gráfico de saldo devedor
    st.area_chart(
        df.set_index('Período')['Saldo Devedor'],
        color=cores['Saldo Devedor']
    )
    
    # Tabela resumida
    with st.expander("Ver estatísticas detalhadas"):
        st.dataframe(df.describe().style.format("{:.2f}"))

def mostrar_comparativo_sistemas(df_price, df_sac):
    st.subheader("Comparação Price vs SAC")
    
    # Criar DataFrame combinado
    df_comparativo = pd.DataFrame({
        'Período': df_price['Período'],
        'Price': df_price['Prestação'],
        'SAC': df_sac['Prestação'],
        'Diferença': df_price['Prestação'] - df_sac['Prestação']
    })
    
    # Gráfico comparativo
    st.line_chart(
        df_comparativo.set_index('Período')[['Price', 'SAC']],
        color=['#1f77b4', '#ff7f0e']  # Azul para Price, Laranja para SAC
    )
    
    # Gráfico de diferença
    st.bar_chart(
        df_comparativo.set_index('Período')['Diferença'],
        color='#d62728'  # Vermelho para diferença
    )

def mostrar_evolucao_investimentos(df_poup, df_imob):
    st.subheader("Evolução dos Investimentos")
    
    # Combinar os dados
    df_combinado = pd.DataFrame({
        'Mês': df_poup['Mês'],
        'Poupança': df_poup['Valor'],
        'Outra Aplicação': df_imob['Valor'],
        'Rendimento Poupança': df_poup['Rendimento'],
        'Rendimento Outra': df_imob['Rendimento']
    })
    
    # Gráfico de valores
    st.line_chart(
        df_combinado.set_index('Mês')[['Poupança', 'Outra Aplicação']],
        color=['#1f77b4', '#ff7f0e']
    )
    
    # Gráfico de rendimentos
    st.area_chart(
        df_combinado.set_index('Mês')[['Rendimento Poupança', 'Rendimento Outra']],
        color=['#a6cee3', '#fdbf6f']
    )

# --- Interface do Streamlit ---
st.title("💰 Calculadora Financeira Avançada")

# Criar abas
tab1, tab2, tab3 = st.tabs(["Cálculo", "Comparativo", "Investimentos"])

with tab1:
    st.header("Cálculo de Financiamento")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        valor_financiado = st.number_input("Valor a Financiar (R$):", min_value=0.0, step=1000.0, value=100000.0)
    with col2:
        taxa_juros = st.number_input("Taxa de Juros (% ao mês):", min_value=0.0, step=0.1, value=1.5)
    with col3:
        prazo_meses = st.number_input("Prazo (em meses):", min_value=1, step=1, value=36)
    
    sistema = st.selectbox("Sistema de Amortização:", ["Price (Parcelas fixas)", "SAC (Amortização constante)"])
    
    if st.button("Calcular Financiamento"):
        try:
            if "Price" in sistema:
                resultado = calcular_price(valor_financiado, taxa_juros, prazo_meses)
                sistema_nome = "Price"
            else:
                resultado = calcular_sac(valor_financiado, taxa_juros, prazo_meses)
                sistema_nome = "SAC"
            
            # Exibir resumo
            st.subheader(f"Resumo - Sistema {sistema_nome}")
            cols = st.columns(3)
            cols[0].metric("Valor Financiado", formatar_moeda(resultado['valor_financiado']))
            cols[1].metric("Taxa de Juros", f"{resultado['taxa_juros']}% a.m.")
            cols[2].metric("Prazo", f"{resultado['prazo_meses']} meses")
            
            if sistema_nome == "Price":
                cols = st.columns(3)
                cols[0].metric("Valor da Parcela", formatar_moeda(resultado['valor_parcela']))
                cols[1].metric("Total Pago", formatar_moeda(resultado['total_pago']))
                cols[2].metric("Total de Juros", formatar_moeda(resultado['total_juros']))
            else:
                cols = st.columns(3)
                cols[0].metric("1ª Parcela", formatar_moeda(resultado['valor_primeira_parc']))
                cols[1].metric("Última Parcela", formatar_moeda(resultado['valor_ultima_parc']))
                cols[2].metric("Total Pago", formatar_moeda(resultado['total_pago']))
                
                cols = st.columns(3)
                cols[0].metric("Total de Juros", formatar_moeda(resultado['total_juros']))
            
            # Tabela de parcelas
            st.subheader("Detalhamento das Parcelas")
            df = pd.DataFrame(resultado['parcelas'])
            st.dataframe(
                df.style.format({
                    'Prestação': lambda x: formatar_moeda(x),
                    'Juros': lambda x: formatar_moeda(x),
                    'Amortização': lambda x: formatar_moeda(x),
                    'Saldo Devedor': lambda x: formatar_moeda(x)
                }),
                hide_index=True,
                use_container_width=True
            )
            
            # Gráficos
            mostrar_evolucao_financiamento(df, sistema_nome)
                    
        except Exception as e:
            st.error(f"Erro ao calcular financiamento: {str(e)}")

with tab2:
    st.header("Comparativo Price vs SAC")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        valor_comp = st.number_input("Valor a Financiar (R$):", min_value=0.0, step=1000.0, value=100000.0, key="valor_comp")
    with col2:
        taxa_comp = st.number_input("Taxa de Juros (% ao mês):", min_value=0.0, step=0.1, value=1.5, key="taxa_comp")
    with col3:
        prazo_comp = st.number_input("Prazo (em meses):", min_value=1, step=1, value=36, key="prazo_comp")
    
    if st.button("Comparar Sistemas", key="comparar"):
        try:
            resultado_price = calcular_price(valor_comp, taxa_comp, prazo_comp)
            resultado_sac = calcular_sac(valor_comp, taxa_comp, prazo_comp)
            
            diff_juros = resultado_price['total_juros'] - resultado_sac['total_juros']
            percentual_diff = round(diff_juros / resultado_sac['total_juros'] * 100, 2)
            
            # Exibir comparativo
            st.subheader("Comparativo entre Sistemas")
            
            cols = st.columns(3)
            cols[0].metric("Valor Financiado", formatar_moeda(resultado_price['valor_financiado']))
            cols[1].metric("Taxa de Juros", f"{resultado_price['taxa_juros']}% a.m.")
            cols[2].metric("Prazo", f"{resultado_price['prazo_meses']} meses")
            
            st.divider()
            
            cols = st.columns(3)
            cols[0].metric("1ª Parcela (Price)", formatar_moeda(resultado_price['valor_parcela']))
            cols[1].metric("1ª Parcela (SAC)", formatar_moeda(resultado_sac['valor_primeira_parc']))
            cols[2].metric("Diferença", formatar_moeda(resultado_price['valor_parcela'] - resultado_sac['valor_primeira_parc']))
            
            cols = st.columns(3)
            cols[0].metric("Última Parcela (Price)", formatar_moeda(resultado_price['valor_parcela']))
            cols[1].metric("Última Parcela (SAC)", formatar_moeda(resultado_sac['valor_ultima_parc']))
            cols[2].metric("Diferença", formatar_moeda(resultado_price['valor_parcela'] - resultado_sac['valor_ultima_parc']))
            
            cols = st.columns(3)
            cols[0].metric("Total Pago (Price)", formatar_moeda(resultado_price['total_pago']))
            cols[1].metric("Total Pago (SAC)", formatar_moeda(resultado_sac['total_pago']))
            cols[2].metric("Diferença", formatar_moeda(resultado_price['total_pago'] - resultado_sac['total_pago']))
            
            cols = st.columns(3)
            cols[0].metric("Total Juros (Price)", formatar_moeda(resultado_price['total_juros']))
            cols[1].metric("Total Juros (SAC)", formatar_moeda(resultado_sac['total_juros']))
            cols[2].metric("Diferença", f"{formatar_moeda(diff_juros)} ({percentual_diff}%)")
            
            # Gráficos comparativos
            df_price = pd.DataFrame(resultado_price['parcelas'])
            df_sac = pd.DataFrame(resultado_sac['parcelas'])
            mostrar_comparativo_sistemas(df_price, df_sac)
            
            # Análise
            st.subheader("Análise")
            st.write("""
            - **Sistema Price**: Parcelas fixas (facilita planejamento)
            - **Sistema SAC**: Parcelas decrescentes (menos juros no longo prazo)
            """)
            st.success(f"Economia de juros com SAC: {percentual_diff}%")
            st.info("Escolha depende da sua capacidade de pagamento inicial")
            
        except Exception as e:
            st.error(f"Erro ao comparar sistemas: {str(e)}")

with tab3:
    st.header("Comparativo com Investimentos")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        valor_invest = st.number_input("Valor Disponível (R$):", min_value=0.0, step=1000.0, value=100000.0, key="valor_invest")
    with col2:
        prazo_invest = st.number_input("Prazo (em meses):", min_value=1, step=1, value=36, key="prazo_invest")
    with col3:
        taxa_poupanca = st.number_input("Rendimento Poupança (% a.m.):", min_value=0.0, step=0.01, value=0.5, key="taxa_poup")
    
    col1, col2 = st.columns(2)
    with col1:
        taxa_imobiliario = st.number_input("Outra aplicação (% a.m.):", min_value=0.0, step=0.01, value=0.7, key="taxa_imob")
    
    if st.button("Simular Investimentos", key="simular"):
        try:
            res_poupanca = simular_poupanca(valor_invest, prazo_invest, taxa_poupanca)
            res_imobiliario = simular_imobiliario(valor_invest, prazo_invest, taxa_imobiliario)
            
            # Resultados
            st.subheader("Resultados dos Investimentos")
            
            cols = st.columns(2)
            with cols[0]:
                st.metric("Poupança - Valor Final", formatar_moeda(res_poupanca['valor_final']))
                st.metric("Poupança - Rendimento", formatar_moeda(res_poupanca['rendimento_total']))
                
                df_poup = pd.DataFrame(res_poupanca['historico'])
                st.line_chart(df_poup.set_index('Mês')['Valor'])
            
            with cols[1]:
                st.metric("Outra aplicação - Valor Final", formatar_moeda(res_imobiliario['valor_final']))
                st.metric("Outra aplicação - Rendimento", formatar_moeda(res_imobiliario['rendimento_total']))
                
                df_imob = pd.DataFrame(res_imobiliario['historico'])
                st.line_chart(df_imob.set_index('Mês')['Valor'])
            
            # Comparativo
            mostrar_evolucao_investimentos(df_poup, df_imob)
                
        except Exception as e:
            st.error(f"Erro ao simular investimentos: {str(e)}")

# Rodapé
st.divider()
st.caption(f"Calculadora Financeira Avançada - © {datetime.now().year}")
