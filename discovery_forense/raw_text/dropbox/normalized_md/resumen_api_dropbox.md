# Demostración y Capacidades de la API de Dropbox

Autor: Manus AI
Fecha: 01 de febrero de 2026

## 1. Introducción

Este documento presenta un resumen de las capacidades de la API de Dropbox, acompañado de un script de demostración en Python que ilustra cómo utilizar sus funcionalidades principales. El objetivo es proporcionar una guía práctica y clara para desarrolladores que deseen integrar Dropbox en sus aplicaciones.

La API de Dropbox V2 ofrece una interfaz robusta y coherente para interactuar mediante programación con los archivos y la estructura de carpetas de un usuario de Dropbox. Permite realizar una amplia gama de operaciones, desde la simple carga y descarga de archivos hasta la gestión de metadatos, el control de versiones y la creación de enlaces para compartir.

## 2. Resumen de Capacidades de la API

La API de Dropbox, a través de su SDK oficial para Python, proporciona acceso a las siguientes funcionalidades clave, que han sido probadas en el script de demostración adjunto:

## 3. Script de Demostración

A continuación se presenta el script completo utilizado para probar las funcionalidades mencionadas. El script está diseñado para ser autoexplicativo, con cada función dedicada a una operación específica de la API.

#!/usr/bin/env python3

"""

Dropbox API Demo Script

=======================

Este script demuestra las principales capacidades de la API de Dropbox.

Características demostradas:

1. Autenticación y verificación de cuenta

2. Subida de archivos (upload)

3. Listado de archivos y carpetas

4. Descarga de archivos

5. Creación de carpetas

6. Obtención de metadatos de archivos

7. Búsqueda de archivos

8. Creación de enlaces compartidos

9. Copia y movimiento de archivos

10. Eliminación de archivos

Autor: Demo Script

Fecha: Febrero 2026

"""

import os

import dropbox

from dropbox.exceptions import ApiError, AuthError

from dropbox.files import WriteMode

from datetime import datetime

import json

# Configuración

DEMO_FOLDER = "/demo_dropbox_api"

TEST_FILE_NAME = "archivo_prueba.txt"

TEST_FILE_CONTENT = f"""

Este es un archivo de prueba creado por el script de demostración.

Fecha de creación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Propósito: Demostrar las capacidades de la API de Dropbox

"""

class DropboxDemo:

"""Clase para demostrar las funcionalidades de la API de Dropbox."""

def __init__(self):

"""Inicializa el cliente de Dropbox con la API key."""

self.api_key = os.environ.get('DROPBOX_API_KEY')

if not self.api_key:

raise ValueError("No se encontró DROPBOX_API_KEY en las variables de entorno")

self.dbx = dropbox.Dropbox(self.api_key)

self.results = {}

def print_section(self, title):

"""Imprime un encabezado de sección formateado."""

print("\n" + "=" * 60)

print(f"  {title}")

print("=" * 60)

def print_result(self, success, message):

"""Imprime el resultado de una operación."""

status = "✓" if success else "✗"

print(f"  [{status}] {message}")

# =========================================================================

# 1. AUTENTICACIÓN Y VERIFICACIÓN DE CUENTA

# =========================================================================

def demo_account_info(self):

"""Demuestra cómo obtener información de la cuenta."""

self.print_section("1. INFORMACIÓN DE CUENTA")

try:

account = self.dbx.users_get_current_account()

print(f"\n  Nombre: {account.name.display_name}")

print(f"  Email: {account.email}")

print(f"  País: {account.country}")

print(f"  Tipo de cuenta: {account.account_type}")

print(f"  ID de cuenta: {account.account_id}")

self.results['account_info'] = {

'success': True,

'name': account.name.display_name,

'email': account.email

}

self.print_result(True, "Información de cuenta obtenida correctamente")

return True

except AuthError as e:

self.print_result(False, f"Error de autenticación: {e}")

