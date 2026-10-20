# SPDX-License-Identifier: GPL-3.0-only
"""ERF mesh reader. Format interpretation adapted from Scanner's 2003
UMW4_ERF / UMW4_LOD / UMW4_mesh sources, preserved under tools/erf-editor-source.
That repository supplies its source under GPL-3.0. See THIRD_PARTY.md.
"""
import math
import struct


class Reader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def take(self, n):
        if n < 0 or self.pos + n > len(self.data):
            raise ValueError(f"ERF read outside file at {self.pos}: {n}")
        data = self.data[self.pos:self.pos+n]
        self.pos += n
        return data

    def unpack(self, fmt):
        return struct.unpack(fmt, self.take(struct.calcsize(fmt)))

    def number(self):
        return self.unpack("<I")[0]

    def vectors(self, count, dimensions):
        if count > 100_000:
            raise ValueError("Implausible ERF vector count")
        values = list(struct.iter_unpack("<" + "f" * dimensions, self.take(count * dimensions * 4)))
        if not all(math.isfinite(v) for item in values for v in item):
            raise ValueError("Nonfinite ERF vector")
        return values


def read_erf(data, lod_limit=None):
    r = Reader(data)
    magic, marker, major, minor = r.unpack("<4sIII")
    if magic != b"#FRE" or marker != 14:
        raise ValueError("Unexpected ERF header")
    transform = None
    sphere = None
    if major == 131 and minor in (1, 2):
        if minor == 1:
            sphere = r.unpack("<4f")
        else:
            transform = r.unpack("<12f")
            sphere = r.unpack("<4f")
        count = 1
    elif major == 144 and minor in (2, 5, 37):
        if minor in (2, 37):
            transform = r.unpack("<12f")
        sphere = r.unpack("<4f")
        count = r.unpack("<H")[0]
    elif major == 145 and minor == 5:
        r.take(22)
        count = r.unpack("<H")[0]
    else:
        raise ValueError(f"Unsupported ERF version {major}:{minor}")
    if r.unpack("<4sI") != (b"#RLM", 18):
        raise ValueError("Unexpected RLM header")
    if not 1 <= count <= 64:
        raise ValueError(f"Unexpected LOD count {count}")
    lods = []
    warnings = []
    for lod_index in range(min(count, lod_limit) if lod_limit else count):
        minimum = maximum = None
        if major == 145:
            r.take(8)
        if major != 131:
            minimum, maximum = r.unpack("<2f")
        block_size, kind, meshes_count = r.unpack("<IIB")
        block_start = r.pos - 5
        meshes = []
        for mesh_index in range(meshes_count):
            mesh_marker = r.number()
            if mesh_marker != 102:
                raise ValueError(f"Unexpected mesh version {mesh_marker}")
            vertices = r.vectors(r.number(), 3)
            uvs = r.vectors(r.number(), 2)
            texture_type, texture_flags = r.unpack("<IB")
            texture_parameters = r.unpack("<5i")
            texture = None
            # High bits also encode render flags. Low 16 bits == 1 is untextured.
            if texture_type & 0xffff != 1:
                name_length = r.number()
                if name_length > 1024:
                    raise ValueError("Implausible texture name length")
                name = r.take(name_length + 1)
                if name[-1:] != b"\0":
                    raise ValueError(f"Texture name not terminated at {r.pos}, texture_type={texture_type}, length={name_length}")
                texture = name[:-1].decode("cp1252")
                r.number()
            indices = r.number()
            if indices % 3:
                raise ValueError(f"Triangle indices {indices} not divisible by three at {r.pos}, texture_type={texture_type}, texture={texture!r}")
            fmt = "<3H" if major == 131 and minor == 2 else "<3B"
            faces = list(struct.iter_unpack(fmt, r.take((indices // 3) * struct.calcsize(fmt))))
            if any(v >= len(vertices) for face in faces for v in face):
                raise ValueError("Triangle references a missing vertex")
            planes = r.vectors(r.number(), 4)
            r.number()
            normals = r.vectors(r.number(), 3)
            meshes.append({
                "vertices": vertices, "uvs": uvs, "faces": faces,
                "normals": normals, "texture": texture,
                "texture_type": texture_type, "texture_flags": texture_flags,
                "texture_parameters": texture_parameters,
            })
        if r.pos - block_start != block_size:
            warnings.append(f"LOD {lod_index}: declared block size {block_size}, consumed {r.pos-block_start}")
        lods.append({"index": lod_index, "min_distance_squared": minimum,
                     "max_distance_squared": maximum, "meshes": meshes})
    if not lod_limit and r.pos != len(data):
        raise ValueError(f"Unparsed ERF tail: {len(data)-r.pos} bytes")
    return {"version": [major, minor], "header_transform": transform,
            "bounding_sphere": sphere, "lod_count": count, "warnings": warnings,
            "lods": lods}
