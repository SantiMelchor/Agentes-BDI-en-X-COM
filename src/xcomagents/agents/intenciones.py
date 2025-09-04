from abc import ABC, abstractmethod
import time

import random
from xcomagents.agents.creencias import Creencias
from xcomagents.utils import createMessage, casillas_alcance, casillas_precision, estoy_a_tiro, calcular_precision, elegir_casilla, mover_hacia
from xcomagents.domain import TipoDeseo,Ontologia, TipoAccion, Clases

class Intencion(ABC):
    @abstractmethod
    def comprobarAlcanzada(self, creencias):
        pass

    @abstractmethod
    def comprobarAnulada(self, creencias):
        pass

    @abstractmethod
    def calcularPrioridad(self, creencias):
        pass

    @abstractmethod
    def ejecutar(self, agent, creencias):
        pass


class IntencionFinalizarTurno(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.FINALIZAR_TURNO

    def comprobarAlcanzada(self, creencias):
         if creencias[Creencias.PUEDO_ACTUAR] and creencias[Creencias.PUEDO_MOVERME]:
            return True
         return False
    def comprobarAnulada(self, creencias):
        return False
    
    def calcularPrioridad(self, creencias):
        return 99999999
    
    def ejecutar(self, agent, creencias):
        creencias[Creencias.MI_TURNO] = False
        print(f"{agent.jid}: Ha sido mi turno mi posicion es {creencias[Creencias.POSICION]} y veo esto:")
        print(creencias[Creencias.MAPA])
        msg = createMessage(creencias[Creencias.TABLERO],"inform", Ontologia.TURNO, {Creencias.EQUIPO: creencias[Creencias.EQUIPO].name})
        return msg, creencias
    
class IntencionExplorarDefensiva(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.EXPLORAR

    def comprobarAlcanzada(self, creencias):
         if creencias[Creencias.ENEMIGOS]:
            return True
         return False
    def comprobarAnulada(self, creencias):
        return False
    
    def calcularPrioridad(self, creencias):
        return 10 + (9 - (creencias[Creencias.ROLES]["agresividad"])) + (creencias[Creencias.ROLES]["estrategia"]/2)
    
    def ejecutar(self, agent, creencias):
        if creencias[Creencias.PUEDO_MOVERME]:
            casillas = casillas_alcance(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION], False)
            opciones = []
            for c,v in creencias[Creencias.MAPA].mapa.items():
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nx, ny = c[0] + dx, c[1] + dy
                    if nx < 15 and ny < 30 and nx >= 0 and ny >= 0:
                        if (nx,ny) in casillas and v!= 0 and casillas[(nx,ny)] != 0:
                            opciones.append((nx,ny))
            eleccion = random.choice(opciones)
            while eleccion in creencias[Creencias.POSICIONES_ALIADAS]:
                eleccion = random.choice(opciones)
            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.MOVIMIENTO, {Creencias.POSICION: eleccion} )
        elif creencias[Creencias.PUEDO_ACTUAR]:
            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.DEFENDERSE.name} )
        return msg, creencias
    
class IntencionExplorarAgresiva(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.EXPLORAR

    def comprobarAlcanzada(self, creencias):
         if creencias[Creencias.ENEMIGOS]:
            return True
         return False
    def comprobarAnulada(self, creencias):
        return False
    
    def calcularPrioridad(self, creencias):
        return 10 + creencias[Creencias.ROLES]["agresividad"] + (9 - (creencias[Creencias.ROLES]["estrategia"]))/2
    
    def ejecutar(self, agent, creencias):
        
        if creencias[Creencias.PUEDO_MOVERME]:
            eleccion = elegir_casilla(creencias)
            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.MOVIMIENTO, {Creencias.POSICION: eleccion} )
        elif creencias[Creencias.PUEDO_ACTUAR]:
            eleccion = elegir_casilla(creencias)
            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.CORRER.name, Creencias.POSICION: eleccion} )
        return msg, creencias
    
