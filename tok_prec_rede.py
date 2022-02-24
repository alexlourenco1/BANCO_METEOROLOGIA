""" 
ROTINA RESPONSÁVEL POR COLETAR OS DADOS DA API TEMPOOK
"""

import pendulum
import requests
from pathlib import Path
import os
from dotenv import load_dotenv
import pandas as pd
import shelve
import time


##########################
# DEFINIÇÃO DE VARIÁVEIS #
##########################
load_dotenv()
token = os.getenv('TOKEN_TOK')
data = pendulum.now('America/Sao_Paulo')


caminho_base = 'C:/scripts/BANCO_METEOROLOGIA/'
caminho_bancodedados = r'J:\SEDE\Comercializadora de Energia\6. MIDDLE\29.DESENVOLVIMENTO\02.dash_meteorologia\bases'
diretorio_saida = Path(f'{caminho_base}/output/diario', data.format('YYYY'), data.format('MM'), data.format('DD'))
diretorio_saida.mkdir(exist_ok=True, parents=True)

def coleta_dados_ascii_tok(modelo:str,data_string:str=None, hoje:bool=False) -> str:
    """Coleta dados txt do repositório da TempoOK

    Args:
        modelo (str): Nome do modelo no padrão da plataforma TEMPOOK
        data_string (str, optional): [DD-MM-YYYY] Data a ser requisitada. Defaults to None.
        hoje (bool, optional): Habilita o uso da data atual no fuso de São Paulo. Defaults to False.

    Returns:
        str: Nome do arquivo baixado
    """

    data = pendulum.today('America/Sao_Paulo') if hoje else pendulum.from_format(data_string, 'DD-MM-YYYY')

    data_requisitada = data.subtract(days=1) if modelo == 'MERGE' else data
    path = f'Comercializadora/Arquivos/bacia_ascii/{modelo}/{data_requisitada.format("YYYY-MM")}'
    arquivo = f'{modelo}_{data_requisitada.format("YYYYMMDD")}T00.dat'
    url = 'https://storage.tempook.com/tokstorage/download_post/'

    ###################
    # COLETA DE DADOS #
    ###################
    # t=token
    # p=path
    dados_para_requisicao = {'t':token, 'p': path+'/'+arquivo}

    requisicao = requests.post(url=url, data=dados_para_requisicao, allow_redirects=True)
    # salvando dados
    arquivo_local = open(f'{diretorio_saida}/TOK-{arquivo}', 'wb')
    arquivo_local.write(requisicao.content)
    arquivo_local.close()

    return arquivo


def parser_dados_tok(modelo:str, arquivo:str, data_string:str=None, hoje:bool=False) -> pd.DataFrame:
    """Leitura dos dados em txt, coleta das bacias de interesse e reformulação para tabela.

    Args:
        modelo (str): Nome do modelo no padrão da plataforma TEMPOOK.
        arquivo (str): nome do arquivo txt baixado.
        data_string (str, optional): [DD-MM-YYYY] Data a ser requisitada. Defaults to None.
        hoje (bool, optional): Habilita o uso da data atual no fuso de São Paulo. Defaults to False.

    Returns:
        pd.DataFrame: Dados tratados no formato de tabela.
    """

    data = pendulum.today('America/Sao_Paulo') if hoje else pendulum.from_format(data_string, 'DD-MM-YYYY')
    ###################
    # PARSEANDO DADOS #
    ###################

    # dict resposável por organizar e selcionar as bacias utilizadas
    coleta_bacias_tok = {22:'alto_grande',
    20:'alto_parana',
    25:'alto_paranaiba',
    16:'alto_sao_francisco',
    23:'baixo_grande',
    19:'baixo_parana',
    24:'baixo_paranaiba',
    17:'baixo_sao_francisco',
    2:'iguacu',
    3:'jacui',
    27:'leste_tocantins',
    26:'madeira',
    18:'medio_sao_francisco',
    34:'oeste_tocantins',
    5:'paranapanema',
    21:'serra_da_mesa_tocantins',
    8:'tiete',
    10:'uruguai',
    28:'xingu'}
    lista = list(coleta_bacias_tok.keys())
    lista_bacias = list(coleta_bacias_tok.values())

    prec = f'{diretorio_saida}/TOK-{arquivo}'
    colunas_do_previsto = ['basin', 'd0','d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10','d11', 'd12', 'd13']
    colunas_do_observado = ['basin', 'd0']
    colunas_usadas = colunas_do_observado if modelo in ['MERGE','MERGE-TOK10'] else colunas_do_previsto
    df = pd.read_csv(prec, index_col='basin',usecols=colunas_usadas)

    #seleciona as bacias utilizadas
    df_ = df.loc[lista]
    # nomeia as bacias
    df_.index = lista_bacias

    if modelo not in ['MERGE', 'MERGE-TOK10']:
        horizonte_previsao = []
        for dia in range(0,14):
            
            dia_horizonte = data.add(days=dia).format('DD-MM-YYYY')
            horizonte_previsao.append(dia_horizonte)

        #adiciona colunas com datas
        df_.columns = horizonte_previsao
    return df_

