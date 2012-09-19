#!/usr/bin/env python
#coding: utf-8

import re
import os
import sys
import math
import urllib2
from googlemaps import GoogleMaps


def distancia_entre_pontos(ponto1, ponto2):
    """
        Função retorna a distância em linha reta de dois pontos do sistema
        de coordenadas do globo terreste. Todos os testes foram realizados
        no 3Quadrante do globo, ou seja, todos os valores de longitude e
        latitude são negativos. Para garantir a consistência da equação seria
        necessários melhores testes, em casos em que um ponto está ao norte e
        o outro está so sul por exemplo.
        
        Parâmetro: Dois pontos contendo o conjunto de coordenadas no seguintes
                   formato tuple('LATITUDE', 'LONGITUDE')
        
    """
    # Conversão de graus pra radianos das latitudes
    firstLatToRad = math.radians(ponto2[0])
    secondLatToRad = math.radians(ponto1[0])

    # Diferença das longitudes
    deltaLongitudeInRad = math.radians( ponto2[1] - ponto1[1] );

    # Cálcula da distância entre os pontos
    parte1 = math.cos(firstLatToRad) * math.cos(secondLatToRad) * math.cos(deltaLongitudeInRad)
    parte2 = math.sin(firstLatToRad) * math.sin(secondLatToRad);
    return math.acos(parte1 + parte2) * 6371.0
    

def converte_plano_carteziano(ponto1, ponto2):
    """
        Recebe duas coordenadas do plano carteziano da terra e retorna as 
        coordenadas correspondentes no plano carteziano em função de x e y.
        
        Parâmetros:
            os parâmetros deve ser passados como uma tupla no seguinte 
            formato: ('latitude', 'longitude')
    """
    
    distanciaReto =  distancia_entre_pontos((ponto1),(ponto2))    
    y = math.sqrt(distanciaReto**2 - distancia_entre_pontos((ponto2[0], ponto1[1]), (ponto2[0], ponto2[1]))**2)
    x = math.sqrt(distanciaReto**2 - y**2)
    
    return x,y


def download_mapa(coordenadas, diretorio=os.environ['HOME']):
    """
    Função para fazer o download do mapa que o usuário deverá configurar na sua 
    simulação, o mapa será gravado em disco com o nome mapa.png
    """
    try:
        url_mapa = 'http://maps.google.com/maps/api/staticmap?size=800x800&sensor=false&path=color:0x00000000|weight:2|fillcolor:0xFFFF0033'
                    
        suffix = ''
        for i in coordenadas:
            suffix += '|{},{}'.format(i[0], i[1])
            
        url_mapa += suffix
        
        req = urllib2.Request(url_mapa)
        site = urllib2.urlopen(req)
    
        if diretorio[-1] == '/':
            diretorio = diretorio[:-1]

        with open('{}/mapa.png'.format(diretorio), 'wb') as f:
            f.write(site.read())
            print '\nMapa salvo com sucesso... {}/mapa.png'.format(diretorio)
            print """Para adicinar o mapa à sua simulação siga os seguinte passos:
            - Recorte o mapa na região mais amarela;
            - Copie o mapa para o diretório omnetpp-4.2.2/imagens/maps/
            - Acrescente o parâmetro "bgi=maps/mapa,s" na tag @display do arquivo "BaseNetwork.net"
            """
        
    except urllib2.URLError:
        sys.stderr.write('Erro ao acessar a url: {}\nFaça o download do mapa manualmente\n'.format(url_mapa))
        
    except IOError:
        sys.stderr.write('Não foi possível gravar o mapa em disco: {}\nFaça o download do mapa manualmente\n'.format(url_mapa) )
    
    
    
