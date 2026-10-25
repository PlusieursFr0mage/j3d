import pyglet
from pyglet.shapes import Circle
# from pyglet.window import key
# from pyglet.window import mouse

window = pyglet.window.Window(
        resizable=True,
        fullscreen = False,
        vsync = True,
        style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS
        )

circle = shapes.Circle(x=100, y=100, radius=50)

@window.event
def on_key_press(symbol, modifiers):
    print(f'{chr(symbol)} key was pressed')


@window.event
def on_mouse_press(x, y, button, modifiers):
    # button -> renvoie le code du bouton de la souris
    # x, y -> renvoie la postion de la souris lors du click
    print(f'The {button} mouse button was pressed')
    print(f'{x, y}')

pyglet.app.run()