###########################
# SALVANDO DADOS NO BANCO #
###########################

def sobe_previsao_no_banco(caminho_bancodedados:str,df_final:pd.DataFrame, modelo:str, data_string:str=None, hoje:bool=False) -> str:
    """ Carrega dados em mini-banco não relacional.

    Args:
        caminho_bancodedados (str): localização do arquivo-banco
        df_final (pd.DataFrame): Tabela parseada/tratada
        modelo (str): nome do modelo no padrão TEMPOOK
        data_string (str, optional): [DD-MM-YYYY] Data a ser requisitada. Defaults to None.
        hoje (bool, optional): Habilita o uso da data atual no fuso de São Paulo. Defaults to False.

    Returns:
        str: mensagem de sucesso
    """

    data = pendulum.today('America/Sao_Paulo') if hoje else pendulum.from_format(data_string, 'DD-MM-YYYY')
    data_anterior = data.subtract(days=1)


    txt_json = df_final.reset_index().to_json(orient='records')
    data_requisitada = data_anterior if modelo == 'MERGE' else data

    if modelo in ['MERGE', 'MERGE-TOK10']:
        bd = shelve.open(f'{caminho_bancodedados}/chuva_observada.db')
        bd[data_requisitada.format('DD-MM-YYYY')] = txt_json
        bd.close()
        print('Dados salvos no banco')
    
    else:
        bd = shelve.open(f'{caminho_bancodedados}/chuva_prevista.db')
        bd[f'tok_{modelo}_{data_string}'] = txt_json
        bd.close()

    
    
    return print(f"Dados do tok_{modelo}_{data_requisitada.format('DD-MM-YYYY')} carregados no banco")

if __name__ == '__main__':
    import pendulum

    caminho_banco = r'J:\SEDE\Comercializadora de Energia\6. MIDDLE\29.DESENVOLVIMENTO\02.dash_meteorologia\bases'

    data = pendulum.now('America/Sao_Paulo').format('DD-MM-YYYY')
    #data = '19-01-2022'

    #modelos_tok = ['MERGE','MERGE-TOK10', 'GEFSav', 'ECENSav']
    modelos_tok = ['MERGE-TOK10']

    for modelo in modelos_tok:
        
        modelo_disponivel = False

        while modelo_disponivel == False:
            arquivo = coleta_dados_ascii_tok(modelo, data_string=data)
            try:
                df_ = parser_dados_tok(modelo, arquivo, data_string=data)
                modelo_disponivel = True
            except:
                print(f'{modelo} não disponível. Aguardando 1 minutos antes da próxima requisição.')
                time.sleep(60)

        sobe_previsao_no_banco(caminho_bancodedados=caminho_banco,df_final=df_, modelo=modelo, data_string=data)
