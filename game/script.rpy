image ctc = Text(" ▼")
image bg scarletOS = LiveTile("bg/scarletOS.png")
image scarlet happy = "scarlet/scarlet_happy.png"
image scarlet sad = "scarlet/scarlet_sad.png"

define kernel = Character(None, kind=nvl, color="#ffffff")
define adv = Character(None, ctc="ctc", ctc_position="nestled")
define s = Character("Scarlet", color="#f88080", image="scarlet")

label splashscreen:
    scene black
    $ title = "{} v{}".format(config.name, config.version)
    kernel "[title]{nw}"
    $ del title
    kernel "CODE: Rob Steward{nw}"
    kernel "ART: Mark Cuerden{w=0.5}{nw}"
    kernel "Booting up...{nw}"
    kernel "{nw}"
    python hide:
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
        for i in xrange(3):
            for msg in messages:
                renpy.say(kernel, msg + "{nw}")
    nvl clear
    scene bg scarletOS
    show scarlet happy
    s "YOU ARE NOW USING SCARLET OS."
    return

label start:
    $ high_score = 0
    show screen konami
    scene bg scarletOS
    show scarlet happy at right
    s "How do you do, Master? I am Scarlet, your new maid. Pleased to meet you. *bows*"

label main:
    menu:
        s "I am at your service, Master."
        "Make tea":
            s "Coming right up, Master~"
            hide scarlet
            "...{w}.{w}.{w}{nw}"
            show scarlet happy at right
            "Scarlet hands you a cup of hot tea."
        "Play Panel de PON":
            call players_menu
        "Controls":
            "ARROW KEYS - move cursor\n\ \ \ \ \ SPACE - swap panels\nLEFT SHIFT - speed up\n\ \ \ \ \ \ \ ESC - quit game\n\ \ \ \ \ ENTER - pause"
        "High Score":
            s "Master's high score is [high_score]."
            if high_score <= 9000:
                s "If you get more than 9000 points I'll give you something special~ *blush*"
        "Stick it in" if high_score > 9000:
            s "It's my first time, but... it's okay if it's with you, Master..."
            scene black with fade
            "*POMF*"
            s "What are we going to do on the bed?"
            "..."
            s "No Master, not there..."
            "..."
            s "Ahn~"
            "..."
            s "If you do that I'll..."
            "..."
            s "Uah!"
            scene bg scarletOS with fade
            show scarlet happy at right
    jump main

label players_menu:
    menu:
        s "How many players?"
        "ONE PLAYER":
            call one_player_mode_menu
        "TWO PLAYER":
            call two_player_mode_menu
        "Back":
            return
    jump players_menu

label one_player_mode_menu:
    show scarlet happy at right
    menu:
        s "Please choose a game mode."
        "Endless":
            call endless
        "Time Trial":
            call one_player_time_trial
        "Stage Clear":
            call stage_clear
        "Puzzle":
            call puzzle
        "VS.":
            call one_player_vs
        "Back":
            return
    jump one_player_mode_menu

label two_player_mode_menu:
    show scarlet happy at right
    menu:
        s "Please choose a game mode."
        "Time Trial":
            call two_player_time_trial
        "VS.":
            call two_player_vs
        "Back":
            return
    jump two_player_mode_menu

label level_menu:
    $ speed = min(
        int(renpy.input("SPEED LV.", default=1, allow="0123456789", length=3)),
        100)
    menu:
        "GAME LV."
        "EASY":
            $ difficulty = 0
        "NORMAL":
            $ difficulty = 1
        "HARD":
            $ difficulty = 2
    return

label endless:
    call level_menu
    hide scarlet
    call pon
    $ score, game_over = _return
    if game_over:
        scene black
        kernel "error: stack overflow at 0x394C6B{w=1.0}{nw}"
        kernel "Rebooting...{w=1.0}{nw}"
        nvl clear
    scene bg scarletOS
    if score > high_score:
        $ high_score = score
        show scarlet happy at right
        s "Your final score was [score]. That's higher than your previous high score! Congratulations, Master!"
        return
    show scarlet sad at right
    s "Your final score was [score]. Better luck next time, Master!"
    return

label one_player_time_trial:
    s sad "Sorry Master, but that mode is not yet implemented."
    return

label stage_clear:
    s sad "Sorry Master, but that mode is not yet implemented."
    return

label puzzle:
    s sad "Sorry Master, but that mode is not yet implemented."
    return

label one_player_vs:
    s sad "Sorry Master, but that mode is not yet implemented."
    return

label two_player_time_trial:
    s sad "Sorry Master, but that mode is not yet implemented."
    return

label two_player_vs:
    s sad "Sorry Master, but that mode is not yet implemented."
    return

label quit:
    scene bg scarletOS
    show scarlet sad at right
    s "Goodbye Master..."
    return
