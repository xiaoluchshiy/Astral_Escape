from devices import *
from player import *
import arcade
import random
from alert import PressE
from pyglet.graphics import Batch

# Константы
SCREEN_WIDTH = 3000
SCREEN_HEIGHT = 2000
SCREEN_TITLE = "Astral Escape"
PLAYER_SPEED = 300
ANIMATION_SPEED = 0.085


class Minigame(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        # устанавливаем фон
        self.game_view = game_view
        self.background = arcade.load_texture("images/space.png")
        self.code = str(random.randint(100, 999))
        self.show_time = 2
        self.current_time = 0
        self.user_input = ""
        self.message = ''
        self.batch = Batch()
        self.batch1 = Batch()

    def setup(self):
        pass

    def on_update(self, delta_time):
        self.current_time += delta_time

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.background,
                                 arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH,
                                                  SCREEN_HEIGHT))
        if self.current_time < self.show_time:
            self.title = arcade.Text(
                self.code,
                self.window.width // 2,
                self.window.height // 2,
                arcade.color.WHITE,
                80,
                anchor_x="center",
                batch=self.batch
            )
            self.batch.draw()
        else:
            self.title1 = arcade.Text(
                f"Ввод: {self.user_input}",
                self.window.width // 2,
                self.window.height // 2,
                arcade.color.YELLOW,
                40,
                anchor_x="center",
                batch=self.batch1
            )
            self.title2 = arcade.Text(
                "Введи цифры (1-9), ENTER — проверить",
                self.window.width // 2,
                self.window.height // 2 - 50,
                arcade.color.GRAY,
                16,
                anchor_x="center",
                batch=self.batch1
            )
            if self.message:
                color = arcade.color.GREEN if self.message == "Верно!" else arcade.color.RED
                self.title3 = arcade.Text(
                    self.message,
                    self.window.width // 2,
                    self.window.height // 2 + 100,
                    color,
                    50,
                    anchor_x="center",
                    batch=self.batch1
                )
            self.batch1.draw()

    def on_key_press(self, key, modifiers):
        if arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
            if len(self.user_input) < 3:
                self.user_input += str(key - arcade.key.KEY_0)
        elif key == arcade.key.ENTER:
            if self.user_input == self.code:
                self.message = "Верно!"
                self.window.show_view(self.game_view)
            else:
                self.message = "Неверно!"
                self.user_input = ""


class StartView(arcade.View):
    def on_draw(self):
        """Отрисовка начального экрана"""
        self.clear()
        self.batch = Batch()
        title = arcade.Text("Нажми SPACE, чтобы начать!",
                            600,
                            400,
                            arcade.color.WHITE,
                            font_size=48,
                            anchor_x="center",
                            anchor_y="center", batch=self.batch)

        self.batch.draw()

    def on_key_press(self, key, modifiers):
        # при нажатии запускается основная игра
        if key == arcade.key.SPACE:
            game_view = Astral_Escape_1()
            game_view.setup()
            self.window.show_view(game_view)


