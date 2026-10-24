"""
main.py
=======
Crea personajes, ejecuta combates y comprueba las reglas del sistema
"Guardians of the Ancient Kingdom".

Las clases se importan desde personajes.py; aquí no se repite su implementación.

Uso:
    python main.py
"""

import sys

from personajes import (
    Arquero,
    AtaqueInvalidoError,
    Combate,
    Guerrero,
    Mago,
    Personaje,
)

resultados = []   # (numero_de_caso, descripcion, aprobado)


# Utilidades para mostrar y registrar las comprobaciones

def titulo(numero, texto):
    print()
    print("-" * 64)
    print(f"CASO {numero}: {texto}")
    print("-" * 64)


def comprobar(numero, descripcion, condicion):
    """Registra e imprime el resultado de una comprobación."""
    marca = "OK   " if condicion else "FALLO"
    print(f"  [{marca}] {descripcion}")
    resultados.append((numero, descripcion, bool(condicion)))


def lanza(excepcion, funcion, *args, **kwargs):
    """Ejecuta funcion y devuelve (True, mensaje) si lanza la excepción esperada."""
    try:
        funcion(*args, **kwargs)
    except excepcion as error:
        return True, str(error)
    except Exception as error:   # otra excepción distinta
        return False, f"se lanzó {type(error).__name__} en lugar de {excepcion.__name__}"
    return False, "no se lanzó ninguna excepción"


def comprobar_error(numero, descripcion, excepcion, funcion, *args, **kwargs):
    ok, mensaje = lanza(excepcion, funcion, *args, **kwargs)
    comprobar(numero, f"{descripcion} -> {excepcion.__name__}: {mensaje}" if ok
              else f"{descripcion} ({mensaje})", ok)



# Casos de prueba obligatorios (1 a 12)

def caso_1_creacion():
    titulo(1, "Creación correcta de los tres tipos de personajes")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    legolas = Arquero("Legolas", 90, 35, 15)
    for p in (arthas, gandalf, legolas):
        p.mostrar_estado()
    comprobar(1, "Guerrero, Mago y Arquero se crean con los datos indicados",
              (arthas.nombre, arthas.vida, arthas.ataque, arthas.defensa) == ("Arthas", 100, 30, 20)
              and (gandalf.nombre, gandalf.vida, gandalf.ataque, gandalf.defensa) == ("Gandalf", 80, 40, 10)
              and (legolas.nombre, legolas.vida, legolas.ataque, legolas.defensa) == ("Legolas", 90, 35, 15))
    comprobar(1, "Los tres son instancias de Personaje",
              all(isinstance(p, Personaje) for p in (arthas, gandalf, legolas)))
    comprobar_error(1, "Personaje es abstracta y no se puede instanciar", TypeError,
                    Personaje, "Intruso", 50, 10, 10)


def caso_2_vida_invalida():
    titulo(2, "Rechazo de personajes con vida superior a 100 o negativa")
    comprobar_error(2, "Vida 101", ValueError, Guerrero, "Arthas", 101, 30, 20)
    comprobar_error(2, "Vida 500", ValueError, Mago, "Gandalf", 500, 40, 10)
    comprobar_error(2, "Vida -1", ValueError, Arquero, "Legolas", -1, 35, 15)
    comprobar_error(2, "Vida -50", ValueError, Guerrero, "Arthas", -50, 30, 20)
    guerrero = Guerrero("Arthas", 100, 30, 20)
    comprobar_error(2, "Setter de vida con 150", ValueError, setattr, guerrero, "vida", 150)
    comprobar(2, "Los límites 0 y 100 sí son válidos",
              Guerrero("Limite", 0, 10, 0).vida == 0 and Guerrero("Limite", 100, 10, 0).vida == 100)


def caso_3_nombre_vacio():
    titulo(3, "Rechazo de nombres vacíos")
    comprobar_error(3, "Nombre ''", ValueError, Guerrero, "", 100, 30, 20)
    comprobar_error(3, "Nombre solo con espacios", ValueError, Mago, "   ", 80, 40, 10)
    comprobar_error(3, "Nombre que no es texto (123)", TypeError, Arquero, 123, 90, 35, 15)
    mago = Mago("Gandalf", 80, 40, 10)
    comprobar_error(3, "Setter de nombre con ''", ValueError, setattr, mago, "nombre", "")


