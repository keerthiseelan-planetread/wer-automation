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
    """
    List all .srt files in a folder (basic info).
    
    Args:
        service: Google Drive API service
        folder_id: Folder ID to search in
        
    Returns:
        List[Dict]: List of files with id and name
    """
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


def list_srt_files_with_metadata(service, folder_id):
    """
    List all .srt files with metadata for incremental processing.
    Includes file ID, name, modification time, and size for detecting changes.
    
    Args:
        service: Google Drive API service
        folder_id: Folder ID to search in
        
    Returns:
        List[Dict]: List of files with id, name, modifiedTime, size, webViewLink, createdTime
    """
    import logging
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    try:
        files = []
        query = (
            f"'{folder_id}' in parents "
            f"and trashed = false "
            f"and name contains '.srt'"
        )
        
        page_token = None
        while True:
            results = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime, size, webViewLink, createdTime)',
                pageSize=100,
                pageToken=page_token
            ).execute()
            
            for file in results.get('files', []):
                # Convert modifiedTime to datetime object for easier comparison
                modified_time = file.get('modifiedTime')
                if modified_time:
                    try:
                        # Parse ISO format timestamp
                        file['modified_datetime'] = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                    except Exception as e:
                        logger.warning(f"Could not parse modifiedTime for {file.get('name')}: {str(e)}")
                
                files.append(file)
            
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        
        logger.info(f"Found {len(files)} .srt files with metadata in folder {folder_id}")
        return files
        
    except Exception as error:
        logger.error(f"Error fetching file metadata: {str(error)}")
        return []


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


