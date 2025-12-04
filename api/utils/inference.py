import io
import time
from typing import List

import numpy as np
from PIL import Image
from PIL.ImageOps import exif_transpose
from tritonclient.http import (InferenceServerClient, InferenceServerException,
                               InferInput, InferRequestedOutput)

from api import logger
from api.config import TritonServiceConfig, config

Image.MAX_IMAGE_PIXELS = None

def triton_inference(
    service_cfg: TritonServiceConfig,
    img_bytes: bytes,
    text: str = "",
    triton_ssl: bool = False,
    max_retries: int = 5
):
    image = exif_transpose(Image.open(io.BytesIO(img_bytes)).convert("RGB"))
    image.thumbnail((512, 512))
    img_array = np.array(image).astype(np.uint8)
    image_array = np.expand_dims(img_array, axis=0)

    text_array = np.array([text], dtype=object)

    image_input = InferInput("image", image_array.shape, "UINT8")
    image_input.set_data_from_numpy(image_array)
    text_input = InferInput("text", text_array.shape, "BYTES")
    text_input.set_data_from_numpy(text_array.astype(np.bytes_))

    triton_output = InferRequestedOutput("output")
    
    triton_client = InferenceServerClient(service_cfg.url, connection_timeout=600.0, network_timeout=600.0, ssl=triton_ssl)
    retries = 0
    response = None
    while not response:
        try:
            response = triton_client.infer(model_name = service_cfg.model_name,
                                            model_version = "1",
                                            inputs = [image_input, text_input],
                                            outputs = [triton_output],
                                            headers = {"X-API-Key": service_cfg.key}
                                            )
        except InferenceServerException as e:
            if retries < max_retries:
                logger.warning(f"Failed to perform inference: {e}. Retrying...")
                retries += 1
                time.sleep(10)
            else:
                raise Exception(
                    f"Failed to perform inference after {max_retries} retries. {e}"
                )
        except Exception as e:
            raise Exception(f"Failed to perform inference: {e}")
    
    return response.as_numpy("output").squeeze()