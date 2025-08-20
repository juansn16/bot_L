import os
import base64
import json
from typing import List, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _build_credentials() -> service_account.Credentials:
    """Crea credenciales desde variable de entorno base64 o archivo."""
    # Primero intentar con base64 desde variable de entorno
    credentials_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
    
    if credentials_base64:
        try:
            # Decodificar el base64
            credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
            credentials_info = json.loads(credentials_json)
            
            return service_account.Credentials.from_service_account_info(
                credentials_info, scopes=SCOPES
            )
        except (base64.binascii.Error, json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Error decodificando las credenciales base64: {str(e)}")
    
    # Fallback: intentar con archivo de credenciales
    credentials_file = (
        os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    
    if credentials_file and os.path.exists(credentials_file):
        return service_account.Credentials.from_service_account_file(
            credentials_file, scopes=SCOPES
        )
    
    # Si no hay ninguna opción disponible
    raise ValueError(
        "No se encontraron credenciales de Google. "
        "Defina GOOGLE_CREDENTIALS_BASE64 (base64) o "
        "GOOGLE_SERVICE_ACCOUNT_FILE/GOOGLE_APPLICATION_CREDENTIALS (ruta de archivo)."
    )

def _get_sheets_service():
    """Obtiene el servicio de Google Sheets."""
    credentials = _build_credentials()
    service = build("sheets", "v4", credentials=credentials)
    return service.spreadsheets()

def append_row(spreadsheet_id: str, sheet_name: str, row_values: List[Optional[str]]):
    """
    Inserta una fila al final de la hoja especificada.
    
    Args:
        spreadsheet_id: ID de la hoja de cálculo de Google
        sheet_name: Nombre de la hoja dentro del spreadsheet
        row_values: Lista de valores para la fila
    """
    if not spreadsheet_id:
        raise ValueError("spreadsheet_id es requerido")
    if not sheet_name:
        raise ValueError("sheet_name es requerido")

    sheets = _get_sheets_service()
    
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
def read_range(spreadsheet_id: str, range_name: str):
    """Lee un rango de datos de la hoja de cálculo."""
    sheets = _get_sheets_service()
    
    result = sheets.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    
    return result.get('values', [])

# Función para actualizar celdas específicas
def update_cell(spreadsheet_id: str, range_name: str, value: any):
    """Actualiza una celda o rango específico."""
    sheets = _get_sheets_service()
    
    request = sheets.values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body={"values": [[value]]}
    )
    return request.execute()

# Función para limpiar un rango
def clear_range(spreadsheet_id: str, range_name: str):
    """Limpia el contenido de un rango."""
    sheets = _get_sheets_service()
    
    request = sheets.values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_name
    )
    return request.execute()