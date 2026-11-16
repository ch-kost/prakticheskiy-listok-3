"""Численные проверки математических свойств пяти моделей."""
import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.special import ellipk
from models import G, descent, billiard, torus, chain_forces, pendulum, exact_pendulum


def run_checks():
    result = {}
    t = np.linspace(0, 2, 400)
    for v, u0 in [(.7, 1.5), (1, 1), (1.4, .6)]:
        x, y, u = descent(t, v, u0)
        energy = .5*(u*u+v*v)+G*y
        assert np.ptp(energy) < 1e-11
        y_from_x = 3+u0*u0/(2*G)-(u0**3+3*G*v*x)**(2/3)/(2*G)
        assert np.max(np.abs(y-y_from_x)) < 1e-12
        assert np.allclose(np.diff(y)/np.diff(t), -v)
    result['3.1: энергия, явная кривая, постоянство vy'] = 'OK'
    t = np.linspace(0, 40, 500)
    for rho in [1., np.sqrt(2)]:
        x, y, u, v = billiard(t, rho)
        assert np.all((x >= 0)&(x <= 3)&(y >= 0)&(y <= 2))
        assert np.allclose(torus(u, v), torus(u+6, v+4))
        h = 1e-6
        xx, yy, _, _ = billiard(t+h, rho)
        regular = (np.minimum(x, 3-x)>1e-4)&(np.minimum(y, 2-y)>1e-4)
        speed2 = ((xx-x)/h)**2+((yy-y)/h)**2
        assert np.allclose(speed2[regular], 1+(2*rho/3)**2, rtol=1e-7)
    assert np.allclose(billiard(t, 1.)[:2], billiard(t+6, 1.)[:2])
    result['3.2: границы, скорость, период T=6, тор'] = 'OK'
    for a in [.7, 1.2, 2.4]:
        xx = np.linspace(-1.5, 1.5, 100)
        assert np.allclose(np.cosh(xx/a)/a, np.sqrt(1+np.sinh(xx/a)**2)/a)
        for mu in [.6, 1, 1.7]:
            assert np.max(np.abs(chain_forces(a, mu).sum(axis=0))) < 1e-12
    result['3.3: ОДУ цепной линии, баланс сил'] = 'OK'
    expected = np.pi/np.sqrt(G)
    arrivals = []
    for height in [.05, .4, 1.8]:
        value = quad(lambda y: np.sqrt(2/y)/np.sqrt(2*G*(height-y)), 0, height,
                     epsabs=1e-10)[0]
        assert abs(value-expected) < 1e-8
    for theta0 in [.6, 1.4, 2.5]:
        def arrival(_, state): return state[0]
        arrival.direction, arrival.terminal = -1, True
        solution = solve_ivp(lambda _, z: [z[1], -G/4*z[0]], (0, 2*expected),
                             [4*np.sin(theta0/2), 0], events=arrival,
                             rtol=1e-11, atol=1e-13, method='DOP853')
        arrivals.append(float(solution.t_events[0][0]))
    assert np.max(np.abs(np.array(arrivals)-expected)) < 1e-9
    result['3.4: интеграл Абеля и времена прибытия'] = arrivals
    t = np.linspace(0, 8, 1600)
    errors, energy_errors = [], []
    for angle, velocity in [(.15, 0), (2.6, 0), (0, 2.4*np.sqrt(G))]:
        th, vel = pendulum(t, angle, velocity)
        energy = vel*vel/2+G*(1-np.cos(th))
        energy_errors.append(float(np.ptp(energy)/energy[0]))
        assert energy_errors[-1] < 1e-8
        if velocity == 0:
            errors.append(float(np.max(np.abs(th-exact_pendulum(t, angle)))))
            assert errors[-1] < 1e-8
    result['3.5: ошибка точного решения'] = max(errors)
    result['3.5: относительный дрейф энергии'] = max(energy_errors)
    assert 4/np.sqrt(G)*ellipk(np.sin(.01/2)**2) > 2*np.pi/np.sqrt(G)
    return result


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    for label, value in run_checks().items(): print(label, ':', value)
