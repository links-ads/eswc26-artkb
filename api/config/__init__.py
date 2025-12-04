from typing import Optional

import yaml
from pydantic import BaseModel, BaseSettings, validator


class TritonServiceConfig(BaseModel):
        url: str
        key: str
        model_name: str

class TritonConfig(BaseModel):
    universal_embedder: TritonServiceConfig

class BaseConfig(BaseSettings):
    # GraphDB Configuration
    graphdb_host: str
    graphdb_port: int
    graphdb_user: str
    graphdb_password: str
    graphdb_repo_name: str

    # MinIO Configuration
    minio_host: str
    minio_port: int
    minio_root_user: str
    minio_root_password: str
    minio_image_bucket_name: str
    minio_file_bucket_name: str

    # Qdrant Configuration
    qdrant_host: str
    qdrant_port: int
    qdrant_api_key: str
    qdrant_collection_name: str
    qdrant_collection_size: int

    # FastAPI Configuration
    api_url_prefix: str
    api_log_level: str = "INFO"
    api_secret: str
    
    # Triton Inference Server Configuration
    triton_ssl: bool = False
    triton_max_retries: int = 5
    triton_config_path: str
    triton_config: Optional[TritonConfig] = None
        
    @validator('triton_config', pre=True, always=True)
    def load_model_config(cls, v, values):
        path = values.get('triton_config_path')
        if not path:
            raise ValueError("triton_config_path non specificato")
        with open(path, 'r') as f:
            cfg = yaml.safe_load(f)
        return TritonConfig(**cfg)


    @validator('api_url_prefix')
    def api_prefix_must_start_with_slash(cls, v):
        if v != "" and not v.startswith('/'):
            return f'/{v}'
        return v

    @property
    def graphdb_url(self):
        return f"http://{self.graphdb_host}:{self.graphdb_port}"

    @property
    def graphdb_auth(self):
        return (self.graphdb_user, self.graphdb_password)

    @property
    def minio_url(self):
        return f"http://{self.minio_host}:{self.minio_port}"
    
    @property
    def qdrant_url(self):
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


config = BaseConfig()
