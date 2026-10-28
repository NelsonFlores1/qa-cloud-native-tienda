"""Enlaza el feature de casos de borde (@ia) con sus steps."""
from pytest_bdd import scenarios

# Importa los steps compartidos (necesario para que pytest-bdd los vea)
from tests.steps_comunes import *  # noqa: F401,F403

scenarios("bordes.feature")
