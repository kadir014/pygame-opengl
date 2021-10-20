"""
Converts OBJ (Wavefront) files to vertex, texture and
normal coordinates.

The parser currently doesn't examine material data.
Only triangular faces are supported
  (f v/vt/vn v/vt/vn v/vt/vn)
"""

from typing import Union

from pathlib import Path
import numpy


class ObjFile:
    def __init__(self,
            object_name: str,
            vert_coords: list[tuple[float, float, float]],
            tex_coords: list[tuple[float, float, float]],
            norm_coords: list[tuple[float, float, float]],
            smooth_shading: bool):

        self.object_name = object_name
        self.vertices = vert_coords
        self.uv_coords = tex_coords
        self.vertex_normals = norm_coords
        self.smooth_shading = smooth_shading


def parse(filepath: Union[Path, str]) -> ObjFile:
    object_name = ""

    vert_coords = []
    tex_coords = []
    norm_coords = []

    vert_indices = []
    tex_indices = []
    norm_indices = []

    smooth_shading = False

    with open(filepath, "r") as f:

        for line in f.readlines():
            cnt = line.split()

            if cnt[0] == "o":
                object_name = cnt[1]

            if cnt[0] == "v":
                vert_coords.append((float(cnt[1]), float(cnt[2]), float(cnt[3])))

            elif cnt[0] == "vt":
                tex_coords.append((float(cnt[1]), float(cnt[2])))

            elif cnt[0] == "vn":
                norm_coords.append((float(cnt[1]), float(cnt[2]), float(cnt[3])))

            elif cnt[0] == "f":
                for d in cnt[1:]:
                    h = d.split("/")
                    vert_indices.append(int(h[0])-1)
                    tex_indices.append(int(h[1])-1)
                    norm_indices.append(int(h[2])-1)

            elif cnt[0] == "s":
                if cnt[1] in ("on", "1"):
                    smooth_shading = True
                else:
                    smooth_shading = False
   
    final_vert = []
    final_tex = []
    final_norm = []

    for i in vert_indices:
        final_vert.append(vert_coords[i])

    for j in tex_indices:
        final_tex.append(tex_coords[j])

    for k in norm_indices:
        final_norm.append(norm_coords[k])


    final_vert = list(numpy.concatenate(final_vert).flat)
    final_tex = list(numpy.concatenate(final_tex).flat)
    final_norm = list(numpy.concatenate(final_norm).flat)

    return ObjFile(object_name, final_vert, final_tex, final_norm, smooth_shading)