""" 
ATUALIZA SQLITE3 (MINI BANCO DE DADOS RELACIONAL) PARA COMPATIBILIZAÇÃO COM POWER BI
"""

import sqlite3
import shelve
import pandas as pd
import pendulum
import config

####################
# DADOS DE ENTRADA #
####################
caminho_banco = config.caminho_bancodedados

# tabelas apenas de modelos de previsão para uso na função preenche_observado_nas_previsoes()
tabelas = ['GEFS_BACIA', 'ECMWF_BACIA']

depara_bacia_subsistema = {'alto_grande': 'sudeste',
 'alto_parana': 'sudeste',
 'alto_paranaiba': 'sudeste',
 'alto_sao_francisco': 'sudeste',
 'baixo_grande': 'sudeste',
 'baixo_parana': 'sudeste',
 'baixo_paranaiba': 'sudeste',
 'baixo_sao_francisco': 'nordeste',
 'iguacu': 'sul',
 'jacui': 'sul',
 'leste_tocantins': 'norte',
 'madeira': 'sudeste',
 'medio_sao_francisco': 'nordeste',
 'oeste_tocantins': 'norte',
 'paranapanema': 'sudeste',
 'serra_da_mesa_tocantins': 'sudeste',
 'tiete': 'sudeste',
 'uruguai': 'sul',
 'xingu': 'norte'}

################################################
# CARREGA DADOS BAIXADOS NO BANCO "RELACIONAL" #
################################################
def preenche_observado(caminho_banco:str, data_string:str=None, hoje:bool=False) -> str:
    """Preenche os dados observado no .db com base no arquivo chuva_observada.db.dat

    Args:
        caminho_banco (str): caminho até a pasta raiz do banco de dados
        data_string (str, optional): data requerida no formato (DD-MM-YYYY). Defaults to None.
        hoje (bool, optional): True para habilitar a data atual. Defaults to False.

    Returns:
        str: mensagem de sucesso
    """
    data_requerida = pendulum.today('America/Sao_Paulo') if hoje else pendulum.from_format(data_string, 'DD-MM-YYYY')
    observado_string = data_requerida.subtract(days=1).format('DD-MM-YYYY')

    conexao=sqlite3.connect(f'{caminho_banco}/banco_de_dados_meteorologia.db')
    c = conexao.cursor()
    bd = shelve.open(f'{caminho_banco}/chuva_observada.db')

    df_clima = pd.read_sql('select * from CHUVA_DIARIA_CLIMA', conexao)
    df_clima = df_clima.set_index('data')

    clima_diario = df_clima.loc[observado_string[:5]]
    clima_diario = clima_diario.set_index('bacia')
    ds = pd.read_json(bd[observado_string], orient='records').set_index('index')

    for valor, bacia in zip(ds['d0'].values, list(ds.index)):

        clima_diario_bacia = clima_diario["precipitacao"][bacia]
        anomalia = valor - clima_diario_bacia

        c.execute(f""" INSERT OR REPLACE INTO CHUVA_OBSERVADA (data, bacia, subsistema, precipitacao, clima, anomalia, fonte)
        VALUES ('{observado_string}', '{bacia}', '{depara_bacia_subsistema[bacia]}', {valor}, {clima_diario_bacia}, {anomalia}, 'tok-merge')
        """)

    conexao.commit()
    c.close()
    bd.close()

    return print('Dados de chuva observada preenchidos na tabela CHUVA_OBSERVADA')