class Astral_Escape_1(arcade.View):
    def __init__(self):
        super().__init__()
        # устанавливаем фон
        self.background = arcade.load_texture("images/space.png")
        self.track_h = 2
        self.track_v = 2
        # устройства
        self.devices = None
        self.current_device = None
        self.batch = Batch()
        self.batch1 = Batch()
        self.text_info = arcade.Text("WASD — ходьба • E — взаимодействие • Q — астральная форма",
                                     16, 16, arcade.color.WHITE, 14, batch=self.batch)
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

    def setup(self):
        # Создание объектов
        self.player = Player()
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.cam_alert = PressE(self.player.center_x, self.player.center_y - 30)
        self.alerts = arcade.SpriteList()
        self.alerts.append(self.cam_alert)
        self.devices = arcade.SpriteList()
        self.robots = arcade.SpriteList()
        self.radius_sprites = arcade.SpriteList()
        camera = Camera(570, 1220, 25, 0)
        camera.radius_sprite_list = self.radius_sprites
        camera1 = Camera(1450, 820, 60, 0)
        camera1.radius_sprite_list = self.radius_sprites
        camera2 = Camera(1050, 1535, 60, 0)
        camera2.radius_sprite_list = self.radius_sprites
        button = Button(1110, 809)
        self.buttons = arcade.SpriteList()
        self.buttons.append(button)
        self.devices.append(camera)
        self.devices.append(camera1)
        self.devices.append(camera2)
        self.devices.append(button)
        self.wall_list = arcade.SpriteList()
        map_name = "map/level1.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=3)
        self.wall_list = tile_map.sprite_lists["walls"]
        self.door_list = tile_map.sprite_lists["door"]
        self.collision_list = tile_map.sprite_lists["collision"]
        self.astral_collision_list = tile_map.sprite_lists["astral_collision"]
        self.door_collision_list = tile_map.sprite_lists["door_collision"]
        self.astral_list = tile_map.sprite_lists["astral"]
        self.door1_collision_list = tile_map.sprite_lists["door1_collision"]
        self.door1_list = tile_map.sprite_lists["door1"]
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.collision_list)
        self.astral_physics_engine = arcade.PhysicsEngineSimple(self.player, self.astral_collision_list)
        self.door_physics_engine = arcade.PhysicsEngineSimple(self.player, self.door_collision_list)
        # звук
        self.explosion_sound = arcade.load_sound("music.wav")

        self.total_time = 0

        self.current_texture = 0
        self.texture_change_time = 0
        robot = Robot(
            x=800, y=1100,
            point_a=(800, 1100),
            point_b=(1000, 1100),
        )
        self.robots.append(robot)
        self.devices.append(robot)
        robot1 = Robot(
            x=1650, y=820,
            point_a=(1650, 820),
            point_b=(1650, 1300),
        )
        self.robots.append(robot1)
        self.devices.append(robot1)
        self.radius_sprites.append(camera.radius_sprite)
        self.radius_sprites.append(camera1.radius_sprite1)
        self.radius_sprites.append(camera2.radius_sprite1)

    def update_animation(self, delta_time: float = 1 / 60):
        """ Обновление анимации """
        if not self.player.astral_form:
            if self.track_h == 1:
                if self.player.is_walking:
                    self.texture_change_time += delta_time
                    if self.texture_change_time >= ANIMATION_SPEED:
                        self.texture_change_time = 0
                        self.current_texture += 1
                        if self.current_texture >= len(self.player.textures_right):
                            self.current_texture = 0
                        self.player.texture = self.player.textures_right[self.current_texture]
            elif self.track_h == 0:
                if self.player.is_walking:
                    self.texture_change_time += delta_time
                    if self.texture_change_time >= ANIMATION_SPEED:
                        self.texture_change_time = 0
                        self.current_texture += 1
                        if self.current_texture >= len(self.player.textures_left):
                            self.current_texture = 0
                        self.player.texture = self.player.textures_left[self.current_texture]
            elif self.track_v == 1:
                if self.player.is_walking:
                    self.texture_change_time += delta_time
                    if self.texture_change_time >= ANIMATION_SPEED:
                        self.texture_change_time = 0
                        self.current_texture += 1
                        if self.current_texture >= len(self.player.textures_back):
                            self.current_texture = 0
                        self.player.texture = self.player.textures_back[self.current_texture]
            elif self.track_v == 0:
                if self.player.is_walking:
                    self.texture_change_time += delta_time
                    if self.texture_change_time >= ANIMATION_SPEED:
                        self.texture_change_time = 0
                        self.current_texture += 1
                        if self.current_texture >= len(self.player.textures_forward):
                            self.current_texture = 0
                        self.player.texture = self.player.textures_forward[self.current_texture]
            else:
                self.player.texture = self.player.texture_forward

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        # Отрисовка фона
        arcade.draw_texture_rect(self.background,
                                 arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH,
                                                  SCREEN_HEIGHT))
        self.wall_list.draw()
        self.radius_sprites.draw()
        for button in self.buttons:
            if button.is_hackable:
                self.door_list.draw()
                self.door_collision_list.draw()
        if self.player.astral_form:
            arcade.draw_texture_rect(self.player.texture_right,
                                     arcade.rect.XYWH(self.player.astral_form_x, self.player.astral_form_y, 80,
                                                      80))
            self.title1 = arcade.Text(f"Выход из астральной формы через: {int(6 - self.player.astral_timer)}",
                                      0, 740,
                                      arcade.color.WHITE, 25,
                                      batch=self.batch1)
            self.astral_list.draw()
        self.door1_list.draw()
        self.devices.draw()
        self.player_list.draw()
        if self.current_device:
            self.alerts.draw()
        for device in self.devices:
            if hasattr(device, 'emitters'):
                for emitter in device.emitters:
                    emitter.draw()
        self.gui_camera.use()
        if self.player.astral_form:
            self.batch1.draw()
        self.batch.draw()

    def on_update(self, delta_time):
        if self.player.astral_form:
            if self.player.astral_timer > 5:
                self.player.astral_form = False
                self.player.center_x = self.player.astral_form_x
                self.player.center_y = self.player.astral_form_y
                self.player.texture = self.player.texture_forward
                self.player.astral_timer = 0
            else:
                self.player.astral_timer += delta_time
        self.cam_alert.center_y = self.player.center_y - 45
        self.cam_alert.center_x = self.player.center_x
        if not self.player.astral_form:  # только в физической форме
            for radius in self.radius_sprites:
                if arcade.check_for_collision(self.player, radius):
                    self.setup()
        for robot in self.robots:
            if arcade.check_for_collision(self.player, robot):
                self.setup()

        minutes = int(self.total_time) // 60
        seconds = int(self.total_time) % 60
        if 1 <= seconds <= 9:
            seconds = "0" + str(seconds)
        self.title = arcade.Text(f"Время: {minutes}:{seconds}",
                                 0, 770,
                                 arcade.color.WHITE, 25,
                                 batch=self.batch)
        self.total_time += delta_time

        self.physics_engine.update()
        self.update_animation()

        for button in self.buttons:
            if button.is_hackable:
                self.door_physics_engine.update()
        if not self.player.astral_form:
            self.astral_physics_engine.update()

        if self.player.astral_form:
            if self.track_h == 1:
                self.player.texture = self.player.astral_texture_left
            if self.track_h == 0:
                self.player.texture = self.player.astral_texture_right
            if self.track_v == 1:
                self.player.texture = self.player.astral_texture_back
            if self.track_v == 0:
                self.player.texture = self.player.astral_texture_forward

        if arcade.check_for_collision_with_list(self.player, self.door1_collision_list):
            with open("time_1.txt", "a", encoding="utf-8") as f:
                f.write(f'{str(self.total_time)}\n')
            game_view = FinalView_1()
            self.window.show_view(game_view)

        self.player.update(delta_time)

        for device in self.devices:
            device.update(delta_time)
        self.current_device = None
        for device in self.devices:
            if device.can_interact(self.player.center_x, self.player.center_y):
                self.current_device = device
                break

        position = (self.player.center_x, self.player.center_y)
        self.world_camera.position = arcade.math.lerp_2d(self.world_camera.position, position, 0.12)
        self.gui_camera.position = (600, 400)

    def on_show_view(self):
        self.explosion_player = self.explosion_sound.play()

    def on_hide_view(self):
        arcade.stop_sound(self.explosion_player)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = 1
            self.track_v = 1
        elif key == arcade.key.S:
            self.player.change_y = -1
            self.track_v = 0
        elif key == arcade.key.A:
            self.player.change_x = -1
            self.track_h = 1
        elif key == arcade.key.D:
            self.player.change_x = 1
            self.track_h = 0
        elif key == arcade.key.Q:
            if self.player.astral_form:
                self.player.astral_form = False
                self.player.center_x = self.player.astral_form_x
                self.player.center_y = self.player.astral_form_y
                self.player.texture = self.player.texture_forward
                self.player.astral_timer = 0
            else:
                self.player.astral_form = True
                self.player.astral_form_x = self.player.center_x
                self.player.astral_form_y = self.player.center_y
                self.player.center_x = self.player.center_x + self.player.width
                self.player.texture = self.player.astral_texture_forward
                self.astral_physics_engine = arcade.PhysicsEngineSimple(self.player, self.astral_collision_list)
        elif key == arcade.key.E:
            if self.current_device and not self.current_device.is_hacked:
                self.current_device.hack()
                if hasattr(self.current_device, 'emitters'):
                    game_view = Minigame(self)
                    game_view.setup()
                    self.window.show_view(game_view)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.S:
            self.player.change_y = 0
            self.track_v = 2
        elif key == arcade.key.A or key == arcade.key.D:
            self.player.change_x = 0
            self.track_h = 2