self.results['account_info'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 2. INFORMACIÓN DE ESPACIO

# =========================================================================

def demo_space_usage(self):

"""Demuestra cómo obtener información del espacio de almacenamiento."""

self.print_section("2. USO DE ESPACIO")

try:

space = self.dbx.users_get_space_usage()

used_gb = space.used / (1024 ** 3)

if hasattr(space.allocation, 'allocated'):

allocated_gb = space.allocation.allocated / (1024 ** 3)

percentage = (space.used / space.allocation.allocated) * 100

print(f"\n  Espacio usado: {used_gb:.2f} GB")

print(f"  Espacio total: {allocated_gb:.2f} GB")

print(f"  Porcentaje usado: {percentage:.1f}%")

else:

print(f"\n  Espacio usado: {used_gb:.2f} GB")

print("  (Cuenta de equipo - espacio compartido)")

self.results['space_usage'] = {'success': True, 'used_gb': used_gb}

self.print_result(True, "Información de espacio obtenida correctamente")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['space_usage'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 3. CREAR CARPETA

# =========================================================================

def demo_create_folder(self):

"""Demuestra cómo crear una carpeta."""

self.print_section("3. CREAR CARPETA")

try:

# Primero intentamos eliminar la carpeta si existe

try:

self.dbx.files_delete_v2(DEMO_FOLDER)

print(f"\n  Carpeta existente eliminada: {DEMO_FOLDER}")

except ApiError:

pass  # La carpeta no existía

# Crear la carpeta

result = self.dbx.files_create_folder_v2(DEMO_FOLDER)

print(f"\n  Carpeta creada: {result.metadata.path_display}")

print(f"  ID: {result.metadata.id}")

self.results['create_folder'] = {

'success': True,

'path': result.metadata.path_display

}

self.print_result(True, f"Carpeta '{DEMO_FOLDER}' creada correctamente")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['create_folder'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 4. SUBIR ARCHIVO

# =========================================================================

def demo_upload_file(self):

"""Demuestra cómo subir un archivo."""

self.print_section("4. SUBIR ARCHIVO")

file_path = f"{DEMO_FOLDER}/{TEST_FILE_NAME}"

try:

result = self.dbx.files_upload(

TEST_FILE_CONTENT.encode('utf-8'),

file_path,

mode=WriteMode.overwrite,

autorename=False

)

print(f"\n  Archivo subido: {result.path_display}")

print(f"  Tamaño: {result.size} bytes")

print(f"  Modificado: {result.server_modified}")

print(f"  ID: {result.id}")

self.results['upload_file'] = {

'success': True,

'path': result.path_display,

'size': result.size

}

self.print_result(True, "Archivo subido correctamente")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['upload_file'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 5. LISTAR ARCHIVOS

# =========================================================================

def demo_list_files(self):

"""Demuestra cómo listar archivos en una carpeta."""

self.print_section("5. LISTAR ARCHIVOS")

try:

result = self.dbx.files_list_folder(DEMO_FOLDER)

print(f"\n  Contenido de '{DEMO_FOLDER}':")

files_list = []

for entry in result.entries:

entry_type = "📁" if isinstance(entry, dropbox.files.FolderMetadata) else "📄"

size_info = f" ({entry.size} bytes)" if hasattr(entry, 'size') else ""

print(f"    {entry_type} {entry.name}{size_info}")

files_list.append(entry.name)

if result.has_more:

print("    ... (hay más archivos)")

self.results['list_files'] = {

'success': True,

'files': files_list,

'count': len(files_list)

}

self.print_result(True, f"Se encontraron {len(files_list)} elementos")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['list_files'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 6. OBTENER METADATOS

# =========================================================================

def demo_get_metadata(self):

"""Demuestra cómo obtener metadatos de un archivo."""

self.print_section("6. OBTENER METADATOS")

file_path = f"{DEMO_FOLDER}/{TEST_FILE_NAME}"

try:

metadata = self.dbx.files_get_metadata(file_path)

print(f"\n  Archivo: {metadata.path_display}")

print(f"  Nombre: {metadata.name}")

print(f"  ID: {metadata.id}")

if isinstance(metadata, dropbox.files.FileMetadata):

print(f"  Tamaño: {metadata.size} bytes")

print(f"  Modificado (servidor): {metadata.server_modified}")

print(f"  Modificado (cliente): {metadata.client_modified}")

print(f"  Rev: {metadata.rev}")

print(f"  Content hash: {metadata.content_hash[:20]}...")

self.results['get_metadata'] = {

'success': True,

'path': metadata.path_display

}

self.print_result(True, "Metadatos obtenidos correctamente")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['get_metadata'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 7. DESCARGAR ARCHIVO

# =========================================================================

def demo_download_file(self):

"""Demuestra cómo descargar un archivo."""

self.print_section("7. DESCARGAR ARCHIVO")

file_path = f"{DEMO_FOLDER}/{TEST_FILE_NAME}"

try:

metadata, response = self.dbx.files_download(file_path)

content = response.content.decode('utf-8')

print(f"\n  Archivo descargado: {metadata.path_display}")

print(f"  Tamaño: {metadata.size} bytes")

print(f"\n  Contenido (primeros 200 caracteres):")

print(f"  {'-' * 40}")

print(f"  {content[:200]}...")

self.results['download_file'] = {

'success': True,

'path': metadata.path_display,

'size': metadata.size

}

self.print_result(True, "Archivo descargado correctamente")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['download_file'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 8. COPIAR ARCHIVO

# =========================================================================

def demo_copy_file(self):

"""Demuestra cómo copiar un archivo."""

self.print_section("8. COPIAR ARCHIVO")

source_path = f"{DEMO_FOLDER}/{TEST_FILE_NAME}"

dest_path = f"{DEMO_FOLDER}/copia_{TEST_FILE_NAME}"

try:

result = self.dbx.files_copy_v2(source_path, dest_path)

print(f"\n  Origen: {source_path}")

print(f"  Destino: {result.metadata.path_display}")

self.results['copy_file'] = {

'success': True,

'source': source_path,

'destination': result.metadata.path_display

}

self.print_result(True, "Archivo copiado correctamente")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['copy_file'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 9. MOVER/RENOMBRAR ARCHIVO

# =========================================================================

def demo_move_file(self):

"""Demuestra cómo mover o renombrar un archivo."""

self.print_section("9. MOVER/RENOMBRAR ARCHIVO")

source_path = f"{DEMO_FOLDER}/copia_{TEST_FILE_NAME}"

dest_path = f"{DEMO_FOLDER}/archivo_renombrado.txt"

try:

result = self.dbx.files_move_v2(source_path, dest_path)

print(f"\n  Origen: {source_path}")

print(f"  Destino: {result.metadata.path_display}")

self.results['move_file'] = {

'success': True,

'source': source_path,

'destination': result.metadata.path_display

}

self.print_result(True, "Archivo movido/renombrado correctamente")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['move_file'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 10. BÚSQUEDA DE ARCHIVOS

# =========================================================================

def demo_search_files(self):

"""Demuestra cómo buscar archivos."""

self.print_section("10. BÚSQUEDA DE ARCHIVOS")

try:

result = self.dbx.files_search_v2("prueba")

print(f"\n  Búsqueda: 'prueba'")

print(f"  Resultados encontrados:")

matches = []

for match in result.matches:

# La estructura de search_v2 es diferente

match_metadata = match.metadata

if hasattr(match_metadata, 'get_metadata'):

file_metadata = match_metadata.get_metadata()

path = file_metadata.path_display

print(f"    📄 {path}")

matches.append(path)

if not matches:

print("    (No se encontraron resultados)")

self.results['search_files'] = {

'success': True,

'query': 'prueba',

'matches': matches

}

self.print_result(True, f"Búsqueda completada: {len(matches)} resultados")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['search_files'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 11. CREAR ENLACE COMPARTIDO

# =========================================================================

def demo_create_shared_link(self):

"""Demuestra cómo crear un enlace compartido."""

self.print_section("11. CREAR ENLACE COMPARTIDO")

file_path = f"{DEMO_FOLDER}/{TEST_FILE_NAME}"

try:

# Intentar crear un nuevo enlace compartido

settings = dropbox.sharing.SharedLinkSettings(

requested_visibility=dropbox.sharing.RequestedVisibility.public

)

try:

result = self.dbx.sharing_create_shared_link_with_settings(

file_path,

settings=settings

)

shared_url = result.url

except ApiError as e:

# Si ya existe un enlace, obtenerlo

if e.error.is_shared_link_already_exists():

links = self.dbx.sharing_list_shared_links(path=file_path)

if links.links:

shared_url = links.links[0].url

else:

raise e

else:

raise e

print(f"\n  Archivo: {file_path}")

print(f"  URL compartida: {shared_url}")

self.results['shared_link'] = {

'success': True,

'path': file_path,

'url': shared_url

}

self.print_result(True, "Enlace compartido creado correctamente")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['shared_link'] = {'success': False, 'error': str(e)}

return False

except Exception as e:

# Manejar errores de permisos (scope no habilitado)

error_msg = str(e)

if 'sharing.write' in error_msg:

print(f"\n  ⚠️  La app no tiene el permiso 'sharing.write' habilitado")

print(f"  Esta función requiere configurar el scope en la consola de Dropbox")

self.results['shared_link'] = {

'success': False,

'error': 'Scope sharing.write no habilitado',

'note': 'Requiere configuración en App Console'

}

self.print_result(False, "Permiso 'sharing.write' no disponible")

else:

self.print_result(False, f"Error: {e}")

self.results['shared_link'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 12. ELIMINAR ARCHIVO

# =========================================================================

def demo_delete_file(self):

"""Demuestra cómo eliminar un archivo."""

self.print_section("12. ELIMINAR ARCHIVO")

file_path = f"{DEMO_FOLDER}/archivo_renombrado.txt"

try:

result = self.dbx.files_delete_v2(file_path)

print(f"\n  Archivo eliminado: {result.metadata.path_display}")

self.results['delete_file'] = {

'success': True,

'path': result.metadata.path_display

}

self.print_result(True, "Archivo eliminado correctamente")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['delete_file'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# 13. OBTENER HISTORIAL DE REVISIONES

# =========================================================================

def demo_get_revisions(self):

"""Demuestra cómo obtener el historial de revisiones de un archivo."""

self.print_section("13. HISTORIAL DE REVISIONES")

file_path = f"{DEMO_FOLDER}/{TEST_FILE_NAME}"

try:

result = self.dbx.files_list_revisions(file_path)

print(f"\n  Archivo: {file_path}")

print(f"  Revisiones encontradas: {len(result.entries)}")

for i, rev in enumerate(result.entries[:5], 1):

print(f"    {i}. Rev: {rev.rev[:10]}... | Fecha: {rev.server_modified}")

self.results['revisions'] = {

'success': True,

'path': file_path,

'count': len(result.entries)

}

self.print_result(True, f"Se encontraron {len(result.entries)} revisiones")

return True

except ApiError as e:

self.print_result(False, f"Error: {e}")

self.results['revisions'] = {'success': False, 'error': str(e)}

return False

# =========================================================================

# RESUMEN FINAL

# =========================================================================

def print_summary(self):

"""Imprime un resumen de todas las operaciones realizadas."""

self.print_section("RESUMEN DE OPERACIONES")

total = len(self.results)

successful = sum(1 for r in self.results.values() if r.get('success', False))

failed = total - successful

print(f"\n  Total de operaciones: {total}")

print(f"  Exitosas: {successful} ✓")

print(f"  Fallidas: {failed} ✗")

print(f"\n  Tasa de éxito: {(successful/total)*100:.1f}%")

print("\n  Detalle por operación:")

for op_name, result in self.results.items():

status = "✓" if result.get('success', False) else "✗"

print(f"    [{status}] {op_name}")

return self.results

def run_all_demos(self):

"""Ejecuta todas las demostraciones."""

print("\n" + "=" * 60)

print("  DEMOSTRACIÓN DE LA API DE DROPBOX")

print("  SDK Version: " + dropbox.__version__)

print("=" * 60)

# Ejecutar todas las demos en orden

self.demo_account_info()

self.demo_space_usage()

self.demo_create_folder()

self.demo_upload_file()

self.demo_list_files()

self.demo_get_metadata()

self.demo_download_file()

self.demo_copy_file()

self.demo_move_file()

self.demo_search_files()

self.demo_create_shared_link()

self.demo_delete_file()

self.demo_get_revisions()

# Mostrar resumen

return self.print_summary()

def main():

"""Función principal."""

try:

demo = DropboxDemo()

results = demo.run_all_demos()

# Guardar resultados en JSON

with open('/home/ubuntu/dropbox_demo_results.json', 'w') as f:

json.dump(results, f, indent=2, default=str)

print("\n" + "=" * 60)

print("  Resultados guardados en: dropbox_demo_results.json")

print("=" * 60 + "\n")

except ValueError as e:

print(f"Error de configuración: {e}")

except Exception as e:

print(f"Error inesperado: {e}")

raise

if __name__ == "__main__":

main()

## 4. Resultados de la Ejecución

El script se ejecutó con éxito, realizando 12 de las 13 operaciones planeadas. La única operación que falló fue la creación de enlaces compartidos, como se detalla a continuación.

### Resumen de Ejecución

Total de operaciones: 13

Exitosas: 12 (92.3%)

Fallidas: 1 (7.7%)

### Detalle del Fallo: Creación de Enlace Compartido

La operación demo_create_shared_link falló debido a un error de permisos. El mensaje de error de la API fue el siguiente:

Error in call to API function "sharing/create_shared_link_with_settings": Your app is not permitted to access this endpoint because it does not have the required scope 'sharing.write'.

Explicación:
Para que una aplicación pueda crear o modificar enlaces compartidos, debe tener el permiso (o scope) sharing.write habilitado. Este permiso se configura en la App Console de Dropbox, en la pestaña de "Permissions". La clave de API utilizada para esta demostración no tenía este permiso activado, lo que resultó en el fallo. El script ha sido modificado para capturar este error específico y mostrar un mensaje informativo.

### Archivo de Resultados (JSON)

Los resultados detallados de cada operación se guardaron en el archivo dropbox_demo_results.json, que se adjunta con este informe. Este archivo muestra el éxito o fracaso de cada paso y los datos relevantes obtenidos.

## 5. Conclusión

La API de Dropbox es una herramienta potente y flexible para la gestión de archivos en la nube. El SDK de Python simplifica enormemente la interacción con la API, permitiendo a los desarrolladores integrar fácilmente funcionalidades de almacenamiento y compartición de archivos en sus aplicaciones.

La demostración ha validado con éxito la mayoría de las operaciones fundamentales. El fallo en la creación de enlaces compartidos sirve como un recordatorio importante de la necesidad de configurar correctamente los permisos de la aplicación en la consola de Dropbox para acceder a todas las funcionalidades deseadas.



| Funcionalidad | Método del SDK (Python) | Descripción |

| Gestión de Cuenta | users_get_current_account() | Obtiene información detallada de la cuenta del usuario autenticado, como nombre, email y tipo de cuenta. |

| Uso de Espacio | users_get_space_usage() | Consulta el espacio de almacenamiento total y el utilizado por el usuario. |

| Creación de Carpetas | files_create_folder_v2() | Crea nuevas carpetas en una ruta específica dentro de la estructura de Dropbox. |

| Subida de Archivos | files_upload() | Sube contenido a Dropbox, permitiendo especificar el modo de escritura (sobrescribir, renombrar) y otros atributos. |

| Listado de Contenido | files_list_folder() | Enumera los archivos y subcarpetas contenidos en una carpeta específica. |

| Metadatos de Archivos | files_get_metadata() | Recupera información detallada de un archivo o carpeta, como tamaño, fecha de modificación, ID y hash de contenido. |

| Descarga de Archivos | files_download() | Descarga el contenido de un archivo específico desde Dropbox. |

| Copia de Archivos | files_copy_v2() | Crea una copia de un archivo o carpeta en una nueva ubicación. |

| Movimiento de Archivos | files_move_v2() | Mueve o renombra un archivo o carpeta a una nueva ruta. |

| Búsqueda | files_search_v2() | Realiza búsquedas de texto completo dentro de los nombres de archivo y, en algunos casos, del contenido. |

| Enlaces Compartidos | sharing_create_shared_link_with_settings() | Genera un enlace público o restringido para compartir un archivo o carpeta. Nota: Requiere el permiso (scope) sharing.write en la configuración de la app. |

| Eliminación | files_delete_v2() | Elimina permanentemente un archivo o carpeta. |

| Historial de Versiones | files_list_revisions() | Obtiene una lista de las revisiones o versiones anteriores de un archivo, permitiendo la restauración de estados previos. |