def caso_4_ataque_defensa_invalidos():
    titulo(4, "Rechazo de ataques y defensas inválidos")
    comprobar_error(4, "Ataque 0 (debe ser positivo)", ValueError, Guerrero, "A", 100, 0, 10)
    comprobar_error(4, "Ataque negativo (-10)", ValueError, Mago, "B", 100, -10, 10)
    comprobar_error(4, "Defensa negativa (-1)", ValueError, Arquero, "C", 100, 30, -1)
    comprobar_error(4, "Ataque no entero ('fuerte')", TypeError, Guerrero, "D", 100, "fuerte", 10)
    comprobar_error(4, "Defensa decimal (3.5)", TypeError, Mago, "E", 100, 30, 3.5)
    comprobar(4, "Defensa 0 sí es válida", Guerrero("F", 100, 30, 0).defensa == 0)


def caso_5_habilidad_guerrero():
    titulo(5, "Habilidad del Guerrero: ataque +20 % antes de la defensa")
    guerrero = Guerrero("Arthas", 100, 30, 20)
    objetivo = Mago("Dummy", 80, 40, 10)
    danio = guerrero.atacar(objetivo)
    print(f"  Ataque 30 vs defensa 10 -> daño {danio}, vida del objetivo: {objetivo.vida}")
    comprobar(5, "Ataque 30 vs defensa 10 produce 26 de daño", danio == 26 and objetivo.vida == 54)

    # 33 * 1.20 = 39.6 -> se redondea hacia abajo (39) y luego se resta la defensa (10)
    guerrero2 = Guerrero("Redondeo", 100, 33, 5)
    objetivo2 = Mago("Dummy2", 100, 40, 10)
    danio2 = guerrero2.atacar(objetivo2)
    print(f"  Ataque 33 vs defensa 10 -> daño {danio2} (39.6 redondeado hacia abajo)")
    comprobar(5, "Los decimales se redondean hacia abajo (33 * 1.2 = 39.6 -> 39 - 10 = 29)", danio2 == 29)

    guerrero3 = Guerrero("Debil", 100, 10, 5)
    objetivo3 = Mago("Muro", 100, 40, 50)
    comprobar(5, "Si la defensa supera el ataque potenciado, el daño es 0",
              guerrero3.atacar(objetivo3) == 0 and objetivo3.vida == 100)


def caso_6_habilidad_mago():
    titulo(6, "Habilidad del Mago: hechizo que ignora la defensa")
    mago = Mago("Gandalf", 80, 40, 10)
    objetivo = Guerrero("Muralla", 100, 30, 20)
    danio = mago.atacar(objetivo)
    print(f"  Ataque 40 vs defensa 20 -> daño {danio}, vida del objetivo: {objetivo.vida}")
    comprobar(6, "Ataque 40 vs defensa 20 produce 40 de daño", danio == 40 and objetivo.vida == 60)

    blindado = Guerrero("Blindado", 100, 30, 500)
    comprobar(6, "Una defensa enorme (500) no reduce el daño del Mago",
              mago.atacar(blindado) == 40 and blindado.vida == 60)


def caso_7_habilidad_arquero():
    titulo(7, "Habilidad del Arquero: disparo crítico (daño x2)")
    arquero = Arquero("Legolas", 90, 35, 15)
    objetivo = Guerrero("Dummy", 100, 30, 15)
    danio = arquero.atacar(objetivo)
    print(f"  Ataque 35 vs defensa 15 -> daño {danio}, vida del objetivo: {objetivo.vida}")
    comprobar(7, "Ataque 35 vs defensa 15: base 20, final 40", danio == 40 and objetivo.vida == 60)

    arquero_debil = Arquero("Novato", 90, 10, 5)
    fuerte = Guerrero("Fuerte", 100, 30, 15)
    comprobar(7, "Si el ataque no supera la defensa (10 vs 15), el daño es 0",
              arquero_debil.atacar(fuerte) == 0 and fuerte.vida == 100)

    arquero_igual = Arquero("Igual", 90, 15, 5)
    fuerte2 = Guerrero("Fuerte2", 100, 30, 15)
    comprobar(7, "Si el ataque solo iguala la defensa (15 vs 15), el daño es 0",
              arquero_igual.atacar(fuerte2) == 0)


