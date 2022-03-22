# BANCO_METEOROLOGIA

![texto](https://img.shields.io/static/v1?label=linguagem&message=python&color=green&style=flat-square "linguagem")
![texto](https://img.shields.io/static/v1?label=ambiente&message=conda&color=orange&style=flat-square "ambiente")
![texto](https://img.shields.io/badge/status-operacional-success.svg "status")
![texto](https://img.shields.io/badge/plataforma-win--64-lightgrey "status")



1. [Descrição do projeto](#descrição-do-projeto)  
2. [Funcionalidades](#funcionalidades)   
4. [Pré-requisitos](#pré-requisitos)  
5. [Como instalar](#como-instalar)
6. [Execução](#execucao)
7. [Desenvolvimento](#desenvolvimento)
8. [Como rodar](#como-rodar)
9. [I/O](#I/O)


## :scroll: Descrição do projeto

Rotina de coleta de dados na tempook e armazenamento no formato banco de dados.

É coletado os dados de chuva observada(MERGE), chuva prevista dos modelos ECMWF e GEFS por bacia. Em seguida é armazenado nos arquivos chuva_observada.db e chuva_prevista.db de forma não-relacional(parecido com uma base de dados mongodb) que é a mais econômica em termos de espaço, em seguida é armazenado em "forma relacional" no arquivo banco_de_dados_meteorologia.db (parecido com SQLServer) que é mais amigável ao PowerBI e, por fim, é recortado 1 ano de dados da base relacional (20/12/ano_anterior até hoje) para um arquivo excel no Onedrive, mais amigável para dashboards do PowerBI publicados


## :sparkles: Funcionalidades

:wrench: Baixa dados da API TempoOK todo dia às 7h30 da manhã  
:wrench: Salva os dados na rede (nos formatos não-relacional, sql e excel)    

## :warning: Pré-requisitos

- [Python + conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) (obrigatório)


## :cd: Como instalar

```bash
# 1. no terminal, clone o projeto
git clone https://github.com/ENEVA-MIDDLE/BANCO_METEOROLOGIA.git

# 2. entre na pasta do projeto
cd BANCO_METEOROLOGIA

# 3. instale/reproduza o ambiente
conda env create -f env.yaml

# 4. crie um arquivo ".env" salvando o token da TOK. Crie um .env na pasta raiz com o seguinte conteúdo
TOKEN_TOK="abc123 seu TOKEN aleatório vai aqui abc123"
```

## :arrow_forward: Execução

:fast_forward: Para colocar no agendador do windows ou rodar o dia atual (horário de Brasília): execute (duplo clique) o arquivo "executa_main.bat".    

:fast_forward: Para executar/carregar datas anteriores: execute (duplo clique) o arquivo "executa_data_especifica.bat" e digite a data de interesse.  


## :construction: Desenvolvimento

:dart: Apagar pastas com txt's da TempoOK : Rotina de exclusão de arquivos desnecessários    

:dart: Adaptar caminhos: Arquivo .db é salvo em middle/29.DESENVOLVIMENTO... e o excel no onedrive. Deve-se padronizar estes caminhos na rede.

## :rotating_light: Como rodar

### Para executar a rotina (para o dia atual), execute (duplo clique) o arquivo "executa_main.bat"


## :green_apple: I/O

Os Inputs/entradas ficam armazenados em ```outuput```.   
Os outputs/saídas vão para ```middle/29.DESENVOLVIMENTO/02.dash_meteorologia/bases```.

