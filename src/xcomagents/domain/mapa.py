
import random
from xcomagents.config import mapa
from xcomagents.utils import casillas_alcance

class Mapa:
    def __init__(self,mapa = None, posicion = (0,0) ):
        self.mapa = mapa
        self.posicion = posicion
        self.enemigos = []
        self.aliados = []

    @classmethod
    def crear_mapa(cls, jid, posicion = None):
        if str(jid).startswith("tablero"):
            return cls(mapa)
        else:
            vision =casillas_alcance(mapa,6,posicion)
            return cls(vision, posicion)
    

    def actualizar_mapa(self, mapa):
        self.mapa.update(mapa.mapa)

    def actualizar_posicion(self, posicion):
        self.posicion = tuple(posicion)

    def actualizar_enemigos(self,enemigos):
        self.enemigos = enemigos
    
    def actualizar_aliados(self,aliados):
        self.aliados = aliados

    def __str__(self):
        cadena = ""
        for i in range(29, -1, -1):
            cadena += "|"
            for j in range(15):
                if self.posicion == (j,i):
                    cadena += " P"
                    continue
                elif (j,i) in self.enemigos:
                    cadena+= " E"
                    continue
                elif (j,i) in self.aliados:
                    cadena += " A"
                    continue
                try:
                    if self.mapa[(j,i)] == 0 or self.mapa[(j,i)] == -1:
                        cadena+="  "
                    elif self.mapa[(j,i)] == 1:
                        cadena += " x"
                    elif self.mapa[(j,i)] == 2:
                        cadena += " O"
                except KeyError:
                    cadena += "  "
            cadena += "|\n"
        return cadena
            
    



