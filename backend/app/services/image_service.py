import io
from typing import Dict, Optional
from PIL import Image
import numpy as np
import pytesseract
import piexif


def _extract_exif(img: Image.Image) -> Dict[str, str]:
    try:
        exif_bytes = img.info.get("exif")
        if not exif_bytes:
            return {}
        data = piexif.load(exif_bytes)
        readable = {}
        for ifd in ("0th", "Exif", "GPS", "1st"):
            for tag, val in data.get(ifd, {}).items():
                tag_name = piexif.TAGS[ifd][tag]["name"]
                readable[tag_name] = str(val)
        return readable
    except Exception:
        return {}


def _infer_platform(text: str) -> Optional[str]:
    t = text.lower()
    patterns = {
        "facebook": "facebook",
        "instagram": "instagram",
        "twitter": "twitter",
        "linkedin": "linkedin",
    }
    for name, pat in patterns.items():
        if pat in t:
            return name.capitalize()
    return None


def analyze_image_bytes(data: bytes) -> Dict:
    try:
        import face_recognition
    except Exception:  # noqa: BLE001
        face_recognition = None
    try:
        import cvlib as cv
    except Exception:  # noqa: BLE001
        cv = None

    img = Image.open(io.BytesIO(data))
    width, height = img.size
    fmt = img.format or "unknown"

    exif = _extract_exif(img)
    text = pytesseract.image_to_string(img)

    arr = np.array(img.convert("RGB"))
    faces = face_recognition.face_locations(arr) if face_recognition else []
    if cv:
        bbox, labels, _ = cv.detect_common_objects(
            arr, confidence=0.25, model="yolov3-tiny"
        )
        objects = list(set(labels))
    else:
        objects = []

    platform = _infer_platform(text)
    return {
        "dimensions": f"{width}x{height}",
        "format": fmt,
        "text": text.strip(),
        "faces_detected": len(faces),
        "objects": objects,
        "exif": exif or None,
        "inferred_platform": platform,
    }


async def a_analyze_image_bytes(data: bytes) -> Dict:
    import asyncio
    return await asyncio.to_thread(analyze_image_bytes, data)
