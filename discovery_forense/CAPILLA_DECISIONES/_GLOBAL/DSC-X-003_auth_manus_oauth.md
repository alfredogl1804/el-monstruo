---
id: DSC-X-003
proyecto: GLOBAL
tipo: patron_replicable
titulo: "Componente compartido: auth via Manus-Oauth (scaffold web-db-user)"
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:el-monstruo-bot
cruza_con: ["El Monstruo Bot", "Command Center", "Mundo de Tata"]
---

# Componente compartido: auth via Manus-Oauth (scaffold web-db-user)

## Decisión

Se establece el uso de Manus-Oauth como el componente de autenticación compartido y patrón replicable (scaffold web-db-user) para los proyectos El Monstruo Bot, Command Center y Mundo de Tata.

## Por qué

Centralizar la autenticación a través de Manus-Oauth garantiza un acceso unificado, seguro y consistente en todo el ecosistema, reduciendo la duplicación de código y facilitando la gestión de identidades entre las distintas interfaces y servicios.

## Implicaciones

Cualquier nuevo servicio o interfaz web dentro del ecosistema que requiera autenticación de usuarios deberá integrar este scaffold, asegurando compatibilidad con la base de datos central de usuarios.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)