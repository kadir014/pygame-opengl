from pyrr import Vector3


class BasicLight:
    """
    Basic Phong (Ambient & Diffuse & Specular) lighting
    """
    def __init__(self,
            color: tuple[float, float, float] = (1.0, 1.0, 1.0),
            ambient_intensity: float = 0.03,
            diffuse_intensity: float = 0.7,
            specular_intensity: float = 0.8,
            specular_power: float = 32,
            position: tuple[float, float, float] = (1.0, 0, 1.0)):

        self.color = color
        self.ambient_intensity = ambient_intensity
        self.diffuse_intensity = diffuse_intensity
        self.specular_intensity = specular_intensity
        self.specular_power = specular_power
        self.position = Vector3(position)