# This file will contain all folder logic.

def find_folder(service, parent_id, folder_name):
    query = (
        f"name = '{folder_name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents "
        f"and trashed = false"
    )

    results = service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()

    folders = results.get("files", [])
    return folders

def create_folder(service, parent_id, folder_name):
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }

    folder = service.files().create(
        body=file_metadata,
        fields="id"
    ).execute()

    return folder.get("id")

def get_or_create_folder(service, parent_id, folder_name):
    folders = find_folder(service, parent_id, folder_name)

    if len(folders) == 0:
        # Folder not found → create
        return create_folder(service, parent_id, folder_name)

    elif len(folders) == 1:
        # Folder exists → return its ID
        return folders[0]["id"]

    else:
        # Multiple matches → take first (safe fallback)
        return folders[0]["id"]
    
def traverse_structure(service, root_id, year, month, language):
    # Root → Year
    year_id = get_or_create_folder(service, root_id, year)

    # Year → Month
    month_id = get_or_create_folder(service, year_id, month)

    # Month → Language
    language_id = get_or_create_folder(service, month_id, language)

    # Return Language folder ID directly
    return language_id

def list_srt_files(service, folder_id):
    query = (
        f"'{folder_id}' in parents "
        f"and trashed = false "
        f"and name contains '.srt'"
    )

    results = service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()

    return results.get("files", [])

from googleapiclient.http import MediaIoBaseDownload
import io


def download_file_content(service, file_id):
    request = service.files().get_media(fileId=file_id)
    file_stream = io.BytesIO()

    downloader = MediaIoBaseDownload(file_stream, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    file_stream.seek(0)
    return file_stream.read().decode("utf-8")


