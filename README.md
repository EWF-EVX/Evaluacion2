Descripción
Este proyecto implementa una aplicación de Python que consulta la API de GraphHopper para localizar dos direcciones y calcular una ruta entre ellas. El programa presenta el resumen del viaje y las instrucciones paso a paso en español.
La aplicación permite seleccionar un medio de transporte, muestra las distancias con un máximo de dos decimales y permite finalizar la ejecución ingresando s o salir.

Instalación
Instala la dependencia con el siguiente comando:
python3 -m pip install requests

Configura la clave de GraphHopper como variable de entorno:
export GRAPHHOPPER_API_KEY="TU_CLAVE_DE_API"
Reemplaza TU_CLAVE_DE_API por tu clave real. No publiques la clave en el repositorio.

Ejecución
Desde la carpeta del proyecto, ejecuta:
python3 geolocalizacion.py

Ingresa el punto de partida, el destino y el medio de transporte solicitado por el programa.
Para terminar, escribe s o salir cuando el programa solicite un dato.