class FinalView_1(arcade.View):
    def __init__(self):
        super().__init__()
        self.time_list = []
        with open("time_1.txt", "r", encoding="utf-8") as f:
            for i in f:
                self.time_list.append(float(i))
        self.total_time = self.time_list[-1]
        self.min_time = min(self.time_list)
        self.min_minutes = int(self.min_time) // 60
        self.min_seconds = int(self.min_time) % 60
        self.minutes = int(self.total_time) // 60
        self.seconds = int(self.total_time) % 60
        if 1 <= self.seconds <= 9:
            self.seconds = "0" + str(self.seconds)
        if 1 <= self.min_seconds <= 9:
            self.min_seconds = "0" + str(self.min_seconds)

    def on_draw(self):
        """Отрисовка начального экрана"""
        self.clear()
        # Батч для текста.
        self.batch = Batch()
        self.title = arcade.Text("Поздравляем с прохождением первого уровня!",
                                 600, 700,
                                 arcade.color.WHITE, 30,
                                 anchor_x="center", batch=self.batch)
        self.title1 = arcade.Text(f"Ваше время: {self.minutes}:{self.seconds} "
                                  f"Лучшее время: {self.min_minutes}:{self.min_seconds}",
                                  600, 600,
                                  arcade.color.WHITE, 30,
                                  anchor_x="center", batch=self.batch)
        self.title2 = arcade.Text("Нажми SPACE, чтобы перейти на следующий уровень!",
                                  600,
                                  300,
                                  arcade.color.WHITE,
                                  font_size=30,
                                  anchor_x="center",
                                  anchor_y="center", batch=self.batch)
        self.title3 = arcade.Text("Нажми Esc, чтобы выйти из игры!",
                                  600,
                                  200,
                                  arcade.color.WHITE,
                                  font_size=30,
                                  anchor_x="center",
                                  anchor_y="center", batch=self.batch)
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        # при нажатии запускается основная игра
        if key == arcade.key.SPACE:
            game_view = Astral_Escape_2()
            game_view.setup()
            self.window.show_view(game_view)
        if key == arcade.key.ESCAPE:
            self.window.close()


