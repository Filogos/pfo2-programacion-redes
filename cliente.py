from getpass import getpass

import requests

URL = "http://127.0.0.1:5000"


def mostrar_respuesta(respuesta):
    print(f"\nCódigo HTTP: {respuesta.status_code}")

    if "application/json" in respuesta.headers.get("Content-Type", ""):
        datos = respuesta.json()
        print(datos.get("mensaje") or datos.get("error") or datos)
    else:
        print(respuesta.text)


def main():
    # Conserva la cookie recibida al iniciar sesión.
    with requests.Session() as cliente:
        while True:
            print("\n--- Sistema de gestión de tareas ---")
            print("1. Registrarse")
            print("2. Iniciar sesión")
            print("3. Acceder a tareas")
            print("4. Salir")

            opcion = input("Elegí una opción: ").strip()

            try:
                if opcion in ("1", "2"):
                    usuario = input("Usuario: ").strip()
                    contraseña = getpass("Contraseña: ")

                    ruta = "/registro" if opcion == "1" else "/login"

                    respuesta = cliente.post(
                        URL + ruta,
                        json={
                            "usuario": usuario,
                            "contraseña": contraseña
                        },
                        timeout=10
                    )
                    mostrar_respuesta(respuesta)

                elif opcion == "3":
                    respuesta = cliente.get(
                        URL + "/tareas",
                        timeout=10
                    )
                    mostrar_respuesta(respuesta)

                elif opcion == "4":
                    print("Cliente finalizado.")
                    break

                else:
                    print("Opción inválida. Elegí entre 1 y 4.")

            except requests.exceptions.ConnectionError:
                print(
                    "\nNo se pudo conectar con el servidor. "
                    "Verificá que servidor.py esté ejecutándose."
                )
            except requests.exceptions.Timeout:
                print("\nEl servidor tardó demasiado en responder.")
            except requests.exceptions.RequestException as error:
                print(f"\nError en la petición: {error}")


if __name__ == "__main__":
    main()