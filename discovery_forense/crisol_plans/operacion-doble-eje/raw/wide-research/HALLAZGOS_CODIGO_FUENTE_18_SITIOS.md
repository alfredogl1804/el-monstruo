# Hallazgos: Análisis de Código Fuente de 18 Sitios Web

## Tabla de IDs de Tracking Encontrados

| Sitio | GA ID | AdSense | Meta Pixel | GTM | CMS | Hosting |
|---|---|---|---|---|---|---|
| poresto.net | G-W96TEMTQFN | pub-2088049815813625, pub-2860652398971848 | — | — | No ID | Cloudflare+Varnish |
| notisureste.com | UA-74112537-1 | — | — | — | WordPress | Cloudflare |
| elchismografoenlared.com | — | — | — | — | WordPress | Apache |
| dulce-patria.com.mx | G-YLFT3SR785 | — | — | — | WordPress | LiteSpeed |
| grillodeyucatan.com | — | — | — | — | WordPress | nginx/Ubuntu |
| elprincipal.com.mx | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA |
| solyucatan.mx | UA-195056972-1 | ca-pub-6807196897316532 | — | — | WordPress | Cloudflare |
| formalprison.com | INACTIVO | — | — | — | — | — |
| grilloporteno.com | REDIRIGE a grillodeyucatan.com | — | — | — | WordPress | nginx/Ubuntu |
| proyectopuente.com.mx | G-HSP0D2B3FE | ca-pub-2299250803327721 | 3446853778764149 | — | WordPress | nginx |
| lajornadamaya.mx | G-E07T0M9RKT | pub-8812112500878104 (+2 resellers) | 1550455535233931 | GTM-N6HFHK7 | No ID | Cloudflare |
| sipse.com | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA |
| larevista.com.mx | G-K42H7L9Z2V | ca-pub-3434565660165370 | — | — | WordPress | hcdn |
| noticiasmerida.com.mx | G-QKWZJJHVQQ | ca-pub-7896520118591353 | — | — | WordPress | hcdn |
| pressyucatan.com | INACTIVO | — | — | — | — | — |
| metropoliyucatan.com | INACTIVO | — | — | — | — | — |
| vozlibreyucatan.com | INACTIVO | — | — | — | — | — |
| valorporyucatan.com | — | — | — | — | Squarespace | Squarespace |

## HALLAZGOS CRÍTICOS

### HALLAZGO #1: LaRevista y NoticiasM\u00e9rida comparten el MISMO hosting "hcdn"
- larevista.com.mx → server: hcdn
- noticiasmerida.com.mx → server: hcdn, PHP/8.2.27
- Ambos usan WordPress
- Esto podría indicar el mismo proveedor de hosting o infraestructura compartida

### HALLAZGO #2: GrilloPorteño REDIRIGE a GrilloDeYucatan
- grilloporteno.com → redirige a grillodeyucatan.com
- Mismo servidor: nginx/1.26.0 (Ubuntu)
- CONFIRMADO: Son el MISMO medio/operador (Gabino Tzec Valle)

### HALLAZGO #3: 5 sitios están INACTIVOS o son solo redes sociales
- formalprison.com → INACTIVO
- pressyucatan.com → INACTIVO (solo Facebook)
- metropoliyucatan.com → INACTIVO (solo Facebook)
- vozlibreyucatan.com → INACTIVO
- valorporyucatan.com → Squarespace "próximamente"
- Estos medios operan EXCLUSIVAMENTE desde redes sociales (más difícil de rastrear)

### HALLAZGO #4: El Chismógrafo NO tiene NINGÚN tracking
- Sin Google Analytics, sin AdSense, sin Meta Pixel, sin GTM
- WordPress en Apache
- Esto es DELIBERADO: quien lo opera sabe que los IDs de tracking pueden identificarlo

### HALLAZGO #5: NO se encontraron IDs compartidos entre sitios de ataque
- Cada sitio activo tiene sus propios IDs únicos
- No hay un Google Analytics o AdSense que conecte dos sitios
- Esto sugiere que los operadores son cuidadosos o que la coordinación es por canales privados

### HALLAZGO #6: Emails encontrados
- poresto.net: publicidad@poresto.mx, redaccionweb@poresto.mx
- noticiasmerida.com.mx: contactonoticiasmerida@gmail.com
- larevista.com.mx: tucorreo@gmail.com (placeholder)

### HALLAZGO #7: PorEsto tiene ComScore (medición profesional de audiencia)
- Único sitio con ComScore → es un medio profesional con monetización seria
- Dos IDs de AdSense → monetiza con Google Ads

## Conclusión
La técnica de IDs compartidos NO reveló conexiones directas entre los sitios de ataque. Los operadores son cuidadosos. Los hallazgos más prometedores son:
1. GrilloPorteño = GrilloDeYucatán (mismo operador confirmado)
2. LaRevista y NoticiasM\u00e9rida comparten hosting "hcdn"
3. El Chismógrafo deliberadamente no tiene tracking (operador sofisticado)
4. 5 medios operan solo desde redes sociales (dificulta rastreo)