def pegar_coordenadas_rotas(arquivo_rotas):
    """
    Função que retorna uma lista contendo um dicionário com as informações 
    das rotas passada no arquivo, este dicionário contém as seguinte informações:
    
    'rotas' -> Contem 
    'distancia' -> Distância em metros entre a origem e o destino
    'tempo' -> Tempo em segundos entre a origem e o destino
    'origem' -> Origem
    'destino' -> Destino
    'velocidade' -> Velocidade em metros por segundos
    """
    
    maps = GoogleMaps()
    rotas = []
    
    try:
        with open(arquivo_rotas, 'r') as f:
            content = f.readlines()

        for i in content:
                
            try:
                source = re.search('from:(.*?)to:(.*)', i).group(1)
                dest = re.search('from:(.*?)to:(.*)', i).group(2)
                
            except:
                sys.stderr.write("Sintaxe do arquivo de rotas errada, verifique a documentação\n\n")
                sys.exit(0)
            
            try:
                info = maps.directions(source, dest)
                
                routes = info['Directions']['Routes'][0]['Steps']
                Distancia = info['Directions']['Distance']['meters']
                Tempo = info['Directions']['Duration']['seconds']
                Origem = info['Placemark'][0]['address']
                Destino = info['Placemark'][1]['address']
                corigem = info['Placemark'][0]['Point']['coordinates']
                cdestino = info['Placemark'][1]['Point']['coordinates']
                
                Velocidade = Distancia/Tempo
                rotas.append({'rotas':routes, 'distancia':Distancia, 'tempo':Tempo, 'origem':Origem, 'destino':Destino, 'velocidade':Velocidade, 'corigem': corigem, 'cdestino': cdestino})
                
            except:
                sys.stderr.write('Rota inexistente para: Origem: {} Destino: {}\n'.format(source, dest))
        
    except IOError:
        sys.stderr.write('Não foi possível abrir o arquivo de rotas\n')        
    
    return rotas
  

def coordenadas_extremas_rotas(info, borda=0.00002):
    """
        Recebe os dados referentes as rotas e retorna os valores extremos,
        menor e maior latitude, menor e maior longitude, com isto é possível
        determinar quais serão os limites do playground, e através destes
        valores será feito o mapeamento das coordenadas geográficas para as
        coordenadas do plano carteziado em função de x e y.
        Para criar uma borda, garantindo que as rotas não atinjam os limites
        do playground, os valores sofrerão incrementados, em aproximadamente 
        300 metros no sistema de coordenadas geográficas
        
        Parâmetros:
            informação retornada pelo método pegar_coordenadas(arquivo_rotas)
            borda, que por default é 0.000010 (não deve ultrapassar a precisão
            de 6 casas decimais, e incremento de 1 representa apriximandamente
            30 metros no sistema de coordenadas)
        
        Retorno:
            (menorLatitude, maiorLatitude, menorLongitude, maiorLongitude)
    """
    
    maiorLon = menorLon = info[0]['corigem'][0]
    maiorLat = menorLat = info[0]['corigem'][1]
    
    for i in info:
        if abs(i['corigem'][0]) < abs(menorLon):
            menorLon = i['corigem'][0]
            
        elif abs(i['corigem'][0]) > abs(maiorLon):
            maiorLon = i['corigem'][0]
        
        
        if abs(i['cdestino'][1]) < abs(menorLat):
            menorLat = i['cdestino'][1]
            
        elif abs(i['cdestino'][1]) > abs(maiorLat):
            maiorLat = i['cdestino'][1]
        
        
        if abs(i['cdestino'][0]) < abs(menorLon):
            menorLon = i['cdestino'][0]
            
        elif abs(i['cdestino'][0]) > abs(maiorLon):
            maiorLon = i['cdestino'][0]
        
        
        if abs(i['cdestino'][1]) < abs(menorLat):
            menorLat = i['cdestino'][1]
            
        elif abs(i['cdestino'][1]) > abs(maiorLat):
            maiorLat = i['cdestino'][1]
        
        
        for r in i['rotas']:
            longit = r['Point']['coordinates'][0]
            
            if abs(longit) < abs(menorLon):
                menorLon = longit
                
            elif abs(longit) > abs(maiorLon):
                maiorLon = longit
                
            lat = r['Point']['coordinates'][1]
            
            if abs(lat) < abs(menorLat):
                menorLat = lat
                
            elif abs(lat) > abs(maiorLat):
                maiorLat = lat
    
    return round(menorLat+borda,6), round(maiorLat-borda,6), round(menorLon+borda,6), round(maiorLon-borda,6)


