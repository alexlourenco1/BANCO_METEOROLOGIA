import tok_prec_rede
import atualiza_sqlite3
import gera_banco_excel
import pendulum
import time

caminho_banco = r'J:\SEDE\Comercializadora de Energia\6. MIDDLE\29.DESENVOLVIMENTO\02.dash_meteorologia\bases'


data = pendulum.now('America/Sao_Paulo').format('DD-MM-YYYY')
#data = '18-01-2022' # para carregar datas que não sejam hoje, descomente essa linha

print('''
######################
# BAIXA DADOS DA TOK #
######################
''')
modelos_tok = ['MERGE', 'GEFSav', 'ECENSav']

for modelo in modelos_tok:
    modelo_disponivel = False

    while modelo_disponivel == False:
        arquivo = tok_prec_rede.coleta_dados_ascii_tok(modelo, data_string=data)
        try:
            df_ = tok_prec_rede.parser_dados_tok(modelo, arquivo, data_string=data)
            modelo_disponivel = True
        except:
            print(f'{modelo} não disponível. Aguardando 1 minutos antes da próxima requisição.')
            time.sleep(60)

    tok_prec_rede.sobe_previsao_no_banco(caminho_banco,df_, modelo, data_string=data)

print('''
######################################
# SOBE DADOS NO BANCO PARA O POWERBI #
######################################
''')
atualiza_sqlite3.preenche_observado(caminho_banco,data_string=data)
atualiza_sqlite3.preenche_observado_nas_previsoes(caminho_banco,data_string=data)
atualiza_sqlite3.preenche_previsoes_ECMWF(caminho_banco,data_string=data)
atualiza_sqlite3.preenche_previsoes_GEFS(caminho_banco,data_string=data)

print('>>>>>>>>>> ROTINA FINALIZADA')


print('''
##########################################
# GERA BANCO EM EXCEL PARA PBI PUBLICADO #
##########################################
''')

gera_banco_excel.main(hoje=True)