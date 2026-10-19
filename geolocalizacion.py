import os
import sys
import requests

URL_GEOCODIFICACION = "https://graphhopper.com/api/1/geocode"
URL_RUTA = "https://graphhopper.com/api/1/route"

CLAVE_API = os.getenv("GRAPHHOPPER_API_KEY", "").strip()

if not CLAVE_API:
    print(
        "Error: configura la variable de entorno "
        "GRAPHHOPPER_API_KEY con tu clave de GraphHopper."
    )
    sys.exit(1)


def pedir_dato(mensaje):
    """Solicita un dato y permite salir con s o salir."""
    dato = input(mensaje).strip()

    if dato.casefold() in {"s", "salir"}:
        print("Programa finalizado. ¡Hasta pronto!")
        sys.exit(0)

    return dato


def geocodificar(ubicacion):
    """Convierte una ubicación escrita en coordenadas."""
    respuesta = requests.get(
        URL_GEOCODIFICACION,
        params={
            "q": ubicacion,
            "limit": 1,
            "locale": "es",
            "key": CLAVE_API
        },
        timeout=20
    )

    datos = respuesta.json()

    if respuesta.status_code != 200:
        raise RuntimeError(
            "No se pudo localizar la dirección. "
            f"Código HTTP: {respuesta.status_code}."
        )

    resultados = datos.get("hits", [])

    if not resultados:
        raise RuntimeError(
            f"No se encontró la ubicación: {ubicacion}."
        )

    resultado = resultados[0]
    punto = resultado["point"]

    nombre = resultado.get("name", ubicacion)
    estado = resultado.get("state", "")
    pais = resultado.get("country", "")

    nombre_completo = ", ".join(
        parte for parte in [nombre, estado, pais] if parte
    )

    latitud = float(punto["lat"])
    longitud = float(punto["lng"])

    print(f"Ubicación identificada: {nombre_completo}")

    return latitud, longitud, nombre_completo


def calcular_ruta(origen, destino, transporte):
    """Solicita a GraphHopper una ruta con instrucciones en español."""
    lat_origen, lon_origen, nombre_origen = origen
    lat_destino, lon_destino, nombre_destino = destino

    respuesta = requests.get(
        URL_RUTA,
        params={
            "key": CLAVE_API,
            "vehicle": transporte,
            "locale": "es",
            "instructions": "true",
            "point": [
                f"{lat_origen},{lon_origen}",
                f"{lat_destino},{lon_destino}"
            ]
        },
        timeout=30
    )

    datos = respuesta.json()

    if respuesta.status_code != 200:
        raise RuntimeError(
            "No fue posible calcular la ruta. "
            f"Código HTTP: {respuesta.status_code}."
        )

    rutas = datos.get("paths", [])

    if not rutas:
        raise RuntimeError(
            "La API no devolvió una ruta para las ubicaciones ingresadas."
        )

    ruta = rutas[0]

    distancia_km = float(ruta["distance"]) / 1000

    # GraphHopper entrega el tiempo en milisegundos.
    duracion_segundos = int(float(ruta["time"]) / 1000)
    horas, resto = divmod(duracion_segundos, 3600)
    minutos, segundos = divmod(resto, 60)

    print("\n========================================")
    print("RESUMEN DEL VIAJE")
    print("========================================")
    print(f"Origen: {nombre_origen}")
    print(f"Destino: {nombre_destino}")
    print(f"Distancia total: {distancia_km:.2f} km")
    print(
        f"Duración estimada: "
        f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    )

    print("\nINSTRUCCIONES DEL VIAJE")
    print("----------------------------------------")

    instrucciones = ruta.get("instructions", [])

    if not instrucciones:
        print("La API no devolvió instrucciones paso a paso.")
        return

    for numero, instruccion in enumerate(instrucciones, start=1):
        texto = instruccion.get(
            "text",
            "Instrucción no disponible."
        )

        distancia_paso_km = (
            float(instruccion.get("distance", 0)) / 1000
        )

        print(
            f"{numero}. {texto} "
            f"({distancia_paso_km:.2f} km)"
        )

    print("----------------------------------------")


def main():
    print("========================================")
    print("PLANIFICADOR DE RUTAS - BIBLIOTECA")
    print("========================================")
    print("Escribe 's' o 'salir' en cualquier pregunta para terminar.\n")

    while True:
        try:
            ubicacion_inicio = pedir_dato(
                "Ingresa el punto de partida: "
            )

            if not ubicacion_inicio:
                print("Debes ingresar un punto de partida.\n")
                continue

            ubicacion_destino = pedir_dato(
                "Ingresa el destino: "
            )

            if not ubicacion_destino:
                print("Debes ingresar un destino.\n")
                continue

            print("\nMedios de transporte disponibles:")
            print("auto, bicicleta, a pie")

            opcion = pedir_dato(
                "Selecciona el medio de transporte: "
            ).casefold()

            transportes = {
                "auto": "car",
                "automovil": "car",
                "automóvil": "car",
                "car": "car",
                "bicicleta": "bike",
                "bici": "bike",
                "bike": "bike",
                "a pie": "foot",
                "pie": "foot",
                "foot": "foot"
            }

            if opcion not in transportes:
                print(
                    "Medio de transporte no válido. "
                    "Usa auto, bicicleta o a pie.\n"
                )
                continue

            print("\nBuscando la ubicación de partida...")
            origen = geocodificar(ubicacion_inicio)

            print("\nBuscando el destino...")
            destino = geocodificar(ubicacion_destino)

            print("\nCalculando la ruta...")
            calcular_ruta(
                origen,
                destino,
                transportes[opcion]
            )

            print(
                "\nPuedes consultar otra ruta o escribir "
                "'s' para salir.\n"
            )

        except requests.RequestException:
            print(
                "Error de conexión con GraphHopper. "
                "Revisa tu conexión a Internet e inténtalo nuevamente.\n"
            )

        except (ValueError, KeyError, IndexError):
            print(
                "La respuesta recibida de la API no tiene "
                "el formato esperado.\n"
            )

        except RuntimeError as error:
            print(f"{error}\n")


if __name__ == "__main__":
    main()