"""Casamento de tópicos MQTT, compartilhado pelos barramentos."""

from __future__ import annotations


# Bloco: casamento de tópico MQTT com curingas (`+` um nível, `#` o restante).
def topic_matches(pattern: str, topic: str) -> bool:
    pattern_parts, topic_parts = pattern.split("/"), topic.split("/")
    for index, part in enumerate(pattern_parts):
        if part == "#":
            return True
        if index >= len(topic_parts) or (part != "+" and part != topic_parts[index]):
            return False
    return len(pattern_parts) == len(topic_parts)
