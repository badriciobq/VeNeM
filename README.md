VeNeM
===========

Uma das maiores dificuldades para simular uma rede veicular, é garantir
que a simulação respeite os padrões de mobilidade de um ambiente real.
Os simuladores existentes que possibilitam desenvolvermos aplicações com
padrões de mobilidade semelhantes aos padrões reais, geralmente são muito
complexos de serem utilizados. A dificuldade em utilizar estes simuladores
motivaram a criação deste software, que permite ao usuário criar padrões
de mobilidade seguindo os parâmetros recebidos pela API de Mapas do Google,
ou ainda, recebendo um arquivo de trace, que pode ser gerado através da 
aplicação android disponibilizada no diretório tools. 


Autor
------------------------------------------------------------------------
Maurício José da Silva

badriciobq [at] gmail [dot] com


Requisitos
------------------------------------------------------------------------
Para satisfazer os requisitos necessário para a execução da aplicação você 
pode utilizar o arquivo requirements.txt disponibilizado no respositório. 
Para isto basta digitar no terminal o seguinte comando

    $ sudo pip install -r requeriments.txt


Forma de usar
-------------------------------------------------------------------------

O programa foi feito para ser utilizado via linha de comando, a sintaxe
de utilização está descrita abaixo:

---------------------------------------------------------------------------

    usage: VeNeM.py [-h] [-r ROTAS] [-o ORIGEM] [-n NOS]
                [-t [TRACES [TRACES ...]]]

    Gera os arquivo necessário para simular a mobilidade veicular em uma cidade,
    utilizando o simulador Omnetpp juntamente com o framwork MiXim.

    optional arguments:
       -h, --help            show this help message and exit
       -r ROTAS, --routes ROTAS
                        Arquivo contendo os endereços das rotas no formato:
                        from: <origem> to: <destino>
       -o ORIGEM, --origem ORIGEM
                        Diretório de origem. Onde serão salvos os arquivos.
       -n NOS, --nos NOS     Arquivo contendo o indice do nó e as rotas que o nó
                        deverá seguir separados por espaço. Ex: <nozero>
                        <tempo inicial> <rotazero> <rotaum> <rotadois> O
                        arquivo deve conter as configurações de cada nó por
                        linha, se o nó não estiver presente no arquivo a
                        rota será gerada utilizando o indíce do nó
       -t [TRACES [TRACES ...]], --traces [TRACES [TRACES ...]]
                        Lista de arquivos dos traces de GPS capturados no
                        seguinte formato:
                        <latitude>,<longitude>,<altitude>,<timestamp
                        UTC>,<velocidade em m/s>
------------------------------------------------------------------------------
