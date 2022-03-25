"""Arquivo de configurações do projeto
"""
######################################
# CAMINHOS PARA AMBIENTE DE PRODUÇÃO #
######################################

#caminho_base = 'C:/scripts/BANCO_METEOROLOGIA/'
#caminho_env = f'{caminho_base}/src'
#caminho_bancodedados = r'J:\SEDE\Comercializadora de Energia\6. MIDDLE\03.PLANILHAS\BASES_DASH_METEOROLOGIA'
#caminho_saida_excel = r'C:\Users\Middle\OneDrive - Eneva S.A\5.Meteorologia_dados'


###################################
# CAMINHOS PARA AMBIENTE DE TESTE #
###################################
"""INSTRUÇÕES:

1. Faça uma cópia das database do ambiente de produção para as pastas "backup" e "ambiente_de_desenvolvimento"
2. Comente o bloco dos caminhos de produção e descomente o bloco do ambiente de teste
3. Após o período de testes, faça as cópias, respectivamente:
    db produção -> backup
    db desenvolvimento -> produção
"""
caminho_base = 'C:/scripts/BANCO_METEOROLOGIA/'
caminho_env = f'{caminho_base}/src'
caminho_bancodedados=r'J:\SEDE\Comercializadora de Energia\6. MIDDLE\03.PLANILHAS\BASES_DASH_METEOROLOGIA\ambiente_de_desenvolvimento'
caminho_saida_excel = r'J:\SEDE\Comercializadora de Energia\6. MIDDLE\03.PLANILHAS\BASES_DASH_METEOROLOGIA\ambiente_de_desenvolvimento'