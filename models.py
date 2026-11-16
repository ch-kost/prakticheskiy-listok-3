"""Пять физических моделей листка 3, графики и управляемые анимации."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.integrate import solve_ivp
from scipy.special import ellipk, ellipj

G = 9.81
FRAMES = 64
COLORS = ['#1768ac', '#df6b22', '#24936e']


def setup():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.grid': True, 'grid.alpha': .22,
                         'animation.embed_limit': 80})


def save(fig, name):
    Path('figures').mkdir(exist_ok=True)
    fig.savefig(Path('figures')/name, dpi=150, bbox_inches='tight')
    return fig


def animate(fig, update):
    animation = FuncAnimation(fig, update, frames=FRAMES, interval=70,
                              blit=False, repeat=False)
    return fig, animation, update


def descent(t, v=1., u0=1., x0=0., y0=3.):
    t = np.asarray(t)
    u = np.sqrt(u0*u0+2*G*v*t)
    return x0+(u**3-u0**3)/(3*G*v), y0-v*t, u


def plot_descent():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout='constrained')
    for color, v, u in zip(COLORS, [.7, 1., 1.4], [1.5, 1., .6]):
        t = np.linspace(0, 2, 300)
        x, y, vx = descent(t, v, u)
        axes[0].plot(x, y, color=color, label=f'v={v}, u₀={u}')
        axes[0].scatter(x[0], y[0], color=color)
        axes[1].plot(t, y, color=color, label=f'vᵧ=−{v}')
    axes[0].set(xlabel='x, м', ylabel='y, м', title='3.1. Семейство кривых; точка — старт')
    axes[1].set(xlabel='t, с', ylabel='y, м', title='Постоянная вертикальная скорость')
    for ax in axes: ax.legend()
    return save(fig, '3_1_descent.png')


def anim_descent():
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), dpi=72, layout='constrained')
    times = np.linspace(0, 2, FRAMES)
    x, y, vx = descent(times)
    axes[0].plot(x, y, color='0.7')
    dot, = axes[0].plot([], [], 'o', color=COLORS[0], ms=9)
    trace, = axes[0].plot([], [], color=COLORS[0])
    axes[0].set(xlabel='x, м', ylabel='y, м', title='3.1. Движение по направляющей')
    axes[1].plot(times, y, color='0.7')
    clock, = axes[1].plot([], [], 'o', color=COLORS[0])
    axes[1].set(xlabel='t, с', ylabel='y, м', title='y(t)=3−t')
    status = fig.suptitle('')
    def update(k):
        dot.set_data([x[k]], [y[k]])
        trace.set_data(x[:k+1], y[:k+1])
        clock.set_data([times[k]], [y[k]])
        status.set_text(f't={times[k]:.2f} с; vᵧ=−1.00 м/с; vₓ={vx[k]:.2f} м/с')
        return dot, trace, clock, status
    return animate(fig, update)


def fold(q, length):
    return length-np.abs(np.mod(q, 2*length)-length)


def billiard(t, ratio=1.):
    t = np.asarray(t)
    u, v = .51+t, .73+(2/3)*ratio*t
    return fold(u, 3.), fold(v, 2.), u, v


def torus(u, v):
    alpha, beta = np.pi*np.asarray(u)/3, np.pi*np.asarray(v)/2
    radius = 2+.65*np.cos(beta)
    return radius*np.cos(alpha), radius*np.sin(alpha), .65*np.sin(beta)


def billiard_axes(fig):
    axes = []
    for row, text in enumerate(['Рациональный наклон, ρ=1', 'Иррациональный наклон, ρ=√2']):
        rect = fig.add_subplot(2, 3, row*3+1)
        rect.plot([0, 3, 3, 0, 0], [0, 0, 2, 2, 0], 'k-', lw=1)
        rect.set(xlim=(-.1, 3.1), ylim=(-.1, 2.1), xlabel='x, м', ylabel='y, м', title=text)
        rect.set_aspect('equal')
        unfolded = fig.add_subplot(2, 3, row*3+2)
        unfolded.set(xlim=(0, 20), ylim=(0, 20), xlabel='U, м', ylabel='V, м', title='Развёртка: прямая')
        unfolded.set_aspect('equal')
        for q in np.arange(0, 21, 3): unfolded.axvline(q, color='0.8', lw=.7)
        for q in np.arange(0, 21, 2): unfolded.axhline(q, color='0.8', lw=.7)
        sphere = fig.add_subplot(2, 3, row*3+3, projection='3d')
        aa, bb = np.meshgrid(np.linspace(0, 2*np.pi, 42), np.linspace(0, 2*np.pi, 18))
        sphere.plot_surface((2+.65*np.cos(bb))*np.cos(aa), (2+.65*np.cos(bb))*np.sin(aa),
                            .65*np.sin(bb), color='#8fb5d4', alpha=.17, linewidth=0)
        sphere.set(xlim=(-2.7, 2.7), ylim=(-2.7, 2.7), zlim=(-.8, .8), title='Тор: периоды 2a и 2b')
        sphere.set_box_aspect((1, 1, .4)); sphere.set_axis_off()
        axes.append((rect, unfolded, sphere))
    return axes


def plot_billiard():
    fig = plt.figure(figsize=(13, 8), layout='constrained')
    axes = billiard_axes(fig)
    for row, (ratio, duration) in enumerate([(1., 6.), (np.sqrt(2), 120.)]):
        t = np.linspace(0, duration, 12000)
        x, y, u, v = billiard(t, ratio)
        axes[row][0].plot(x, y, color=COLORS[row], lw=.7)
        tt = np.linspace(0, 18, 1500)
        _, _, uu, vv = billiard(tt, ratio)
        axes[row][1].plot(uu, vv, color=COLORS[row])
        axes[row][2].plot(*torus(u, v), color=COLORS[row], lw=.65)
    fig.suptitle('3.2. Бильярд: периодическая и непериодическая траектории')
    return save(fig, '3_2_billiard.png')


def anim_billiard():
    fig = plt.figure(figsize=(10, 6.5), dpi=72, layout='constrained')
    axes = billiard_axes(fig)
    times = np.linspace(0, 18, FRAMES)
    # Промежуточные точки подробно отображают изломы возле стенок.
    data, artists = [], []
    for row, ratio in enumerate([1., np.sqrt(2)]):
        fine = np.linspace(0, 18, 4000)
        x, y, u, v = billiard(fine, ratio)
        data.append((fine, x, y, u, v, torus(u, v), ratio))
        lines = []
        for ax in axes[row][:2]:
            lines.append(ax.plot([], [], color=COLORS[row], lw=1)[0])
            lines.append(ax.plot([], [], 'o', color=COLORS[row], ms=5)[0])
        lines.append(axes[row][2].plot([], [], [], color=COLORS[row], lw=.8)[0])
        lines.append(axes[row][2].plot([], [], [], 'o', color=COLORS[row], ms=4)[0])
        artists.append(lines)
    title = fig.suptitle('')
    def update(k):
        for datum, lines in zip(data, artists):
            fine, x, y, u, v, xyz, ratio = datum
            count = np.searchsorted(fine, times[k], side='right')
            bx, by, bu, bv = billiard(times[k], ratio)
            lines[0].set_data(x[:count], y[:count]); lines[1].set_data([bx], [by])
            lines[2].set_data(u[:count], v[:count]); lines[3].set_data([bu], [bv])
            lines[4].set_data_3d(*(p[:count] for p in xyz))
            lines[5].set_data_3d(*(np.atleast_1d(p) for p in torus(bu, bv)))
        title.set_text(f'3.2. t={times[k]:.2f} с; |v| сохраняется при каждом отражении')
        return [title]
    return animate(fig, update)


def chain(x, a, span=3.):
    return a*(np.cosh(np.asarray(x)/a)-np.cosh(span/(2*a)))


def chain_forces(a, mu, left=.35, right=.65):
    horizontal = mu*G*a
    return np.array([[-horizontal, -horizontal*np.sinh(left/a)],
                     [horizontal, horizontal*np.sinh(right/a)],
                     [0., -mu*G*a*(np.sinh(right/a)-np.sinh(left/a))]])


def plot_chain():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout='constrained')
    x = np.linspace(-1.5, 1.5, 300)
    for a, c in zip([.7, 1.2, 2.4], COLORS):
        axes[0].plot(x, chain(x, a), color=c, label=f'a={a} м')
    axes[0].scatter([-1.5, 1.5], [0, 0], c='k')
    axes[0].set(xlabel='x, м', ylabel='y, м', title='3.3. Цепная линия при разных a')
    axes[0].legend()
    h = np.linspace(7, 30, 200); a = h/G
    axes[1].plot(h, a*(np.cosh(1.5/a)-1))
    axes[1].set(xlabel='H, Н', ylabel='Провисание, м', title='μ=1 кг/м: влияние натяжения')
    mu = np.linspace(.6, 2, 200); a = 16/(mu*G)
    axes[2].plot(mu, a*(np.cosh(1.5/a)-1))
    axes[2].set(xlabel='μ, кг/м', ylabel='Провисание, м', title='H=16 Н: влияние плотности')
    return save(fig, '3_3_chain.png')


def anim_chain():
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), dpi=72, layout='constrained')
    x = np.linspace(-1.5, 1.5, 300)
    line, = axes[0].plot([], [], color=COLORS[0], lw=2)
    axes[0].scatter([-1.5, 1.5], [0, 0], c='k')
    axes[0].plot([], [], color=COLORS[1], lw=5, label='Выделенный элемент')
    element, = axes[0].plot([], [], color=COLORS[1], lw=5)
    axes[0].set(xlim=(-1.7, 1.7), ylim=(-2.7, .2), xlabel='x, м', ylabel='y, м', title='Семейство равновесных цепей')
    axes[0].legend(loc='lower left', fontsize=8)
    force = axes[1].quiver([0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
                            color=COLORS, angles='xy', scale_units='xy', scale=1)
    axes[1].set(xlim=(-28, 28), ylim=(-25, 25), xlabel='Fₓ, Н', ylabel='Fᵧ, Н',
                title='Силы на элементе: сумма равна нулю')
    for label, color in zip(['T слева', 'T справа', 'Вес элемента'], COLORS):
        axes[1].plot([], [], color=color, label=label)
    axes[1].legend(fontsize=8)
    text = fig.suptitle('')
    def update(k):
        phase = k/(FRAMES-1)
        if phase < .5:
            mu, h = 1., 9+30*phase
            mode = 'меняется H, μ=1'
        else:
            mu, h = .7+2*(phase-.5), 16.
            mode = 'меняется μ, H=16'
        a = h/(mu*G)
        line.set_data(x, chain(x, a))
        xe = np.linspace(.35, .65, 20); element.set_data(xe, chain(xe, a))
        forces = chain_forces(a, mu); force.set_UVC(forces[:, 0], forces[:, 1])
        length = 2*a*np.sinh(1.5/a)
        sag = a*(np.cosh(1.5/a)-1)
        text.set_text(f'3.3. {mode}; a={a:.2f} м; провисание={sag:.2f} м; длина={length:.2f} м')
        return line, element, force, text
    return animate(fig, update)


def cycloid(theta, radius=1.):
    theta = np.asarray(theta)
    return radius*(theta+np.sin(theta)), radius*(1-np.cos(theta))


def tautochrone(t, theta0, radius=1.):
    omega = np.sqrt(G/(4*radius))
    s = 4*radius*np.sin(theta0/2)*np.cos(omega*np.asarray(t))
    theta = 2*np.arcsin(np.clip(s/(4*radius), -1, 1))
    return (*cycloid(theta, radius), s)


def generator(ax, u):
    center = u-np.pi
    theta = np.linspace(0, 2*np.pi, 150)
    ax.plot(center+np.cos(theta), 1+np.sin(theta), color=COLORS[1])
    px, py = u-np.pi-np.sin(u), 1+np.cos(u)
    ax.plot([center, px], [1, py], color=COLORS[1])
    ax.scatter([px], [py], color=COLORS[1])


def plot_tautochrone():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout='constrained')
    theta = np.linspace(-np.pi, np.pi, 600)
    xx, yy = cycloid(theta)
    axes[0].plot(xx, yy, color='0.6')
    arrival = np.pi/np.sqrt(G)
    time = np.linspace(0, arrival, 200)
    for color, start in zip(COLORS, [.6, 1.4, 2.5]):
        x, y, s = tautochrone(time, start)
        axes[0].plot(x, y, color=color, label=f'θ₀={start}')
        axes[0].scatter(x[0], y[0], c=color)
        axes[1].plot(time, s, color=color, label=f'θ₀={start}')
    axes[0].set(xlabel='x, м', ylabel='y, м', title='3.4. Таутохрона — циклоида'); axes[0].legend()
    axes[1].axvline(arrival, ls='--', color='k', label=f'T={arrival:.4f} с')
    axes[1].set(xlabel='t, с', ylabel='s, м', title='Одновременное прибытие в s=0'); axes[1].legend()
    axes[2].plot(xx, yy, color=COLORS[0]); axes[2].axhline(2, color='0.6', ls='--')
    generator(axes[2], 2.1)
    axes[2].set(xlabel='x, м', ylabel='y, м', title='Окружность катится под y=2R')
    axes[2].set_aspect('equal')
    return save(fig, '3_4_tautochrone.png')


def anim_tautochrone():
    fig, axes = plt.subplots(1, 2, figsize=(9, 3), dpi=72, layout='constrained')
    theta = np.linspace(-np.pi, np.pi, 600)
    curve = cycloid(theta)
    arrival = np.pi/np.sqrt(G)
    times = np.linspace(0, arrival, FRAMES)
    dots, tracks = [], []
    for ax in axes:
        ax.plot(*curve, color='0.65')
        ax.set(xlim=(-3.4, 3.4), ylim=(-.15, 2.3), xlabel='x, м', ylabel='y, м')
        ax.set_aspect('equal')
    axes[0].set_title('3.4. Пуск из покоя с разных высот')
    for color, start in zip(COLORS, [.6, 1.4, 2.5]):
        tracks.append(tautochrone(times, start))
        dots.append(axes[0].plot([], [], 'o', color=color, ms=8, label=f'θ₀={start}')[0])
    axes[0].legend(fontsize=8)
    axes[1].set_title('Геометрическое построение; время условное')
    axes[1].axhline(2, color='0.6', ls='--')
    circle, = axes[1].plot([], [], color=COLORS[1])
    rod, = axes[1].plot([], [], color=COLORS[1])
    trace, = axes[1].plot([], [], color=COLORS[0], lw=2)
    point, = axes[1].plot([], [], 'o', color=COLORS[1])
    text = fig.suptitle('')
    ang = np.linspace(0, 2*np.pi, 100)
    def update(k):
        for dot, (x, y, s) in zip(dots, tracks): dot.set_data([x[k]], [y[k]])
        u = 2*np.pi*k/(FRAMES-1); center = u-np.pi
        px, py = center-np.sin(u), 1+np.cos(u)
        circle.set_data(center+np.cos(ang), 1+np.sin(ang))
        rod.set_data([center, px], [1, py]); point.set_data([px], [py])
        path = np.linspace(0, u, max(2, 5*k))
        trace.set_data(path-np.pi-np.sin(path), 1+np.cos(path))
        text.set_text(f't={times[k]:.4f} с; общее время T={arrival:.4f} с; '
                      + ('все в нижней точке' if k == FRAMES-1 else 'все шарики движутся'))
        return dots+[circle, rod, trace, point, text]
    return animate(fig, update)


def pendulum(t, angle, velocity=0., length=1.):
    t = np.asarray(t)
    solution = solve_ivp(lambda _, z: [z[1], -G/length*np.sin(z[0])],
                         (0, float(t[-1])), [angle, velocity], t_eval=t,
                         method='DOP853', rtol=1e-11, atol=1e-13)
    if not solution.success: raise RuntimeError(solution.message)
    return solution.y


def exact_pendulum(t, amplitude, length=1.):
    m = np.sin(amplitude/2)**2
    sn = ellipj(ellipk(m)-np.sqrt(G/length)*np.asarray(t), m)[0]
    return 2*np.arcsin(np.sin(amplitude/2)*sn)


def phase_axes(ax):
    theta, velocity = np.meshgrid(np.linspace(-np.pi, np.pi, 240), np.linspace(-9, 9, 240))
    energy = velocity**2/2+G*(1-np.cos(theta))
    ax.contour(theta, velocity, energy/G, levels=[.2, .8, 1.5, 2.6, 3.5], colors='0.7', linewidths=.6)
    ax.contour(theta, velocity, energy/G, levels=[2], colors='#b91c1c', linewidths=1.5)
    ax.set(xlim=(-np.pi, np.pi), ylim=(-9, 9), xlabel='θ mod 2π, рад', ylabel='θ̇, рад/с',
           title='Фазовый портрет; красным — сепаратриса')


def phase_line(theta, velocity):
    wrapped = (theta+np.pi)%(2*np.pi)-np.pi
    wrapped = wrapped.copy(); velocity = velocity.copy()
    jumps = np.r_[False, np.abs(np.diff(wrapped)) > np.pi]
    wrapped[jumps] = np.nan; velocity[jumps] = np.nan
    return wrapped, velocity


def plot_pendulum():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), layout='constrained')
    t = np.linspace(0, 8, 1800)
    phase_axes(axes[1])
    for (angle, velocity), color, label in zip([(.15, 0), (2.6, 0), (0, 2.4*np.sqrt(G))],
                                                COLORS, ['Малые колебания', 'Нелинейные колебания', 'Вращение']):
        th, vel = pendulum(t, angle, velocity)
        if velocity == 0:
            axes[0].plot(t, th, color=color, label=label)
        axes[1].plot(*phase_line(th, vel), color=color, lw=1.3)
    axes[0].plot(t, .15*np.cos(np.sqrt(G)*t), 'k--', lw=.7, label='Линейное, A=0.15')
    axes[0].plot(t, 2.6*np.cos(np.sqrt(G)*t), '--', color=COLORS[1], lw=.8, label='Линейное, A=2.6')
    axes[0].set(xlabel='t, с', ylabel='θ, рад', title='3.5. Сравнение точного и линейного решений')
    axes[0].legend(fontsize=8)
    amplitude = np.linspace(.001, np.pi-.015, 300)
    period = 4/np.sqrt(G)*ellipk(np.sin(amplitude/2)**2)
    axes[2].plot(amplitude, period, label='Точный период')
    axes[2].axhline(2*np.pi/np.sqrt(G), ls='--', color='0.4', label='Малые углы')
    axes[2].set(xlabel='Амплитуда, рад', ylabel='T, с', title='Период растёт с амплитудой'); axes[2].legend(fontsize=8)
    return save(fig, '3_5_pendulum.png')


def anim_pendulum():
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), dpi=72, layout='constrained')
    times = np.linspace(0, 8, FRAMES)
    fine = np.linspace(0, 8, 2000)
    axes[0].set(xlim=(-1.3, 1.3), ylim=(-1.35, 1.2), xlabel='x, м', ylabel='y, м', title='3.5. Маятник: малый, большой, вращение')
    axes[0].set_aspect('equal'); axes[0].scatter([0], [0], c='k')
    phase_axes(axes[1]); rods, dots, markers, data = [], [], [], []
    for (angle, velocity), color in zip([(.15, 0), (2.6, 0), (0, 2.4*np.sqrt(G))], COLORS):
        th, vel = pendulum(fine, angle, velocity)
        axes[1].plot(*phase_line(th, vel), color=color, lw=.6, alpha=.4)
        data.append(pendulum(times, angle, velocity))
        rods.append(axes[0].plot([], [], color=color)[0])
        dots.append(axes[0].plot([], [], 'o', color=color, ms=8)[0])
        markers.append(axes[1].plot([], [], 'o', color=color, ms=7)[0])
    text = fig.suptitle('')
    def update(k):
        for rod, dot, marker, (th, vel) in zip(rods, dots, markers, data):
            x, y = np.sin(th[k]), -np.cos(th[k])
            rod.set_data([0, x], [0, y]); dot.set_data([x], [y])
            marker.set_data([(th[k]+np.pi)%(2*np.pi)-np.pi], [vel[k]])
        text.set_text(f't={times[k]:.2f} с; длина l=1 м; трение отсутствует')
        return rods+dots+markers+[text]
    return animate(fig, update)


PLOTTERS = [plot_descent, plot_billiard, plot_chain, plot_tautochrone, plot_pendulum]
ANIMATORS = [anim_descent, anim_billiard, anim_chain, anim_tautochrone, anim_pendulum]
