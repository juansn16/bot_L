import os
import base64
import json
from typing import List, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _build_credentials_from_base64(credentials_base64: str) -> service_account.Credentials:
    """Crea credenciales desde un string base64."""
    if not credentials_base64:
        raise ValueError("El string base64 de credenciales es requerido")
    
    try:
        # Decodificar el base64
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        credentials_info = json.loads(credentials_json)
        
        return service_account.Credentials.from_service_account_info(
            credentials_info, scopes=SCOPES
        )
    except (base64.binascii.Error, json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Error decodificando las credenciales: {str(e)}")

def _build_credentials_from_file() -> service_account.Credentials:
    """Crea credenciales desde un archivo de cuenta de servicio (fallback)."""
    credentials_file = (
        os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    if not credentials_file or not os.path.exists(credentials_file):
        raise FileNotFoundError(
            "No se encontró el archivo de credenciales de Google. "
            "Defina GOOGLE_SERVICE_ACCOUNT_FILE o GOOGLE_APPLICATION_CREDENTIALS con la ruta del JSON."
        )

    return service_account.Credentials.from_service_account_file(
        credentials_file, scopes=SCOPES
    )

def _get_sheets_service(credentials_base64: str = None):
    """Obtiene el servicio de Google Sheets."""
    if credentials_base64:
        credentials = _build_credentials_from_base64(credentials_base64)
    else:
        credentials = _build_credentials_from_file()
    
    service = build("sheets", "v4", credentials=credentials)
    return service.spreadsheets()

def append_row(
    spreadsheet_id: str, 
    sheet_name: str, 
    row_values: List[Optional[str]], 
    credentials_base64: str = None
):
    """
    Inserta una fila al final de la hoja especificada.
    
    Args:
        spreadsheet_id: ID de la hoja de cálculo de Google
        sheet_name: Nombre de la hoja dentro del spreadsheet
        row_values: Lista de valores para la fila
        credentials_base64: Credenciales en formato base64 (opcional)
    """
    if not spreadsheet_id:
        raise ValueError("spreadsheet_id es requerido")
    if not sheet_name:
        raise ValueError("sheet_name es requerido")

    sheets = _get_sheets_service(credentials_base64)
    
    # Cambiar el rango para cubrir desde la columna A hasta AS
    range_name = f"{sheet_name}!A:AS"
    values = [row_values]

    request = sheets.values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    )
    return request.execute()

# Función adicional para leer datos
def read_range(
    spreadsheet_id: str,
    range_name: str,
    credentials_base64: str = None
):
    """Lee un rango de datos de la hoja de cálculo."""
    sheets = _get_sheets_service(credentials_base64)
    
    result = sheets.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    
    return result.get('values', [])

# Función para actualizar celdas específicas
def update_cell(
    spreadsheet_id: str,
    range_name: str,
    value: any,
    credentials_base64: str = None
):
    """Actualiza una celda o rango específico."""
    sheets = _get_sheets_service(credentials_base64)
    
    request = sheets.values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body={"values": [[value]]}
    )
    return request.execute()

# Función para limpiar un rango
def clear_range(
    spreadsheet_id: str,
    range_name: str,
    credentials_base64: str = None
):
    """Limpia el contenido de un rango."""
    sheets = _get_sheets_service(credentials_base64)
    
    request = sheets.values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_name
    )
    return request.execute()