class IntencionExplorarFrancotirador(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.EXPLORAR

    def comprobarAlcanzada(self, creencias):
         if creencias[Creencias.ENEMIGOS]:
            return True
         return False
    def comprobarAnulada(self, creencias):
        return False
    
    def calcularPrioridad(self, creencias):
        if creencias[Creencias.CLASE] != Clases.FRANCOTIRADOR:
            return -1
        return 40
    
    def ejecutar(self, agent, creencias):
        if len(creencias[Creencias.PREGUNTADOS]) != len(creencias[Creencias.ALIADOS]):
            for i in creencias[Creencias.ALIADOS].keys():
                if i not in creencias[Creencias.PREGUNTADOS]:
                    msg = createMessage(f"{i}@localhost", "query-ref", Ontologia.COMUNICACION, {Creencias.OBJETIVO: i, Creencias.ROLES: creencias[Creencias.ROLES]["rango"]} )
                    break
        else:
            if creencias[Creencias.PUEDO_MOVERME]:
                eleccion = elegir_casilla(creencias)
                msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.MOVIMIENTO, {Creencias.POSICION: eleccion} )
            elif creencias[Creencias.PUEDO_ACTUAR]:
                msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.DEFENDERSE.name} )
        return msg, creencias

class IntencionNeutralizarEnemigoAgresiva(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.NEUTRALIZAR

    def comprobarAlcanzada(self, creencias):
        if len(creencias[Creencias.ENEMIGOS_MUERTOS]) == 4:
            return True
        return False
    def comprobarAnulada(self, creencias):
        if not creencias[Creencias.ENEMIGOS]:
            return True
        return False
    
    def calcularPrioridad(self, creencias):
        return creencias[Creencias.ROLES]["agresividad"] + (9 - (creencias[Creencias.ROLES]["estrategia"]))/2 + (creencias[Creencias.ROLES]["egoismo"])/4
    
    def ejecutar(self, agent, creencias):
        if creencias[Creencias.PUEDO_MOVERME]:
            enemigo_seleccionado = next(iter(creencias[Creencias.ENEMIGOS]))
            casillas = casillas_precision(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION],creencias[Creencias.ARMA], creencias[Creencias.ENEMIGOS][enemigo_seleccionado] )
            if len(casillas) == 0:
                casilla_elegida = elegir_casilla(creencias)
            else:
                casilla_elegida = random.choice(casillas)
            enemigos_pos = []
            tries = 0
            for c,v in creencias[Creencias.ENEMIGOS].items():
                enemigos_pos.append(tuple(v[Creencias.POSICION]))
            while casilla_elegida in enemigos_pos or casilla_elegida in creencias[Creencias.POSICIONES_ALIADAS]:
                tries += 1
                if tries >= 30:
                    #print(1.2)
                    casillas = []
                    dict_dir = casillas_alcance(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION], False)
                    for c,v in dict_dir.items():
                        if v != 0 and c not in creencias[Creencias.POSICIONES_ALIADAS] and c not in enemigos_pos:
                            casillas.append(c)
                if len(casillas) == 0:
                    casilla_elegida = elegir_casilla(creencias)
                else:
                    casilla_elegida = random.choice(casillas)
            #print(enemigos_pos)
            #print("aliados", creencias[Creencias.POSICIONES_ALIADAS])
            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.MOVIMIENTO, {Creencias.POSICION: casilla_elegida} )
        elif creencias[Creencias.PUEDO_ACTUAR]:
            if creencias[Creencias.ARMA][1] == 0:
                msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.RECARGAR.name} )
            else:
                enemigo_seleccionado = next(iter(creencias[Creencias.ENEMIGOS]))
                if estoy_a_tiro(creencias[Creencias.MAPA].mapa, creencias[Creencias.POSICION], creencias[Creencias.ARMA], creencias[Creencias.ENEMIGOS][enemigo_seleccionado]):
                    distancia = abs(creencias[Creencias.POSICION][0] - creencias[Creencias.ENEMIGOS][enemigo_seleccionado][Creencias.POSICION][0]) + abs(creencias[Creencias.POSICION][1] - creencias[Creencias.ENEMIGOS][enemigo_seleccionado][Creencias.POSICION][1])
                    precision = calcular_precision(creencias[Creencias.MAPA].mapa, creencias[Creencias.POSICION], distancia, creencias[Creencias.ARMA],  creencias[Creencias.ENEMIGOS][enemigo_seleccionado])
                    msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.DISPARAR.name, Creencias.PRECISION: precision, Creencias.OBJETIVO: enemigo_seleccionado } )
                else:
                    casillas = casillas_precision(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION],creencias[Creencias.ARMA], creencias[Creencias.ENEMIGOS][enemigo_seleccionado] )
                    if len(casillas) == 0:
                        casilla_elegida = elegir_casilla(creencias)
                    else:
                        casilla_elegida = random.choice(casillas)
                    #print(casillas)
                    enemigos_pos = []
                    tries = 0
                    for c,v in creencias[Creencias.ENEMIGOS].items():
                        enemigos_pos.append(tuple(v[Creencias.POSICION]))
                    while casilla_elegida in enemigos_pos or casilla_elegida in creencias[Creencias.POSICIONES_ALIADAS]:
                        tries += 1
                        #print(2)
                        if tries >= 30:
                            #print(2.1)
                            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.DEFENDERSE.name} )
                            return msg, creencias
                        if len(casillas) == 0:
                            casilla_elegida = elegir_casilla(creencias)
                        else:
                            casilla_elegida = random.choice(casillas)
                    #print(enemigos_pos)
                    #print("aliados", creencias[Creencias.POSICIONES_ALIADAS])
                    msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.CORRER.name, Creencias.POSICION: casilla_elegida} )
        return msg, creencias


