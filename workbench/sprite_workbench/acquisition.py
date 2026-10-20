"""Bounded local image import with retained source bytes and decoder identity."""
from fractions import Fraction
from io import BytesIO
from pathlib import Path
import struct
import zlib

import numpy as np
import PIL
from PIL import Image

from .core import MAX_FRAMES, MAX_PIXELS, MAX_SEQUENCE_BYTES, ValidationError, save_sequence


def _apng_timing(raw):
    """Read authoritative APNG delay fractions, rather than rounded Pillow ms."""
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        return None
    offset, control, holds = 8, None, []
    while offset + 12 <= len(raw):
        length = struct.unpack_from('>I', raw, offset)[0]
        kind = raw[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(raw):
            raise ValidationError('Truncated PNG chunk')
        body = raw[offset + 8:offset + 8 + length]
        if kind in (b'acTL', b'fcTL'):
            crc = struct.unpack_from('>I', raw, offset + 8 + length)[0]
            if zlib.crc32(kind + body) & 0xffffffff != crc:
                raise ValidationError('Invalid APNG control CRC')
            if kind == b'acTL':
                if control is not None or length != 8 or holds:
                    raise ValidationError('Invalid APNG animation control')
                control = struct.unpack('>II', body)
                if not 1 <= control[0] <= MAX_FRAMES:
                    raise ValidationError('APNG frame count exceeds local limits')
            else:
                if control is None or length != 26:
                    raise ValidationError('Invalid APNG frame control')
                numerator, denominator = struct.unpack_from('>HH', body, 20)
                hold = Fraction(numerator, denominator or 100)
                if hold <= 0:
                    raise ValidationError('Zero-duration animation needs an explicit clock policy')
                holds.append(hold)
        offset = end
        if kind == b'IEND':
            break
    if control is None:
        return None
    if len(holds) != control[0]:
        raise ValidationError('APNG declared and controlled frame counts differ')
    return holds


def _import_image(store, path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 256*1024*1024:
        raise ValidationError("Input must be a local image file <=256MiB")
    raw = path.read_bytes()
    exact_apng_holds = _apng_timing(raw)
    with Image.open(BytesIO(raw)) as image:
        source_count = getattr(image, "n_frames", 1)
        has_poster = bool(image.info.get('default_image', False))
        count = source_count - int(has_poster)
        if exact_apng_holds is not None and len(exact_apng_holds) != count:
            raise ValidationError('APNG decoder frame count differs from its control records')
        w, h = image.size
        if not 1 <= count <= MAX_FRAMES or w*h > MAX_PIXELS or w*h*4*count > MAX_SEQUENCE_BYTES:
            raise ValidationError("Decoded image exceeds frame/pixel budget")
        source_format = image.format
        source_loop = image.info.get("loop")
        play_count = (1 if source_loop is None else source_loop+1 if image.format == 'GIF' and source_loop>0 else source_loop)
        poster = np.array(image.convert('RGBA'),dtype=np.uint8) if has_poster else None
        frames = []; durations = []; disposal = []
        for i in range(int(has_poster), source_count):
            image.seek(i)
            frames.append(np.array(image.convert("RGBA"), dtype=np.uint8))
            # No duration in a still is a local12fps default, explicitly recorded.
            duration_ms = image.info.get("duration")
            if exact_apng_holds is not None:
                durations.append(exact_apng_holds[i - int(has_poster)])
            elif duration_ms is None:
                durations.append(Fraction(1, 12))
            else:
                duration = Fraction(str(duration_ms))/1000
                if duration <= 0:
                    raise ValidationError("Zero-duration animation needs an explicit clock policy")
                durations.append(duration)
            disposal.append(getattr(image, "disposal_method", None))
    source = store.put_bytes(raw)
    poster_id = store.put_raster(poster) if poster is not None else None
    sequence = save_sequence(store, frames, durations, loop=play_count == 0, play_count=play_count,
        metadata={"acquisition": "local-file-v1", "source_bytes": source, "source_name": path.name,
                  "source_format": source_format, "source_loop_count": source_loop,
                  "source_frame_indices": list(range(int(has_poster),source_count)), "poster_raster": poster_id,
                  "source_disposal": disposal, "decoder": f"Pillow-{PIL.__version__}",
                  "hidden_rgb_policy": "preserve decodedRGBA; retain encodedsource separately",
                  "duration_source": "APNG fcTL exact rational" if exact_apng_holds is not None else "Pillow milliseconds or declared still default",
                  "missing_duration_policy": "1/12second local default"})
    return {"sequence": sequence, "source_bytes": source, "frames": count, "canvas": [w, h],
            "rasters": [store.put_raster(a) for a in frames], "poster_raster": poster_id}


def import_image(store, path):
    try:
        return _import_image(store, path)
    except ValidationError:
        raise
    except (OSError, SyntaxError, EOFError, ValueError, Image.DecompressionBombError) as e:
        raise ValidationError('Unable to decode the captured image bytes') from e
