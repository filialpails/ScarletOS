# I maid a thing
image ctc = Text("▼", xalign=0.98, yalign=0.98)
image bg scarletOS = LiveTile("bg/scarletOS.png")
image scarlet happy = "scarlet/scarlet_happy.png"
image scarlet sad = "scarlet/scarlet_sad.png"
image red = "pon/red.png"
image green = "pon/green.png"
image blue = "pon/blue.png"
image cyan = "pon/cyan.png"
image magenta = "pon/magenta.png"
image yellow = "pon/yellow.png"
image grey = "pon/grey.png"
image cursor = "pon/cursor.png"

define kernel = Character(None, kind=nvl, color="#ffffff")
define adv = Character(None, ctc="ctc", ctc_position="fixed")
define s = Character("Scarlet", color="#f88080", image="scarlet")

init python:
    import random
    import pygame

    class Panel(object):
        WIDTH = 16
        HEIGHT = 16
        RED = 0
        GREEN = 1
        BLUE = 2
        CYAN = 3
        MAGENTA = 4
        YELLOW = 5
        GREY = 6
        COLOR_TO_IMAGE = (
            "red", "green", "blue", "cyan", "magenta", "yellow", "grey")

        def __init__(self, color, sprite):
            self.color = color
            self.sprite = sprite

    class Pon(object):
        COMBO_POINTS = (
            0, 0, 0, 0, 30, 50, 150, 190, 230, 270, 310, 400, 450, 500, 550)

        def __init__(self, width, height):
            self.width = width
            self.height = height
            self.game_over = None
            self.pressed = set()
            self.pressed_last_frame = set()
            self.old_st = 0
            self.panels = [[None for x in xrange(width)] for y in xrange(height)]
            self.cursor_x = self.width / 2
            self.cursor_y = self.height - 1
            self.score = 0
            self.speed = 1
            self.sprite_manager = SpriteManager(update=self.update,
                                                event=self.input,
                                                predict=self.predict)
            self.title_text = Text("Every day Panel de PON\nEvery time is Panel de PON")
            self.score_text = Text("")
            self.increase_score(0)
            self.cursor = self.sprite_manager.create("cursor")
            self.cursor.zorder = 9001
            for y in xrange(-1, -4, -1):
                row = self.panels[y]
                for x in xrange(self.width):
                    panel = self.new_panel(random.randint(0, 5))
                    row[x] = panel

        def new_panel(self, color):
            return Panel(color,
                         self.sprite_manager.create(Panel.COLOR_TO_IMAGE[color]))

        def gravity(self):
            fall = True
            while fall:
                fall = False
                for x in xrange(self.width):
                    for y in xrange(self.height - 2, -1, -1):
                        row = self.panels[y]
                        next_row = self.panels[y + 1]
                        panel = row[x]
                        if panel is not None and next_row[x] is None:
                            next_row[x] = panel
                            row[x] = None
                            fall = True

        def increase_score(self, amount):
            self.score += amount
            while self.score > 1000 * self.speed:
                self.speed += 1
            self.score_text.set_text("Score: {}\nSpeed: {}".format(self.score,
                                                                   self.speed))
            renpy.redraw(self.score_text, 0)

        def check_matches(self):
            combo = 0
            to_destroy = set()
            for y in xrange(self.height):
                row = self.panels[y]
                for x in xrange(self.width - 2):
                    p1 = row[x]
                    p2 = row[x + 1]
                    p3 = row[x + 2]
                    if p1 is not None and p2 is not None and p3 is not None and p1.color == p2.color == p3.color:
                        for x2 in xrange(3):
                            coords = (x + x2, y)
                            if coords in to_destroy: continue
                            to_destroy.add(coords)
                            combo += 1
                        for x2 in xrange(x, self.width):
                            if row[x2] is None or row[x2].color != p1.color:
                                continue
                            coords = (x2, y)
                            if coords not in to_destroy:
                                to_destroy.add(coords)
                                combo += 1
            for x in xrange(self.width):
                for y in xrange(self.height - 2):
                    row = self.panels[y]
                    next_row = self.panels[y + 1]
                    next_next_row = self.panels[y + 2]
                    p1 = row[x]
                    p2 = next_row[x]
                    p3 = next_next_row[x]
                    if p1 is not None and p2 is not None and p3 is not None and p1.color == p2.color == p3.color:
                        for y2 in xrange(3):
                            coords = (x, y + y2)
                            if coords in to_destroy: continue
                            to_destroy.add(coords)
                            combo += 1
                        for y2 in xrange(y, self.height):
                            next_panel = self.panels[y2][x]
                            if next_panel is None or next_panel.color != p1.color:
                                continue
                            coords = (x, y2)
                            if coords not in to_destroy:
                                to_destroy.add(coords)
                                combo += 1
            for x, y in to_destroy:
                self.destroy_panel(x, y)
            if combo > 3:
                self.increase_score(self.COMBO_POINTS[combo])

        def new_row(self):
            for y in xrange(self.height):
                row = self.panels[y]
                prev_row = self.panels[y - 1]
                for x in xrange(self.width):
                    panel = row[x]
                    if panel is None: continue
                    if y == 0:
                        self.game_over = True
                        renpy.timeout(0)
                        return
                    prev_row[x] = panel
            bottom_row = self.panels[-1]
            for x in xrange(self.width):
                panel = self.new_panel(random.randint(0, 5))
                panel.sprite.x = x * Panel.WIDTH
                panel.sprite.y = self.height * Panel.HEIGHT
                bottom_row[x] = panel
            self.cursor_y -= 1

        def destroy_panel(self, x, y):
            row = self.panels[y]
            row[x].sprite.destroy()
            row[x] = None
            self.increase_score(10)

        def input(self, ev, x, y, st):
            if self.game_over is not None:
                return self.score, self.game_over
            if ev.type != pygame.KEYDOWN: return
            if ev.key not in self.pressed_last_frame:
                self.pressed.add(ev.key)

        def update(self, st):
            self.pressed_last_frame = self.pressed.copy()
            if pygame.K_ESCAPE in self.pressed:
                self.game_over = False
                renpy.timeout(0)
            if pygame.K_UP in self.pressed and self.cursor_y > 0:
                self.cursor_y -= 1
            if pygame.K_DOWN in self.pressed and self.cursor_y < self.height - 1:
                self.cursor_y += 1
            if pygame.K_LEFT in self.pressed and self.cursor_x > 0:
                self.cursor_x -= 1
            if pygame.K_RIGHT in self.pressed and self.cursor_x < self.width - 2:
                self.cursor_x += 1
            if pygame.K_SPACE in self.pressed:
                row = self.panels[self.cursor_y]
                temp = row[self.cursor_x]
                row[self.cursor_x] = row[self.cursor_x + 1]
                row[self.cursor_x + 1] = temp
            if pygame.K_TAB in self.pressed:
                self.new_row()
                self.increase_score(1)
            self.cursor.x = self.cursor_x * Panel.WIDTH - 2
            self.cursor.y = self.cursor_y * Panel.HEIGHT - 2
            for y in xrange(self.height):
                row = self.panels[y]
                for x in xrange(self.width):
                    if row[x] is None: continue
                    sprite = row[x].sprite
                    sprite.x = x * Panel.WIDTH
                    sprite.y = y * Panel.HEIGHT
            self.check_matches()
            self.gravity()
            if st - self.old_st >= 16 - self.speed - 1:
                self.new_row()
                self.old_st = st
            self.pressed.clear()
            return 0.0333333333

        def predict(self):
            return ["red",
                    "green",
                    "blue",
                    "cyan",
                    "magenta",
                    "yellow",
                    "grey",
                    "cursor"]

