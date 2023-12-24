"""
AI utils
"""

import os

from gradio_client import Client

poketwo_client = Client(
    "https://lightningdev1-poketwo.hf.space/--replicas/jr4pv/",
    hf_token=os.environ["HF_TOKEN"],
)


def get_poketwo_prediction(url: str) -> tuple[str, float]:
    """
    Get a prediction from Poketwo
    """

    try:
        result = poketwo_client.predict(url)
    except Exception as exc:
        raise Exception("Failed to get predictions") from exc

    return result["label"], result["confidences"][0]["confidence"]
