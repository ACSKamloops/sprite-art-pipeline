"""Read-only MW4 VBD archive reader, including its 9-12 bit LZW streams.

Archive fields verified against the community BMS specifications and the
Mechstorm archive tool, then against the downloaded game files.
"""
import struct
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


def lzw_decode(data: bytes, expected: int) -> bytes:
    table = [bytes([i]) for i in range(256)] + [b"", b""]
    width = 9
    bitpos = 0
    previous = b""
    output = bytearray()
    terminated = False
    while bitpos + width <= len(data) * 8:
        bytepos, shift = divmod(bitpos, 8)
        code = (int.from_bytes(data[bytepos:bytepos + 3], "little") >> shift) & ((1 << width) - 1)
        bitpos += width
        if code == 256:
            table = table[:258]
            width = 9
            previous = b""
            continue
        if code == 257:
            terminated = True
            break
        if code < len(table):
            word = table[code]
        elif code == len(table) and previous:
            word = previous + previous[:1]
        else:
            raise ValueError(f"Invalid LZW code {code} at bit {bitpos}")
        if not word:
            raise ValueError("Empty LZW word")
        output.extend(word)
        if len(output) > expected:
            raise ValueError("LZW output exceeded declared length")
        if previous:
            table.append(previous + word[:1])
            if len(table) >= (1 << width) and width < 12:
                width += 1
        previous = word
    if len(output) != expected:
        raise ValueError(f"LZW length mismatch: {len(output)} != {expected}")
    if not terminated:
        raise ValueError("LZW end marker missing")
    return bytes(output)


@dataclass(frozen=True)
class Entry:
    name: str
    size: int
    compressed_size: int
    offset: int
    id: int

    @property
    def path(self):
        path = PurePosixPath(self.name.replace("\\", "/"))
        if path.is_absolute() or ".." in path.parts or ":" in str(path):
            raise ValueError(f"Unsafe archive path: {self.name}")
        return path


class Archive:
    def __init__(self, path):
        self.path = Path(path)
        with self.path.open("rb") as stream:
            header = stream.read(20)
            magic, version, flags, self.base, count_a, count = struct.unpack("<4sIIIHH", header)
            if magic != b"#VBD" or version != 4:
                raise ValueError(f"Unsupported VBD header in {path}")
            index = stream.read(self.base - 20)
        self.entries = []
        pos = 0
        for _ in range(count):
            _, size, compressed, offset, ident, name_len = struct.unpack_from("<QIIIHB", index, pos)
            name = index[pos + 23:pos + 23 + name_len].decode("cp1252")
            entry = Entry(name, size, compressed, offset, ident)
            entry.path
            if compressed > size or self.base + offset + compressed > self.path.stat().st_size:
                raise ValueError(f"Invalid entry bounds: {name}")
            self.entries.append(entry)
            pos += 23 + name_len
        if pos != len(index):
            raise ValueError("Index length mismatch")

    def read(self, entry):
        with self.path.open("rb") as stream:
            stream.seek(self.base + entry.offset)
            data = stream.read(entry.compressed_size)
        if len(data) != entry.compressed_size:
            raise ValueError("Truncated resource")
        return data if entry.compressed_size == entry.size else lzw_decode(data, entry.size)
