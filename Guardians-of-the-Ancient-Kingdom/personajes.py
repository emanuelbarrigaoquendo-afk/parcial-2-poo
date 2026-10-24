"""
personajes.py
=============
Definición de las clases del sistema "Guardians of the Ancient Kingdom".

Clases incluidas:
    - Personaje (abstracta): características y comportamientos comunes.
    - Guerrero, Mago, Arquero: guardianes con su propia forma de atacar.
    - Combate: administra el enfrentamiento por turnos entre dos personajes.

Este módulo solo DEFINE las clases. No crea personajes ni ejecuta pruebas al
importarse; eso se hace en main.py.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class AtaqueInvalidoError(Exception):
    """Se lanza cuando un ataque no se puede realizar por el estado de los
    personajes (atacante derrotado, objetivo derrotado o ataque a sí mismo)."""



# Clase abstracta Personaje

class Personaje(ABC):
    """Clase base abstracta de todos los guardianes del reino.

    Centraliza lo que comparten todos los personajes (nombre, vida, ataque,
    defensa, recibir daño, estar vivo, mostrar estado) y obliga a las
    subclases a definir su propia forma de atacar mediante `atacar()`.
    """

    VIDA_MINIMA = 0
    VIDA_MAXIMA = 100

    def __init__(self, nombre: str, vida: int, ataque: int, defensa: int):
        # Se asigna mediante los setters para que se apliquen las validaciones.
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa
        self._ultimo_danio_calculado = 0

   
    # Validación auxiliar
    
    @staticmethod
    def _validar_entero(valor, campo: str) -> int:
        """Comprueba que el valor sea un entero (los booleanos no cuentan)."""
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError(
                f"{campo} debe ser un número entero (se recibió {type(valor).__name__})."
            )
        return valor

    
    # Atributos encapsulados: getters y setters con validación
    
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise TypeError(
                f"El nombre debe ser texto (se recibió {type(valor).__name__})."
            )
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor

    @property
    def vida(self) -> int:
        return self._vida

    @vida.setter
    def vida(self, valor: int) -> None:
        self._validar_entero(valor, "La vida")
        if not (self.VIDA_MINIMA <= valor <= self.VIDA_MAXIMA):
            raise ValueError(
                f"La vida debe estar entre {self.VIDA_MINIMA} y {self.VIDA_MAXIMA} "
                f"(se recibió {valor})."
            )
        self._vida = valor

    @property
    def ataque(self) -> int:
        return self._ataque

    @ataque.setter
    def ataque(self, valor: int) -> None:
        self._validar_entero(valor, "El ataque")
        if valor <= 0:
            raise ValueError(f"El ataque debe ser un entero positivo (se recibió {valor}).")
        self._ataque = valor

    @property
    def defensa(self) -> int:
        return self._defensa

    @defensa.setter
    def defensa(self, valor: int) -> None:
        self._validar_entero(valor, "La defensa")
        if valor < 0:
            raise ValueError(f"La defensa no puede ser negativa (se recibió {valor}).")
        self._defensa = valor

    @property
    def ultimo_danio_calculado(self) -> int:
        """Daño que calculó el último ataque (antes de limitarlo por la vida
        que le quedaba al objetivo). Solo lectura."""
        return self._ultimo_danio_calculado

    
    # Comportamientos comunes
    
    def recibir_danio(self, cantidad: int) -> int:
        """Descuenta `cantidad` de vida y devuelve el daño efectivamente recibido.

        La cantidad ya llega calculada (la defensa NO se descuenta de nuevo).
        La vida nunca baja de cero: si el daño supera la vida restante, solo
        se recibe lo que quedaba.
        """
        self._validar_entero(cantidad, "El daño")
        if cantidad < 0:
            raise ValueError(f"El daño no puede ser negativo (se recibió {cantidad}).")
        danio_efectivo = min(cantidad, self._vida)
        self._vida -= danio_efectivo
        return danio_efectivo

    def esta_vivo(self) -> bool:
        """True si el personaje conserva vida; False si fue derrotado."""
        return self._vida > 0

    def mostrar_estado(self, imprimir: bool = True) -> str:
        """Devuelve (y por defecto imprime) el estado actual del personaje."""
        situacion = "vivo" if self.esta_vivo() else "derrotado"
        texto = (
            f"[{type(self).__name__}] {self.nombre} - Vida: {self.vida} | "
            f"Ataque: {self.ataque} | Defensa: {self.defensa} | {situacion}"
        )
        if imprimir:
            print(texto)
        return texto

    
    # Apoyo para las subclases (lógica compartida de cualquier ataque)
    
    def _validar_ataque(self, objetivo: "Personaje") -> None:
        """Validaciones comunes que deben cumplirse antes de atacar."""
        if not isinstance(objetivo, Personaje):
            raise TypeError(
                f"El objetivo debe ser un Personaje (se recibió {type(objetivo).__name__})."
            )
        if objetivo is self:
            raise AtaqueInvalidoError("Un personaje no puede atacarse a sí mismo.")
        if not self.esta_vivo():
            raise AtaqueInvalidoError(f"{self.nombre} está derrotado y no puede atacar.")
        if not objetivo.esta_vivo():
            raise AtaqueInvalidoError(
                f"{objetivo.nombre} ya está derrotado y no puede ser atacado."
            )

    def _aplicar_danio(self, objetivo: "Personaje", danio_calculado: int) -> int:
        """Entrega el daño ya calculado al objetivo y devuelve el daño efectivo.
        Garantiza que el daño nunca sea negativo."""
        self._ultimo_danio_calculado = max(0, danio_calculado)
        return objetivo.recibir_danio(self._ultimo_danio_calculado)

    
    # Método abstracto: cada guardián ataca a su manera
    
    @abstractmethod
    def atacar(self, objetivo: "Personaje") -> int:
        """Ataca al objetivo y devuelve el daño efectivo que recibió.
        Cada subclase está obligada a implementarlo."""

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(nombre={self.nombre!r}, vida={self.vida}, "
            f"ataque={self.ataque}, defensa={self.defensa})"
        )



# Subclases

class Guerrero(Personaje):
    """Golpe poderoso: su ataque aumenta un 20 % antes de restar la defensa.

    Daño = max(0, ataque * 1.20 - defensa del objetivo), redondeado hacia abajo.
    """

    BONO_PORCENTUAL = 20

    def atacar(self, objetivo: Personaje) -> int:
        self._validar_ataque(objetivo)
        # Aritmética entera: evita errores de redondeo de los decimales.
        # (ataque * 120) // 100 equivale a floor(ataque * 1.20).
        ataque_potenciado = self.ataque * (100 + self.BONO_PORCENTUAL) // 100
        danio = max(0, ataque_potenciado - objetivo.defensa)
        return self._aplicar_danio(objetivo, danio)


class Mago(Personaje):
    """Hechizo penetrante: ignora por completo la defensa del objetivo.

    Daño = ataque del Mago.
    """

    def atacar(self, objetivo: Personaje) -> int:
        self._validar_ataque(objetivo)
        danio = self.ataque
        return self._aplicar_danio(objetivo, danio)


class Arquero(Personaje):
    """Disparo crítico: si su ataque supera la defensa, duplica el daño.

    Daño base = max(0, ataque - defensa del objetivo)
    Daño final = daño base * 2 cuando el ataque supera la defensa; si no, 0.
    """

    MULTIPLICADOR_CRITICO = 2

    def atacar(self, objetivo: Personaje) -> int:
        self._validar_ataque(objetivo)
        danio_base = max(0, self.ataque - objetivo.defensa)
        if self.ataque > objetivo.defensa:
            danio = danio_base * self.MULTIPLICADOR_CRITICO
        else:
            danio = 0
        return self._aplicar_danio(objetivo, danio)



# Clase Combate

class Combate:
    """Administra un enfrentamiento por turnos entre dos personajes.

    Los personajes se crean por fuera y se le entregan al combate (agregación).
    Combate solo conoce la interfaz de Personaje (`atacar`, `esta_vivo`,
    `mostrar_estado`), así que nunca pregunta si alguien es Guerrero, Mago o
    Arquero: el polimorfismo decide cómo ataca cada uno.
    """

    MAX_RONDAS = 50

    VICTORIA = "victoria"
    EMPATE_TECNICO = "empate técnico"
    EMPATE_POR_RONDAS = "empate por límite de rondas"

    def __init__(self, personaje1: Personaje, personaje2: Personaje, verbose: bool = True):
        for personaje in (personaje1, personaje2):
            if not isinstance(personaje, Personaje):
                raise TypeError(
                    f"Los participantes deben ser Personaje (se recibió {type(personaje).__name__})."
                )
        if personaje1 is personaje2:
            raise ValueError("Un combate necesita dos personajes distintos.")
        if not (personaje1.esta_vivo() and personaje2.esta_vivo()):
            raise ValueError("Ambos personajes deben estar vivos para iniciar un combate.")

        self._participantes: Tuple[Personaje, Personaje] = (personaje1, personaje2)
        self._verbose = verbose
        self._indice_turno = 0          # 0: ataca personaje1, 1: ataca personaje2
        self._turnos = 0
        self._rondas_completadas = 0
        self._danio_en_ronda = 0
        self._ganador: Optional[Personaje] = None
        self._resultado: Optional[str] = None
        self._historial: List[Dict] = []

    
    # Consulta del estado del combate
    
    @property
    def atacante(self) -> Personaje:
        return self._participantes[self._indice_turno]

    @property
    def defensor(self) -> Personaje:
        return self._participantes[1 - self._indice_turno]

    @property
    def ganador(self) -> Optional[Personaje]:
        return self._ganador

    @property
    def resultado(self) -> Optional[str]:
        return self._resultado

    @property
    def turnos(self) -> int:
        return self._turnos

    @property
    def rondas_completadas(self) -> int:
        return self._rondas_completadas

    @property
    def historial(self) -> List[Dict]:
        """Copia del registro turno por turno del combate."""
        return [dict(registro) for registro in self._historial]

    def _imprimir(self, texto: str = "") -> None:
        if self._verbose:
            print(texto)

    
    # Métodos requeridos
    
    def iniciar(self) -> Optional[Personaje]:
        """Ejecuta el combate por turnos hasta que termine.
        Devuelve el ganador, o None si hubo empate."""
        if self._resultado is not None:
            raise RuntimeError("Este combate ya finalizó.")

        p1, p2 = self._participantes
        self._imprimir(f"=== COMBATE: {p1.nombre} vs {p2.nombre} ===")
        if self._verbose:
            p1.mostrar_estado()
            p2.mostrar_estado()
            print()

        while self._resultado is None:
            self._jugar_turno()

        self.mostrar_resultado()
        return self._ganador

    def cambiar_turno(self) -> None:
        """Alterna el personaje que debe atacar."""
        self._indice_turno = 1 - self._indice_turno

    def verificar_ganador(self) -> Optional[Personaje]:
        """Devuelve el personaje vencedor si el otro fue derrotado; si no, None."""
        p1, p2 = self._participantes
        if p1.esta_vivo() and not p2.esta_vivo():
            return p1
        if p2.esta_vivo() and not p1.esta_vivo():
            return p2
        return None

    def mostrar_resultado(self) -> None:
        """Presenta el resultado final del combate."""
        if self._resultado is None:
            print("El combate todavía no ha finalizado.")
            return

        print("=" * 50)
        print("RESULTADO FINAL")
        print("=" * 50)
        if self._resultado == self.VICTORIA:
            g = self._ganador
            print(
                f"Ganador: {g.nombre} ({type(g).__name__}) con {g.vida} "
                f"punto(s) de vida restante(s)."
            )
        elif self._resultado == self.EMPATE_TECNICO:
            print("Empate técnico: ambos personajes completaron una ronda sin causarse daño.")
        else:
            print(f"Empate: se completaron {self.MAX_RONDAS} rondas sin un ganador.")
        print(f"Turnos jugados: {self._turnos} | Rondas completadas: {self._rondas_completadas}")

    
    # Lógica interna de un turno
    
    def _jugar_turno(self) -> None:
        atacante, defensor = self.atacante, self.defensor

        danio_efectivo = atacante.atacar(defensor)   # polimorfismo
        self._turnos += 1
        self._danio_en_ronda += danio_efectivo
        calculado = atacante.ultimo_danio_calculado

        self._registrar_turno(atacante, defensor, calculado, danio_efectivo)
        self._mostrar_turno(atacante, defensor, calculado, danio_efectivo)

        # Una ronda se completa cuando ataca el segundo participante.
        ronda_completa = self._indice_turno == 1
        if ronda_completa:
            self._rondas_completadas += 1

        ganador = self.verificar_ganador()
        if ganador is not None:
            self._ganador = ganador
            self._resultado = self.VICTORIA
            return

        if ronda_completa:
            if self._danio_en_ronda == 0:
                self._resultado = self.EMPATE_TECNICO
            elif self._rondas_completadas >= self.MAX_RONDAS:
                self._resultado = self.EMPATE_POR_RONDAS
            self._danio_en_ronda = 0

        self.cambiar_turno()

    def _registrar_turno(self, atacante, defensor, calculado, efectivo) -> None:
        p1, p2 = self._participantes
        self._historial.append({
            "turno": self._turnos,
            "ronda": (self._turnos + 1) // 2,
            "atacante": atacante.nombre,
            "objetivo": defensor.nombre,
            "danio_calculado": calculado,
            "danio_efectivo": efectivo,
            "vidas": (p1.vida, p2.vida),
        })

    def _mostrar_turno(self, atacante, defensor, calculado, efectivo) -> None:
        if not self._verbose:
            return
        ronda = (self._turnos + 1) // 2
        if efectivo == calculado:
            detalle = f"daño {efectivo}"
        else:
            detalle = f"daño {efectivo} efectivo (calculado: {calculado})"
        print(f"Turno {self._turnos} (Ronda {ronda}): {atacante.nombre} ataca a "
              f"{defensor.nombre} -> {detalle}")
        for personaje in self._participantes:
            print("   ", end="")
            personaje.mostrar_estado()
        print()
