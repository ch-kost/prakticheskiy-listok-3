"""Отдельное окно Matplotlib с кнопкой Пауза/Продолжить: python live.py 1..5."""
import argparse
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import models

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('task', type=int, choices=range(1, 6))
args = parser.parse_args()
models.setup()
fig, animation, update = models.ANIMATORS[args.task-1]()
button = Button(fig.add_axes([.43, .005, .18, .05]), 'Пауза / Пуск')
state = {'paused': False}


def toggle(_):
    state['paused'] = not state['paused']
    if state['paused']: animation.pause()
    else: animation.resume()


button.on_clicked(toggle)
plt.show()
