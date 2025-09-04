from abc import ABC, abstractmethod
from xcomagents.agents.creencias import Creencias
from xcomagents.agents.intenciones import IntencionFinalizarTurno, IntencionExplorarAgresiva, IntencionExplorarDefensiva, IntencionNeutralizarEnemigoAgresiva, IntencionNeutralizarEnemigoEstrategica, IntencionNeutralizarEnemigoFrancotirador, IntencionObjetivoHolografico, IntencionExplorarFrancotirador, IntencionHuir, IntencionCurarAliado, IntencionPedirAyuda
from xcomagents.domain import TipoDeseo


class Deseo(ABC):
    @abstractmethod
    def comprobarAlcanzado(self, creencias):
        pass

    @abstractmethod
    def comprobarImposible(self, creencias):
        pass

    @abstractmethod
    def comprobarInteres(self, creencias):
        pass

    @abstractmethod
    def comprobarActivar(self, creencias):
        pass

    def generarIntencion(self):
        pass

class DeseoFinalizarTurno(Deseo):
    def __init__(self):
        self.activo = False
        self.tipo = TipoDeseo.FINALIZAR_TURNO
        
    def comprobarAlcanzado(self, creencias):
        return False
    def comprobarImposible(self, creencias):
        return False
    def comprobarInteres(self, creencias):
        if not creencias[Creencias.PUEDO_ACTUAR] and not creencias[Creencias.PUEDO_MOVERME]:
            return True
        return False
    def comprobarActivar(self, creencias):
        return self.comprobarInteres(creencias)
    
    def generarIntencion(self):
        return [IntencionFinalizarTurno()]
    
class DeseoExplorar(Deseo):
    def __init__(self):
        self.activo = False
        self.tipo = TipoDeseo.EXPLORAR
        
    def comprobarAlcanzado(self, creencias):
        if creencias[Creencias.ENEMIGOS]:
            return True
        return False
    def comprobarImposible(self, creencias):
        return False
    def comprobarInteres(self, creencias):
        if not creencias[Creencias.ENEMIGOS]:
            return True
        return False
    def comprobarActivar(self, creencias):
        if self.comprobarInteres(creencias) and (creencias[Creencias.PUEDO_MOVERME] or creencias[Creencias.PUEDO_ACTUAR]):
            return True
        return False
    
    def generarIntencion(self):
        return [IntencionExplorarDefensiva(), IntencionExplorarAgresiva(), IntencionExplorarFrancotirador()]

class DeseoNeutralizarEnemigo(Deseo):
    def __init__(self):
        self.activo = False
        self.tipo = TipoDeseo.NEUTRALIZAR
        
    def comprobarAlcanzado(self, creencias):
        if len(creencias[Creencias.ENEMIGOS_MUERTOS]) == 4:
            return True
        return False
    def comprobarImposible(self, creencias):
        if not creencias[Creencias.ENEMIGOS]:
            return True
        return False
    def comprobarInteres(self, creencias):
        if creencias[Creencias.ENEMIGOS]:
            return True
        return False
    def comprobarActivar(self, creencias):
        if self.comprobarInteres(creencias) and (creencias[Creencias.PUEDO_MOVERME] or creencias[Creencias.PUEDO_ACTUAR]):
            return True
        return False
    
    def generarIntencion(self):
        return [IntencionNeutralizarEnemigoFrancotirador(), IntencionNeutralizarEnemigoAgresiva(),IntencionNeutralizarEnemigoEstrategica()]

class DeseoObjetivoHolografico(Deseo):
    def __init__(self):
        self.activo = False
        self.tipo = TipoDeseo.HOLOGRAFICO
        
    def comprobarAlcanzado(self, creencias):
        if not creencias[Creencias.HOLOGRAFICO]:
            return True
        return False
    def comprobarImposible(self, creencias):
        if not creencias[Creencias.HOLOGRAFICO]:
            return True
        return False
    def comprobarInteres(self, creencias):
        if creencias[Creencias.HOLOGRAFICO] and creencias[Creencias.ENEMIGOS]:
            return True
        return False
    def comprobarActivar(self, creencias):
        if self.comprobarInteres(creencias) and creencias[Creencias.PUEDO_ACTUAR]:
            return True
        return False
    
    def generarIntencion(self):
        return [IntencionObjetivoHolografico()]
    

class DeseoPedirAyuda(Deseo):
    def __init__(self):
        self.activo = False
        self.tipo = TipoDeseo.PEDIR_AYUDA
        
    def comprobarAlcanzado(self, creencias):
        if creencias[Creencias.AYUDA_PEDIDA] or creencias[Creencias.AYUDA_ACEPTADA]:
            return True
        return False
    def comprobarImposible(self, creencias):
        if creencias[Creencias.SOPORTE] not in creencias[Creencias.ALIADOS].keys():
            return True
        return False
    def comprobarInteres(self, creencias):
        if not creencias[Creencias.AYUDA_PEDIDA] and creencias[Creencias.VIDA] < 7:
            return True
        return False
    def comprobarActivar(self, creencias):
        if self.comprobarInteres(creencias):
            return True
        return False
    
    def generarIntencion(self):
        return [IntencionPedirAyuda()]

class DeseoCurarAliado(Deseo):
    def __init__(self):
        self.activo = False
        self.tipo = TipoDeseo.CURAR
        
    def comprobarAlcanzado(self, creencias):
        if creencias[Creencias.BOTIQUIN] == 0:
            return True
        return False
    def comprobarImposible(self, creencias):
        if creencias[Creencias.BOTIQUIN] == 0:
            return True
        return False
    def comprobarInteres(self, creencias):
        if creencias[Creencias.BOTIQUIN] > 0:
            for c in creencias[Creencias.ALIADOS].keys():
                if creencias[Creencias.ALIADOS][c][Creencias.VIDA] < 7:
                    return True
        return False
    def comprobarActivar(self, creencias):
        if self.comprobarInteres(creencias) and (creencias[Creencias.PUEDO_MOVERME] or creencias[Creencias.PUEDO_ACTUAR]):
            return True
        return False
    
    def generarIntencion(self):
        return [IntencionCurarAliado()]

class DeseoHuir(Deseo):
    def __init__(self):
        self.activo = False
        self.tipo = TipoDeseo.HUIR
        
    def comprobarAlcanzado(self, creencias):
        return False
    def comprobarImposible(self, creencias):
        return False
    def comprobarInteres(self, creencias):
        if creencias[Creencias.ENEMIGOS] and len(creencias[Creencias.ALIADOS]) < 3:
            return True
        return False
    def comprobarActivar(self, creencias):
        if self.comprobarInteres(creencias) and (creencias[Creencias.PUEDO_ACTUAR] or creencias[Creencias.PUEDO_MOVERME]):
            return True
        return False
    
    def generarIntencion(self):
        return [IntencionHuir()]