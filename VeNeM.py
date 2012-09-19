#!/usr/bin/env python
#coding: utf-8

import os
import sys
import Utils
import argparse
from threading import Thread


config = """

Para configurar sua simulação siga os seguintes passos:

Copie o arquivo: "{0}" para a raiz do seu projeto;

Configure no seu arquivo omnetpp.ini os seguinte parâmetros:
**.playgroundSizeY: {1}km
**.playgroundSizeX: {2}km
**.numNodes = {3}           # O número de nós pode ser alterado se tiver o nodeId ajustado corretamente.


**.node[*].mobilityType = "BonnMotionMobility"
**.node[*].mobility.traceFile = "{4}"
**.node[*].mobility.nodeId = -1
**.node[*].mobility.debug = false
**.node[*].mobility.updateInterval = 0.01s

"""


def boon_to_routes(arquivo, origem=os.getcwd(), nos=None):
    """
    Função para gerar o arquivo de mobilidade compatível com o mixim através
    de um arquivo contendo as rotas.  
    """
    
    lista = Utils.pegar_coordenadas_rotas(arquivo)
    
    if not lista:
        sys.stderr.write('Não existe rota para os endereços configurados.\n')
        exit(1)
    
    menorLat, maiorLat, menorLon, maiorLon = Utils.coordenadas_extremas_rotas(lista)    
    
    playgroundx, playgroundy = Utils.converte_plano_carteziano((menorLat, maiorLon),(maiorLat, menorLon))
    
    Thread(target=Utils.download_mapa, args=([(menorLat,maiorLon),(maiorLat, maiorLon),(maiorLat, menorLon),(menorLat, menorLon)], origem)).start()

    dic_nos = Utils.formata_dicionario_nos(len(lista), nos)
    
    with open('route.boon', 'w') as f:
    
        for i in xrange(len(dic_nos)):
        
            if dic_nos.has_key(i):
                inter = dic_nos.get(i)
    
            tempo_simulacao = 0
            
            for t in inter:
                t = int(t)
                            
                for r in lista[t]['rotas']:
                    time = r['Duration']['seconds']
                    longit = r['Point']['coordinates'][0]
                    latit = r['Point']['coordinates'][1]
                    
                    tempo_simulacao = time + tempo_simulacao
                    x,y = Utils.converte_plano_carteziano((menorLat, maiorLon), (latit, longit))
                    f.write('{} {} {} '.format(tempo_simulacao, x*1000, y*1000))
            
            f.write('\n')

    if origem[-1] != '/':
        origem += '/'
    
    print config.format(origem + 'route.boon', playgroundy, playgroundx, len(dic_nos), 'route.boon')



def boon_to_traces(files, origem=os.getcwd(), nos=None):
    """
    Função para gerar o arquivo de mobilidade compatível com o mixim através
    de um arquivo de traces no seguinte formato: 
    <latitude>,<longitude>,<altitude>,<timestamp UTC>,<velocidade m/s>
    """
    trac = Utils.pegar_coordenadas_traces(files)

    menorLat, maiorLat, menorLon, maiorLon = Utils.coordenadas_extremas_traces(trac)
    
    playgroundx, playgroundy = Utils.converte_plano_carteziano((menorLat, maiorLon),(maiorLat, menorLon))
    
    Thread(target=Utils.download_mapa, args=([(menorLat,maiorLon),(maiorLat, maiorLon),(maiorLat, menorLon),(menorLat, menorLon)] , origem)).start()

    dic_nos = Utils.formata_dicionario_nos(len(trac), nos)
        
    with open('traces.boon', 'w') as f:
    
        for i in xrange(len(dic_nos)):
        
            if dic_nos.has_key(i):
                inter = dic_nos.get(i)
    
            for t in inter:
                t = int(t)
                tempo_simulacao = 0
                
                for r in trac[t]:
                    time = r['tempo']
                    latit = round(float(r['latitude']), 6)
                    longit = round(float(r['longitude']), 6)
                    tempo_simulacao = time + tempo_simulacao
                
                    x,y = Utils.converte_plano_carteziano((menorLat, maiorLon), (latit, longit))
                    f.write('{} {} {} '.format(tempo_simulacao, x*1000, y*1000))
            
                f.write('\n')   
            
    if origem[-1] != '/':
        origem += '/'
    
    print config.format(origem + 'traces.boon', playgroundy, playgroundx, len(trac), 'traces.boon')



if __name__ == '__main__':
    
    des = """
    Gera os arquivo necessário para simular a mobilidade veicular em uma cidade, utilizando o simulador
    Omnetpp juntamente com o framwork MiXim.
    """
    
    parser = argparse.ArgumentParser(description=des, epilog='copyleft=badriciobq [at] gmail [dot] com')
    
    parser.add_argument("-r", "--routes", dest="rotas",
                        help="""Arquivo contendo os endereços das rotas no formato:
                                from: <origem> to: <destino> """)
                  
    parser.add_argument("-o", "--origem", dest="origem",
                        help='Diretório de origem. Onde serão salvos os arquivos.')
                                
    parser.add_argument("-n", "--nos", dest="nos",
                        help="""Arquivo contendo o indice do nó e as rotas que o nó deverá seguir separados por
                                espaço. Ex: <nozero> <rotazero> <rotaum> <rotadois>
                                
                                O arquivo deve conter as configurações de cada nó por linha, se o nó não estiver
                                presente no arquivo a rota será gerada utilizando o indíce do nó""")
                                      
    parser.add_argument("-t", "--traces", dest="traces", nargs="*",
                        help="""Lista de arquivos dos traces de GPS capturados no seguinte formato: 
                                <latitude>,<longitude>,<altitude>,<timestamp UTC>,<velocidade em m/s> """)
                                
    argumentos = parser.parse_args()
    
    
    if not (bool(argumentos.rotas) ^ bool(argumentos.traces)):
        parser.print_help()
        exit(1)
    
    if argumentos.origem and os.path.isdir(argumentos.origem):
        origem = argumentos.origem
    else:
        origem = os.getcwd()
    
    if argumentos.traces:
        boon_to_traces(argumentos.traces, origem, argumentos.nos)
    
    if argumentos.rotas:
        boon_to_routes(argumentos.rotas, origem, argumentos.nos)

