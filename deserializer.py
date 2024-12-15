import numpy as np
import json

def deserialize(payload):

    # Extract metadata
    metadata_length = int.from_bytes(payload[:4], 'big')
    metadata = json.loads(payload[4:4 + metadata_length].decode('utf-8'))

    # Extract binary data
    binary_data = payload[4 + metadata_length:]
    chunk = np.frombuffer(binary_data, dtype=np.uint8).reshape(metadata['shape'])

    # print(metadata)
    # print(chunk.shape)
    return chunk