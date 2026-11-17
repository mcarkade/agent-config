"""Reference example: shows every op. Not part of the final video."""
from studio import *
import numpy as np

ch = Chapter(99, 'Example: the effective potential')

say("Why can't a planet just fall straight into the Sun? Something must be holding it out. Let's find it.",
    HOOK("Why doesn't a planet fall into the Sun?", sub="Gravity pulls it inward the whole time."))

E1 = [r'E = ', r'\frac{1}{2}m\dot{r}^2', r' + \frac{1}{2}mr^2\dot{\theta}^2', r' + V(r)']
say("Start with the energy of a particle moving under a central force.",
    CLEAR(), LABEL('Energy of the particle'), G('E1', E1, 1))
say("There's kinetic energy for motion in and out, along r,", G('E1', E1, 2))
say("kinetic energy for motion around the centre,", G('E1', E1, 3))
say("and potential energy, which depends only on r.", G('E1', E1, 4))
say("The force points along r, so there's no torque, and the angular momentum l stays constant.",
    ROW(N('No torque'), N('angular momentum is conserved')),
    M(r'l = mr^2\dot{\theta} = \mathrm{constant}', id='L'))
say("So theta dot equals l over m r squared. Put that into the middle term.",
    ROW(M(r'\dot{\theta} = \frac{l}{mr^2}', id='thd')), CIRCLE('E1', terms=(2, 3)))

E2 = [r'E = ', r'\frac{1}{2}m\dot{r}^2', r' + \frac{l^2}{2mr^2}', r' + V(r)']
say("The middle term becomes l squared over two m r squared.",
    CLEAR('E1'), M(E2, id='E2'), ARROW('E1', 'E2'))
say("Now the angle has disappeared. These last two terms act together like one potential.",
    UNDER('E2', 'acts like a potential', terms=(2, 4)))
say("We call it the effective potential.",
    CLEAR(), KEY(r'V_{\mathrm{eff}}(r) = V(r) + \frac{l^2}{2mr^2}', id='VEFF'))

r = np.linspace(0.3, 4.2, 500)
AX = dict(xlim=(0, 4.3), ylim=(-1.0, 1.6), xlabel='$r$', ylabel='$V$')
say("For gravity, V is minus k over r. Let's plot both pieces.",
    FIG('plot', axes=AX),
    M(r'V_{\mathrm{eff}} = -\frac{k}{r} + \frac{l^2}{2mr^2}', id='V2'))
say("Minus k over r dives down, and the l squared term shoots up.",
    FIGADD('plot', 'g', lambda ax: ax.plot(r, -1 / r, color=BLUE, lw=2.5, ls='--')),
    FIGADD('plot', 'c', lambda ax: ax.plot(r, 0.5 / r**2, color=ORANGE, lw=2.5, ls='--')))
say("Add them, and we get a well.",
    ANIM('plot', 'w', lambda ax, u: ax.plot(r[:max(2, int(u * len(r)))], (-1 / r + 0.5 / r**2)[:max(2, int(u * len(r)))],
                                            color=EQ, lw=3.2), dur=1.5),
    N('a well: the orbit is trapped'))

say("Here's a question for you.",
    QUESTION(T('A particle moves in the potential'), M(r'V(r) = -\frac{k}{r}'),
             T('with angular momentum $l$. Find the radius of the circular orbit.'), title='circular orbit'))
say("A circular orbit sits at the bottom of the well, where the slope of V effective is zero.",
    SOLVE(), M(r'\frac{dV_{\mathrm{eff}}}{dr} = 0'))
say("That gives k over r squared minus l squared over m r cubed equals zero.",
    M(r'\frac{k}{r^2} - \frac{l^2}{mr^3} = 0'))
say("So the radius is l squared over m k.", KEY(r'r_c = \frac{l^2}{mk}'))
say("Let's check the units quickly.", M(r'\frac{l^2}{mk}: \frac{(\mathrm{kg\,m^2/s})^2}{\mathrm{kg}\cdot\mathrm{kg\,m^3/s^2}} = \mathrm{m}'))
say("Good. And here's the whole story in one picture.",
    CLEAR(), DIAGRAM('d', 'veff_kepler'), N('turning points: where E meets the curve'))