def caso_8_vida_nunca_negativa():
    titulo(8, "Imposibilidad de tener vida negativa")
    personaje = Guerrero("Herido", 20, 30, 10)
    efectivo = personaje.recibir_danio(50)
    print(f"  Vida 20 recibe 50 de daño -> vida actual: {personaje.vida}, daño efectivo: {efectivo}")
    comprobar(8, "Vida 20 + daño 50 queda en 0 (no en -30)", personaje.vida == 0)
    comprobar(8, "El daño efectivo devuelto es 20", efectivo == 20)
    comprobar(8, "El personaje queda derrotado (esta_vivo() == False)", not personaje.esta_vivo())
    comprobar_error(8, "Asignar vida -1 con el setter", ValueError, setattr, personaje, "vida", -1)
    comprobar_error(8, "recibir_danio con cantidad negativa", ValueError, personaje.recibir_danio, -5)


def caso_9_derrotado_no_ataca():
    titulo(9, "Imposibilidad de atacar estando derrotado")
    derrotado = Mago("Caido", 100, 40, 10)
    derrotado.recibir_danio(100)
    vivo = Guerrero("Vivo", 100, 30, 10)
    comprobar_error(9, "Un personaje derrotado intenta atacar", AtaqueInvalidoError,
                    derrotado.atacar, vivo)
    comprobar(9, "La vida del objetivo no cambió", vivo.vida == 100)
    comprobar_error(9, "Atacar a un personaje ya derrotado", AtaqueInvalidoError,
                    vivo.atacar, derrotado)
    comprobar_error(9, "Atacarse a sí mismo", AtaqueInvalidoError, vivo.atacar, vivo)
    comprobar_error(9, "Objetivo que no es un Personaje", TypeError, vivo.atacar, "un fantasma")


def caso_10_y_11_combate_completo():
    titulo(10, "Ejecución de un combate completo (Arthas vs Gandalf)")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf)
    ganador = combate.iniciar()

    # Tabla esperada del enunciado: (turno, atacante, daño efectivo, vida Arthas, vida Gandalf)
    esperado = [
        (1, "Arthas", 26, 100, 54),
        (2, "Gandalf", 40, 60, 54),
        (3, "Arthas", 26, 60, 28),
        (4, "Gandalf", 40, 20, 28),
        (5, "Arthas", 26, 20, 2),
        (6, "Gandalf", 20, 0, 2),
    ]
    obtenido = [(r["turno"], r["atacante"], r["danio_efectivo"], *r["vidas"])
                for r in combate.historial]
    print()
    comprobar(10, "El combate se desarrolló turno a turno igual que la tabla del enunciado",
              obtenido == esperado)
    comprobar(10, "El combate duró 6 turnos y terminó en victoria",
              combate.turnos == 6 and combate.resultado == Combate.VICTORIA)
    comprobar(10, "En el turno 6 el daño calculado fue 40 pero el efectivo 20",
              combate.historial[-1]["danio_calculado"] == 40
              and combate.historial[-1]["danio_efectivo"] == 20)

    titulo(11, "Identificación correcta del ganador")
    comprobar(11, "iniciar() devuelve a Gandalf como ganador", ganador is gandalf)
    comprobar(11, "verificar_ganador() también devuelve a Gandalf", combate.verificar_ganador() is gandalf)
    comprobar(11, "Arthas quedó derrotado y Gandalf conserva 2 de vida",
              not arthas.esta_vivo() and gandalf.vida == 2)