class Astral_Escape_2(arcade.View):
    def __init__(self):
        super().__init__()
        # устанавливаем фон
        self.background = arcade.load_texture("images/space.png")
        self.track_h = 2
        self.track_v = 2
        # устройства
        self.devices = None
        self.current_device = None
        self.batch = Batch()
        self.batch1 = Batch()
        self.text_info = arcade.Text("WASD — ходьба • E — взаимодействие • Q — астральная форма",
                                     16, 16, arcade.color.WHITE, 14, batch=self.batch)
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

    def setup(self):
        # Создание объектов
        self.player = Player()
        self.player_list = arcade.SpriteList()
        self.player.center_x = 510
        self.player.center_y = 820
        self.player_list.append(self.player)
        self.cam_alert = PressE(self.player.center_x, self.player.center_y - 30)
        self.alerts = arcade.SpriteList()
        self.alerts.append(self.cam_alert)
        self.devices = arcade.SpriteList()
        self.robots = arcade.SpriteList()
        self.radius_sprites = arcade.SpriteList()
        camera = Camera(744, 460, 60, 0)
        camera.radius_sprite_list = self.radius_sprites
        self.button = Button(1260, 540)
        self.button1 = Button(2100, 660)
        self.buttons = arcade.SpriteList()
        self.buttons.append(self.button)
        self.buttons.append(self.button1)
        self.devices.append(camera)
        self.devices.append(self.button)
        self.devices.append(self.button1)
        self.wall_list = arcade.SpriteList()
        map_name = "map/level2.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=3)
        self.wall_list = tile_map.sprite_lists["walls"]
        self.door_list = tile_map.sprite_lists["door"]
        self.collision_list = tile_map.sprite_lists["collision"]
        self.astral_collision_list = tile_map.sprite_lists["astral_collision"]
        self.door_collision_list = tile_map.sprite_lists["door_collision"]
        self.astral_list = tile_map.sprite_lists["astral"]
        self.door1_collision_list = tile_map.sprite_lists["door1_collision"]
        self.door1_list = tile_map.sprite_lists["door1"]
        self.door2_collision_list = tile_map.sprite_lists["door2_collision"]
        self.door2_list = tile_map.sprite_lists["door2"]
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.collision_list)
        self.astral_physics_engine = arcade.PhysicsEngineSimple(self.player, self.astral_collision_list)
        self.door_physics_engine = arcade.PhysicsEngineSimple(self.player, self.door_collision_list)
        self.door1_physics_engine = arcade.PhysicsEngineSimple(self.player, self.door1_collision_list)
        # звук
        self.explosion_sound = arcade.load_sound("music.wav")

        self.total_time = 0

        self.current_texture = 0
        self.texture_change_time = 0
        robot = Robot(
            x=935, y=830,
            point_a=(935, 830),
            point_b=(1350, 830),
        )
        self.robots.append(robot)
        self.devices.append(robot)
        robot1 = Robot(
            x=1790, y=450,
            point_a=(1790, 450),
            point_b=(2600, 450),
        )
        self.robots.append(robot1)
        self.devices.append(robot1)
        self.radius_sprites.append(camera.radius_sprite1)

    def update_animation(self, delta_time: float = 1 / 60):
        """ Обновление анимации """
        if not self.player.astral_form:
            if self.track_h == 1:
                if self.player.is_walking:
                    self.texture_change_time += delta_time
                    if self.texture_change_time >= ANIMATION_SPEED:
                        self.texture_change_time = 0
                        self.current_texture += 1
                        if self.current_texture >= len(self.player.textures_right):
                            self.current_texture = 0
                        self.player.texture = self.player.textures_right[self.current_texture]
            elif self.track_h == 0:
                if self.player.is_walking:
                    self.texture_change_time += delta_time
                    if self.texture_change_time >= ANIMATION_SPEED:
                        self.texture_change_time = 0
                        self.current_texture += 1
                        if self.current_texture >= len(self.player.textures_left):
                            self.current_texture = 0
                        self.player.texture = self.player.textures_left[self.current_texture]
            elif self.track_v == 1:
                if self.player.is_walking:
                    self.texture_change_time += delta_time
                    if self.texture_change_time >= ANIMATION_SPEED:
                        self.texture_change_time = 0
                        self.current_texture += 1
                        if self.current_texture >= len(self.player.textures_back):
                            self.current_texture = 0
                        self.player.texture = self.player.textures_back[self.current_texture]
            elif self.track_v == 0:
                if self.player.is_walking:
                    self.texture_change_time += delta_time
                    if self.texture_change_time >= ANIMATION_SPEED:
                        self.texture_change_time = 0
                        self.current_texture += 1
                        if self.current_texture >= len(self.player.textures_forward):
                            self.current_texture = 0
                        self.player.texture = self.player.textures_forward[self.current_texture]
            else:
                self.player.texture = self.player.texture_forward

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        # Отрисовка фона
        arcade.draw_texture_rect(self.background,
                                 arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH,
                                                  SCREEN_HEIGHT))
        self.wall_list.draw()
        self.radius_sprites.draw()
        if self.button.is_hackable:
            self.door_list.draw()
            self.door_collision_list.draw()
        if self.button1.is_hackable:
            self.door1_list.draw()
            self.door1_collision_list.draw()
        if self.player.astral_form:
            arcade.draw_texture_rect(self.player.texture_right,
                                     arcade.rect.XYWH(self.player.astral_form_x, self.player.astral_form_y, 80,
                                                      80))
            self.title1 = arcade.Text(f"Выход из астральной формы через: {int(6 - self.player.astral_timer)}",
                                      0, 740,
                                      arcade.color.WHITE, 25,
                                      batch=self.batch1)
            self.astral_list.draw()
        self.door2_list.draw()
        self.devices.draw()
        self.player_list.draw()
        if self.current_device:
            self.alerts.draw()
        for device in self.devices:
            if hasattr(device, 'emitters'):
                for emitter in device.emitters:
                    emitter.draw()
        self.gui_camera.use()
        if self.player.astral_form:
            self.batch1.draw()
        self.batch.draw()

    def on_show_view(self):
        self.explosion_player = self.explosion_sound.play()

    def on_hide_view(self):
        arcade.stop_sound(self.explosion_player)

    def on_update(self, delta_time):
        if self.player.astral_form:
            if self.player.astral_timer > 5:
                self.player.astral_form = False
                self.player.center_x = self.player.astral_form_x
                self.player.center_y = self.player.astral_form_y
                self.player.texture = self.player.texture_forward
                self.player.astral_timer = 0
            else:
                self.player.astral_timer += delta_time
        self.cam_alert.center_y = self.player.center_y - 45
        self.cam_alert.center_x = self.player.center_x
        if not self.player.astral_form:  # только в физической форме
            for radius in self.radius_sprites:
                if arcade.check_for_collision(self.player, radius):
                    self.setup()
        for robot in self.robots:
            if arcade.check_for_collision(self.player, robot):
                self.setup()

        minutes = int(self.total_time) // 60
        seconds = int(self.total_time) % 60
        if 1 <= seconds <= 9:
            seconds = "0" + str(seconds)
        self.title = arcade.Text(f"Время: {minutes}:{seconds}",
                                 0, 770,
                                 arcade.color.WHITE, 25,
                                 batch=self.batch)
        self.total_time += delta_time

        self.physics_engine.update()
        self.update_animation()

        if self.button.is_hackable:
            self.door_physics_engine.update()
        if self.button1.is_hackable:
            self.door1_physics_engine.update()
        if not self.player.astral_form:
            self.astral_physics_engine.update()

        if self.player.astral_form:
            if self.track_h == 1:
                self.player.texture = self.player.astral_texture_left
            if self.track_h == 0:
                self.player.texture = self.player.astral_texture_right
            if self.track_v == 1:
                self.player.texture = self.player.astral_texture_back
            if self.track_v == 0:
                self.player.texture = self.player.astral_texture_forward

        if arcade.check_for_collision_with_list(self.player, self.door2_collision_list):
            with open("time_2.txt", "a", encoding="utf-8") as f:
                f.write(f'{str(self.total_time)}\n')
            game_view = FinalView_2()
            self.window.show_view(game_view)

        self.player.update(delta_time)

        for device in self.devices:
            device.update(delta_time)
        self.current_device = None
        for device in self.devices:
            if device.can_interact(self.player.center_x, self.player.center_y):
                self.current_device = device
                break

        position = (self.player.center_x, self.player.center_y)
        self.world_camera.position = arcade.math.lerp_2d(self.world_camera.position, position, 0.12)
        self.gui_camera.position = (600, 400)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = 1
            self.track_v = 1
        elif key == arcade.key.S:
            self.player.change_y = -1
            self.track_v = 0
        elif key == arcade.key.A:
            self.player.change_x = -1
            self.track_h = 1
        elif key == arcade.key.D:
            self.player.change_x = 1
            self.track_h = 0
        elif key == arcade.key.Q:
            if self.player.astral_form:
                self.player.astral_form = False
                self.player.center_x = self.player.astral_form_x
                self.player.center_y = self.player.astral_form_y
                self.player.texture = self.player.texture_forward
                self.player.astral_timer = 0
            else:
                self.player.astral_form = True
                self.player.astral_form_x = self.player.center_x
                self.player.astral_form_y = self.player.center_y
                self.player.center_x = self.player.center_x + self.player.width
                self.player.texture = self.player.astral_texture_forward
                self.astral_physics_engine = arcade.PhysicsEngineSimple(self.player, self.astral_collision_list)
        elif key == arcade.key.E:
            if self.current_device and not self.current_device.is_hacked:
                self.current_device.hack()
                if hasattr(self.current_device, 'emitters'):
                    game_view = Minigame(self)
                    game_view.setup()
                    self.window.show_view(game_view)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.S:
            self.player.change_y = 0
            self.track_v = 2
        elif key == arcade.key.A or key == arcade.key.D:
            self.player.change_x = 0
            self.track_h = 2


