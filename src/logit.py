'''
ARQUIVO RESPONSÁVEL POR SALVAR (TXT) E PRINTAR DADOS DE EXECUÇÃO NO CONSOLE

ARQUIVO DE LOG FICA SALVO NA REDE ENEVA EM ...\6. MIDDLE\20.SCRIPTS\00.Arquivos de LOG
'''

import logging
import pendulum
from pathlib import Path
import sys
from src import config

hoje = pendulum.now('America/Sao_Paulo')
saida_log = Path(f'{config.caminho_logs}', hoje.format('YYYY'))
saida_log.mkdir(exist_ok=True, parents=True)

arquivo_mensal_de_log = f'BD_meteorologia_{pendulum.now("America/Sao_Paulo").format("YYYY-MM")}.log'

#################################
# REGISTRANDO CONTEÚDO EM LOG's #
#################################
log = logging.getLogger(__name__)

logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s : %(name)s  : %(funcName)s : %(levelname)s : %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p',
                    handlers=[
                        logging.FileHandler(f'{saida_log}/{arquivo_mensal_de_log}'),
                        logging.StreamHandler(sys.stdout)
                            ]
                    )

log.info(f'\n\n\n\n\n{config.ambiente} - {hoje.format("DD-MM-YYYY")}')
