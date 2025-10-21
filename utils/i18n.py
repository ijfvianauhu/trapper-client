import subprocess
import os

# Constante para el nombre del paquete/proyecto
PACKAGE_NAME = "trapper_client"

def extract_translations():
    """
    Genera el archivo POT a partir de las cadenas marcadas en el proyecto.
    """
    subprocess.run([
        "pybabel",
        "extract",
        "-F", "babel.cfg",
        "-o", f"{PACKAGE_NAME}/ui/typer/locales/messages.pot",
        "."
    ], check=True)
    print(f"Archivo POT generado en {PACKAGE_NAME}/ui/typer/locales/messages.pot")

def init_translation(lang="en"):
    """
    Genera el archivo PO para el idioma especificado a partir del POT.
    Si el PO ya existe, actualiza su contenido.
    """
    po_dir = f"{PACKAGE_NAME}/ui/typer/locales/{lang}/LC_MESSAGES"
    po_file = os.path.join(po_dir, "messages.po")

    # Crear carpeta si no existe
    os.makedirs(po_dir, exist_ok=True)

    if not os.path.exists(po_file):
        # Inicializar archivo PO si no existe
        subprocess.run([
            "pybabel",
            "init",
            "-i", f"{PACKAGE_NAME}/locales/messages.pot",
            "-d", f"{PACKAGE_NAME}/locales",
            "-l", lang
        ], check=True)
        print(f"Archivo PO creado para idioma {lang} en {po_file}")
    else:
        # Actualizar PO existente
        subprocess.run([
            "pybabel",
            "update",
            "-i", f"{PACKAGE_NAME}/ui/typer/locales/messages.pot",
            "-d", f"{PACKAGE_NAME}/ui/typer/locales",
            "-l", lang
        ], check=True)
        print(f"Archivo PO actualizado para idioma {lang} en {po_file}")

def compile_translations():
    """
    Compila todos los archivos PO a MO para que Python pueda usarlos.
    """
    locales_dir = f"{PACKAGE_NAME}/ui/typer/locales"
    subprocess.run([
        "pybabel",
        "compile",
        "-d", locales_dir
    ], check=True)
    print("Todos los archivos PO han sido compilados a MO")