class FinalView_2(arcade.View):
    def __init__(self):
        super().__init__()
        self.time_list = []
        with open("time_2.txt", "r", encoding="utf-8") as f:
            for i in f:
                self.time_list.append(float(i))
        self.total_time = self.time_list[-1]
        self.min_time = min(self.time_list)
        self.min_minutes = int(self.min_time) // 60
        self.min_seconds = int(self.min_time) % 60
        self.minutes = int(self.total_time) // 60
        self.seconds = int(self.total_time) % 60
        if 1 <= self.seconds <= 9:
            self.seconds = "0" + str(self.seconds)
        if 1 <= self.min_seconds <= 9:
            self.min_seconds = "0" + str(self.min_seconds)

    def on_draw(self):
        """Отрисовка начального экрана"""
        self.clear()
        # Батч для текста.
        self.batch = Batch()
        self.title = arcade.Text("Поздравляем с прохождением игры!",
                                 600, 700,
                                 arcade.color.WHITE, 30,
                                 anchor_x="center", batch=self.batch)
        self.title1 = arcade.Text(f"Ваше время: {self.minutes}:{self.seconds} "
                                  f"Лучшее время: {self.min_minutes}:{self.min_seconds}",
                                  600, 600,
                                  arcade.color.WHITE, 30,
                                  anchor_x="center", batch=self.batch)
        self.title2 = arcade.Text("Нажми SPACE, чтобы начать игру заново!",
                                  600,
                                  300,
                                  arcade.color.WHITE,
                                  font_size=48,
                                  anchor_x="center",
                                  anchor_y="center", batch=self.batch)
        self.title3 = arcade.Text("Нажми Esc, чтобы выйти из игры!",
                                  600,
                                  200,
                                  arcade.color.WHITE,
                                  font_size=48,
                                  anchor_x="center",
                                  anchor_y="center", batch=self.batch)
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        # при нажатии запускается основная игра
        if key == arcade.key.SPACE:
            game_view = Astral_Escape_1()
            game_view.setup()
            self.window.show_view(game_view)
        if key == arcade.key.ESCAPE:
            self.window.close()


def main():
    window = arcade.Window(1200, 800, SCREEN_TITLE)
    start_view = StartView()  # запускаем стартовое окно
    game_view_1 = Astral_Escape_1()
    game_view_1.setup()
    game_view_2 = Astral_Escape_2()
    game_view_2.setup()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