label splashscreen:
    scene black
    python hide:
        renpy.say(kernel, "{} v{}{{w=0.5}}{{nw}}".format(config.name.upper(),
                                                         config.version.upper()))
        messages = (
            "PUTTING ON BLOOMERS...",
            "TYING BOWS...",
            "BREWING TEA...",
            "TIDYING UP A BIT...",
            "HOPING MASTER-SAMA NOTICES ME...",
            "PUTTING PONS AND WAYS IN ORDER...",
            "KAWAII LEVELS TO MAXIMUM...",
            "RETICULATING SPLINES...")
        for msg in messages:
            renpy.say(kernel, msg + "{w=0.5}{nw}")
        for i in xrange(2):
            for msg in messages:
                renpy.say(kernel, msg + "{nw}")
    nvl clear
    scene bg scarletOS
    "YOU ARE NOW USING SCARLET OS."
    return

label start:
    $ high_score = 0
    show screen konami
    scene bg scarletOS
    $ master_name = renpy.input("ENTER NAME:")
    show scarlet happy at right
    s "Pleased to meet you, Master [master_name]. I am Scarlet, your new maid."
    while True:
        show scarlet happy at right
        menu:
            s "I am at your service, Master [master_name]."
            "Make tea":
                s "Coming right up, Master~"
                hide scarlet
                "...{w}.{w}.{w}{nw}"
                show scarlet happy at right
                "Scarlet hands you a cup of hot tea."
            "Play Panel de PON":
                hide scarlet
                call pon
            "How to play":
                "ARROW KEYS - move cursor\nSPACE - swap panels\nTAB - speed up\nESC - quit game"
            "Check high score":
                if high_score <= 9000:
                    s "[master_name]-sama's high score is [high_score]. If you get more than 9000 I'll give you something special~ *blush*"
                else:
                    s "[master_name]-sama's high score is [high_score]."
            "Stick it in" if high_score > 9000:
                s "It's my first time, but... it's okay if it's with you, [master_name]-sama..."
                scene black with fade
                s "No Master, not there..."
                s "Ahn~"
                s "If you do that I'll..."
                s "Uah!"
                scene bg scarletOS with fade
    return

label pon:
    window hide None
    play music "ponponpon.mp3"
    python hide:
        pon = Pon(6, 13)
        ui.add(pon.sprite_manager, at=Transform(zoom=2.0))
        ui.add(pon.title_text, at=Transform(zoom=2.0,
                                            xanchor=0.5,
                                            xpos=0.5))
        ui.add(pon.score_text, at=Transform(zoom=2.0,
                                            xanchor=1.0,
                                            xpos=1.0,
                                            yanchor=0.5,
                                            ypos=0.5))
        store.score, store.game_over = ui.interact(suppress_overlay=True,
                                                   suppress_underlay=True)
    stop music
    window auto
    if game_over:
        scene black
        kernel "error 394C6B: Exceeded PON threshold{w=1.0}{nw}"
        kernel "Rebooting...{w=1.0}{nw}"
        nvl clear
    scene bg scarletOS
    if score > high_score:
        $ high_score = score
        show scarlet happy at right
        s "Your final score was [score]. That's higher than your previous high score! Congratulations, Master [master_name]!"
        return
    show scarlet sad at right
    s "Your final score was [score]. Sometimes the only winning move is not to play..."
    return

label quit:
    scene bg scarletOS
    show scarlet sad at right
    s "Goodbye Master..."
    return