class IntencionNeutralizarEnemigoEstrategica(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.NEUTRALIZAR

    def comprobarAlcanzada(self, creencias):
        if len(creencias[Creencias.ENEMIGOS_MUERTOS]) == 4:
            return True
        return False
    def comprobarAnulada(self, creencias):
        if not creencias[Creencias.ENEMIGOS]:
            return True
        return False
    
    def calcularPrioridad(self, creencias):
        return creencias[Creencias.ROLES]["agresividad"] + (creencias[Creencias.ROLES]["estrategia"])/2 + (creencias[Creencias.ROLES]["egoismo"])/4
    
    def ejecutar(self, agent, creencias):
        if creencias[Creencias.PUEDO_MOVERME]:
            enemigo_seleccionado = next(iter(creencias[Creencias.ENEMIGOS]))
            casillas = casillas_precision(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION],creencias[Creencias.ARMA], creencias[Creencias.ENEMIGOS][enemigo_seleccionado] )
            #print(casillas)
            if len(casillas) == 0:
                casilla_elegida = elegir_casilla(creencias)
            else:
                opciones = []
                for c,v in creencias[Creencias.MAPA].mapa.items():
                    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                        nx, ny = c[0] + dx, c[1] + dy
                        if nx < 15 and ny < 30 and nx >= 0 and ny >= 0:
                            if (nx,ny) in casillas and v!= 0:
                                opciones.append((nx,ny))
                if len(opciones) == 0:
                    casilla_elegida = random.choice(casillas)
                else:
                    casilla_elegida = random.choice(opciones)
            enemigos_pos = []
            tries = 0
            for c,v in creencias[Creencias.ENEMIGOS].items():
                enemigos_pos.append(tuple(v[Creencias.POSICION]))
            while casilla_elegida in enemigos_pos or casilla_elegida in creencias[Creencias.POSICIONES_ALIADAS]:
                tries += 1
                if tries >= 30:
                    #print(1.2)
                    casillas = []
                    dict_dir = casillas_alcance(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION], False)
                    for c,v in dict_dir.items():
                        if v != 0 and c not in creencias[Creencias.POSICIONES_ALIADAS] and c not in enemigos_pos:
                            casillas.append(c)
                if len(casillas) == 0:
                    casilla_elegida = elegir_casilla(creencias)
                else:
                    casilla_elegida = random.choice(casillas)
            
            #print(enemigos_pos)
            #print("aliados", creencias[Creencias.POSICIONES_ALIADAS])
            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.MOVIMIENTO, {Creencias.POSICION: casilla_elegida} )
        elif creencias[Creencias.PUEDO_ACTUAR]:
            if creencias[Creencias.ARMA][1] == 0:
                msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.RECARGAR.name} )
            else:
                enemigo_seleccionado = next(iter(creencias[Creencias.ENEMIGOS]))
                if estoy_a_tiro(creencias[Creencias.MAPA].mapa, creencias[Creencias.POSICION], creencias[Creencias.ARMA], creencias[Creencias.ENEMIGOS][enemigo_seleccionado]):
                    distancia = abs(creencias[Creencias.POSICION][0] - creencias[Creencias.ENEMIGOS][enemigo_seleccionado][Creencias.POSICION][0]) + abs(creencias[Creencias.POSICION][1] - creencias[Creencias.ENEMIGOS][enemigo_seleccionado][Creencias.POSICION][1])
                    precision = calcular_precision(creencias[Creencias.MAPA].mapa, creencias[Creencias.POSICION], distancia, creencias[Creencias.ARMA],  creencias[Creencias.ENEMIGOS][enemigo_seleccionado])
                    msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.DISPARAR.name, Creencias.PRECISION: precision, Creencias.OBJETIVO: enemigo_seleccionado } )
                else:
                     msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.DEFENDERSE.name} )
        return msg, creencias
