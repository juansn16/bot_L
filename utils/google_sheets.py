import os
from typing import List, Optional
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _build_credentials() -> service_account.Credentials:
    """Crea credenciales desde un archivo de cuenta de servicio.
    
    Busca el archivo en este orden de prioridad:
    1. Variable de entorno GOOGLE_SERVICE_ACCOUNT_FILE (ruta absoluta o relativa)
    2. Variable de entorno GOOGLE_APPLICATION_CREDENTIALS (ruta absoluta o relativa)
    3. Archivo 'prefab-mapper-446507-v8-1a1433a487d4.json' en el directorio raíz
    """
    # Obtener el directorio raíz donde se ejecuta el script
    root_dir = Path.cwd()
    
    # 1. Buscar en variable de entorno GOOGLE_SERVICE_ACCOUNT_FILE
    env_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if env_file:
        env_path = Path(env_file)
        if env_path.is_absolute() and env_path.exists():
            return service_account.Credentials.from_service_account_file(
                str(env_path), scopes=SCOPES
            )
        # Si es ruta relativa, buscar desde el directorio raíz
        relative_path = root_dir / env_file
        if relative_path.exists():
            return service_account.Credentials.from_service_account_file(
                str(relative_path), scopes=SCOPES
            )
    
    # 2. Buscar en variable de entorno GOOGLE_APPLICATION_CREDENTIALS
    app_cred_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if app_cred_file:
        app_cred_path = Path(app_cred_file)
        if app_cred_path.is_absolute() and app_cred_path.exists():
            return service_account.Credentials.from_service_account_file(
                str(app_cred_path), scopes=SCOPES
            )
        # Si es ruta relativa, buscar desde el directorio raíz
        relative_path = root_dir / app_cred_file
        if relative_path.exists():
            return service_account.Credentials.from_service_account_file(
                str(relative_path), scopes=SCOPES
            )
    
    # 3. Buscar el archivo específico en el directorio raíz
    default_file = root_dir / "prefab-mapper-446507-v8-1a1433a487d4.json"
    if default_file.exists():
        return service_account.Credentials.from_service_account_file(
            str(default_file), scopes=SCOPES
        )
    
    # 4. Si no se encuentra ningún archivo, mostrar error con información útil
    raise FileNotFoundError(
        "No se encontró el archivo de credenciales de Google. \n"
        "Busqué en:\n"
        f"1. Variable GOOGLE_SERVICE_ACCOUNT_FILE: {env_file}\n"
        f"2. Variable GOOGLE_APPLICATION_CREDENTIALS: {app_cred_file}\n"
        f"3. Archivo en directorio raíz: {default_file}\n"
        "Asegúrate de que el archivo JSON exista en una de estas ubicaciones."
    )

def _get_sheets_service():
    credentials = _build_credentials()
    service = build("sheets", "v4", credentials=credentials)
    return service.spreadsheets()

def append_row(spreadsheet_id: str, sheet_name: str, row_values: List[Optional[str]]):
    """Inserta una fila al final de la hoja especificada de manera segura para múltiples usuarios."""
    if not spreadsheet_id:
        raise ValueError("spreadsheet_id es requerido")
    if not sheet_name:
        raise ValueError("sheet_name es requerido")

    sheets = _get_sheets_service()
    
    # Estrategia: usar append con inserción de fila
    # INSERT_ROWS asegura que Google Sheets maneje la concurrencia internamente
    range_name = f"{sheet_name}!B:AT"
    values = [row_values]

    request = sheets.values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    )
    return request.execute()