# PREENCHE OBSERVADO NO GEFS E EC
def preenche_observado_nas_previsoes(caminho_banco:str, data_string:str=None, hoje:bool=False) -> str:
    """Inclui nas tabelas de previsões APENAS os dados observados.

    Args:
        caminho_banco (str): caminho até a pasta raiz do banco de dados
        data_string (str, optional): data requerida no formato (DD-MM-YYYY). Defaults to None.
        hoje (bool, optional): True para habilitar a data atual. Defaults to False.

    Returns:
        str: mensagem de sucesso
    """
    
    data_requerida = pendulum.today('America/Sao_Paulo') if hoje else pendulum.from_format(data_string, 'DD-MM-YYYY')
    observado_string = data_requerida.subtract(days=1).format('DD-MM-YYYY')

    conexao=sqlite3.connect(f'{caminho_banco}/banco_de_dados_meteorologia.db')
    c = conexao.cursor()

    df_observado = pd.read_sql('select * from CHUVA_OBSERVADA', conexao)
    df_observado_data_filtrada = df_observado.set_index('data').loc[observado_string]
    df_observado_filtrado = df_observado_data_filtrada.set_index('bacia')#.loc['alto_grande']

    for tabela in tabelas:
        df = pd.read_sql(f'select * from {tabela}', conexao)
        df_filtrado = df.set_index('data_previsao').loc[observado_string] #filtra todas as PREVISÕES para o dia do realizado

        for loop_linhas in range(0,len(df_filtrado)):

            data_rodada = df_filtrado.iloc[loop_linhas][0]
            bacia = df_filtrado.iloc[loop_linhas][1]
            subsistema = df_filtrado.iloc[loop_linhas][2]
            precipitacao = df_filtrado.iloc[loop_linhas][3]
            clima = df_filtrado.iloc[loop_linhas][4]
            observado = df_observado_filtrado.loc[bacia]['precipitacao'] #depende da variavel "bacia" acima
            anomalia_clima = df_filtrado.iloc[loop_linhas][6]
            anomalia_realizado = observado - precipitacao #depende do observado acima e da precipitação(previsão)
            fonte = df_filtrado.iloc[loop_linhas][8]

            c.execute(f""" INSERT OR REPLACE INTO {tabela} (data_rodada, data_previsao, bacia, subsistema, precipitacao, clima,
                observado, anomalia_clima, anomalia_realizado, fonte)
            VALUES ('{data_rodada}', '{observado_string}', '{bacia}', '{subsistema}', {precipitacao},
            {clima}, {observado}, {anomalia_clima}, {anomalia_realizado}, '{fonte}') 
            """)
            
    conexao.commit()
    c.close()

    return print(f'Dados de chuva observada preenchidos nas tabelas {tabelas}')


def preenche_previsoes_ECMWF(caminho_banco:str, data_string:str=None, hoje:bool=False) -> str:
    """Preenche as previsões no arquivo .db com base no arquivo chuva_prevista.db.dat

    Args:
        caminho_banco (str): caminho até a pasta raiz do banco de dados
        data_string (str, optional): data requerida no formato (DD-MM-YYYY). Defaults to None.
        hoje (bool, optional): True para habilitar a data atual. Defaults to False.

    Returns:
        str: mensagem de sucesso.
    """
    data_requerida = pendulum.today('America/Sao_Paulo') if hoje else pendulum.from_format(data_string, 'DD-MM-YYYY')
    observado_string = data_requerida.subtract(days=1).format('DD-MM-YYYY')
    data_requerida_string = data_requerida.format('DD-MM-YYYY')

    conexao=sqlite3.connect(f'{caminho_banco}/banco_de_dados_meteorologia.db')
    c = conexao.cursor()
    bd = shelve.open(f'{caminho_banco}/chuva_observada.db')
    bd_prev = shelve.open(f'{caminho_banco}/chuva_prevista.db')
    
    # PREENCHE NOVAS PREVISÕES NO ECMWF
    registro = f'tok_ECENSav_{data_requerida_string}'
    df_prev = pd.read_json(bd_prev[registro], orient='records').set_index('index')

    df_clima = pd.read_sql('select * from CHUVA_DIARIA_CLIMA', conexao)
    df_clima = df_clima.set_index('data')
    clima_diario = df_clima.loc[observado_string[:5]]
    clima_diario = clima_diario.set_index('bacia')

    data_rodada = registro[-10:]
    separacao_string = registro.partition('_')
    fonte_modelo = separacao_string[0]

    for coluna_previsto in df_prev.columns:
        for bacia in df_prev.index:

            valor_prec = df_prev[coluna_previsto][bacia]

            clima_diario = df_clima.loc[coluna_previsto[:5]]
            clima_diario = clima_diario.set_index('bacia')
            clima_diario_bacia = clima_diario["precipitacao"][bacia]

            anomalia_clima = valor_prec - clima_diario_bacia

            try:
                ds = pd.read_json(bd[coluna_previsto], orient='records').set_index('index')
                observado = ds['d0'][bacia]
                anomalia_realizado = observado - valor_prec
            except:
                observado = 0
                anomalia_realizado = 0


            c.execute(f""" INSERT OR REPLACE INTO ECMWF_BACIA (data_rodada, data_previsao, bacia, subsistema, precipitacao, clima,
            observado, anomalia_clima, anomalia_realizado, fonte)
        VALUES ('{data_rodada}', '{coluna_previsto}', '{bacia}', '{depara_bacia_subsistema[bacia]}', {valor_prec},
        {clima_diario_bacia}, {observado}, {anomalia_clima}, {anomalia_realizado}, '{fonte_modelo}') 
        """)


    conexao.commit()
    c.close()
    bd.close()
    bd_prev.close()

    return print('Dados de chuva observada preenchidos na tabela ECMWF_BACIA')