class IntencionNeutralizarEnemigoFrancotirador(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.NEUTRALIZAR

    def comprobarAlcanzada(self, creencias):
        if len(creencias[Creencias.ENEMIGOS_MUERTOS]) == 4:
            return True
        return False
    def comprobarAnulada(self, creencias):
        if not creencias[Creencias.ENEMIGOS]:
            return True
        return False
    
    def calcularPrioridad(self, creencias):
        if creencias[Creencias.CLASE] != Clases.FRANCOTIRADOR:
            return -1
        return 20
    
    def ejecutar(self, agent, creencias):
        #print("Soyfranco")
        if creencias[Creencias.ARMA][1] == 0:
                msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.RECARGAR.name} )
        else:
            enemigo_seleccionado = None
            for i in creencias[Creencias.ENEMIGOS]:
                if estoy_a_tiro(creencias[Creencias.MAPA].mapa, creencias[Creencias.POSICION], creencias[Creencias.ARMA], creencias[Creencias.ENEMIGOS][i]):
                    enemigo_seleccionado = i
                    break
            if not enemigo_seleccionado:
                enemigo_seleccionado = next(iter(creencias[Creencias.ENEMIGOS]))
            #print(creencias[Creencias.PUEDO_MOVERME])
            if estoy_a_tiro(creencias[Creencias.MAPA].mapa, creencias[Creencias.POSICION], creencias[Creencias.ARMA], creencias[Creencias.ENEMIGOS][enemigo_seleccionado]) and creencias[Creencias.PUEDO_ACTUAR] and creencias[Creencias.PUEDO_MOVERME]:
                distancia = abs(creencias[Creencias.POSICION][0] - creencias[Creencias.ENEMIGOS][enemigo_seleccionado][Creencias.POSICION][0]) + abs(creencias[Creencias.POSICION][1] - creencias[Creencias.ENEMIGOS][enemigo_seleccionado][Creencias.POSICION][1])
                precision = calcular_precision(creencias[Creencias.MAPA].mapa, creencias[Creencias.POSICION], distancia, creencias[Creencias.ARMA],  creencias[Creencias.ENEMIGOS][enemigo_seleccionado])
                msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.DISPARAR.name, Creencias.PRECISION: precision, Creencias.OBJETIVO: enemigo_seleccionado } )
            else:
                
                if creencias[Creencias.PUEDO_MOVERME]:
                    casillas = casillas_precision(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION],creencias[Creencias.ARMA], creencias[Creencias.ENEMIGOS][enemigo_seleccionado] )
                    #print(casillas)
                    if len(casillas) == 0:
                        casilla_elegida = elegir_casilla(creencias)
                    else:
                        opciones = []
                        for c,v in creencias[Creencias.MAPA].mapa.items():
                            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                                nx, ny = c[0] + dx, c[1] + dy
                                if nx < 15 and ny < 30 and nx >= 0 and ny >= 0:
                                    if (nx,ny) in casillas and v!= 0:
                                        opciones.append((nx,ny))
                        if len(opciones) == 0:
                            casilla_elegida = random.choice(casillas)
                        else:
                            casilla_elegida = random.choice(opciones)
                    enemigos_pos = []
                    tries = 0
                    for c,v in creencias[Creencias.ENEMIGOS].items():
                        enemigos_pos.append(tuple(v[Creencias.POSICION]))
                    while casilla_elegida in enemigos_pos or casilla_elegida in creencias[Creencias.POSICIONES_ALIADAS]:
                        tries += 1
                        if tries >= 30:
                            #print(1.2)
                            casillas = []
                            dict_dir = casillas_alcance(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION], False)
                            for c,v in dict_dir.items():
                                if v != 0 and c not in creencias[Creencias.POSICIONES_ALIADAS] and c not in enemigos_pos:
                                    casillas.append(c)
                        if len(casillas) == 0:
                            casilla_elegida = elegir_casilla(creencias)
                        else:
                            casilla_elegida = random.choice(casillas)
                    
                    #print(enemigos_pos)
                    #print("aliados", creencias[Creencias.POSICIONES_ALIADAS])
                    msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.MOVIMIENTO, {Creencias.POSICION: casilla_elegida} )
                elif creencias[Creencias.PUEDO_ACTUAR]:
                    msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.DEFENDERSE.name} )
        return msg, creencias

