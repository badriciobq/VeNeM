#!/usr/bin/env python
#coding: utf-8

import os
import sys
import argparse
from Utils import Utils
from threading import Thread


config = """

Para configurar sua simulação siga os seguintes passos:

Copie o arquivo: "{0}" para a raiz do seu projeto;

Configure no seu arquivo omnetpp.ini os seguinte parâmetros:
**.playgroundSizeY: {1}km
**.playgroundSizeX: {2}km
**.numNodes = {3}           


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
    if origem[-1] != '/':
        origem += '/'
    
    lista = Utils.pegar_coordenadas_rotas(arquivo)
    
    if not lista:
        sys.stderr.write('Não existe rota para os endereços configurados.\n')
        exit(1)   

    menorLat, maiorLat, menorLon, maiorLon = Utils.coordenadas_extremas_rotas(lista)     

    if menorLat < 0 and maiorLat < 0 and menorLon < 0 and maiorLon < 0:
        pontoZero = (menorLat, maiorLon)
        pontoUm = (menorLat, menorLon)
        pontoDois = (maiorLat, menorLon)
        pontoTres = (maiorLat, maiorLon)

    elif menorLat > 0 and maiorLat > 0 and menorLon < 0 and maiorLon < 0:
	pontoZero = (maiorLat, maiorLon) 
        pontoUm = (maiorLat, menorLon)
        pontoDois = (menorLat, menorLon)
        pontoTres = (menorLat, maiorLon)

    elif menorLat > 0 and maiorLat > 0 and menorLon > 0 and maiorLon > 0:
	pontoZero = (maiorLat, menorLon)  
        pontoUm = (maiorLat, maiorLon)
        pontoDois = (menorLat, maiorLon)
        pontoTres = (menorLat, menorLon)

    elif menorLat < 0 and maiorLat < 0 and menorLon > 0 and maiorLon > 0:
	pontoZero = (menorLat, menorLon)
        pontoUm = (menorLat, maiorLon)
        pontoDois = (maiorLat, maiorLon)
        pontoTres = (maiorLat, menorLon)

    else:
	sys.stderr.write("Erro nas coordenadas.\n")
        exit(1)

    playgroundx, playgroundy = Utils.converte_plano_carteziano(pontoZero, pontoDois)
    
    try:
        dic_nos = Utils.formata_dicionario_nos(len(lista), nos)
        
    except Utils.RouterError:
        sys.stderr.write("Não é possível gerar rota para os indices definidos\n")
        sys.exit(1)
        
    Thread(target=Utils.download_mapa, args=([pontoZero, pontoTres, pontoDois, pontoUm], origem)).start()
 
    with open(origem + 'route.boon', 'w') as f:
    
        for i in xrange(len(dic_nos)):
        
            if dic_nos.has_key(i):
                inter = dic_nos.get(i)
    
            tempo_simulacao = inter[0]
            
            for t in inter[1:]:
                t = int(t)
                tamanho = len(lista[t]['rotas'])
                
                for i in xrange(tamanho-1):
                
                    p1 = lista[t]['rotas'][i]
                    p2 = lista[t]['rotas'][i+1]
                    
                    percurso = Utils.trace_from_gmaps(p1, p2)
                    for i in percurso:
                        time = i[0]
                        longit = i[1]
                        latit = i[2]
                        
                        tempo_simulacao = time + tempo_simulacao
                        x,y = Utils.converte_plano_carteziano(pontoZero, (latit, longit))
                        f.write('{} {} {} '.format(tempo_simulacao, x*1000, y*1000))
                        
                # Necessário para impedir que existe duas coordenadas com o mesmo ponto, o que
                # provoca uma exceção na simulação
                tempo_simulacao = tempo_simulacao + 2

            f.write('\n')
    
    print config.format(origem + 'route.boon', playgroundy, playgroundx, len(dic_nos), 'route.boon')



def boon_to_traces(files, origem=os.getcwd(), nos=None):
    """
    Função para gerar o arquivo de mobilidade compatível com o mixim através
    de um arquivo de traces no seguinte formato: 
    <latitude>,<longitude>,<altitude>,<timestamp UTC>,<velocidade m/s>
    """
        
    if origem[-1] != '/':
        origem += '/'
        
    trac = Utils.pegar_coordenadas_traces(files)

    menorLat, maiorLat, menorLon, maiorLon = Utils.coordenadas_extremas_traces(trac)
    
    playgroundx, playgroundy = Utils.converte_plano_carteziano((menorLat, maiorLon),(maiorLat, menorLon))
    
    try:
        dic_nos = Utils.formata_dicionario_nos(len(trac), nos)
    
    except Utils.RouterError:
        sys.stderr.write("Não é possível gerar rota para os indices definidos\n")
        sys.exit(1)
        
    Thread(target=Utils.download_mapa, args=([(menorLat,maiorLon),(maiorLat, maiorLon),(maiorLat, menorLon),(menorLat, menorLon)] , origem)).start()
    
        
    with open(origem + 'traces.boon', 'w') as f:
    
        for i in xrange(len(dic_nos)):
        
            if dic_nos.has_key(i):
                inter = dic_nos.get(i)
    
            tempo_simulacao = inter[0]
            
            for t in inter[1:]:
                t = int(t)
                
                for r in trac[t]:
                    time = r['tempo']
                    latit = round(float(r['latitude']), 6)
                    longit = round(float(r['longitude']), 6)
                    tempo_simulacao = time + tempo_simulacao
                
                    x,y = Utils.converte_plano_carteziano((menorLat, maiorLon), (latit, longit))
                    f.write('{} {} {} '.format(tempo_simulacao, x*1000, y*1000))
                
                # Necessário para impedir que existe duas coordenadas com o mesmo ponto, o que
                # provoca uma exceção na simulação
                tempo_simulacao = tempo_simulacao + 2
            
            f.write('\n')   
    
    print config.format(origem + 'traces.boon', playgroundy, playgroundx, len(dic_nos), 'traces.boon')


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
                                espaço. Ex: <nozero> <tempo inicial> <rotazero> <rotaum> <rotadois>
                                
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

