@echo OFF
rem Este pacote executável do windows permite executar um script python a partir de um ambiente conda

rem Ativa o ambiente conda 
call C:\ProgramData\Miniconda3\Scripts\activate.bat C:/Users/Middle/.conda/envs/banco_meteorologia
rem Executa o script com a partir do ambiente conda que foi ativado
call python main.py

rem Dá 10 segundos, para uma breve leitura, e fecha a aba.
timeout 10