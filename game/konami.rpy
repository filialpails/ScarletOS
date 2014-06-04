init python:
    class KonamiListener(renpy.Displayable):
        def __init__(self, target):
            renpy.Displayable.__init__(self)
            import pygame
            # The label we jump to when the code is entered.
            self.target = target
            # This is the index (in self.code) of the key we're expecting.
            self.state = 0
            # The code itself.
            self.code = (
                pygame.K_UP,
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_DOWN,
                pygame.K_LEFT,
                pygame.K_RIGHT,
                pygame.K_LEFT,
                pygame.K_RIGHT,
                pygame.K_b,
                pygame.K_a)

        # This function listens for events.
        def event(self, ev, x, y, st):
            import pygame
            # We only care about keydown events.
            if ev.type != pygame.KEYDOWN:
                return
            # If it's not the key we want, go back to the start of the state machine.
            code = self.code
            if ev.key != code[self.state]:
                self.state = 0
                return
            # Otherwise, go to the next state.
            self.state += 1
            # If we are at the end of the code, then call the target label in the new context. (After we reset the state machine.)
            if self.state == len(code):
                self.state = 0
                renpy.call_in_new_context(self.target)

        # Return a small empty render, so we get events.
        def render(self, width, height, st, at):
            return renpy.Render(1, 1)

    # Create a KonamiListener to actually listen for the code.
    konami_listener = KonamiListener('konami')

# This adds konami_listener to each interaction.
screen konami:
    add konami_listener

# This is called in a new context when the konami code is entered.
label konami:
    $ high_score = renpy.input('Set high score:')
    return
