# SAGE TreeView
Aplicativo feito para acessar a base de dados do SAGE usando python

## Versão Atual
1.0

Instalador: https://drive.google.com/file/d/1s0VpAiJ7qoTcU7krgnQVZ2SRQAAiYTPj/view?usp=sharing

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

    ![Passo 1](https://user-images.githubusercontent.com/69806937/138185330-0313edc6-7485-40af-8199-bfad2db50c93.png)
    
2. Insira as informações da conexão SSH
    1. É possível salvar ou carregar um arquivo contendo esses dados assim como testar a conexão
    
        ![passo_2](https://user-images.githubusercontent.com/69806937/138185434-ef4e42c2-bb43-4c2a-95be-1af2e685b4ea.png)
    
    
3. Selecione a entidade que cuja informação é de interesse no visualizador

    ![passo_3](https://user-images.githubusercontent.com/69806937/138185447-3f2484ae-faac-4b53-bc88-1d12fcbf4733.png)
    
4. Visualize as informações na área de abas

    ![passo_4](https://user-images.githubusercontent.com/69806937/138185451-fa5c5229-9d93-4649-aa2c-75d5f4b7418c.png)

5. Nas abas Alarmes, Consulta e Filme pode-se escolher um número de atributos e, ao clicar no botão consultar, observar os dados em questão em forma de tabela

    ![passo_5](https://user-images.githubusercontent.com/69806937/138185453-77744e1c-830e-4154-9c6c-54f1e1f890e7.png)

    1. O intervalo de busca fica logo abaixo das abas

    2. Para Consulta e Filme, existe a opção de fazer um gráfico no menu Gráfico. Nesse caso se deve especificar os valores antes de abrir o menu de opções
        
        ![passo_5_2](https://user-images.githubusercontent.com/69806937/138185456-58e1a837-7fab-497d-b5c6-6bc7fe312ff7.png)
        ![passo_5_2_2](https://user-images.githubusercontent.com/69806937/138185459-e635487d-bc12-4176-915a-42e449f7520f.png)
        
        ![passo_5_2_3](https://user-images.githubusercontent.com/69806937/138185460-467a96e6-9dc8-49d4-b836-b255dd837b33.png)

    3. É possível salvar tanto a tabela quanto o gráfico, além de alterar as opções visuais do gráfico

        ![passo_5_3](https://user-images.githubusercontent.com/69806937/138185461-ab75b469-59a7-4587-9082-e287d92505fa.png)
