import json
import time
import random


from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from xcomagents.domain import Clases,Equipo, Mapa, Ontologia, TipoAccion, TipoCobertura, TipoArma
from xcomagents.agents.creencias import Creencias


class Tablero(Agent):
    class BDICycle(CyclicBehaviour):
        def eliminar_jugador(self, equipo, nombre):
            for i in range(len(self.creencias[equipo]) - 1, -1, -1):
                if self.creencias[equipo][i] == nombre:
                    del self.creencias[equipo][i]
                
        def generar_enemigo_info(self, enemigo):
            serial_enemigo = {}
            serial_enemigo[Creencias.POSICION] = enemigo[Creencias.POSICION]
            serial_enemigo[Creencias.DEFENSA] = enemigo[Creencias.DEFENSA]
            serial_enemigo[Creencias.VIDA] = enemigo[Creencias.VIDA]
            serial_enemigo[Creencias.A_CUBIERTO] = enemigo[Creencias.A_CUBIERTO]
            serial_enemigo[Creencias.TIPO_COBERTURA] = enemigo[Creencias.TIPO_COBERTURA]
            return serial_enemigo
        async def ejecutarAccion(self,msg):
            print("Recibiendo mensaje y actuando acorde")
            if msg.get_metadata("ontology") == Ontologia.TURNO:
                body = json.loads(msg.body)
                equipo = Equipo[body[Creencias.EQUIPO]]
                equipo_actual = Creencias.EQUIPO_ROJO if equipo == Equipo.ROJO else Creencias.EQUIPO_AZUL
                for jugador in self.creencias[equipo_actual]:
                    if jugador not in self.creencias[Creencias.TURNOS_JUGADORES]:
                        print(f"{self.agent.jid}: Turno de {jugador}")
                        self.creencias[Creencias.TURNOS_JUGADORES].append(jugador)
                        self.creencias[Creencias.JUGADORES][jugador][Creencias.PUEDO_ACTUAR] = True
                        self.creencias[Creencias.JUGADORES][jugador][Creencias.PUEDO_MOVERME] = True
                        self.creencias[Creencias.JUGADORES][jugador][Creencias.DEFENSA] = 0
                        pos_visibles = Mapa.crear_mapa(jugador,self.creencias[Creencias.JUGADORES][jugador][Creencias.POSICION]).mapa
                        equipo = self.creencias[Creencias.JUGADORES][jugador][Creencias.EQUIPO] 
                        enemigos = []
                        aliados = []
                        for c,v in self.creencias[Creencias.JUGADORES].items():
                            if c!= jugador and v[Creencias.POSICION] in pos_visibles and v[Creencias.EQUIPO] != equipo:
                                enemigos.append((c,self.generar_enemigo_info(v)))
                            elif c!= jugador and v[Creencias.EQUIPO] == equipo:
                                aliados.append((c, self.generar_enemigo_info(v)))
                        
                        await self.sendMessage(self.creencias[Creencias.JIDS_JUGADORES][jugador], "inform", Ontologia.TURNO,{Creencias.MI_TURNO: True, Creencias.ENEMIGOS: enemigos, Creencias.VIDA: self.creencias[Creencias.JUGADORES][jugador][Creencias.VIDA], Creencias.ALIADOS: aliados})
                        return
                print(f"{self.agent.jid}: Pasando el turno al otro equipo")
                equipo_contrario = Creencias.EQUIPO_ROJO if equipo == Equipo.AZUL else Creencias.EQUIPO_AZUL
                if len(self.creencias[equipo_contrario]) == 0:
                    self.terminado = True
                    self.equipo_ganador = equipo
                    return
                self.creencias[Creencias.TURNOS_JUGADORES] = []
                self.creencias[Creencias.TURNO_EQUIPO] = equipo_contrario
                self.creencias[Creencias.TURNOS_JUGADORES].append(self.creencias[equipo_contrario][0])
                self.creencias[Creencias.JUGADORES][self.creencias[equipo_contrario][0]][Creencias.PUEDO_MOVERME] = True
                self.creencias[Creencias.JUGADORES][self.creencias[equipo_contrario][0]][Creencias.PUEDO_ACTUAR] = True
                self.creencias[Creencias.JUGADORES][self.creencias[equipo_contrario][0]][Creencias.DEFENSA] = 0
                pos_visibles = Mapa.crear_mapa(self.creencias[equipo_contrario][0],self.creencias[Creencias.JUGADORES][self.creencias[equipo_contrario][0]][Creencias.POSICION]).mapa
                equipo = self.creencias[Creencias.JUGADORES][self.creencias[equipo_contrario][0]][Creencias.EQUIPO] 
                enemigos = []
                aliados = []
                for c,v in self.creencias[Creencias.JUGADORES].items():
                    if c!= self.creencias[equipo_contrario][0] and v[Creencias.POSICION] in pos_visibles and v[Creencias.EQUIPO] != equipo:
                        enemigos.append((c,self.generar_enemigo_info(v)))
                    elif c!= self.creencias[equipo_contrario][0] and v[Creencias.EQUIPO] == equipo:
                        aliados.append((c, self.generar_enemigo_info(v)))
                await self.sendMessage(self.creencias[Creencias.JIDS_JUGADORES][self.creencias[equipo_contrario][0]], "inform", Ontologia.TURNO,{Creencias.MI_TURNO: True, Creencias.ENEMIGOS: enemigos, Creencias.VIDA: self.creencias[Creencias.JUGADORES][self.creencias[equipo_contrario][0]][Creencias.VIDA], Creencias.ALIADOS: aliados})
                return
            elif msg.get_metadata("ontology") == Ontologia.MOVIMIENTO:
                body = json.loads(msg.body)
                pos_deseada = tuple(body[Creencias.POSICION])
                sender_id = str(msg.sender).split("@")[0]
                for c,v in self.creencias[Creencias.JUGADORES].items():
                    if c != sender_id and self.creencias[Creencias.JUGADORES][c][Creencias.POSICION] == pos_deseada:
                        print("no puede moverse")
                        print(self.creencias[Creencias.JUGADORES][c])
                        contenido = {
                            Creencias.TIPO_FALLO: Creencias.FALLO_MOVIMIENTO,
                            Creencias.POSICION: self.creencias[Creencias.JUGADORES][sender_id][Creencias.POSICION]
                        }
                        await self.sendMessage(str(msg.sender), "failure", Ontologia.MOVIMIENTO,contenido)
                        return
                    elif c == sender_id and self.creencias[Creencias.JUGADORES][c][Creencias.PUEDO_MOVERME] == False:
                        print("no tiene movimiento")
                        contenido = {
                            Creencias.TIPO_FALLO: Creencias.FALLO_MOVIMIENTO,
                            Creencias.POSICION: self.creencias[Creencias.JUGADORES][sender_id][Creencias.POSICION]
                        }
                        await self.sendMessage(str(msg.sender), "failure", Ontologia.MOVIMIENTO,contenido)
                        return
                self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_MOVERME] = False
                self.creencias[Creencias.JUGADORES][sender_id][Creencias.POSICION] = pos_deseada
                cobertura = False
                pos_visibles = Mapa.crear_mapa(sender_id,pos_deseada).mapa
                equipo = self.creencias[Creencias.JUGADORES][sender_id][Creencias.EQUIPO] 
                enemigos = []
                aliados = []
                for c,v in self.creencias[Creencias.JUGADORES].items():
                    if c!= sender_id and v[Creencias.POSICION] in pos_visibles and v[Creencias.EQUIPO] != equipo:
                        enemigos.append((c,self.generar_enemigo_info(v)))
                    elif c!= sender_id and v[Creencias.EQUIPO] == equipo:
                        aliados.append((c, self.generar_enemigo_info(v)))
                tipo_cobertura = []
                for dx,dy,dir in [(1,0,TipoCobertura.ESTE),(-1,0,TipoCobertura.OESTE),(0,1, TipoCobertura.NORTE),(0,-1, TipoCobertura.SUR)]:
                    nx,ny = pos_deseada[0] +dx, pos_deseada[1]+dy
                    if nx < 15 and ny < 30 and nx >= 0 and ny >= 0:
                        if self.creencias[Creencias.MAPA].mapa[(nx,ny)] != 0:
                            tipo_cobertura.append(dir.name)
                            cobertura = True
                self.creencias[Creencias.JUGADORES][sender_id][Creencias.A_CUBIERTO] = cobertura
                self.creencias[Creencias.JUGADORES][sender_id][Creencias.TIPO_COBERTURA] = tipo_cobertura
                contenido = {
                    Creencias.POSICION: pos_deseada,
                    Creencias.A_CUBIERTO: cobertura,
                    Creencias.TIPO_COBERTURA: tipo_cobertura,
                    Creencias.ENEMIGOS: enemigos,
                    Creencias.ALIADOS: aliados

                }
                await self.sendMessage(str(msg.sender), "inform-result", Ontologia.MOVIMIENTO,contenido)
                return
            elif msg.get_metadata("ontology") == Ontologia.ACCION:
                body = json.loads(msg.body)
                accion = TipoAccion[body[Creencias.ACCION]]
                #print(accion)
                sender_id = str(msg.sender).split("@")[0]
                if accion == TipoAccion.CORRER:
                    pos_deseada = tuple(body[Creencias.POSICION])
                    sender_id = str(msg.sender).split("@")[0]
                    for c,v in self.creencias[Creencias.JUGADORES].items():
                        if c != sender_id and self.creencias[Creencias.JUGADORES][c][Creencias.POSICION] == pos_deseada:
                            print("no puede moverse")
                            print(self.creencias[Creencias.JUGADORES][c])
                            contenido = {
                                Creencias.TIPO_FALLO: Creencias.FALLO_CORRER,
                                Creencias.ACCION: accion.name,
                                Creencias.POSICION: self.creencias[Creencias.JUGADORES][sender_id][Creencias.POSICION]
                            }
                            await self.sendMessage(str(msg.sender), "failure", Ontologia.ACCION,contenido)
                            return
                        elif c == sender_id and self.creencias[Creencias.JUGADORES][c][Creencias.PUEDO_ACTUAR] == False:
                            print("no tiene movimiento")
                            contenido = {
                                Creencias.TIPO_FALLO: Creencias.FALLO_CORRER,
                                Creencias.ACCION: accion.name,
                                Creencias.POSICION: self.creencias[Creencias.JUGADORES][sender_id][Creencias.POSICION]
                            }
                            await self.sendMessage(str(msg.sender), "failure", Ontologia.ACCION,contenido)
                            return
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] = False
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.POSICION] = pos_deseada
                    cobertura = False
                    pos_visibles = Mapa.crear_mapa(sender_id,pos_deseada).mapa
                    equipo = self.creencias[Creencias.JUGADORES][sender_id][Creencias.EQUIPO] 
                    enemigos = []
                    aliados = []
                    for c,v in self.creencias[Creencias.JUGADORES].items():
                        if c!= sender_id and v[Creencias.POSICION] in pos_visibles and v[Creencias.EQUIPO] != equipo:
                            enemigos.append((c,self.generar_enemigo_info(v)))
                        elif c!= sender_id and v[Creencias.EQUIPO] == equipo:
                            aliados.append((c, self.generar_enemigo_info(v)))
                    tipo_cobertura = []
                    for dx,dy,dir in [(1,0,TipoCobertura.ESTE),(-1,0,TipoCobertura.OESTE),(0,1, TipoCobertura.NORTE),(0,-1, TipoCobertura.SUR)]:
                        nx,ny = pos_deseada[0] +dx, pos_deseada[1]+dy
                        if nx < 15 and ny < 30 and nx >= 0 and ny >= 0:
                            if self.creencias[Creencias.MAPA].mapa[(nx,ny)] != 0:
                                tipo_cobertura.append(dir.name)
                                cobertura = True
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.A_CUBIERTO] = cobertura
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.TIPO_COBERTURA] = tipo_cobertura
                    contenido = {
                        Creencias.ACCION: accion.name,
                        Creencias.POSICION: pos_deseada,
                        Creencias.A_CUBIERTO: cobertura,
                        Creencias.TIPO_COBERTURA: tipo_cobertura,
                        Creencias.ENEMIGOS: enemigos,
                        Creencias.ALIADOS: aliados

                    }
                    await self.sendMessage(str(msg.sender), "inform-result", Ontologia.ACCION,contenido)
                    return
                elif accion == TipoAccion.DEFENDERSE:
                    if self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] == False:
                        contenido = {
                            Creencias.TIPO_FALLO: Creencias.FALLO_DEFENDERSE,
                            Creencias.ACCION: accion.name,
                        }
                        await self.sendMessage(str(msg.sender), "failure", Ontologia.ACCION,contenido)
                        return
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.DEFENSA] = self.creencias[Creencias.JUGADORES][sender_id][Creencias.DEFENSA] + 3
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] = False
                    contenido = {
                        Creencias.ACCION: accion.name,
                        Creencias.DEFENSA: self.creencias[Creencias.JUGADORES][sender_id][Creencias.DEFENSA]
                    }
                    await self.sendMessage(str(msg.sender), "inform-result", Ontologia.ACCION,contenido)
                    return
                elif accion == TipoAccion.RECARGAR:
                    if self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] == False:
                        contenido = {
                            Creencias.TIPO_FALLO: Creencias.FALLO_RECARGA,
                            Creencias.ACCION: accion.name,
                        }
                        await self.sendMessage(str(msg.sender), "failure", Ontologia.ACCION,contenido)
                        return
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] = False
                    if self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.ESCOPETA or self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.METRALLETA:
                        self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA] = (self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0],3,self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][2])
                    elif self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.FRANCOTIRADOR:
                        self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA] = (self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0],2,self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][2])
                    elif self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.RIFLE:
                        self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA] = (self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0],4,self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][2])
                    contenido = {
                        Creencias.ACCION: accion.name,
                    }
                    await self.sendMessage(str(msg.sender), "inform-result", Ontologia.ACCION,contenido)
                    return
                elif accion == TipoAccion.DISPARAR:
                    if self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] == False or self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][1] == 0:
                        contenido = {
                            Creencias.TIPO_FALLO: Creencias.FALLO_DISPARO,
                            Creencias.ACCION: accion.name,
                        }
                        await self.sendMessage(str(msg.sender), "failure", Ontologia.ACCION,contenido)
                        return
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] = False    
                    if self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.ESCOPETA or self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.METRALLETA:
                        self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA] = (self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0],self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][1] - 1,self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][2])
                    elif self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.FRANCOTIRADOR:
                        self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA] = (self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0],self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][1] - 1,self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][2])
                        self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_MOVERME] = False
                    elif self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.RIFLE:
                        self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA] = (self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0],self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][1] - 1,self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][2])
                    if random.random() < body[Creencias.PRECISION]:
                        #TODO Si se muere que pasa, si el tio al que apunta no esta en la casilla que pone que esta
                        daño = 0
                        muerte = False
                        if self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.ESCOPETA or self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.FRANCOTIRADOR:
                            daño = 5
                        elif self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.METRALLETA:
                            daño = 3
                        elif self.creencias[Creencias.JUGADORES][sender_id][Creencias.ARMA][0] == TipoArma.RIFLE:
                            daño = 2
                        
                        objetivo = body[Creencias.OBJETIVO]
                        if self.creencias[Creencias.JUGADORES][objetivo][Creencias.HOSTIGADO]:
                            daño += 1
                        if daño < self.creencias[Creencias.JUGADORES][objetivo][Creencias.VIDA]:
                            self.creencias[Creencias.JUGADORES][objetivo][Creencias.VIDA] = self.creencias[Creencias.JUGADORES][objetivo][Creencias.VIDA] - daño
                        else:
                            daño = self.creencias[Creencias.JUGADORES][objetivo][Creencias.VIDA]
                            muerte = True
                            sender = str(msg.sender).split("@")[0]
                            for c in self.creencias[Creencias.JIDS_JUGADORES].keys():
                                if c != sender:
                                    await self.sendMessage(str(self.creencias[Creencias.JIDS_JUGADORES][c]), "inform", Ontologia.MUERTE, {Creencias.OBJETIVO: objetivo, Creencias.EQUIPO: self.creencias[Creencias.JUGADORES][objetivo][Creencias.EQUIPO].name})
                            del self.creencias[Creencias.JIDS_JUGADORES][objetivo]
                        if self.creencias[Creencias.JUGADORES][objetivo][Creencias.EQUIPO] == Equipo.AZUL:
                            self.vida_perdida += daño
                            if muerte:
                                self.eliminar_jugador(Creencias.EQUIPO_AZUL, objetivo)
                                del self.creencias[Creencias.JUGADORES][objetivo]
                        else:
                            self.vida_eliminada += daño
                            if muerte:
                                self.eliminar_jugador(Creencias.EQUIPO_ROJO, objetivo)
                                del self.creencias[Creencias.JUGADORES][objetivo]
                        contenido = {
                            Creencias.ACCION: accion.name,
                            Creencias.ENEMIGOS: (objetivo,self.generar_enemigo_info( self.creencias[Creencias.JUGADORES][objetivo]) if not muerte else None) 
                        }
                        await self.sendMessage(str(msg.sender), "inform-result", Ontologia.ACCION,contenido)
                    else:
                        objetivo = body[Creencias.OBJETIVO]
                        contenido = {
                            Creencias.TIPO_FALLO: Creencias.DISPARO_FALLADO,
                            Creencias.ACCION: accion.name,
                            Creencias.ENEMIGOS: (objetivo,self.generar_enemigo_info( self.creencias[Creencias.JUGADORES][objetivo]))
                        }
                        await self.sendMessage(str(msg.sender), "failure", Ontologia.ACCION,contenido)
                elif accion == TipoAccion.HOLOGRAFICO:
                    if self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] == False or not self.creencias[Creencias.JUGADORES][sender_id][Creencias.HOLOGRAFICO]:
                        contenido = {
                            Creencias.TIPO_FALLO: Creencias.FALLO_DRON,
                            Creencias.ACCION: accion.name,
                        }
                        await self.sendMessage(str(msg.sender), "failure", Ontologia.ACCION,contenido)
                        return
                    objetivo = body[Creencias.OBJETIVO]
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] = False
                    self.creencias[Creencias.JUGADORES][objetivo][Creencias.HOSTIGADO] = True
                    contenido = {
                            Creencias.ACCION: accion.name,
                        }
                    await self.sendMessage(str(msg.sender), "inform-result", Ontologia.ACCION,contenido)
                elif accion == TipoAccion.CURAR:
                    if self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] == False or self.creencias[Creencias.JUGADORES][sender_id][Creencias.BOTIQUIN] == 0:
                        contenido = {
                            Creencias.TIPO_FALLO: Creencias.FALLO_CURACION,
                            Creencias.ACCION: accion.name,
                        }
                        await self.sendMessage(str(msg.sender), "failure", Ontologia.ACCION,contenido)
                        return
                    objetivo = body[Creencias.OBJETIVO_CURACION]
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.PUEDO_ACTUAR] = False
                    self.creencias[Creencias.JUGADORES][sender_id][Creencias.BOTIQUIN] -= 1
                    self.creencias[Creencias.JUGADORES][objetivo][Creencias.VIDA] += 4
                    contenido = {
                            Creencias.ACCION: accion.name,
                        }
                    await self.sendMessage(str(msg.sender), "inform-result", Ontologia.ACCION,contenido)
            else:
                print("no se lo que haser wtf")
                

        async def sendMessage(self,jid,type,ontologia,content):
            msg = Message(to=jid)
            msg.set_metadata("performative", type)
            msg.set_metadata("ontology", ontologia)
            #print(content)
            msg.body = json.dumps(content)
            await self.send(msg)

        async def on_start(self):
            print("Starting")
            self.creencias = self.get("creencias")
            self.intencion_actual = None
            self.started = False
            self.equipo_jugando = Equipo.AZUL
            self.vida_eliminada = 0
            self.vida_perdida = 0
            self.terminado = False
            self.equipo_ganador = None

        async def run(self):
            if not self.started:
                aliados = []
                for c,v in self.creencias[Creencias.JUGADORES].items():
                    if c!= self.creencias[Creencias.EQUIPO_AZUL][0] and v[Creencias.EQUIPO] == Equipo.AZUL:
                        aliados.append((c, self.generar_enemigo_info(v)))
                self.creencias[Creencias.JUGADORES][self.creencias[Creencias.EQUIPO_AZUL][0]][Creencias.PUEDO_MOVERME] = True
                self.creencias[Creencias.JUGADORES][self.creencias[Creencias.EQUIPO_AZUL][0]][Creencias.PUEDO_ACTUAR] = True
                await self.sendMessage(self.creencias[Creencias.JIDS_JUGADORES][self.creencias[Creencias.EQUIPO_AZUL][0]], "inform", Ontologia.TURNO,{Creencias.MI_TURNO: True, Creencias.VIDA: self.creencias[Creencias.JUGADORES][self.creencias[Creencias.EQUIPO_AZUL][0]][Creencias.VIDA], Creencias.ENEMIGOS: [], Creencias.ALIADOS: aliados})
                self.creencias[Creencias.TURNOS_JUGADORES].append(self.creencias[Creencias.EQUIPO_AZUL][0])
                self.started = True
            msg = await self.receive(timeout=10)
            #print(self.terminado)
            if msg:
                await self.ejecutarAccion(msg)
                if self.terminado:
                    if self.equipo_ganador == Equipo.AZUL:
                        for i in self.creencias[Creencias.EQUIPO_AZUL]:
                            await self.sendMessage(str(self.creencias[Creencias.JIDS_JUGADORES][i]), "inform", Ontologia.MUERTE, {Creencias.OBJETIVO: i})
                    else:
                        for i in self.creencias[Creencias.EQUIPO_ROJO]:
                            await self.sendMessage(str(self.creencias[Creencias.JIDS_JUGADORES][i]), "inform", Ontologia.MUERTE, {Creencias.OBJETIVO: i})
                    self.kill()
                    return
            else:
                #print(self.creencias[Creencias.MAPA])
                self.kill(exit_code=1)
                return
            #     self.actualizarCreencias("hola")
            #     self.actualizarDeseos()
            #     self.seleccionarIntencion()
            #     self.ejecutarIntencion()
         
        
        async def on_end(self):
            self.agent.vida_eliminada = self.vida_eliminada
            self.agent.vida_perdida = self.vida_perdida
            print(f"ELIMINADOS: {self.vida_eliminada}, PERDIDOS: {self.vida_perdida}" )
            
    
    def __init__(self, jid, password, jids, equipoRojo, equipoAzul, jugs):
        super().__init__(jid, password)
        creencias = {
            Creencias.JIDS_JUGADORES: jids,
            Creencias.EQUIPO_ROJO: equipoRojo,
            Creencias.EQUIPO_AZUL: equipoAzul,
            Creencias.TURNOS_JUGADORES: [],
            Creencias.TURNO_EQUIPO: Equipo.AZUL,
            Creencias.MAPA: Mapa.crear_mapa(jid),
            Creencias.JUGADORES: self.param_jugadores(jugs)
        }
        self.set("creencias", creencias)

    def param_jugadores(self,jugadores):
        nuevo_jug = {}
        for c,v in jugadores.items():
            jugador = {}
            for x,y in v.items():
                if x == "clase":
                    jugador[Creencias.CLASE] = y
                    if y == Clases.ASALTO:
                        jugador[Creencias.VIDA] = 13
                    else:
                        jugador[Creencias.VIDA] = 10
                    if y == Clases.PESADA:
                        jugador[Creencias.HOLOGRAFICO] = True
                    else:
                        jugador[Creencias.HOLOGRAFICO] = False
                    if y == Clases.SOPORTE:
                        jugador[Creencias.BOTIQUIN] = 2
                    else:
                        jugador[Creencias.BOTIQUIN] = 0
                elif x == "equipo":
                    jugador[Creencias.EQUIPO] = y
                elif x == "posicion":
                    jugador[Creencias.POSICION] = y
                elif x == "arma":
                    jugador[Creencias.ARMA] = y
            jugador[Creencias.PUEDO_ACTUAR] = False
            jugador[Creencias.PUEDO_MOVERME] = False
            jugador[Creencias.DEFENSA] = 0
            jugador[Creencias.A_CUBIERTO] = False
            jugador[Creencias.TIPO_COBERTURA] = []
            jugador[Creencias.HOSTIGADO] = False
            nuevo_jug[c] = jugador
        return nuevo_jug

    async def setup(self):
        print(f"{self.jid} configurado.")
        self.bdicycle = self.BDICycle()
        self.add_behaviour(self.bdicycle)


