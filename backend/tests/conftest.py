"""Isola os testes do `.env` local: backends em memória, sem Postgres nem MQTT."""

import os

os.environ["PERSISTENCE_BACKEND"] = "memory"
os.environ["MESSAGE_BUS_BACKEND"] = "memory"
