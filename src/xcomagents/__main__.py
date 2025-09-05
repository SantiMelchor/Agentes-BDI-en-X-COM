import asyncio
import spade
import gc
from multiprocessing import Process, get_start_method, Queue
from pathlib import Path

from xcomagents.agents import XCOMAgent,Clases,Equipo, Tablero
from xcomagents.config import config, data, mapa, jugadores
from xcomagents.genetics import *
import json

BASE_DIR = Path(__file__).resolve().parent
RAIZ = BASE_DIR.parent.parent


async def iteracion(i,roles):
        roles_agente = []
        for k in range(8):
            act_rol = {}
            for h in range(5):
                pos = k*5 + h
                if pos % 5 == 0:
                    act_rol["agresividad"] = roles[pos]
                elif pos %5 == 1:
                    act_rol["rango"] = roles[pos]
                elif pos%5 == 2:
                    act_rol["miedo"] = roles[pos]
                elif pos%5 == 3:
                    act_rol["egoismo"] = roles[pos]
                else:
                    act_rol["estrategia"] = roles[pos]
            roles_agente.append(act_rol)
        agentes = []
        roles_azul = roles_agente[:4]
        roles_rojo = roles_agente[4:]
        jids = {}
        ticket = 0
        ticket2 = 0
        for key,value in config.items():
            if key != "tablero":
                if value["equipo"] == Equipo.AZUL:
                    rol = roles_azul[ticket]
                    ticket += 1
                else:
                    rol = roles_rojo[ticket2]
                    ticket2 += 1
                agentes.append(XCOMAgent(jid=f"{key}_{i}@localhost", password=str(value["pass"]), roles=rol, clase=value["clase"], team=value["equipo"], tablero=f"tablero_{i}@localhost", posicion=value["posicion"], arma=value["arma"], soporte=f"soporteazul_{i}" if value["equipo"] == Equipo.AZUL else f"soporterojo_{i}"))
                jids[f"{key}_{i}"] = f"{key}_{i}@localhost"
        copia_jugadores = {}
        for c,v in jugadores.items():
            copia_jugadores[f"{c}_{i}"] = v
        copia_equipoAzul = []
        for j in data["equipoAzul"]:
            copia_equipoAzul.append(f"{j}_{i}")
        
        copia_equipoRojo = []
        for j in data["equipoRojo"]:
            copia_equipoRojo.append(f"{j}_{i}")
        agentes.append(Tablero(jid=f"tablero_{i}@localhost", password=str(config["tablero"]["pass"]), jids=jids.copy(), equipoAzul=copia_equipoAzul, equipoRojo=copia_equipoRojo, jugs=copia_jugadores.copy()))

        for agente in agentes:
            await agente.start()

        for agente in agentes:
            await agente.bdicycle.join()
        
        # assert agentes[-1].bdicycle.exit_code == 1

        for agente in agentes:
            await agente.stop()
 
        await asyncio.sleep(0)

        
        vida_perdida= agentes[-1].vida_perdida
        vida_eliminada= agentes[-1].vida_eliminada

        for i in range(len(agentes) - 1, -1, -1):
            del agentes[i]
        agentes.clear()
        gc.collect()

        return vida_eliminada,vida_perdida

   

def hilo(cola, i, roles):
    resultado = asyncio.run(iteracion(i,roles))
    cola.put(resultado)

def main():
    #PARAMETROS A CAMBIAR PARA LAS SIMULACIONES
    #+++++++++++++++++++++++++++++++++++++++++++
    mejores_a_guardar = 3
    generations = 150
    iteraciones = 10
    individuos_por_gen = 50
    seed = None #Si no se quiere seed poner None
    filename = "listas-50-150-k5-rseed.json"
    #+++++++++++++++++++++++++++++++++++++++++++

    #ORQUESTACION
    #--------------------------------------------------------------
    directory = RAIZ / "/".join(["data",filename])
    data = {}
    data["soluciones"] = {}
    population = generate_pop(individuos_por_gen,8,5,seed)
    primeros = []
    ultimos = []
    media = []
    for g in range(generations - 1):
        for a in population:
            vida_perdida_total = 0
            vida_eliminada_total = 0

            hilos = []
            cola = Queue()

            for i in range(iteraciones):
                p= Process(target=hilo,args=(cola, i, a.values))
                hilos.append(p)
            
            for j in hilos:
                j.start()
            
            for j in hilos:
                j.join()
            
            

            for k in range(iteraciones):
                retorno = cola.get()
                vida_perdida_total += retorno[1]
                vida_eliminada_total += retorno[0]

            fit = ((vida_eliminada_total/iteraciones) * 2) - (vida_perdida_total/iteraciones)
            a.fitness = fit
            cola.close()
            cola.join_thread()
        population.sort(reverse=True,key=lambda x: x.fitness)
        primeros.append(population[0].fitness)
        for x in range(mejores_a_guardar):
            cadena = "".join(str(n) for n in population[x].values)
            if cadena in data["soluciones"].keys():
                data["soluciones"][cadena][0] =  data["soluciones"][cadena][0] + 1
                data["soluciones"][cadena][1].append(population[x].fitness)
            else:
                data["soluciones"][cadena] = [1, [population[x].fitness]]
        ultimos.append(population[-1].fitness)
        total = 0
        for f in population:
            total += f.fitness
        media.append(total/len(population))
        data["primeros"] = primeros
        data["ultimos"] = ultimos
        data["media"] = media
        with open(directory, "w") as f:
            json.dump(data,f,indent=4)
        population = new_generation_tournament(population)
    if generations != 0:
        for a in population:
            vida_perdida_total = 0
            vida_eliminada_total = 0
            hilos = []
            cola = Queue()

            for i in range(iteraciones):
                p= Process(target=hilo,args=(cola, i, a.values))
                hilos.append(p)
            
            for j in hilos:
                j.start()
            
            for j in hilos:
                j.join()

            for k in range(iteraciones):
                retorno = cola.get()
                vida_perdida_total += retorno[1]
                vida_eliminada_total += retorno[0]

            fit = ((vida_eliminada_total/iteraciones) * 2) - (vida_perdida_total/iteraciones)
            a.fitness = fit
        population.sort(reverse=True,key=lambda x: x.fitness)
        primeros.append(population[0].fitness)
        for x in range(mejores_a_guardar):
            cadena = "".join(str(n) for n in population[x].values)
            if cadena in data["soluciones"].keys():
                data["soluciones"][cadena][0] =  data["soluciones"][cadena][0] + 1
                data["soluciones"][cadena][1].append(population[x].fitness)
            else:
                data["soluciones"][cadena] = [1, [population[x].fitness]]
        ultimos.append(population[-1].fitness)
        total = 0
        for f in population:
            total += f.fitness
        media.append(total/len(population))
        data["primeros"] = primeros
        data["ultimos"] = ultimos
        data["media"] = media
        with open(directory, "w") as f:
            json.dump(data,f,indent=4)
    print(population)

if __name__ == "__main__":
   get_start_method("spawn")
   main()