class IntencionObjetivoHolografico(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.HOLOGRAFICO

    def comprobarAlcanzada(self, creencias):
         if not creencias[Creencias.HOLOGRAFICO]:
            return True
         return False
    def comprobarAnulada(self, creencias):
         if not creencias[Creencias.HOLOGRAFICO]:
            return True
         return False
    
    def calcularPrioridad(self, creencias):
        if creencias[Creencias.CLASE] != Clases.PESADA:
            return -1
        elif not creencias[Creencias.HOLOGRAFICO]:
            return -1
        else:
            return 3 + (creencias[Creencias.ROLES]["estrategia"]) + (9 -creencias[Creencias.ROLES]["egoismo"])/2
    
    def ejecutar(self, agent, creencias):
        if creencias[Creencias.PUEDO_ACTUAR]:
            enemigo_seleccionado = next(iter(creencias[Creencias.ENEMIGOS]))
            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.HOLOGRAFICO.name, Creencias.OBJETIVO: enemigo_seleccionado} )
        return msg, creencias
    
class IntencionHuir(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.HUIR

    def comprobarAlcanzada(self, creencias):
         return False
    def comprobarAnulada(self, creencias):
         return False
    
    def calcularPrioridad(self, creencias):
        prioridad = 0
        if creencias[Creencias.CLASE] == Clases.FRANCOTIRADOR:
            prioridad += 7 + creencias[Creencias.ROLES]["miedo"] + ((creencias[Creencias.ROLES]["egoismo"])/4) + random.randint(0,5)
        else:
            prioridad += creencias[Creencias.ROLES]["miedo"] + ((creencias[Creencias.ROLES]["egoismo"])/4)
            if len(creencias[Creencias.ALIADOS]) > 1:
                aleatorio = random.randint(0,5)
                prioridad += aleatorio
            else:
                aleatorio = random.randint(2,7)
                prioridad += aleatorio
        return prioridad
    
    def ejecutar(self, agent, creencias):
        if creencias[Creencias.PUEDO_MOVERME]:
            eleccion = elegir_casilla(creencias)
            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.MOVIMIENTO, {Creencias.POSICION: eleccion} )
        elif creencias[Creencias.PUEDO_ACTUAR]:
            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.DEFENDERSE.name} )
        return msg, creencias