def caso_12_empate_tecnico():
    titulo(12, "Finalización de un combate sin daño: empate técnico")
    # Guerrero: 10 * 1.2 = 12 < 15  |  Arquero: 10 <= 15  -> nadie causa daño
    guerrero = Guerrero("Escudero", 100, 10, 15)
    arquero = Arquero("Vigia", 100, 10, 15)
    combate = Combate(guerrero, arquero)
    ganador = combate.iniciar()
    print()
    comprobar(12, "El resultado es empate técnico", combate.resultado == Combate.EMPATE_TECNICO)
    comprobar(12, "No hay ganador", ganador is None and combate.ganador is None)
    comprobar(12, "Terminó tras completar una sola ronda (2 turnos)",
              combate.turnos == 2 and combate.rondas_completadas == 1)
    comprobar(12, "Ambos conservan toda su vida", guerrero.vida == 100 and arquero.vida == 100)



# Casos adicionales (no obligatorios)

def caso_extra_a_limite_de_rondas():
    titulo("EXTRA A", "Empate por límite de 50 rondas")
    # El Guerrero causa 1 de daño por turno (12 - 11); el Arquero no puede dañarlo (5 <= 20).
    guerrero = Guerrero("Paciente", 100, 10, 20)
    arquero = Arquero("Resistente", 100, 5, 11)
    combate = Combate(guerrero, arquero, verbose=False)
    ganador = combate.iniciar()
    comprobar("EXTRA A", "El resultado es empate por límite de rondas",
              combate.resultado == Combate.EMPATE_POR_RONDAS and ganador is None)
    comprobar("EXTRA A", "Se completaron exactamente 50 rondas (100 turnos)",
              combate.rondas_completadas == 50 and combate.turnos == 100)
    comprobar("EXTRA A", "Nadie murió: el Arquero conserva 50 de vida", arquero.vida == 50)


def caso_extra_b_polimorfismo():
    titulo("EXTRA B", "Polimorfismo: la misma llamada atacar() se comporta distinto")
    atacantes = [Guerrero("G", 100, 30, 0), Mago("M", 100, 30, 0), Arquero("A", 100, 30, 0)]
    danios = []
    for atacante in atacantes:
        objetivo = Guerrero("Muñeco", 100, 10, 10)   # defensa 10
        danios.append(atacante.atacar(objetivo))
        print(f"  {type(atacante).__name__:8} (ataque 30) vs defensa 10 -> daño {danios[-1]}")
    comprobar("EXTRA B", "Guerrero 26, Mago 30 y Arquero 40 con la misma llamada atacar()",
              danios == [26, 30, 40])



# Programa principal

def main():
    print("=" * 64)
    print("  GUARDIANS OF THE ANCIENT KINGDOM - Casos de prueba")
    print("=" * 64)

    caso_1_creacion()
    caso_2_vida_invalida()
    caso_3_nombre_vacio()
    caso_4_ataque_defensa_invalidos()
    caso_5_habilidad_guerrero()
    caso_6_habilidad_mago()
    caso_7_habilidad_arquero()
    caso_8_vida_nunca_negativa()
    caso_9_derrotado_no_ataca()
    caso_10_y_11_combate_completo()
    caso_12_empate_tecnico()
    caso_extra_a_limite_de_rondas()
    caso_extra_b_polimorfismo()

    # Resumen
    print()
    print("=" * 64)
    print("  RESUMEN")
    print("=" * 64)
    casos = []
    for numero, _, _ in resultados:
        if numero not in casos:
            casos.append(numero)
    for numero in casos:
        del_caso = [ok for n, _, ok in resultados if n == numero]
        estado = "APROBADO" if all(del_caso) else "FALLÓ"
        etiqueta = f"Caso {numero}" if isinstance(numero, int) else numero
        print(f"  {etiqueta:<10} {estado:<9} ({sum(del_caso)}/{len(del_caso)} comprobaciones)")
    total = len(resultados)
    aprobadas = sum(1 for _, _, ok in resultados if ok)
    print(f"\n  Total: {aprobadas}/{total} comprobaciones aprobadas")
    return 0 if aprobadas == total else 1


if __name__ == "__main__":
    sys.exit(main())
