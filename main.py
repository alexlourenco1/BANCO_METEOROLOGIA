import pendulum
import time
from src import tok_prec_rede
from src import atualiza_sqlite3
from src import gera_banco_excel
from src import config

caminho_banco = config.caminho_bancodedados

# Abre para o usuário um campo para inserir a data
data_input = input("Digite a data requisitada no formato [DD-MM-YYYY] ou pressione Enter para data atual: ")

data = pendulum.now('America/Sao_Paulo').format('DD-MM-YYYY') if data_input == "" else data_input
# data necessária para coleta do dado mais recente realizado 12ZONTEM a 12ZHOJE 
data_seguinte_tok = pendulum.from_format(data,'DD-MM-YYYY').add(days=1).format('DD-MM-YYYY')

# para carregar datas que não sejam hoje direto no código, descomente as linhas abaixo
#data = '18-01-2022' 
#data_seguinte_tok ='19-01-2022'

print('''
######################
# BAIXA DADOS DA TOK #
######################
''')
modelos_tok = ['MERGE', 'MERGE-TOK10', 'GEFSav', 'ECENSav', 'CFS45av']

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

tok_prec_rede.deleta_pastas(path=f'{config.caminho_base}/output')

print('''
######################################
# SOBE DADOS NO BANCO PARA O POWERBI #
######################################
''')
atualiza_sqlite3.preenche_observado(caminho_banco,data_string=data)
atualiza_sqlite3.preenche_observado(caminho_banco,data_string=data_seguinte_tok)
atualiza_sqlite3.preenche_observado_nas_previsoes(caminho_banco,data_string=data)
atualiza_sqlite3.preenche_observado_nas_previsoes(caminho_banco,data_string=data_seguinte_tok)
atualiza_sqlite3.preenche_previsoes_ECMWF(caminho_banco,data_string=data)
atualiza_sqlite3.preenche_previsoes_GEFS(caminho_banco,data_string=data)
atualiza_sqlite3.preenche_previsoes_CFS(caminho_banco=caminho_banco, data_string=data)

print('>>>>>>>>>> ROTINA FINALIZADA')


print('''
##########################################
# GERA BANCO EM EXCEL PARA PBI PUBLICADO #
##########################################
''')

gera_banco_excel.main(hoje=True)