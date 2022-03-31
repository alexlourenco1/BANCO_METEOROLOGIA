"""
Vai ao banco de dados SQLite3, iterando em todas as tabelas
Recorta dados de 20/12/ano_anterior até (hoje ou data_requisitada)
gera base em excel
"""

import sqlite3
from typing import Any
import pandas as pd
import pendulum
from src import config
from src.logit import log

caminho_bd = config.caminho_bancodedados
#caminho_bd = r'C:\scripts\BOLETIM-ENEVA\mapas'
banco = 'banco_de_dados_meteorologia.db'
caminho_saida_excel = config.caminho_saida_excel


def retorna_datas(data_requerida:pendulum.datetime) -> dict:
    """Retorna dicionario com data de início 20 de dezembro do ano anterior e final o dia atual

    Args:
        data_requerida (pendulum.datetime): data base para criar o período

    Returns:
        dict: dicionario['data'] = (pendulum.datetime) data_requerida
              dicionario['data_anterior'] = (pendulum.datetime) data_anterior
              dicionario['data_inicio'] = (pendulum.datetime) data_inicio
    """
    dicionario = {}
    
    data_anterior = data_requerida.subtract(days=1)

    ano_anterior = data_requerida.subtract(years=1)
    data_inicio = pendulum.from_format(f'20-12-{ano_anterior.format("YYYY")}', 'DD-MM-YYYY')
    
    dicionario['data'] = data_requerida
    dicionario['data_anterior'] = data_anterior
    dicionario['data_inicio'] = data_inicio
    
    return dicionario 

def seleciona_dados(tabela:str, data_inic:str, data_final:str, conn:sqlite3.Connection) -> pd.DataFrame:
    """Trata e recorta os dados da base de dados para salvar em arquivo excel.
    É recortado do dia 20/12 do ano anterior até o dia atual.

    Args:
        tabela (str): nome da tabela do banco a ser trabalhada
        data_inic (str): (DD-MM-YYYY) data inicial do recorte
        data_final (str): (DD-MM-YYYY) data final do recorte
        conn (sqlite3.Connection): conexão com arquivo .db

    Returns:
        pd.DataFrame: Dataframe tratado e recortado
    """
    df = pd.read_sql(f'select * from {tabela}', conn)
    
    index = 'data' if tabela=='CHUVA_OBSERVADA' else 'data_rodada'
    
    # Tratamento de datas na base de dados
    df_com_index = df.set_index(index) # seleciono data como índice
    df_com_index.index = pd.to_datetime(df_com_index.index, format='%d-%m-%Y') # transformo o índice de string para datetime
    df_com_index_datetime_ordenado = df_com_index.sort_values(index) # ordeno pela data
    df_com_index_datetime_ordenado.index = df_com_index_datetime_ordenado.index.strftime('%d-%m-%Y') # retorna para string no formato brasileiro de data (dia-mes-ano)
    
    dado_selecionado = df_com_index_datetime_ordenado[data_inic:data_final]
    
    return dado_selecionado

def main(hoje:bool=False, data_string:str=None) -> None:
    """Função Principal.

    Vai até

    Args:
        hoje (bool, optional): True para usar a data atual. Defaults to False.
        data_string (str, optional): Use para datas diferentes da de hoje (DD-MM-YYYY). Defaults to None.

    Returns:
        [type]: mensagem de sucesso.
    """
    
    data_requerida = pendulum.now('America/Sao_Paulo') if hoje else pendulum.from_format(data_string, 'DD-MM-YYYY')
    datas = retorna_datas(data_requerida)

    # Conecta ao banco
    conn = sqlite3.connect(f'{caminho_bd}/{banco}')
    cursor = conn.cursor()
    
    # Lista as tabelas
    cursor.execute('SELECT name from sqlite_master where type= "table"')
    tabelas = cursor.fetchall()
    
    # Prepara um excel para salvar os dados
    excel = pd.ExcelWriter(f'{caminho_saida_excel}/banco_de_dados_meteorologia.xlsx', engine='xlsxwriter')
    
    for tabela in tabelas:
        log.info(f' Gerando {tabela[0]}')
        
        if tabela[0]=='CHUVA_DIARIA_CLIMA':
            
            df = pd.read_sql('select * from CHUVA_DIARIA_CLIMA', conn).set_index('data')
            df.to_excel(excel, sheet_name=tabela[0])
            
        else:
            # Pega o range das datas que serão salvas no excel
            data_inic = datas['data_inicio'].format('DD-MM-YYYY')
            data_final_requerida = datas['data'].format('DD-MM-YYYY')
            data_final = pendulum.now('America/Sao_Paulo').format('DD-MM-YYYY')

            try:
                # Pega da data inicial até hoje | funciona no operacional automatizado diário
                # objetivo: Para ocasiões de preenchimento de dados de dias faltantes
                # Trativa: Não trazer na base até somente o dia recarregado. 
                df = seleciona_dados(tabela[0], data_inic, data_final, conn)
                df.to_excel(excel, sheet_name=tabela[0])
            except:
                # Pega a data inicial até a data requisitada | funciona no operacional automatizado diário
                # objetivo: Para preencher ultimas datas, caso o processo tenha parado
                # Tratativa: Caso não tenha todos os últimos dias, não retornar erro ao tentar recortar do inicio até "hoje"
                df = seleciona_dados(tabela[0], data_inic, data_final_requerida, conn)
                df.to_excel(excel, sheet_name=tabela[0])
    
    conn.commit()
    cursor.close()
    excel.save()
    
    return log.info(f'>>>>>> Base em excel banco_de_dados_meteorologia_{data_requerida.format("YYYY")}.xlsx para power bi gerado !')

if __name__ == '__main__':

    main(hoje=True)