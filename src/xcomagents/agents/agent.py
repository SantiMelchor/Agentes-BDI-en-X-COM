import asyncio
import time
import json
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from xcomagents.domain import Clases,Equipo, Mapa, Ontologia, TipoCobertura, TipoAccion, TipoArma, TipoDeseo
from xcomagents.agents.creencias import Creencias
from xcomagents.agents.deseos import DeseoFinalizarTurno, DeseoExplorar, DeseoNeutralizarEnemigo, DeseoObjetivoHolografico, DeseoHuir, DeseoCurarAliado, DeseoPedirAyuda
from xcomagents.utils.utils import createMessage


class XCOMAgent(Agent):
    class BDICycle(CyclicBehaviour):
        async def actualizarCreencias(self,msg):
            
            contenido = json.loads(msg.body)
            print(f"Actualizando mis creencias con el mensaje recibido: {contenido} ")
            if msg.get_metadata("ontology") == Ontologia.TURNO:
                print("Reseteando turno")
                if self.creencias[Creencias.CLASE] == Clases.FRANCOTIRADOR:
                    self.creencias[Creencias.PREGUNTADOS] = []
                if not self.creencias[Creencias.AYUDA_ACEPTADA]:
                    self.creencias[Creencias.AYUDA_PEDIDA] = False
                self.creencias[Creencias.PUEDO_ACTUAR] = True
                self.creencias[Creencias.PUEDO_MOVERME] = True
                self.creencias[Creencias.MI_TURNO] = contenido[Creencias.MI_TURNO]
                self.creencias[Creencias.DEFENSA] = 0
                self.creencias[Creencias.VIDA] = contenido[Creencias.VIDA]
                pos_enemigos = []
                new_enemigos = {}
                new_aliados = {}
                pos_aliados = []
                for enemy in contenido[Creencias.ENEMIGOS]:
                    new_enemigos[enemy[0]] = enemy[1]
                    pos_enemigos.append(tuple(enemy[1][Creencias.POSICION]))
                for ally in contenido[Creencias.ALIADOS]:
                    new_aliados[ally[0]] = ally[1]
                    pos_aliados.append(tuple(ally[1][Creencias.POSICION]))
                #print(new_enemigos)
                self.creencias[Creencias.MAPA].actualizar_aliados(pos_aliados)
                self.creencias[Creencias.MAPA].actualizar_enemigos(pos_enemigos)
                self.creencias[Creencias.ENEMIGOS] = new_enemigos
                self.creencias[Creencias.ALIADOS] = new_aliados
            elif msg.get_metadata("ontology") == Ontologia.MOVIMIENTO:
                print("Actualizando mi posicion")
                if msg.get_metadata("performative") == "inform-result":
                    posicion = contenido[Creencias.POSICION]
                    self.creencias[Creencias.PUEDO_MOVERME] = False
                    nueva_vision = Mapa.crear_mapa(str(self.agent.jid), posicion)
                    self.creencias[Creencias.MAPA].actualizar_mapa(nueva_vision)
                    self.creencias[Creencias.MAPA].actualizar_posicion(posicion)
                    self.creencias[Creencias.POSICION] = posicion
                    self.creencias[Creencias.A_CUBIERTO] = contenido[Creencias.A_CUBIERTO]
                    tipo_coberturas = []
                    for cob in contenido[Creencias.TIPO_COBERTURA]:
                        tipo_coberturas.append(TipoCobertura[cob])
                    self.creencias[Creencias.TIPO_COBERTURA] = tipo_coberturas
                    pos_enemigos = []
                    new_enemigos = {}
                    new_aliados = {}
                    pos_aliados = []
                    for enemy in contenido[Creencias.ENEMIGOS]:
                        new_enemigos[enemy[0]] = enemy[1]
                        pos_enemigos.append(tuple(enemy[1][Creencias.POSICION]))
                    for ally in contenido[Creencias.ALIADOS]:
                        new_aliados[ally[0]] = ally[1]
                        pos_aliados.append(tuple(ally[1][Creencias.POSICION]))
                    self.creencias[Creencias.MAPA].actualizar_enemigos(pos_enemigos)
                    self.creencias[Creencias.MAPA].actualizar_aliados(pos_aliados)
                    self.creencias[Creencias.ENEMIGOS] = new_enemigos
                    self.creencias[Creencias.ALIADOS] = new_aliados
            elif msg.get_metadata("ontology") == Ontologia.ACCION:
                accion = TipoAccion[contenido[Creencias.ACCION]]
                #print(accion)
                if accion == TipoAccion.DEFENDERSE:
                    print("Actualizando mi defensa")
                    if msg.get_metadata("performative") == "inform-result":
                        self.creencias[Creencias.DEFENSA] = contenido[Creencias.DEFENSA]
                        self.creencias[Creencias.PUEDO_ACTUAR] = False
                elif accion == TipoAccion.CORRER:
                    print("Actualizando mi posicion despues de correr")
                    if msg.get_metadata("performative") == "inform-result":
                        posicion = contenido[Creencias.POSICION]
                        self.creencias[Creencias.PUEDO_ACTUAR] = False
                        nueva_vision = Mapa.crear_mapa(str(self.agent.jid), posicion)
                        self.creencias[Creencias.MAPA].actualizar_mapa(nueva_vision)
                        self.creencias[Creencias.MAPA].actualizar_posicion(posicion)
                        self.creencias[Creencias.POSICION] = posicion
                        self.creencias[Creencias.A_CUBIERTO] = contenido[Creencias.A_CUBIERTO]
                        tipo_coberturas = []
                        for cob in contenido[Creencias.TIPO_COBERTURA]:
                            tipo_coberturas.append(TipoCobertura[cob])
                        self.creencias[Creencias.TIPO_COBERTURA] = tipo_coberturas
                        pos_enemigos = []
                        new_enemigos = {}
                        new_aliados = {}
                        pos_aliados = []
                        for enemy in contenido[Creencias.ENEMIGOS]:
                            new_enemigos[enemy[0]] = enemy[1]
                            pos_enemigos.append(tuple(enemy[1][Creencias.POSICION]))
                        for ally in contenido[Creencias.ALIADOS]:
                            new_aliados[ally[0]] = ally[1]
                            pos_aliados.append(tuple(ally[1][Creencias.POSICION]))
                        self.creencias[Creencias.MAPA].actualizar_enemigos(pos_enemigos)
                        self.creencias[Creencias.MAPA].actualizar_aliados(pos_aliados)
                        print(new_enemigos)
                        self.creencias[Creencias.ENEMIGOS] = new_enemigos
                        self.creencias[Creencias.ALIADOS] = new_aliados
                elif accion == TipoAccion.RECARGAR:
                    print("Actualizando mi arma")
                    if msg.get_metadata("performative") == "inform-result":
                        self.creencias[Creencias.PUEDO_ACTUAR] = False
                        if self.creencias[Creencias.ARMA][0] == TipoArma.ESCOPETA or self.creencias[Creencias.ARMA][0] == TipoArma.METRALLETA:
                            self.creencias[Creencias.ARMA] = (self.creencias[Creencias.ARMA][0], 3, self.creencias[Creencias.ARMA][2])
                        elif self.creencias[Creencias.ARMA][0] == TipoArma.FRANCOTIRADOR:
                            self.creencias[Creencias.ARMA] = (self.creencias[Creencias.ARMA][0], 2, self.creencias[Creencias.ARMA][2])
                        elif self.creencias[Creencias.ARMA][0] == TipoArma.RIFLE:
                            self.creencias[Creencias.ARMA] = (self.creencias[Creencias.ARMA][0], 4, self.creencias[Creencias.ARMA][2])
                elif accion == TipoAccion.DISPARAR:
                    print("Actualizando mis enemigos y mi arma despues de disparar")
                    if msg.get_metadata("performative") == "inform-result":
                        if self.creencias[Creencias.CLASE] == Clases.FRANCOTIRADOR:
                            self.creencias[Creencias.PUEDO_MOVERME] = False
                        self.creencias[Creencias.PUEDO_ACTUAR] = False
                        self.creencias[Creencias.ARMA] = (self.creencias[Creencias.ARMA][0],self.creencias[Creencias.ARMA][1] - 1, self.creencias[Creencias.ARMA][2])
                        if not contenido[Creencias.ENEMIGOS][1]: 
                            del self.creencias[Creencias.ENEMIGOS][contenido[Creencias.ENEMIGOS][0]]
                        else:
                            self.creencias[Creencias.ENEMIGOS][contenido[Creencias.ENEMIGOS][0]] = contenido[Creencias.ENEMIGOS][1]
                    elif msg.get_metadata("performative") == "failure":
                        if contenido[Creencias.TIPO_FALLO] == Creencias.DISPARO_FALLADO:
                            if self.creencias[Creencias.CLASE] == Clases.FRANCOTIRADOR:
                                self.creencias[Creencias.PUEDO_MOVERME] = False
                            self.creencias[Creencias.PUEDO_ACTUAR] = False
                            self.creencias[Creencias.ARMA] = (self.creencias[Creencias.ARMA][0],self.creencias[Creencias.ARMA][1] - 1, self.creencias[Creencias.ARMA][2])
                elif accion == TipoAccion.HOLOGRAFICO:
                    print("Actualizando mi dron")
                    if msg.get_metadata("performative") == "inform-result":
                        self.creencias[Creencias.PUEDO_ACTUAR] = False
                        self.creencias[Creencias.HOLOGRAFICO] = False
                elif accion == TipoAccion.CURAR:
                    print("Actualizando mi botiquin")
                    if msg.get_metadata("performative") == "inform-result":
                        self.creencias[Creencias.PUEDO_ACTUAR] = False
                        self.creencias[Creencias.BOTIQUIN] -= 1
                        if self.creencias[Creencias.PROMESA_AYUDA]:
                            msg = createMessage(f"{self.creencias[Creencias.OBJETIVO_CURACION]}@localhost","inform-done", Ontologia.AYUDA, {})
                            await self.send(msg)
                        self.creencias[Creencias.OBJETIVO_CURACION] = None
                        self.creencias[Creencias.PROMESA_AYUDA] = False
                    elif msg.get_metadata("performative") == "failure":
                        self.creencias[Creencias.PUEDO_ACTUAR] = False
                        self.creencias[Creencias.BOTIQUIN] = 0
                        self.creencias[Creencias.OBJETIVO_CURACION] = None
                        self.creencias[Creencias.PROMESA_AYUDA] = False
            elif msg.get_metadata("ontology") == Ontologia.MUERTE:
                myself = str(self.agent.jid).split("@")[0]
                if contenido[Creencias.OBJETIVO] == myself:
                    print("He muerto")
                    self.muerte = True
                else:
                    if Equipo[contenido[Creencias.EQUIPO]] == self.creencias[Creencias.EQUIPO]:
                        print("Un aliado ha muerto")
                        del self.creencias[Creencias.ALIADOS][contenido[Creencias.OBJETIVO]]
                    else:
                        print("Un enemigo ha muerto")
                        a_eliminar = False
                        for i in self.creencias[Creencias.ENEMIGOS].keys():
                            if i == contenido[Creencias.OBJETIVO]:
                                a_eliminar = True
                        if a_eliminar:
                            del self.creencias[Creencias.ENEMIGOS][contenido[Creencias.OBJETIVO]]
                    
            elif msg.get_metadata("ontology") == Ontologia.COMUNICACION:
                if msg.get_metadata("performative") == "query-ref":
                    print("Recibiendo propuesta de intercambio de informacion")
                    if contenido[Creencias.ROLES] > self.creencias[Creencias.ROLES]["rango"]:
                        print("Aceptandola")
                        msg = createMessage(str(msg.sender), "inform-result", Ontologia.COMUNICACION, {Creencias.OBJETIVO: contenido[Creencias.OBJETIVO], Creencias.ENEMIGOS: self.creencias[Creencias.ENEMIGOS]})
                    else:
                        if self.creencias[Creencias.ROLES]["egoismo"] > 4:
                            print(f'Denegandola porque mi egoismo es {self.creencias[Creencias.ROLES]["egoismo"]} y mi rango es {self.creencias[Creencias.ROLES]["rango"]}')
                            msg = createMessage(str(msg.sender), "refuse", Ontologia.COMUNICACION, {Creencias.OBJETIVO: contenido[Creencias.OBJETIVO]} )
                        else:
                            print("Aceptandola")
                            msg = createMessage(str(msg.sender), "inform-result", Ontologia.COMUNICACION, {Creencias.OBJETIVO: contenido[Creencias.OBJETIVO], Creencias.ENEMIGOS: self.creencias[Creencias.ENEMIGOS]} )    
                    await self.send(msg)
                elif msg.get_metadata("performative") == "inform-result":
                    print("Actualizando mis enemigos ddespues el mensaje")
                    self.creencias[Creencias.PREGUNTADOS].append(str(contenido[Creencias.OBJETIVO]))
                    for c,v in contenido[Creencias.ENEMIGOS].items():
                        if c not in self.creencias[Creencias.ENEMIGOS]:
                            self.creencias[Creencias.ENEMIGOS][c] = v
                elif msg.get_metadata("performative") == "refuse":
                    print("Rechazaron mi peticion")
                    self.creencias[Creencias.PREGUNTADOS].append(str(contenido[Creencias.OBJETIVO]))
            elif msg.get_metadata("ontology") == Ontologia.AYUDA:
                if msg.get_metadata("performative") == "request":
                    print("Me pidieron que les cure")
                    if self.creencias[Creencias.CLASE] != Clases.SOPORTE or self.creencias[Creencias.BOTIQUIN] == 0 or self.creencias[Creencias.PROMESA_AYUDA]:
                        print("Rechazando")
                        msg = createMessage(str(msg.sender), "refuse", Ontologia.AYUDA, {})
                    elif self.creencias[Creencias.ROLES]["rango"] < contenido[Creencias.ROLES]:
                        print("Aceptando")
                        self.creencias[Creencias.PROMESA_AYUDA] = True
                        self.creencias[Creencias.OBJETIVO_CURACION] = str(msg.sender).split("@")[0]
                        msg = createMessage(str(msg.sender), "agree",Ontologia.AYUDA, {})
                    else:
                        if self.creencias[Creencias.ROLES]["egoismo"] > 4:
                            print("Rechazando")
                            msg = createMessage(str(msg.sender), "refuse", Ontologia.AYUDA, {} )
                        else:
                            print("Aceptando")
                            self.creencias[Creencias.PROMESA_AYUDA] = True
                            self.creencias[Creencias.OBJETIVO_CURACION] = str(msg.sender).split("@")[0]
                            msg = createMessage(str(msg.sender), "agree", Ontologia.AYUDA, {} )    
                    await self.send(msg)
                elif msg.get_metadata("performative") == "agree":
                    print("Me han aceptado la ayuda")
                    self.creencias[Creencias.AYUDA_PEDIDA] = True
                    self.creencias[Creencias.AYUDA_ACEPTADA] = True

                elif msg.get_metadata("performative") == "refuse":
                    print("Me han rechazado la ayuda")
                    self.creencias[Creencias.AYUDA_PEDIDA] = True

                elif msg.get_metadata("performative") == "inform-done":
                    print("Ya terminaron de ayudarme")
                    self.creencias[Creencias.AYUDA_ACEPTADA] = False

            
                    

            lista = []
            for c,v in self.creencias[Creencias.ALIADOS].items(): 
                lista.append(tuple(v[Creencias.POSICION]))
            if self.creencias[Creencias.PROMESA_AYUDA]:
                if self.creencias[Creencias.OBJETIVO_CURACION] not in self.creencias[Creencias.ALIADOS].keys():
                    self.creencias[Creencias.PROMESA_AYUDA] = False
                    self.creencias[Creencias.OBJETIVO_CURACION] = None
            self.creencias[Creencias.POSICIONES_ALIADAS] = lista
        def actualizarDeseos(self):
            print("Actualizando mis deseos")
            if not self.creencias[Creencias.MI_TURNO]:
                return 
            for deseo in self.deseos:
                
                if deseo.activo:
                    if deseo.comprobarAlcanzado(self.creencias) or deseo.comprobarImposible(self.creencias) or not deseo.comprobarInteres(self.creencias):
                        for i in range(len(self.intenciones) -1, -1, -1):
                            if self.intenciones[i].asociado == deseo.tipo:
                                del self.intenciones[i]
                        deseo.activo = False
                else:
                    if deseo.comprobarActivar(self.creencias):
                        for intencion in deseo.generarIntencion():
                            self.intenciones.append(intencion)
                        deseo.activo = True
        def seleccionarIntencion(self):
            if not self.creencias[Creencias.MI_TURNO]:
                return 
            if len(self.intenciones) > 0:
                print("Seleccionando mis intenciones")
                self.intenciones.sort(reverse=True,key=lambda x: x.calcularPrioridad(self.creencias))
                index = 0
                self.intencion_actual = self.intenciones[index]
                # if self.intencion_actual.tipo == TipoDeseo.NEUTRALIZAR and self.creencias[Creencias.ROLES]["estrategia"] == 10:
                #     while 1:
                #         print()
                while (self.intencion_actual.comprobarAlcanzada(self.creencias) or self.intencion_actual.comprobarAnulada(self.creencias)) and index < len(self.intenciones) - 1:
                    index += 1
                    self.intencion_actual = self.intenciones[index]


        async def ejecutarIntencion(self):
            if not self.creencias[Creencias.MI_TURNO]:
                return 
            if self.intencion_actual:
                print(f"Ejecutando mi intencion actual {self.intencion_actual}")
                msg, creencias = self.intencion_actual.ejecutar(self.agent, self.creencias)
                self.creencias = creencias
                print(f"Enviando mensaje al tablero {msg}")
                await self.send(msg)
                self.intencion_actual = None
            #print(self.creencias)

        async def on_start(self):
            print("Starting")
            self.creencias = self.get("creencias")
            self.intencion_actual = None
            self.deseos = [DeseoFinalizarTurno(), DeseoExplorar(), DeseoNeutralizarEnemigo(), DeseoObjetivoHolografico(), DeseoHuir(), DeseoCurarAliado(), DeseoPedirAyuda()]
            self.intenciones = []
            self.muerte = False

        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                await self.actualizarCreencias(msg)
                if self.muerte:
                    self.kill()
                    return
                self.actualizarDeseos()
                self.seleccionarIntencion()
                await self.ejecutarIntencion()
                return
        
        async def on_end(self):
            print(f"Terminado con codigo {self.exit_code}")
    
    def __init__(self, jid, password, roles, clase, team, tablero, posicion, arma, soporte):
        super().__init__(jid, password)
        creencias = {
            Creencias.ROLES: roles,
            Creencias.CLASE: clase,
            Creencias.EQUIPO: team,
            Creencias.MI_TURNO: False,
            Creencias.TABLERO: tablero,
            Creencias.POSICION: posicion,
            Creencias.MAPA: Mapa.crear_mapa(jid,posicion),
            Creencias.PUEDO_ACTUAR: False,
            Creencias.PUEDO_MOVERME: False,
            Creencias.ENEMIGOS: {},
            Creencias.DEFENSA: 0,
            Creencias.ENEMIGOS_MUERTOS: [],
            Creencias.ARMA: arma,
            Creencias.ALIADOS: {},
            Creencias.POSICIONES_ALIADAS: [],
            Creencias.HOLOGRAFICO: True if clase == Clases.PESADA else False,
            Creencias.PREGUNTADOS: [],
            Creencias.SOPORTE: soporte,
            Creencias.BOTIQUIN: 2 if clase == Clases.SOPORTE else 0,
            Creencias.PROMESA_AYUDA: False,
            Creencias.OBJETIVO_CURACION: None,
            Creencias.AYUDA_PEDIDA: False,
            Creencias.AYUDA_ACEPTADA: False
        }
        self.set("creencias", creencias)


    async def setup(self):
        print(f"{self.jid} configurado.")
        self.bdicycle = self.BDICycle()
        self.add_behaviour(self.bdicycle)


