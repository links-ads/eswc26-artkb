from typing import Tuple
from io import BytesIO
import uuid
import magic

def infer_content_type(image_bytes: bytes) -> str:
    """
    Inferisce il content type dai byte di un'immagine.

    Args:
        image_bytes: I byte dell'immagine.

    Returns:
        Il content type inferito (ad esempio, "image/jpeg", "image/png"),
        oppure "application/octet-stream" se non è possibile determinarlo.
    """
    try:
        mime_type = magic.from_buffer(image_bytes, mime=True)
        return mime_type
    except Exception:
        return "application/octet-stream"  # Tipo di fallback generico




def get_file_by_id(minio, file_id: str, bucket_name:str, **kwargs) -> Tuple[BytesIO, str]:
    file_stream = BytesIO()
    minio.download_fileobj(bucket_name, file_id, file_stream)
    file_stream.seek(0)  # Torna all'inizio del flusso
    metadata = minio.head_object(Bucket=bucket_name, Key=file_id)
    return file_stream, metadata.get("ContentType", "application/octet-stream")


def upload_file_content(minio, file_bytes: bytes, file_id:str,bucket_name:str, **kwargs) -> str:
    content_type = infer_content_type(file_bytes)
    file_io = BytesIO(file_bytes)
    if file_id is None:
        file_id = str(uuid.uuid4())    
    minio.upload_fileobj(
        Fileobj=file_io,
        Bucket=bucket_name,
        Key=file_id,
        ExtraArgs={
            "ContentType": content_type
        }
    )
    return file_id