image red_panel = "pon/red.png"
image green_panel = "pon/green.png"
image blue_panel = "pon/blue.png"
image cyan_panel = "pon/cyan.png"
image magenta_panel = "pon/magenta.png"
image yellow_panel = "pon/yellow.png"
image grey_panel = "pon/grey.png"
image cursor = "pon/cursor.png"

style pon_text is text:
    antialias False
    outlines [(1, "#000", 0, 0)]
    size 28

init python:
    from __future__ import division, absolute_import, print_function, unicode_literals
    from itertools import islice
    import math
    from random import randint

    class Panel(object):
        WIDTH = 16
        HEIGHT = 16
        EMPTY = 0
        RED = 1
        GREEN = 2
        CYAN = 3
        YELLOW = 4
        MAGENTA = 5
        BLUE = 6
        GREY = 7
        COLOR_TO_REST_IMAGE = (
            None, "red_panel", "green_panel", "cyan_panel", "yellow_panel",
            "magenta_panel", "blue_panel", "grey_panel")
        COLOR_TO_FLASH_IMAGE = (
            None, "red_panel", "green_panel", "cyan_panel", "yellow_panel",
            "magenta_panel", "blue_panel", "grey_panel")
        COLOR_TO_MUTATE_IMAGE = (
            None, "red_panel", "green_panel", "cyan_panel", "yellow_panel",
            "magenta_panel", "blue_panel", "grey_panel")
        REST = 0
        LEVITATE = 1
        FALL = 2
        LAID = 3
        FLASH = 4
        MUTATE = 5
        CLEARED = 6
        TRANSFORMED = 7

        def __init__(self, color, sprite_manager):
            self.color = color
            self.sprite = sprite_manager.create(DynamicDisplayable(self.func))
            self.state = self.REST
            self.levitate_duration = 0
            self.warning_bounce = False
            self.chaining = False

        def func(self, st, at):
            state = self.state
            if state == self.FLASH:
                return (self.COLOR_TO_FLASH_IMAGE[self.color], Pon.FRAME_RATE)
            if state == self.MUTATE:
                return (self.COLOR_TO_MUTATE_IMAGE[self.color], Pon.FRAME_RATE)
            return (self.COLOR_TO_REST_IMAGE[self.color], Pon.FRAME_RATE)

    class Pon(object):
        WIDTH = 6
        HEIGHT = 12
        FRAME_RATE = 1 / 60
        DIFFICULTIES = ("EASY", "NORMAL", "HARD")
        ENDLESS_COLORS = (5, 5, 6)
        TIME_TRIAL_COLORS = (5, 5, 6)
        CHAIN_POINTS = (
            0, 0, 50, 80, 150, 300, 400, 500, 700, 900, 1100, 1300, 1500, 1800)
        COMBO_POINTS = (
            0, 0, 0, 0, 30, 50, 150, 190, 230, 270, 310, 400, 450, 500, 550)

        def __init__(self, speed, difficulty):
            self.speed = speed
            self.difficulty = difficulty
            self.tick = 0
            self.game_over = None
            self.panels = tuple(
                [None for y in xrange(self.HEIGHT)] for x in xrange(self.WIDTH))
            self.cursor_x = self.WIDTH // 2
            self.cursor_y = self.HEIGHT - 1
            self.score = 0
            self.time = 0
            self.stop_time = 0
            self.next_row_countdown = 0
            self.paused = False
            self.sprite_manager = SpriteManager(
                update=self.update, event=self.input, predict=self.predict)
            self.time_text = self.make_text("")
            self.high_score_text = self.make_text(
                "HI-SCORE\n{:6}".format(store.high_score))
            self.score_text = self.make_text("")
            self.speed_text = DynamicDisplayable(self.speed_func)
            self.pause_text = DynamicDisplayable(self.pause_func)
            self.level_text = self.make_text(
                "LEVEL\n{:>6}".format(self.DIFFICULTIES[difficulty]))
            self.next_row_shadow = self.sprite_manager.create(Solid(
                    "#00000080",
                    xsize=self.WIDTH * Panel.WIDTH,
                    ysize=Panel.HEIGHT))
            self.frame = Solid(
                "#000",
                xsize=self.WIDTH * Panel.WIDTH,
                ysize=Panel.HEIGHT)
            self.next_row_shadow.zorder = 9001
            self.increase_score(0)
            self.cursor = self.sprite_manager.create("cursor")
            self.cursor.zorder = 9002
            new_panel = self.new_panel
            for col in self.panels:
                for y in xrange(-1, -4, -1):
                    rnd = randint(0, self.ENDLESS_COLORS[self.difficulty])
                    col[y] = None if rnd == 0 else new_panel(rnd)
            new_random_panel = self.new_random_panel
            self.next_row_preview = [
                new_random_panel() for x in xrange(self.WIDTH)]
            self.pause_text_real = self.make_text("PAUSED")
            self.speed_text_real = self.make_text(
                "SPEED LV.\n{:6}".format(self.speed))
            self.stop_text_real =  self.make_text(
                "SPEED LV.\n{:02d}STOP".format(self.stop_time // 60))

        def make_text(self, *args, **kwargs):
            return Text(*args, style="pon_text", **kwargs)

        def pause_func(self, st, at):
            if self.paused:
                return (self.pause_text_real, self.FRAME_RATE)
            return (Null(), self.FRAME_RATE)

        def speed_func(self, st, at):
            if self.stop_time > 0:
                return (self.stop_text_real, self.FRAME_RATE)
            return (self.speed_text_real, self.FRAME_RATE)

        def new_panel(self, color):
            return Panel(color, self.sprite_manager)

        def new_random_panel(self):
            return self.new_panel(
                randint(1, self.ENDLESS_COLORS[self.difficulty]))

        def increase_score(self, amount):
            self.score += amount
            score = self.score
            while score > 300 * self.speed:
                if self.speed == 100: break
                self.speed += 1
                self.speed_text_real.set_text(
                    "SPEED LV.\n{:6}".format(self.speed))

        def check_match(self, panel, color):
            return panel is not None and panel.color == color and (panel.state == Panel.REST or panel.state == Panel.FLASH)

        def check_matches(self):
            combo = 0
            panels = self.panels
            WIDTH = self.WIDTH
            HEIGHT = self.HEIGHT
            WIDTH_minus_2 = WIDTH - 2
            HEIGHT_minus_2 = HEIGHT - 2
            REST = Panel.REST
            FLASH = Panel.FLASH
            for x in xrange(WIDTH):
                col = panels[x]
                if x < WIDTH_minus_2:
                    next_col = panels[x + 1]
                    next_next_col = panels[x + 2]
                for y in xrange(HEIGHT):
                    p1 = col[y]
                    if p1 is None or not (p1.state == REST or p1.state == FLASH): continue
                    if y < HEIGHT_minus_2:
                        p2 = col[y + 1]
                        p3 = col[y + 2]
                        color = p1.color
                        if self.check_match(p2, color) and self.check_match(p3, color):
                            for panel in islice(col, y, None):
                                if not self.check_match(panel, color):
                                    break
                                panel.state = FLASH
                                combo += 1
                    if x < WIDTH_minus_2:
                        p2 = next_col[y]
                        p3 = next_next_col[y]
                        color = p1.color
                        if self.check_match(p2, color) and self.check_match(p3, color):
                            for col2 in islice(panels, x, None):
                                panel = col2[y]
                                if not self.check_match(panel, color):
                                    break
                                panel.state = FLASH
                                combo += 1
            if combo > 3:
                self.increase_score(self.COMBO_POINTS[combo])
                self.stop_time = max(
                    self.stop_time, 42 + 10 * (combo - 4))
                self.stop_text_real.set_text(
                    "SPEED LV.\n{:02d}STOP".format(self.stop_time // 60))
            return combo >= 3

        def new_row(self):
            panels = self.panels
            next_row_preview = self.next_row_preview
            new_random_panel = self.new_random_panel
            overflow = False
            for x in xrange(self.WIDTH):
                col = panels[x]
                top = col.pop(0)
                col.append(next_row_preview[x])
                next_row_preview[x] = new_random_panel()
                if top is not None: overflow = True
            if self.cursor_y > 0:
                self.cursor_y -= 1
            if overflow:
                self.game_over = True
                renpy.timeout(0)

        def input(self, ev, x, y, st):
            game_over = self.game_over
            if game_over is not None:
                return self.score, game_over

        def move_up(self):
            if not self.paused and self.cursor_y > 0:
                self.cursor_y -= 1

        def move_down(self):
            if not self.paused and self.cursor_y < self.HEIGHT - 1:
                self.cursor_y += 1

        def move_left(self):
            if not self.paused and self.cursor_x > 0:
                self.cursor_x -= 1

        def move_right(self):
            if not self.paused and self.cursor_x < self.WIDTH - 2:
                self.cursor_x += 1

        def swap_panels(self):
            if self.paused: return
            panels = self.panels
            cursor_x = self.cursor_x
            l_col = panels[cursor_x]
            r_col = panels[cursor_x + 1]
            y = self.cursor_y
            l = l_col[y]
            r = r_col[y]
            LEVITATE = Panel.LEVITATE
            if l and l.state == LEVITATE or r and r.state == LEVITATE:
                return
            if y > 0:
                y2 = y - 1
                l2 = l_col[y2]
                r2 = r_col[y2]
                if l2 and l2.state == LEVITATE or r2 and r2.state == LEVITATE:
                    return
            l_col[y], r_col[y] = r, l

        def speed_up(self):
            if self.paused: return
            self.stop_time = 0
            self.next_row_countdown = 0
            self.increase_score(1)
            self.new_row()

        def pause(self):
            self.paused ^= True

        def quit(self):
            self.game_over = False
            renpy.timeout(0)

        def rise_speed(self):
            return 16 * 60 * (1 - (self.speed - 1) / 100)

        def update(self, st):
            self.tick += 1
            if not self.paused:
                chain = 0
                self.check_matches()
                if chain > 1:
                    self.increase_score(self.CHAIN_POINTS[chain])
                    self.stop_time = max(self.stop_time, 85 + 10 * (chain - 2))
                if chain == 0 and self.stop_time > 0:
                    self.stop_time -= 1
                self.stop_text_real.set_text(
                    "SPEED LV.\n{:02}STOP".format(self.stop_time // 60))
                self.time += 1
                if self.stop_time <= 0:
                    self.next_row_countdown += 1
                    if self.next_row_countdown >= self.rise_speed():
                        self.new_row()
                        self.next_row_countdown = 0
                panels = self.panels
                HEIGHT = self.HEIGHT
                REST = Panel.REST
                LEVITATE = Panel.LEVITATE
                FALL = Panel.FALL
                LAID = Panel.LAID
                FLASH = Panel.FLASH
                MUTATE = Panel.MUTATE
                CLEARED = Panel.CLEARED
                for x in xrange(self.WIDTH):
                    col = panels[x]
                    for y in xrange(HEIGHT - 1, -1, -1):
                        panel = col[y]
                        if panel is None: continue
                        state = panel.state
                        if state == REST:
                            if y == HEIGHT - 1: continue
                            below = col[y + 1]
                            if below is None:
                                panel.state = LEVITATE
                                panel.levitate_duration = 12
                                continue
                            if below.state == LEVITATE:
                                dur = below.levitate_duration
                                for y2 in xrange(y, -1, -1):
                                    p = col[y2]
                                    if p is None or p.state != REST: break
                                    p.state = LEVITATE
                                    p.levitate_duration = dur
                            continue
                        if state == LEVITATE:
                            panel.levitate_duration -= 1
                            if panel.levitate_duration == 0:
                                panel.state = FALL
                            continue
                        if state == FALL:
                            if y == HEIGHT - 1:
                                panel.state = LAID
                                continue
                            below = col[y + 1]
                            if below is not None:
                                if below.state == LEVITATE:
                                    panel.state = LEVITATE
                                    panel.levitate_duration = below.levitate_duration
                                    continue
                                panel.state = LAID
                                continue
                            col[y + 1] = panel
                            col[y] = None
                            continue
                        if state == LAID:
                            panel.state = REST
                            continue
                        if state == FLASH:
                            panel.state = MUTATE
                            continue
                        if state == MUTATE:
                            panel.state = CLEARED
                            continue
                        if state == CLEARED:
                            panel.sprite.destroy()
                            col[y] = None
                            self.increase_score(10)
            self.draw()
            return self.FRAME_RATE

        def draw(self):
            WIDTH = self.WIDTH
            HEIGHT = self.HEIGHT
            PANEL_WIDTH = Panel.WIDTH
            PANEL_HEIGHT = Panel.HEIGHT
            y_offset = self.next_row_countdown / self.rise_speed()
            cursor = self.cursor
            cursor.x = self.cursor_x * PANEL_WIDTH - 2
            cursor.y = (self.cursor_y - y_offset) * PANEL_HEIGHT - 2
            preview_y = (HEIGHT - y_offset) * PANEL_HEIGHT
            next_row_preview = self.next_row_preview
            panels = self.panels
            for x in xrange(WIDTH):
                col = panels[x]
                sprite_x = x * PANEL_WIDTH
                for y in xrange(HEIGHT):
                    panel = col[y]
                    if panel is None: continue
                    sprite = panel.sprite
                    sprite.x = sprite_x
                    sprite.y = (y - y_offset) * PANEL_HEIGHT
                sprite = next_row_preview[x].sprite
                sprite.x = sprite_x
                sprite.y = preview_y
            self.next_row_shadow.y = preview_y
            time_text = self.time_text
            seconds = self.time // 60
            time_text.set_text(
                "TIME\n{:3}'{:02}".format(seconds // 60, seconds % 60))
            redraw = renpy.redraw
            redraw(time_text, 0)
            score_text = self.score_text
            score_text.set_text("SCORE\n{:6}".format(self.score))
            redraw(score_text, 0)

        def predict(self):
            return [
                "red_panel", "green_panel", "cyan_panel", "yellow_panel",
                "magenta_panel", "blue_panel", "grey_panel", "cursor"]

label pon:
    window hide None
    play music "ponponpon.mp3"
    call screen pon_screen(pon=Pon(speed, difficulty))
    stop music
    window auto
    return _return

screen pon_screen(pon):
    add pon.time_text xalign 0.0 yanchor 0.0
    add pon.sprite_manager xpos 0.313 zoom 4.0
    add pon.pause_text xalign 0.5 yalign 0.5
    add pon.high_score_text xalign 1.0 yalign 0.0
    add pon.score_text xalign 1.0 yalign 0.33
    add pon.speed_text xalign 1.0 yalign 0.67
    add pon.level_text xalign 1.0 yalign 1.0
    add pon.frame xalign 0.5 yalign 0.915 zoom 4.0
    key "K_UP" action pon.move_up
    key "K_DOWN" action pon.move_down
    key "K_LEFT" action pon.move_left
    key "K_RIGHT" action pon.move_right
    key "K_SPACE" action pon.swap_panels
    key "K_LSHIFT" action pon.speed_up
    key "K_RETURN" action pon.pause
    key "K_ESCAPE" action pon.quit
