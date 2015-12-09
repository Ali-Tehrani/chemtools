#!/usr/bin/env python
'''Global Conceptual Density Functional Theory (DFT) Reactivity Tools.'''


import math


class QuadraticGlobalTool(object):
    '''
    Class of Global Conceptual DFT Reactivity Descriptors based on the Quadratic Energy Model.
    '''
    def __init__(self, ip, ea):
        '''
        Parameters
        ----------
        ip : float
            The ionization potential.
        ea : float
            The electron affinity.
        '''
        self._ip = ip
        self._ea = ea

    @property
    def ip(self):
        '''Ionization Potential (IP).'''
        return self._ip

    @property
    def ionization_potential(self):
        '''Ionization Potential (IP).'''
        return self._ip

    @property
    def electron_affinity(self):
        '''Electron Affinity (EA).'''
        return self._ea

    @property
    def ea(self):
        '''Electron Affinity (EA).'''
        return self._ea

    @property
    def mu(self):
        '''
        Chemical potential defined as the first derivative of quadratic energy model w.r.t.
        the number of electrons at fixed external potential.
        $\mu  = {\left( {\frac{{\partial E}}{{\partial N}}} \right)_{v(r)}} =  - \frac{{I + A}}{2}$
        '''
        return -0.5 * (self._ip + self._ea)

    @property
    def chemical_potential(self):
        '''
        Chemical potential defined as the first derivative of the quadratic energy model w.r.t.
        the number of electrons at fixed external potential.
        $\mu  = {\left( {\frac{{\partial E}}{{\partial N}}} \right)_{v(r)}} =  - \frac{{I + A}}{2}$
        '''
        return self.mu

    @property
    def eta(self):
        '''
        Chemical hardness defined as the second derivative of the quadratic energy model w.r.t.
        the number of electrons at fixed external potential.
        $\mu  = {\left( {\frac{{{\partial ^2}E}}{{\partial {N^2}}}} \right)_{v(r)}} = I - A$
        '''
        return self._ip - self._ea

    @property
    def chemical_hardness(self):
        '''
        Chemical hardness defined as the second derivative of the quadratic energy model w.r.t.
        the number of electrons at fixed external potential.
        $\mu  = {\left( {\frac{{{\partial ^2}E}}{{\partial {N^2}}}} \right)_{v(r)}} = I - A$
        '''
        return self.eta

    @property
    def softness(self):
        '''Chemical softness.'''
        value = 1.0 / self.eta
        return value

    @property
    def electronegativity(self):
        '''Mulliken Electronegativity.'''
        value = -1 * self.mu
        return value

    @property
    def electrophilicity(self):
        '''Electrophilicity.'''
        value = math.pow(self.mu, 2) / (2 * self.eta)
        return value

    @property
    def n_max(self):
        '''N_max value.'''
        value = - self.mu / self.eta
        return value

    @property
    def nucleofugality(self):
        '''Nucleofugality.'''
        value = math.pow(self._ip - 3 * self._ea, 2)
        value /= (8 * (self._ip - self._ea))
        return value

    @property
    def electrofugality(self):
        '''Electrofugality.'''
        value = math.pow(3 * self._ip - self._ea, 2)
        value /= (8 * (self._ip - self._ea))
        return value
