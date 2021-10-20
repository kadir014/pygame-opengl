from math import sin, cos, radians
import pygame
import pyrr


class Camera:
    """
    Base camera class
    """
    def __init__(self,
            aspect_ratio: float,
            fov: float = 80.0,
            position: tuple[float, float, float] = (0.0, 0.0, 0.0),
            ortho: bool = False):

        self.ortho = ortho

        self.aspect_ratio = aspect_ratio
        self._fov = fov
        self.fov = fov # create projection matrix
        self.position = pyrr.Vector3(position)

        self.final_position = pyrr.Vector3(position)
        self.front = pyrr.Vector3([0.0, 0.0, -1.0])
        self.up    = pyrr.Vector3([0.0, 1.0, 0.0])
        self.right = pyrr.Vector3([1.0, 0.0, 0.0])

        self.yaw = -90
        self.pitch = 0

    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(self.final_position, self.final_position + self.front, self.up)

    def update_vectors(self):
        front = pyrr.Vector3([0.0, 0.0, 0.0])
        front.x = cos(radians(self.yaw)) * cos(radians(self.pitch))
        front.y = sin(radians(self.pitch))
        front.z = sin(radians(self.yaw)) * cos(radians(self.pitch))

        self.front = pyrr.vector.normalise(front)
        self.right = pyrr.vector.normalise(pyrr.vector3.cross(self.front, pyrr.Vector3([0.0, 1.0, 0.0])))
        self.up    = pyrr.vector.normalise(pyrr.vector3.cross(self.right, self.front))

    @property
    def fov(self):
        return self._fov

    @fov.setter
    def fov(self, new_fov):
        self._fov = new_fov
        if self.ortho:
            self.projection = pyrr.matrix44.create_orthogonal_projection_matrix(0, 1280, 720, 0, 0.1, 100)
        else:
            self.projection = pyrr.matrix44.create_perspective_projection_matrix(self._fov, self.aspect_ratio, 0.1, 1000)


class FirstPersonController(Camera):
    """
    First-person controlled camera
    """
    def __init__(self,
            aspect_ratio: float,
            fov: float = 80.0,
            position: tuple[float, float, float] = (0.0, 0.0, 0.0),
            movement_speed: float = 0.09):
        super().__init__(aspect_ratio, fov, position)

        self.velocity = pyrr.Vector3([0.0, 0.0, 0.0])
        self.jump_height = 0.2

        self.movement_speed = movement_speed
        self._default_movement_speed = movement_speed
        self.mouse_sensitivity = 0.17

        self.noclip = False

        self.on_ground = False
        self.is_sprinting = False
        self.is_ducking = False
        self.is_walking = False

        self.key_map = {
            "forward" : pygame.K_w,
            "backward": pygame.K_s,
            "left"    : pygame.K_a,
            "right"   : pygame.K_d,
            "up"      : pygame.K_SPACE,
            "down"    : pygame.K_LCTRL,
            "sprint"  : pygame.K_LSHIFT,
            "duck"    : pygame.K_LCTRL,
            "jump"    : pygame.K_SPACE,
            "noclip"  : pygame.K_v
        }

    def process(self, 
            offset_x: float,
            offset_y: float,
            events: list[pygame.event.Event],
            keys: list[int],
            constrain_pitch: bool = True):

        offset_x *= self.mouse_sensitivity
        offset_y *= self.mouse_sensitivity

        self.yaw += offset_x
        self.pitch += offset_y

        if constrain_pitch:
            if self.pitch > 90: self.pitch = 90
            if self.pitch < -90: self.pitch = -90

        self.update_vectors()

        # Movement
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == self.key_map["sprint"]:
                    self.movement_speed = self._default_movement_speed * 2
                    self.is_sprinting = True

                elif not self.noclip and event.key == self.key_map["duck"]:
                    self.movement_speed = self._default_movement_speed / 3
                    self.is_ducking = True

                elif event.key == self.key_map["jump"]:
                    if self.on_ground and not self.noclip:
                        #jump_sound.play()
                        self.velocity.y = -self.jump_height
                        self.on_ground = False

                elif event.key == self.key_map["noclip"]:
                    if self.noclip: self.noclip = False
                    else:
                        self.noclip = True
                        self.velocity.y = 0.0
                        self.on_ground = False

            elif event.type == pygame.KEYUP:
                if event.key == self.key_map["sprint"]:
                    self.movement_speed = self._default_movement_speed
                    self.is_sprinting = False

                elif not self.noclip and event.key == self.key_map["duck"]:
                    self.movement_speed = self._default_movement_speed
                    self.is_ducking = False

            elif event.type == pygame.MOUSEWHEEL:
                if self.on_ground and not self.noclip:
                    #jump_sound.play()
                    self.velocity.y = -self.jump_height
                    self.on_ground = False

        self.is_walking = False

        if keys[self.key_map["forward"]]:
            self.is_walking = True

            if self.noclip:
                self.position += self.front * self.movement_speed
            else:
                self.position.x += cos(radians(self.yaw)) * self.movement_speed
                self.position.z += sin(radians(self.yaw)) * self.movement_speed

        if keys[self.key_map["backward"]]:
            if self.is_walking: self.is_walking = False
            else: self.is_walking = True

            if self.noclip:
                self.position -= self.front * self.movement_speed
            else:
                self.position.x -= cos(radians(self.yaw)) * self.movement_speed
                self.position.z -= sin(radians(self.yaw)) * self.movement_speed

        if keys[self.key_map["left"]]:
            self.position -= self.right * self.movement_speed

        if keys[self.key_map["right"]]:
            self.position += self.right * self.movement_speed

        if self.noclip and keys[self.key_map["up"]]:
            self.position += self.up * self.movement_speed

        if self.noclip and keys[self.key_map["down"]]:
            self.position -= self.up * self.movement_speed

        self.final_position = self.position.copy()

        # Applying gravity
        if not self.noclip:
            self.velocity.y += 0.008
        
            if self.position.y - self.velocity.y < -2.1:
                self.velocity.y = 0
                self.on_ground = True

            self.position.y -= self.velocity.y

            if self.is_ducking:
                self.final_position.y = self.position.y - 0.9
            else:
                self.final_position.y = self.position.y

        # Head obbing
        if not self.noclip and self.is_walking and not self.is_ducking:
            if self.is_sprinting: bobbing_factor = 2.14
            else: bobbing_factor = 1.4

            self.final_position += self.right * sin(pygame.time.get_ticks()*bobbing_factor*0.005) / 3
            self.final_position.y += cos(pygame.time.get_ticks()*(bobbing_factor*2)*0.005) / 5