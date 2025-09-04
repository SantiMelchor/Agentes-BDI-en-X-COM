from spade.message import Message
from collections import deque
from xcomagents.agents.creencias import Creencias
from xcomagents.domain.enums import TipoCobertura, TipoArma

import json
import random

def createMessage(jid,type,ontologia,content ):
        msg = Message(to=jid)
        msg.set_metadata("performative", type)
        msg.set_metadata("ontology", ontologia)
        msg.body = json.dumps(content)
        return msg

def casillas_alcance(mapa, distancia,posicion, vision=True):
        visibles = {}
        cola = deque()
        cola.append((posicion[0], posicion[1], 0)) 

        while cola:
            x, y, d = cola.popleft()
            if (x, y) in visibles.keys():
                    continue
            try:
                if vision:
                    visibles[(x,y)] = mapa[(x,y)]
                elif not vision and mapa[(x,y)] == 0:
                    visibles[(x,y)] = d
            except KeyError as e:
                continue


            if d < distancia:
                if mapa[(x,y)] == 2:
                    continue
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nx, ny = x + dx, y + dy
                    if nx < 15 and ny < 30 and nx >= 0 and ny >= 0:
                            cola.append((nx, ny, d + 1))
        return visibles

def casillas_precision(mapa, movimiento, posicion, arma, enemigo):
    casillas_prim = casillas_alcance(mapa, movimiento, posicion, False)
    alcance_prim = casillas_alcance(mapa, arma[2], tuple(enemigo[Creencias.POSICION]), False)
    alcance = {}
    casillas = {}
    for c,v in alcance_prim.items():
        if v != 0:
            alcance[c] = v
    for c,v in casillas_prim.items():
        if v!= 0:
            casillas[c] = v 
    backup = casillas_alcance(mapa, 3, tuple(enemigo[Creencias.POSICION]), False)
    viables = {k: alcance[k] for k in casillas.keys() & alcance.keys()}
    backup_viables = {k: backup[k] for k in casillas.keys() & backup.keys()}
    max = 0
    casilla = []
    for c,v in viables.items():
        precision = calcular_precision(mapa, c, v ,arma,enemigo)
        if precision > max:
            max = precision
            casilla = [c]
        elif precision == max:
            casilla.append(c)
    if len(casilla) == 0:
        for c in backup_viables.keys():
            casilla.append(c)
    return casilla

def calcular_precision(mapa, casilla, distancia, arma,objetivo):
    x,y = casilla[0] - objetivo[Creencias.POSICION][0], casilla[1] - objetivo[Creencias.POSICION][1]
    coberturaX = 0
    coberturaY = 0
    try:
        if (x > 0 and TipoCobertura.ESTE.name in objetivo[Creencias.TIPO_COBERTURA]):
            coberturaX = mapa[(objetivo[Creencias.POSICION][0] +1, objetivo[Creencias.POSICION][1])]
        elif (x < 0 and TipoCobertura.OESTE.name in objetivo[Creencias.TIPO_COBERTURA]):
            coberturaX = mapa[(objetivo[Creencias.POSICION][0] -1, objetivo[Creencias.POSICION][1])]
        if (y > 0 and TipoCobertura.NORTE.name in objetivo[Creencias.TIPO_COBERTURA]): 
            coberturaY = mapa[(objetivo[Creencias.POSICION][0], objetivo[Creencias.POSICION][1] + 1)]
        elif (y < 0 and TipoCobertura.SUR.name in objetivo[Creencias.TIPO_COBERTURA]):
            coberturaY = mapa[(objetivo[Creencias.POSICION][0], objetivo[Creencias.POSICION][1] - 1)]
    except KeyError:
        return 0
    
    cobertura = 0
    if coberturaX != 0:
        cobertura = coberturaX
    if coberturaY != 0 and coberturaX < coberturaY:
        cobertura = coberturaY
    defensa = objetivo[Creencias.DEFENSA] + ((cobertura * 2))
    if arma[0] == TipoArma.ESCOPETA:
        if distancia == 1:
            return 0.99
        else:
            return round((-0.07 * defensa) + 0.99, 2)
    elif arma[0] == TipoArma.METRALLETA:
        if cobertura == 0:
            return 0.7
        else:
            return round(((-0.036 * defensa) + 0.36) + ((-0.0625 * distancia) + 0.36),2)
    elif arma[0] == TipoArma.RIFLE:
        if cobertura == 0:
            return 0.85
        else:
            return round(((-0.021 * defensa) + 0.4) + ((-0.033 * distancia) + 0.45),2)
    elif arma[0] == TipoArma.FRANCOTIRADOR:
        if cobertura == 0:
            return 0.99
        else:
            return round(((-0.058 * defensa) + 0.7) + ((-0.02 * distancia) + 0.3),2)

def estoy_a_tiro(mapa, casilla,arma, objetivo):
    alcance = casillas_alcance(mapa, arma[2], tuple(objetivo[Creencias.POSICION]), False)
    if tuple(casilla) in alcance:
        return True
    return False

def elegir_casilla(creencias):
            casillas = casillas_alcance(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION], False)
            max = 0
            opciones = []
            todas = []
            for c,v in casillas.items():
                if v > max:
                    opciones = []
                    opciones.append(c)
                    max = v
                elif v == max:
                    opciones.append(c)
                todas.append(c)
            eleccion = random.choice(opciones)
            tries = 0
            enemigos_pos = []
            for c,v in creencias[Creencias.ENEMIGOS].items():
                enemigos_pos.append(tuple(v[Creencias.POSICION]))
            while eleccion in creencias[Creencias.POSICIONES_ALIADAS] or eleccion in enemigos_pos:
                tries += 1
                if tries > 30:
                    eleccion = random.choice(todas)
                else:
                    eleccion = random.choice(opciones)
            return eleccion

def mover_hacia(creencias, objetivo):
    casillas = casillas_alcance(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION], False)
    for c in casillas.keys():
        distancia_al_objetivo = abs(creencias[Creencias.ALIADOS][objetivo][Creencias.POSICION][0] - c[0]) + abs(creencias[Creencias.ALIADOS][objetivo][Creencias.POSICION][1] - c[1])
        casillas[c] = distancia_al_objetivo
    min = 10000
    opciones = []
    antiguas = []
    for c,v in casillas.items():
        if c == tuple(creencias[Creencias.POSICION]):
            continue
        if v < min:
            min = v
            antiguas = opciones
            opciones = []
            opciones.append(c)
        elif v == min:
            opciones.append(c)
    return opciones + antiguas
