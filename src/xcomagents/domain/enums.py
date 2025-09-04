from enum import Enum

class Ontologia:
    TURNO= "TURNO"
    MOVIMIENTO = "MOVIMIENTO"
    ACCION = "ACCION"
    MUERTE = "MUERTE"
    COMUNICACION = "COMUNICACION"
    AYUDA = "AYUDA"

class Clases(Enum):
    ASALTO = 1
    FRANCOTIRADOR = 2
    PESADA = 3
    SOPORTE = 4
    TABLERO = 5

class Equipo(Enum):
    ROJO= 1
    AZUL = 2
    TABLERO = 3

class TipoDeseo(Enum):
    FINALIZAR_TURNO = 1
    EXPLORAR = 2
    NEUTRALIZAR = 3
    HOLOGRAFICO = 4
    HUIR = 5
    CURAR = 6
    PEDIR_AYUDA = 7

class TipoAccion(Enum):
    CORRER = 1
    DEFENDERSE = 2
    RECARGAR = 3
    DISPARAR = 4
    HOLOGRAFICO = 5
    CURAR = 6

class TipoCobertura(Enum):
    NORTE = 1
    SUR = 2
    ESTE = 3
    OESTE = 4

class TipoArma(Enum):
    ESCOPETA = 1
    FRANCOTIRADOR = 2
    RIFLE = 3
    METRALLETA = 4