class IntencionCurarAliado(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.CURAR

    def comprobarAlcanzada(self, creencias):
        if creencias[Creencias.BOTIQUIN] == 0:
            return True
        return False
    def comprobarAnulada(self, creencias):
        if creencias[Creencias.BOTIQUIN] == 0:
            return True
        elif creencias[Creencias.PROMESA_AYUDA]:
            if creencias[Creencias.OBJETIVO_CURACION] not in creencias[Creencias.ALIADOS].keys():
                return True
        return False
    
    def calcularPrioridad(self, creencias):
        if creencias[Creencias.CLASE] != Clases.SOPORTE:
            return -1
        else:
            if creencias[Creencias.PROMESA_AYUDA]:
                return 40
            else:
                return  (creencias[Creencias.ROLES]["estrategia"])/4 + ((9 -creencias[Creencias.ROLES]["egoismo"]) * 1.5)

    
    def ejecutar(self, agent, creencias):
        objetivo = None
        if creencias[Creencias.PROMESA_AYUDA]:
            objetivo = creencias[Creencias.OBJETIVO_CURACION]
        else:
            min = 10000
            posibles = []
            for c in creencias[Creencias.ALIADOS].keys():
                if creencias[Creencias.ALIADOS][c][Creencias.VIDA] < 7:
                    posibles.append(c)
            for i in posibles:
                distancia = abs(creencias[Creencias.ALIADOS][i][Creencias.POSICION][0] - creencias[Creencias.POSICION][0]) + abs(creencias[Creencias.ALIADOS][i][Creencias.POSICION][1] - creencias[Creencias.POSICION][1])
                if distancia < min:
                    min = distancia
                    objetivo = i
        if creencias[Creencias.PUEDO_MOVERME]:
            posibles = mover_hacia(creencias, objetivo)
            casilla_elegida = random.choice(posibles)
            enemigos_pos = []
            tries = 0
            for c,v in creencias[Creencias.ENEMIGOS].items():
                enemigos_pos.append(tuple(v[Creencias.POSICION]))
            while casilla_elegida in enemigos_pos or casilla_elegida in creencias[Creencias.POSICIONES_ALIADAS] or (abs(casilla_elegida[0] - creencias[Creencias.ALIADOS][objetivo][Creencias.POSICION][0]) + abs(casilla_elegida[1] - creencias[Creencias.ALIADOS][objetivo][Creencias.POSICION][1])) == 0:
                tries += 1
                if tries >= 30:
                    posibles = []
                    dict_dir = casillas_alcance(creencias[Creencias.MAPA].mapa, 4, creencias[Creencias.POSICION], False)
                    for c,v in dict_dir.items():
                        if v != 0 and c not in creencias[Creencias.POSICIONES_ALIADAS] and c not in enemigos_pos:
                            posibles.append(c)
                casilla_elegida = random.choice(posibles)
            msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.MOVIMIENTO, {Creencias.POSICION: casilla_elegida} )
        elif creencias[Creencias.PUEDO_ACTUAR]:
            if (abs(creencias[Creencias.ALIADOS][objetivo][Creencias.POSICION][0] - creencias[Creencias.POSICION][0]) + abs(creencias[Creencias.ALIADOS][objetivo][Creencias.POSICION][1] - creencias[Creencias.POSICION][1])) <= 2:
                msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.CURAR.name, Creencias.OBJETIVO_CURACION: objetivo} )
            else:
                msg = createMessage(creencias[Creencias.TABLERO], "request", Ontologia.ACCION, {Creencias.ACCION: TipoAccion.DEFENDERSE.name} )
        return msg, creencias
    

class IntencionPedirAyuda(Intencion):
    def __init__(self):
        self.asociado = TipoDeseo.PEDIR_AYUDA

    def comprobarAlcanzada(self, creencias):
        if creencias[Creencias.AYUDA_PEDIDA]:
            return True
        return False
    def comprobarAnulada(self, creencias):
        if creencias[Creencias.SOPORTE] not in creencias[Creencias.ALIADOS].keys():
            return True
        return False
    
    def calcularPrioridad(self, creencias):
        if creencias[Creencias.CLASE] == Clases.SOPORTE:
            return -1
        return 8 + creencias[Creencias.ROLES]["egoismo"]
    
    def ejecutar(self, agent, creencias):
        msg = createMessage(f"{creencias[Creencias.SOPORTE]}@localhost", "request", Ontologia.AYUDA, {Creencias.ROLES: creencias[Creencias.ROLES]["rango"]} )
        return msg, creencias