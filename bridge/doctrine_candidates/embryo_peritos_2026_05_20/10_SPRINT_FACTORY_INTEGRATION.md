# 10 SPRINT FACTORY INTEGRATION

**Estado:** DOCTRINE_CANDIDATE
**Fuente:** chat_context / assistant_synthesis

## Integración de Peritos con el Sprint Factory

El Sprint Factory es el orquestador que gestiona la invocación y el ciclo de vida de los Embriones Peritos durante un Sprint.

### 1. Invocación por Dominio
Cuando se crea un Sprint, el Dispatcher analiza el dominio de las tareas. Si la tarea es "Configurar Stripe", el Dispatcher invoca al **Embrión Perito de Negocio, Monetización y Escala**, inyectándole su Boot Pack específico.

### 2. Producción de Sprint Candidates
Los embriones peritos (especialmente el Oráculo de IAs y Hari Seldon) pueden proponer nuevos Sprints basados en su análisis. Estas propuestas entran al backlog como `SPRINT_CANDIDATE` y requieren aprobación T1.

### 3. Auditoría Cruzada (Separación de Roles)
**Regla de Oro:** Ningún embrión perito se audita a sí mismo.
- Si el Embrión de Infraestructura propone un cambio en la arquitectura, el **Embrión Perito del Monstruo** o un auditor externo (Perplexity) debe validarlo.
- El Sprint Factory actúa como juez: si el auditor rechaza la propuesta, el Sprint se bloquea.

### 4. Actualización del Boot Pack
Al finalizar un Sprint exitoso, el Sprint Factory extrae la lección aprendida (ver `06_EMBRYO_LEARNING_LOOP.md`) y actualiza el Boot Pack del perito involucrado, incrementando su pericia.
