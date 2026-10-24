"""
test_personajes.py
==================
Pruebas automatizadas (Pytest) de "Guardians of the Ancient Kingdom".

Ejecutar desde la carpeta del proyecto:
    pytest -v
"""

import subprocess
import sys
from pathlib import Path

import pytest

from personajes import (
    Arquero,
    AtaqueInvalidoError,
    Combate,
    Guerrero,
    Mago,
    Personaje,
)

CLASES = [Guerrero, Mago, Arquero]



# Creación de personajes válidos

@pytest.mark.parametrize("clase", CLASES)
def test_creacion_valida(clase):
    p = clase("Heroe", 80, 25, 10)
    assert (p.nombre, p.vida, p.ataque, p.defensa) == ("Heroe", 80, 25, 10)
    assert isinstance(p, Personaje)
    assert p.esta_vivo()


def test_personaje_es_abstracta():
    with pytest.raises(TypeError):
        Personaje("Intruso", 50, 10, 10)


def test_subclase_sin_atacar_no_se_puede_instanciar():
    class Incompleta(Personaje):
        pass

    with pytest.raises(TypeError):
        Incompleta("X", 50, 10, 10)


@pytest.mark.parametrize("vida", [0, 1, 100])
def test_vida_en_los_limites_es_valida(vida):
    assert Guerrero("Limite", vida, 10, 0).vida == vida


def test_nombre_se_limpia_de_espacios():
    assert Mago("  Gandalf  ", 80, 40, 10).nombre == "Gandalf"



# Rechazo de valores incorrectos

@pytest.mark.parametrize("clase", CLASES)
@pytest.mark.parametrize("vida", [-1, -50, 101, 1000])
def test_rechaza_vida_fuera_de_rango(clase, vida):
    with pytest.raises(ValueError):
        clase("Heroe", vida, 25, 10)


@pytest.mark.parametrize("clase", CLASES)
@pytest.mark.parametrize("nombre", ["", "   "])
def test_rechaza_nombre_vacio(clase, nombre):
    with pytest.raises(ValueError):
        clase(nombre, 80, 25, 10)


@pytest.mark.parametrize("nombre", [123, None, 4.5])
def test_rechaza_nombre_que_no_es_texto(nombre):
    with pytest.raises(TypeError):
        Guerrero(nombre, 80, 25, 10)


@pytest.mark.parametrize("ataque", [0, -1, -100])
def test_rechaza_ataque_no_positivo(ataque):
    with pytest.raises(ValueError):
        Mago("Heroe", 80, ataque, 10)


@pytest.mark.parametrize("defensa", [-1, -100])
def test_rechaza_defensa_negativa(defensa):
    with pytest.raises(ValueError):
        Arquero("Heroe", 80, 25, defensa)


@pytest.mark.parametrize("valor", ["10", 3.5, None, True])
def test_rechaza_tipos_incorrectos_en_numeros(valor):
    with pytest.raises(TypeError):
        Guerrero("Heroe", valor, 25, 10)
    with pytest.raises(TypeError):
        Guerrero("Heroe", 80, valor, 10)
    with pytest.raises(TypeError):
        Guerrero("Heroe", 80, 25, valor)


def test_setters_aplican_las_mismas_validaciones():
    p = Guerrero("Heroe", 80, 25, 10)
    with pytest.raises(ValueError):
        p.vida = 101
    with pytest.raises(ValueError):
        p.nombre = ""
    with pytest.raises(ValueError):
        p.ataque = 0
    with pytest.raises(ValueError):
        p.defensa = -1
    p.vida, p.ataque, p.defensa = 50, 40, 5     # valores válidos sí se aceptan
    assert (p.vida, p.ataque, p.defensa) == (50, 40, 5)



# Cálculo del daño de cada clase

def test_guerrero_golpe_poderoso():
    # 30 * 1.20 = 36; 36 - 10 = 26
    objetivo = Mago("Objetivo", 80, 40, 10)
    assert Guerrero("Arthas", 100, 30, 20).atacar(objetivo) == 26
    assert objetivo.vida == 54


def test_guerrero_redondea_hacia_abajo():
    # 33 * 1.20 = 39.6 -> 39; 39 - 10 = 29
    objetivo = Mago("Objetivo", 100, 40, 10)
    assert Guerrero("Arthas", 100, 33, 5).atacar(objetivo) == 29


def test_guerrero_dano_minimo_cero():
    objetivo = Mago("Muro", 100, 40, 50)
    assert Guerrero("Debil", 100, 10, 5).atacar(objetivo) == 0
    assert objetivo.vida == 100