def pegar_coordenadas_traces(arquivos_traces):
    """
    Função que retorna uma lista dos traces recebidos nos arquivos, cada possição
    da lista contém um lista com informações de cada ponto capturado.
    
    As informações do ponto estão em um dicionário com as seguintes chaves:
    latitude, longitude, altitude, tempo, velocidade

    """    
    rotas = []
    
    for arq in arquivos_traces:
        
        begin_time = open(arq).readline().split(',')[3]
        info = []
        
        for lin in open(arq).readlines():
            attr = lin.split(',')
            latitude = attr[0]
            longitude = attr[1]
            altitude = attr[2]
            time_seconds = round((int(attr[3]) - int(begin_time)) / 1000.0, 5)
            begin_time = attr[3]
            speed = attr[4]
            
            info.append({'latitude' : latitude, 'longitude' : longitude, 'altitude' : altitude, 'tempo' : time_seconds, 'velocidade' : speed})
        rotas.append(info)
    
    return rotas
            
            
def coordenadas_extremas_traces(info, borda=0.00002):
    """
        Recebe os dados referentes os traces e retorna os valores extremos,
        menor e maior latitude, menor e maior longitude, com isto é possível
        determinar quais serão os limites do playground, e através destes
        valores será feito o mapeamento das coordenadas geográficas para as
        coordenadas do plano carteziado em função de x e y.
        Para criar uma borda, garantindo que as rotas não atinjam os limites
        do playground, os valores sofrerão incrementados, em aproximadamente 
        300 metros no sistema de coordenadas geográficas
        
        Parâmetros:
            informação retornada pelo método pegar_coordenadas(arquivo_rotas)
            borda, que por default é 0.000010 (não deve ultrapassar a precisão
            de 6 casas decimais, e incremento de 1 representa apriximandamente
            30 metros no sistema de coordenadas)
        
        Retorno:
            (menorLatitude, maiorLatitude, menorLongitude, maiorLongitude)
    """
    menorLatitude = maiorLatitude = float(info[0][0]['latitude'])
    menorLongitude = maiorLongitude = float(info[0][0]['longitude'])
    
    for i in info:
        for dados in i:
            
            lat = float(dados['latitude'])
            
            if abs(menorLatitude) > abs(lat):
                menorLatitude = lat
                
            elif abs(maiorLatitude) < abs(lat):
                maiorLatitude = lat
            
            lon = float(dados['longitude'])
                
            if abs(menorLongitude) > abs(lon):
                menorLongitude = lon
                
            elif abs(maiorLongitude) < abs(lon):
                maiorLongitude = lon
                
    return round(menorLatitude+borda, 6), round(maiorLatitude-borda, 6), round(menorLongitude+borda, 6), round(maiorLongitude-borda, 6)



def formata_dicionario_nos(numero_rotas, arquivo):
    """
        Formata o dicionário que será utilizado para gerar as rotas. Com isto, 
        é possível configurar mais uma rota para um veiculo, se configurados
        corretamente no arquivo que recebe como parâmetro.
    """

    dic_nos = {}    
    if arquivo:
        with open(arquivo) as n:
            linhas = n.readlines()
            for l in linhas:
                try:
                    splited = l.strip().split(' ')
                    key = int(splited[0])
                    values = []
                    for i in splited[1:]:
                        if int(i) < numero_rotas:
                            values.append(int(i))
                        else:
                            sys.stderr.write('Indice de rota errado, verifique o arquivo "{0}"\n'.format(arquivo))
                            sys.exit(1)
                except:
                    #Ignora caracteres não numericos presente no arquivo de nós
                    pass
                        
                dic_nos.update({key : values})
    
    for i in xrange(numero_rotas):
        if not dic_nos.has_key(i):
            dic_nos.update({i : [i]})
    
    return dic_nos
                
                
                