def preenche_previsoes_GEFS(caminho_banco:str, data_string:str=None, hoje:bool=False) -> str:
    """Preenche as previsões no arquivo .db com base no arquivo chuva_prevista.db.dat

    Args:
        caminho_banco (str): caminho até a pasta raiz do banco de dados
        data_string (str, optional): data requerida no formato (DD-MM-YYYY). Defaults to None.
        hoje (bool, optional): True para habilitar a data atual. Defaults to False.

    Returns:
        str: mensagem de sucesso.
    """
    data_requerida = pendulum.today('America/Sao_Paulo') if hoje else pendulum.from_format(data_string, 'DD-MM-YYYY')
    observado_string = data_requerida.subtract(days=1).format('DD-MM-YYYY')
    data_requerida_string = data_requerida.format('DD-MM-YYYY')

    conexao=sqlite3.connect(f'{caminho_banco}/banco_de_dados_meteorologia.db')
    c = conexao.cursor()
    bd = shelve.open(f'{caminho_banco}/chuva_observada.db')
    bd_prev = shelve.open(f'{caminho_banco}/chuva_prevista.db')

    df_clima = pd.read_sql('select * from CHUVA_DIARIA_CLIMA', conexao)
    df_clima = df_clima.set_index('data')
    clima_diario = df_clima.loc[observado_string[:5]]
    clima_diario = clima_diario.set_index('bacia')

    # PREENCHE NOVAS PREVISÕES NO GEFS
    registro = f'tok_GEFSav_{data_requerida_string}'


    df_prev = pd.read_json(bd_prev[registro], orient='records').set_index('index')

    data_rodada = registro[-10:]
    separacao_string = registro.partition('_')
    fonte_modelo = separacao_string[0]

    for coluna_previsto in df_prev.columns:
        for bacia in df_prev.index:

            valor_prec = df_prev[coluna_previsto][bacia]

            clima_diario = df_clima.loc[coluna_previsto[:5]]
            clima_diario = clima_diario.set_index('bacia')
            clima_diario_bacia = clima_diario["precipitacao"][bacia]

            anomalia_clima = valor_prec - clima_diario_bacia

            try:
                ds = pd.read_json(bd[coluna_previsto], orient='records').set_index('index')
                observado = ds['d0'][bacia]
                anomalia_realizado = observado - valor_prec
            except:
                observado = 0
                anomalia_realizado = 0


            c.execute(f""" INSERT OR REPLACE INTO GEFS_BACIA (data_rodada, data_previsao, bacia, subsistema, precipitacao, clima,
            observado, anomalia_clima, anomalia_realizado, fonte)
        VALUES ('{data_rodada}', '{coluna_previsto}', '{bacia}', '{depara_bacia_subsistema[bacia]}', {valor_prec},
        {clima_diario_bacia}, {observado}, {anomalia_clima}, {anomalia_realizado}, '{fonte_modelo}') 
        """)
            
    conexao.commit()
    c.close()
    bd.close()
    bd_prev.close()

    return print('Dados de chuva observada preenchidos na tabela GEFS_BACIA')


if __name__ == "__main__":

    import pendulum
    import config

    caminho_banco = config.caminho_bancodedados

    data = pendulum.now('America/Sao_Paulo').format('DD-MM-YYYY')
    #data = '19-01-2022'
    # data necessária para coleta do dado mais recente realizado 12ZONTEM a 12ZHOJE 
    data_seguinte_tok = pendulum.now('America/Sao_Paulo').add(days=1).format('DD-MM-YYYY')
    

    preenche_observado(caminho_banco=caminho_banco,data_string=data)
    preenche_observado(caminho_banco=caminho_banco,data_string=data_seguinte_tok)
    preenche_observado_nas_previsoes(caminho_banco=caminho_banco, data_string=data)
    preenche_observado_nas_previsoes(caminho_banco=caminho_banco, data_string=data_seguinte_tok)
    preenche_previsoes_ECMWF(caminho_banco=caminho_banco, data_string=data)
    preenche_previsoes_GEFS(caminho_banco=caminho_banco, data_string=data)