def test_mago_ignora_la_defensa():
    objetivo = Guerrero("Muralla", 100, 30, 20)
    assert Mago("Gandalf", 80, 40, 10).atacar(objetivo) == 40
    assert objetivo.vida == 60


def test_mago_con_defensa_enorme_hace_el_mismo_dano():
    objetivo = Guerrero("Blindado", 100, 30, 9999)
    assert Mago("Gandalf", 80, 40, 10).atacar(objetivo) == 40


def test_arquero_disparo_critico():
    # base = 35 - 15 = 20; final = 40
    objetivo = Guerrero("Objetivo", 100, 30, 15)
    assert Arquero("Legolas", 90, 35, 15).atacar(objetivo) == 40
    assert objetivo.vida == 60


@pytest.mark.parametrize("ataque, defensa", [(10, 15), (15, 15)])
def test_arquero_sin_critico_si_no_supera_la_defensa(ataque, defensa):
    objetivo = Guerrero("Objetivo", 100, 30, defensa)
    assert Arquero("Legolas", 90, ataque, 5).atacar(objetivo) == 0
    assert objetivo.vida == 100


def test_polimorfismo_misma_llamada_distinto_resultado():
    danios = []
    for clase in CLASES:
        objetivo = Guerrero("Objetivo", 100, 10, 10)
        danios.append(clase("Atacante", 100, 30, 0).atacar(objetivo))
    assert danios == [26, 30, 40]



# La vida nunca es negativa

def test_vida_nunca_queda_negativa():
    p = Guerrero("Herido", 20, 30, 10)
    assert p.recibir_danio(50) == 20          # daño efectivo
    assert p.vida == 0
    assert not p.esta_vivo()


def test_recibir_danio_no_descuenta_defensa_otra_vez():
    p = Guerrero("Escudo", 100, 30, 50)
    assert p.recibir_danio(30) == 30
    assert p.vida == 70


def test_recibir_danio_rechaza_negativos():
    p = Mago("Heroe", 80, 40, 10)
    with pytest.raises(ValueError):
        p.recibir_danio(-5)
    assert p.vida == 80


def test_recibir_danio_rechaza_tipos_incorrectos():
    p = Mago("Heroe", 80, 40, 10)
    with pytest.raises(TypeError):
        p.recibir_danio(2.5)


def test_ataque_que_supera_la_vida_deja_al_objetivo_en_cero():
    objetivo = Guerrero("Casi muerto", 5, 10, 0)
    efectivo = Mago("Gandalf", 80, 40, 10).atacar(objetivo)
    assert objetivo.vida == 0
    assert efectivo == 5



# Un personaje derrotado no puede atacar (ni ser atacado)

@pytest.mark.parametrize("clase", CLASES)
def test_derrotado_no_puede_atacar(clase):
    derrotado = clase("Caido", 100, 40, 10)
    derrotado.recibir_danio(100)
    vivo = Guerrero("Vivo", 100, 30, 10)
    with pytest.raises(AtaqueInvalidoError):
        derrotado.atacar(vivo)
    assert vivo.vida == 100


@pytest.mark.parametrize("clase", CLASES)
def test_no_se_puede_atacar_a_un_derrotado(clase):
    derrotado = Guerrero("Caido", 100, 30, 10)
    derrotado.recibir_danio(100)
    with pytest.raises(AtaqueInvalidoError):
        clase("Atacante", 100, 40, 10).atacar(derrotado)


def test_objetivo_invalido():
    guerrero = Guerrero("Arthas", 100, 30, 20)
    with pytest.raises(TypeError):
        guerrero.atacar("no soy un personaje")
    with pytest.raises(TypeError):
        guerrero.atacar(None)
    with pytest.raises(AtaqueInvalidoError):
        guerrero.atacar(guerrero)


def test_mostrar_estado_describe_al_personaje(capsys):
    texto = Mago("Gandalf", 80, 40, 10).mostrar_estado()
    salida = capsys.readouterr().out
    assert "Gandalf" in texto and "80" in texto and "vivo" in texto
    assert texto in salida



# Combate

def test_combate_del_enunciado_gandalf_gana():
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf, verbose=False)

    ganador = combate.iniciar()

    assert ganador is gandalf
    assert combate.ganador is gandalf
    assert combate.resultado == Combate.VICTORIA
    assert not arthas.esta_vivo()
    assert gandalf.vida == 2
    assert combate.turnos == 6
    assert combate.rondas_completadas == 3


