#init python hide:
#    image = renpy.image
#    for p in ("p1", "p2"):
#        name = "{}_garbage1x1".format(p)
#        image(name, "pon/{}.png".format(name))
#        for width in xrange(3, 7):
#            name = "{}_garbage{}x1".format(p, width)
#            image(name, "pon/{}.png".format(name))
#        for height in xrange(1, 10):
#            name = "{}_garbage6x{}".format(p, height)
#            image(name, "pon/{}.png".format(name))
#    for height in xrange(1, 10):
#        name = "grey_garbage6x{}".format(p, height)
#        image(name, "pon/{}.png".format(name))

init 1 python:
    class EndlessMode(object):
        def __init__(self):
            pass

    class TimeTrialMode(object):
        def __init__(self):
            self.time_left = 120
            self.level = 0

        def update(self):
            self.time_left -= 1
            if self.time_left == 0:
                self.game_over = True

    class StageClearMode(object):
        def __init__(self, clear_level):
            self.clear_level = clear_level
            self.current_level = 0

        def on_new_line(self):
            self.current_level += 1

    class PuzzleMode(object):
        def __init__(self, i1, i2):
            puzzle = Puzzle(i1, i2)
            self.panels = puzzle.panels
            self.moves_left = puzzle.moves

        def on_swap(self):
            self.moves_left -= 1

        def update(self):
            # check if all panels are empty
            pass

    class Garbage(Panel):
        COLOR_TO_IMAGE = ("p1_garbage", "p2_garbage", "grey_garbage")

        def __init__(self, color, sprite, width, height):
            Panel.__init__(self, color, sprite)
            self.width = width
            self.height = height

    class VersusMode(object):
        def __init__(self, player1, player2):
            self.player1 = player1
            self.player2 = player2

        def new_garbage(self, color, width, height):
            return Garbage(
                color,
                self.sprite_manager.create("{}{}x{}".format(
                        Garbage.COLOR_TO_IMAGE[color], width, height)),
                width,
                height)

        def make_garbage(self, type, level, color):
            if type == 'combo' and level > 3:
                new_garbage = self.new_garbage
                if level < 8: return (new_garbage(color, level - 1, 1),)
                level = (level - 1) / 2
                return (new_garbage(color, int(level), 1),
                        new_garbage(color, int(math.ceil(level)), 1))
            if type == 'chain' and level > 1:
                return (self.new_garbage(color, self.WIDTH, level - 1),)
            if type == 'surprise':
                return (self.new_garbage(color, self.WIDTH, level - 2),)

        def destroy_garbage(self, x, y):
            garbage = self.panels[x][y]
            for x2 in self.WIDTH:
                self.panels[x2][y] = self.new_random_panel()
            garbage.height -= 1
