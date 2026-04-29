# Estado actual — 2026-04-18 ~23:00 CST

## Último deploy
- Commit: `8047b6c` (fix: seed function no longer overwrites isActive/capacity)
- Status: SUCCESS (auto-deploy por Railway)
- Verificado: sitio responde HTTP 200, API retorna 7 eventos activos

## Eventos
- 8 eventos totales, 7 activos (J1 Bravos oculto con isActive=0)
- Venta total acumulada: $105,035 MXN (128 órdenes pagadas)
- J2 Bravos (hoy 18 abr): $15,000 MXN, 16 órdenes
- J3 Bravos (dom 19 abr): $2,660 MXN, 5 órdenes

## Última auditoría de integridad
- Fecha: 2026-04-18
- Resultado: 0 problemas de integridad real
- Nota: 6 blocked seats con orderId residual son intencionales (Daniel bloqueó mesas con cortesías)

## En vuelo (trabajo sin terminar)
- [ ] Bug #6: Pending zombies en vip_group_members (M4-04, M4-05 muestran ocupado en frontend)
- [ ] Deploy pendiente de verificar: los 6 ajustes de Daniel (capacidad, boletos, alertas)
- [ ] Ticket PDF: falta agregar seatLabels al PDF descargable (solo se agregó al email)

## Bugs vivos
- Bug #6: Pending zombies en VIP groups (cosmético, no bloquea ventas reales)

## Próximo paso recomendado
Limpiar vip_group_members con status='pending' de órdenes que nunca se completaron (Bug #6).