def test_combate_coincide_turno_a_turno_con_la_tabla_del_enunciado():
    combate = Combate(Guerrero("Arthas", 100, 30, 20), Mago("Gandalf", 80, 40, 10), verbose=False)
    combate.iniciar()
    obtenido = [(r["turno"], r["atacante"], r["danio_efectivo"], *r["vidas"])
                for r in combate.historial]
    assert obtenido == [
        (1, "Arthas", 26, 100, 54),
        (2, "Gandalf", 40, 60, 54),
        (3, "Arthas", 26, 60, 28),
        (4, "Gandalf", 40, 20, 28),
        (5, "Arthas", 26, 20, 2),
        (6, "Gandalf", 20, 0, 2),
    ]


def test_ultimo_golpe_registra_dano_calculado_y_efectivo():
    combate = Combate(Guerrero("Arthas", 100, 30, 20), Mago("Gandalf", 80, 40, 10), verbose=False)
    combate.iniciar()
    ultimo = combate.historial[-1]
    assert ultimo["danio_calculado"] == 40
    assert ultimo["danio_efectivo"] == 20


def test_gana_el_primero_si_derrota_antes_al_segundo():
    fuerte = Mago("Fuerte", 100, 60, 0)
    debil = Guerrero("Debil", 50, 10, 0)
    combate = Combate(fuerte, debil, verbose=False)
    assert combate.iniciar() is fuerte
    assert combate.turnos == 1               # el derrotado nunca llegó a atacar


def test_gana_el_segundo_participante():
    debil = Guerrero("Debil", 50, 10, 0)
    fuerte = Mago("Fuerte", 100, 60, 0)
    combate = Combate(debil, fuerte, verbose=False)
    assert combate.iniciar() is fuerte


def test_empate_tecnico_cuando_nadie_causa_dano():
    guerrero = Guerrero("Escudero", 100, 10, 15)    # 12 - 15 -> 0
    arquero = Arquero("Vigia", 100, 10, 15)         # 10 <= 15 -> 0
    combate = Combate(guerrero, arquero, verbose=False)

    assert combate.iniciar() is None
    assert combate.resultado == Combate.EMPATE_TECNICO
    assert combate.ganador is None
    assert combate.turnos == 2
    assert guerrero.vida == 100 and arquero.vida == 100


def test_empate_tras_50_rondas_sin_ganador():
    guerrero = Guerrero("Paciente", 100, 10, 20)    # hace 1 de daño por turno
    arquero = Arquero("Resistente", 100, 5, 11)     # no logra dañar (5 <= 20)
    combate = Combate(guerrero, arquero, verbose=False)

    assert combate.iniciar() is None
    assert combate.resultado == Combate.EMPATE_POR_RONDAS
    assert combate.rondas_completadas == 50
    assert combate.turnos == 100
    assert arquero.vida == 50


def test_cambiar_turno_alterna_el_atacante():
    a, b = Guerrero("A", 100, 10, 0), Mago("B", 100, 10, 0)
    combate = Combate(a, b, verbose=False)
    assert combate.atacante is a and combate.defensor is b
    combate.cambiar_turno()
    assert combate.atacante is b and combate.defensor is a
    combate.cambiar_turno()
    assert combate.atacante is a


def test_verificar_ganador_sin_ganador_y_con_ganador():
    a, b = Guerrero("A", 100, 10, 0), Mago("B", 100, 10, 0)
    combate = Combate(a, b, verbose=False)
    assert combate.verificar_ganador() is None
    b.recibir_danio(100)
    assert combate.verificar_ganador() is a


def test_combate_rechaza_participantes_invalidos():
    guerrero = Guerrero("A", 100, 10, 0)
    with pytest.raises(TypeError):
        Combate(guerrero, "no soy un personaje")
    with pytest.raises(ValueError):
        Combate(guerrero, guerrero)
    derrotado = Mago("B", 100, 10, 0)
    derrotado.recibir_danio(100)
    with pytest.raises(ValueError):
        Combate(guerrero, derrotado)


def test_combate_no_se_puede_iniciar_dos_veces():
    combate = Combate(Mago("A", 100, 60, 0), Guerrero("B", 50, 10, 0), verbose=False)
    combate.iniciar()
    with pytest.raises(RuntimeError):
        combate.iniciar()


def test_combate_muestra_estado_despues_de_cada_ataque(capsys):
    combate = Combate(Guerrero("Arthas", 100, 30, 20), Mago("Gandalf", 80, 40, 10))
    combate.iniciar()
    salida = capsys.readouterr().out
    assert salida.count("Turno ") == 6
    assert "Ganador: Gandalf" in salida



# personajes.py no debe ejecutar nada al importarse

def test_importar_personajes_no_imprime_ni_ejecuta_pruebas():
    carpeta = Path(__file__).resolve().parent
    resultado = subprocess.run(
        [sys.executable, "-c", "import personajes"],
        cwd=carpeta, capture_output=True, text=True,
    )
    assert resultado.returncode == 0
    assert resultado.stdout == ""
