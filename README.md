# SAGE TreeView
Aplicativo feito para acessar a base de dados do SAGE usando python

## Versão Atual
1.0

### Python 3.7.8

## Bibliotecas Externas
Psycopg2 - https://www.psycopg.org/

Pandas - https://pandas.pydata.org/

PyQt5 - https://www.riverbankcomputing.com/

sshtunnel - https://pypi.org/project/sshtunnel/

Matplotlib - https://matplotlib.org/

Qt - https://www.qt.io/

PyInstaller - https://www.pyinstaller.org/

Inno Setup - https://jrsoftware.org/isinfo.php

## Uso

1. Clique no menu Conexão que se encontra no canto superior esquerdo
2. Insira as informações da conexão SSH
    1. É possível salvar ou carregar um arquivo contendo esses dados assim como testar a conexão
3. Selecione a entidade que cuja informação é de interesse no visualizador
4. Visualize as informações na área de abas
5. Nas abas Alarmes, Consulta e Filme pode-se escolher um número de atributos e, ao clicar no botão consultar, observar os dados em questão em forma de tabela
    1. O intervalo de busca fica logo abaixo das abas
    2. Para Consulta e Filme, existe a opção de fazer um gráfico no menu Gráfico. Nesse caso se deve especificar os valores antes de abrir o menu de opções
    3. É possível salvar salvar tanto a tabela quanto o gráfico

