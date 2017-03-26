# -*- coding: utf-8 -*-
# ChemTools is a collection of interpretive chemical tools for
# analyzing outputs of the quantum chemistry calculations.
#
# Copyright (C) 2014-2015 The ChemTools Development Team
#
# This file is part of ChemTools.
#
# ChemTools is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# ChemTools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --
#pylint: skip-file


from chemtools import *


def test_global_quadratic1():
    # E(N) = -9.0 + (-25.0)*N + N^2, N0=15
    model = QuadraticGlobalTool(-159.0, -153.0, -163.0, 15)
    # check parameters
    np.testing.assert_almost_equal(model.params[0], -9.0, decimal=6)
    np.testing.assert_almost_equal(model.params[1], -25.0, decimal=6)
    np.testing.assert_almost_equal(model.params[2], 1.0, decimal=6)
    np.testing.assert_almost_equal(model.n0, 15, decimal=6)
    np.testing.assert_almost_equal(model.n_max, 12.5, decimal=6)
    # check E(N)
    energy = lambda(n): -9.0 - 25.0*n + n*n
    np.testing.assert_almost_equal(model.energy(20), energy(20), decimal=6)
    np.testing.assert_almost_equal(model.energy(10), energy(10), decimal=6)
    np.testing.assert_almost_equal(model.energy(16.5), energy(16.5), decimal=6)
    # check dE(N)
    deriv = lambda(n): -25.0 + 2*n
    np.testing.assert_almost_equal(model.energy_derivative(20), deriv(20), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10), deriv(10), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(16.5), deriv(16.5), decimal=6)
    # check d2E(N)
    np.testing.assert_almost_equal(model.energy_derivative(20, 2), 2.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10, 2), 2.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(16.5, 2), 2.0, decimal=6)
    # check d^nE(N) for n > 2
    np.testing.assert_almost_equal(model.energy_derivative(20, 3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10, 4), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(16.5, 5), 0.0, decimal=6)
    # check ionization potential and electron affinity
    ip = energy(14) - energy(15)
    ea = energy(15) - energy(16)
    np.testing.assert_almost_equal(model.ionization_potential, ip, decimal=6)
    np.testing.assert_almost_equal(model.electron_affinity, ea, decimal=6)
    np.testing.assert_almost_equal(model.ip, ip, decimal=6)
    np.testing.assert_almost_equal(model.ea, ea, decimal=6)
    np.testing.assert_almost_equal(model.electronegativity, 0.5 * (ip + ea), decimal=6)
    electrophil = (-0.5 * (ip + ea))**2 / (2 * (ip - ea))
    np.testing.assert_almost_equal(model.electrophilicity, electrophil, decimal=6)
    nucleofugal = (ip - 3 * ea)**2 / (8 * (ip - ea))
    np.testing.assert_almost_equal(model.nucleofugality, nucleofugal, decimal=6)
    electrofugal = (3 * ip - ea)**2 / (8 * (ip - ea))
    np.testing.assert_almost_equal(model.electrofugality, electrofugal, decimal=6)
    # check chemical potential, chemical hardness, and related tools
    np.testing.assert_almost_equal(model.chemical_potential, -0.5 * (ip + ea), decimal=6)
    np.testing.assert_almost_equal(model.chemical_hardness, ip - ea, decimal=6)
    np.testing.assert_almost_equal(model.mu, -0.5 * (ip + ea), decimal=6)
    np.testing.assert_almost_equal(model.eta, ip - ea, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(2), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(4), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.softness, 1.0 / (ip - ea), decimal=6)
    #np.testing.assert_almost_equal(model.hyper_softness(2), 0.0, decimal=6)
    # check grand potential
    grand = lambda n: energy(n) + 0.5 * (ip + ea) * n
    np.testing.assert_almost_equal(model.grand_potential(15), grand(15), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(10), grand(10), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(20), grand(20), decimal=6)
    # check derivative of grand potential


def test_global_quadratic2():
    # E(N) = 30.0 + (-6.0)*N + 3*N^2, N0=10
    model = QuadraticGlobalTool(75.0, 102.0, 54.0, 5)
    # check parameters
    np.testing.assert_almost_equal(model.params[0], 30.0, decimal=6)
    np.testing.assert_almost_equal(model.params[1], -6.0, decimal=6)
    np.testing.assert_almost_equal(model.params[2], 3.0, decimal=6)
    np.testing.assert_almost_equal(model.n0, 5, decimal=6)
    np.testing.assert_almost_equal(model.n_max, 1, decimal=6)
    # check E(N)
    energy = lambda(n): 30.0 - 6.0*n + 3*n*n
    np.testing.assert_almost_equal(model.energy(20), energy(20), decimal=6)
    np.testing.assert_almost_equal(model.energy(10), energy(10), decimal=6)
    np.testing.assert_almost_equal(model.energy(16.5), energy(16.5), decimal=6)
    # check dE(N)
    deriv = lambda(n): -6.0 + 6*n
    np.testing.assert_almost_equal(model.energy_derivative(20), deriv(20), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10), deriv(10), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(16.5), deriv(16.5), decimal=6)
    # check d2E(N)
    np.testing.assert_almost_equal(model.energy_derivative(20, 2), 6.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10, 2), 6.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(16.5, 2), 6.0, decimal=6)
    # check d^nE(N) for n > 2
    np.testing.assert_almost_equal(model.energy_derivative(20, 3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10, 4), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(16.5, 5), 0.0, decimal=6)
    # check ionization potential and electron affinity
    ip = energy(4) - energy(5)
    ea = energy(5) - energy(6)
    np.testing.assert_almost_equal(model.ionization_potential, ip, decimal=6)
    np.testing.assert_almost_equal(model.electron_affinity, ea, decimal=6)
    np.testing.assert_almost_equal(model.ip, ip, decimal=6)
    np.testing.assert_almost_equal(model.ea, ea, decimal=6)
    np.testing.assert_almost_equal(model.electronegativity, 0.5 * (ip + ea), decimal=6)
    electrophil = (-0.5 * (ip + ea))**2 / (2 * (ip - ea))
    np.testing.assert_almost_equal(model.electrophilicity, electrophil, decimal=6)
    nucleofugal = (ip - 3 * ea)**2 / (8 * (ip - ea))
    np.testing.assert_almost_equal(model.nucleofugality, nucleofugal, decimal=6)
    electrofugal = (3 * ip - ea)**2 / (8 * (ip - ea))
    np.testing.assert_almost_equal(model.electrofugality, electrofugal, decimal=6)
    # check chemical potential, chemical hardness, and related tools
    np.testing.assert_almost_equal(model.chemical_potential, -0.5 * (ip + ea), decimal=6)
    np.testing.assert_almost_equal(model.chemical_hardness, ip - ea, decimal=6)
    np.testing.assert_almost_equal(model.mu, -0.5 * (ip + ea), decimal=6)
    np.testing.assert_almost_equal(model.eta, ip - ea, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(2), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(4), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.softness, 1.0 / (ip - ea), decimal=6)
    #np.testing.assert_almost_equal(model.hyper_softness(2), 0.0, decimal=6)
    # check grand potential
    grand = lambda n: energy(n) + 0.5 * (ip + ea) * n
    np.testing.assert_almost_equal(model.grand_potential(15), grand(15), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(10), grand(10), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(20), grand(20), decimal=6)
    # check derivative of grand potential


def test_global_quadratic3():
    # E(N) = -100 + 5*N^2, N0=5
    model = QuadraticGlobalTool(25.0, 80.0, -20.0, 5)
    # check parameters
    np.testing.assert_almost_equal(model.params[0], -100.0, decimal=6)
    np.testing.assert_almost_equal(model.params[1], 0.0, decimal=6)
    np.testing.assert_almost_equal(model.params[2], 5.0, decimal=6)
    np.testing.assert_almost_equal(model.n0, 5, decimal=6)
    np.testing.assert_almost_equal(model.n_max, 0.0, decimal=6)
    # check E(N)
    energy = lambda(n): -100.0 + 5*n*n
    np.testing.assert_almost_equal(model.energy(20), energy(20), decimal=6)
    np.testing.assert_almost_equal(model.energy(10), energy(10), decimal=6)
    np.testing.assert_almost_equal(model.energy(16.5), energy(16.5), decimal=6)
    # check dE(N)
    deriv = lambda(n): 10*n
    np.testing.assert_almost_equal(model.energy_derivative(20), deriv(20), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10), deriv(10), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(16.5), deriv(16.5), decimal=6)
    # check d2E(N)
    np.testing.assert_almost_equal(model.energy_derivative(20, 2), 10.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10, 2), 10.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(16.5, 2), 10.0, decimal=6)
    # check d^nE(N) for n > 2
    np.testing.assert_almost_equal(model.energy_derivative(20, 3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10, 4), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(16.5, 5), 0.0, decimal=6)
    # check ionization potential and electron affinity
    ip = energy(4) - energy(5)
    ea = energy(5) - energy(6)
    np.testing.assert_almost_equal(model.ionization_potential, ip, decimal=6)
    np.testing.assert_almost_equal(model.electron_affinity, ea, decimal=6)
    np.testing.assert_almost_equal(model.ip, ip, decimal=6)
    np.testing.assert_almost_equal(model.ea, ea, decimal=6)
    np.testing.assert_almost_equal(model.electronegativity, 0.5 * (ip + ea), decimal=6)
    electrophil = (-0.5 * (ip + ea))**2 / (2 * (ip - ea))
    np.testing.assert_almost_equal(model.electrophilicity, electrophil, decimal=6)
    nucleofugal = (ip - 3 * ea)**2 / (8 * (ip - ea))
    np.testing.assert_almost_equal(model.nucleofugality, nucleofugal, decimal=6)
    electrofugal = (3 * ip - ea)**2 / (8 * (ip - ea))
    np.testing.assert_almost_equal(model.electrofugality, electrofugal, decimal=6)
    # check chemical potential, chemical hardness, and related tools
    np.testing.assert_almost_equal(model.chemical_potential, -0.5 * (ip + ea), decimal=6)
    np.testing.assert_almost_equal(model.chemical_hardness, ip - ea, decimal=6)
    np.testing.assert_almost_equal(model.mu, -0.5 * (ip + ea), decimal=6)
    np.testing.assert_almost_equal(model.eta, ip - ea, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(2), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(4), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.softness, 1.0 / (ip - ea), decimal=6)
    #np.testing.assert_almost_equal(model.hyper_softness(2), 0.0, decimal=6)
    # check grand potential
    grand = lambda n: energy(n) + 0.5 * (ip + ea) * n
    np.testing.assert_almost_equal(model.grand_potential(15), grand(15), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(10), grand(10), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(20), grand(20), decimal=6)
    # check derivative of grand potential


def test_global_exponential1():
    # E(N) = 5.0 * exp(-0.1 * (N - 10)) + 3.0
    model = ExponentialGlobalTool(8.0, 7.524187090179797, 8.525854590378238, 10)
    np.testing.assert_almost_equal(model.params[0], 5.0, decimal=6)
    np.testing.assert_almost_equal(model.params[2], 3.0, decimal=6)
    np.testing.assert_almost_equal(model.params[1], 0.1, decimal=6)
    np.testing.assert_almost_equal(model.n0, 10, decimal=6)
    # check E(N)
    energy = lambda n: 5.0 * math.exp(-0.1 * (n - 10)) + 3.0
    np.testing.assert_almost_equal(model.energy(20), energy(20), decimal=6)
    np.testing.assert_almost_equal(model.energy(10), energy(10), decimal=6)
    np.testing.assert_almost_equal(model.energy(8), energy(8), decimal=6)
    np.testing.assert_almost_equal(model.energy(16.5), energy(16.5), decimal=6)
    # check dE(N)
    dE = lambda n, r: 5.0 * math.pow(-0.1, r) * math.exp(-0.1 * (n - 10))
    np.testing.assert_almost_equal(model.energy_derivative(18.1), dE(18.1, 1), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10), dE(10, 1), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(8.5), dE(8.5, 1), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(12.25), dE(12.25, 1), decimal=6)
    # # check d2E(N)
    np.testing.assert_almost_equal(model.energy_derivative(17.3, 2), dE(17.3, 2), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10, 2), dE(10, 2), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(9.1, 2), dE(9.1, 2), decimal=6)
    # check d^nE(N) for n > 2
    np.testing.assert_almost_equal(model.energy_derivative(13.7, 3), dE(13.7, 3), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10, 4), dE(10, 4), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(4.5, 5), dE(4.5, 5), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(6.5, 10), dE(6.5, 10), decimal=6)
    # check ionization potential and electron affinity
    ip = energy(9) - energy(10)
    ea = energy(10) - energy(11)
    np.testing.assert_almost_equal(model.ionization_potential, ip, decimal=6)
    np.testing.assert_almost_equal(model.electron_affinity, ea, decimal=6)
    np.testing.assert_almost_equal(model.ip, ip, decimal=6)
    np.testing.assert_almost_equal(model.ea, ea, decimal=6)
    np.testing.assert_almost_equal(model.electronegativity, -dE(10, 1), decimal=6)
    # check chemical potential, chemical hardness, and related tools
    np.testing.assert_almost_equal(model.chemical_potential, dE(10, 1), decimal=6)
    np.testing.assert_almost_equal(model.chemical_hardness, dE(10, 2), decimal=6)
    np.testing.assert_almost_equal(model.mu, dE(10, 1), decimal=6)
    np.testing.assert_almost_equal(model.eta, dE(10, 2), decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(2), dE(10, 3), decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(3), dE(10, 4), decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(4), dE(10, 5), decimal=6)
    np.testing.assert_almost_equal(model.softness, 1.0 / dE(10, 2), decimal=6)
    # check n_max and related descriptors (expected values are computed symbolically)
    np.testing.assert_equal(model.n_max, float('inf'))
    np.testing.assert_almost_equal(model.energy(model.n_max), 3.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(model.n_max), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(model.n_max, 2), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(model.n_max, 3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.electrophilicity, 5.0, decimal=6)
    np.testing.assert_almost_equal(model.nucleofugality, 4.52418709, decimal=6)
    np.testing.assert_almost_equal(model.electrofugality, 5.52585459, decimal=6)
    #np.testing.assert_almost_equal(model.hyper_softness(2), 0.0, decimal=6)
    # check grand potential
    grand = lambda n: energy(n) - dE(10, 1) * n
    np.testing.assert_almost_equal(model.grand_potential(15), grand(15), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(10), grand(10), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(20), grand(20), decimal=6)
    # check derivative of grand potential


def test_global_rational1():
    # E(N) = (0.5 - 2.2 N) / (1 + 0.7 N)
    model = RationalGlobalTool(-1.6250, -1.96774193, -1.0, 2.0)
    # check parameters
    np.testing.assert_almost_equal(model.n0, 2.0, decimal=6)
    np.testing.assert_almost_equal(model.params[0], 0.5, decimal=6)
    np.testing.assert_almost_equal(model.params[1], -2.2, decimal=6)
    np.testing.assert_almost_equal(model.params[2], 0.7, decimal=6)
    # check energy values (expected values are computed symbolically)
    np.testing.assert_almost_equal(model.energy(0), 0.5, decimal=6)
    np.testing.assert_almost_equal(model.energy(1), -1.0, decimal=6)
    np.testing.assert_almost_equal(model.energy(2), -1.6250, decimal=6)
    np.testing.assert_almost_equal(model.energy(3), -1.96774193, decimal=6)
    np.testing.assert_almost_equal(model.energy(4), -2.18421052, decimal=6)
    np.testing.assert_almost_equal(model.energy(5), -2.33333333, decimal=6)
    np.testing.assert_almost_equal(model.energy(6), -2.44230769, decimal=6)
    np.testing.assert_almost_equal(model.energy(1.5), -1.36585365, decimal=6)
    np.testing.assert_almost_equal(model.energy(0.8), -0.80769230, decimal=6)
    # check energy derivatives (expected values are computed symbolically)
    np.testing.assert_almost_equal(model.energy_derivative(0), -2.55, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(1), -0.88235294, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(2), -0.44270833, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(3), -0.26534859, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(4), -0.17659279, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(5), -0.12592592, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(6), -0.09430473, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(1.5), -0.60678167, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(0.8), -1.04783037, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(1.5, 2), 0.41438748, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(0.8, 2), 0.94036059, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(1.1, 3), -0.7638260, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(2.5, 4), 0.13346951, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(0.65, 5), -7.74347011, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(1.90, 6), 0.827697092, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(3.20, 3), -0.06803109, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(4.05, 7), -0.03231737, decimal=6)
    # check global descriptors (expected values are computed symbolically)
    np.testing.assert_almost_equal(model.ip, 0.625, decimal=6)
    np.testing.assert_almost_equal(model.ea, 0.34274193, decimal=6)
    np.testing.assert_almost_equal(model.mu, -0.44270833, decimal=6)
    np.testing.assert_almost_equal(model.eta, 0.258246527, decimal=6)
    np.testing.assert_almost_equal(model.ionization_potential, 0.625, decimal=6)
    np.testing.assert_almost_equal(model.electron_affinity, 0.34274193, decimal=6)
    np.testing.assert_almost_equal(model.chemical_potential, -0.44270833, decimal=6)
    np.testing.assert_almost_equal(model.chemical_hardness, 0.258246527, decimal=6)
    np.testing.assert_almost_equal(model.electronegativity, 0.44270833, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(2), -0.22596571, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(3), 0.263626663, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(4), -0.38445555, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(5), 0.672797214, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(6), -1.37362764, decimal=6)
    np.testing.assert_almost_equal(model.softness, 3.87226890, decimal=6)
    # check n_max and related descriptors (expected values are computed symbolically)
    np.testing.assert_equal(model.n_max, float('inf'))
    np.testing.assert_almost_equal(model.energy(model.n_max), -3.14285714, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(model.n_max), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(model.n_max, 2), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(model.n_max, 3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.electrophilicity, 1.51785714, decimal=6)
    np.testing.assert_almost_equal(model.nucleofugality, 1.17511520, decimal=6)
    np.testing.assert_almost_equal(model.electrofugality, 2.14285714, decimal=6)


def test_global_rational2():
    # E(N) = (-0.15 - 4.2 N) / (1 + 0.45 N)
    model = RationalGlobalTool(-6.99363057, -7.23428571, -6.69064748, 6.5)
    # check parameters
    np.testing.assert_almost_equal(model.n0, 6.5, decimal=6)
    np.testing.assert_almost_equal(model.params[0], -0.15, decimal=6)
    np.testing.assert_almost_equal(model.params[1], -4.2, decimal=6)
    np.testing.assert_almost_equal(model.params[2], 0.45, decimal=6)
    # check energy values (expected values are computed symbolically)
    np.testing.assert_almost_equal(model.energy(6.5), -6.99363057, decimal=6)
    np.testing.assert_almost_equal(model.energy(7.5), -7.23428571, decimal=6)
    np.testing.assert_almost_equal(model.energy(5.5), -6.69064748, decimal=6)
    np.testing.assert_almost_equal(model.energy(5.0), -6.507692307, decimal=6)
    np.testing.assert_almost_equal(model.energy(8.0), -7.336956521, decimal=6)
    # check energy derivatives (expected values are computed symbolically)
    np.testing.assert_almost_equal(model.energy_derivative(6.5), -0.26824617, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(7.5), -0.21590204, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(5.5), -0.34221831, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(4, 2), 0.16942647, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10., 3), -0.00548704, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(9.5, 4), 0.002212836, decimal=6)
    # check global descriptors (expected values are computed symbolically)
    np.testing.assert_almost_equal(model.ip, 0.30298309, decimal=6)
    np.testing.assert_almost_equal(model.ea, 0.24065514, decimal=6)
    np.testing.assert_almost_equal(model.mu, -0.26824617, decimal=6)
    np.testing.assert_almost_equal(model.eta, 0.06150867, decimal=6)
    np.testing.assert_almost_equal(model.ionization_potential, 0.30298309, decimal=6)
    np.testing.assert_almost_equal(model.electron_affinity, 0.24065514, decimal=6)
    np.testing.assert_almost_equal(model.chemical_potential, -0.26824617, decimal=6)
    np.testing.assert_almost_equal(model.chemical_hardness, 0.06150867, decimal=6)
    np.testing.assert_almost_equal(model.electronegativity, 0.26824617, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(2), -0.0211558, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(3), 0.00970204, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(4), -0.0055616, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(5), 0.00382587, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(6), -0.0030704, decimal=6)
    np.testing.assert_almost_equal(model.softness, 16.25786868, decimal=6)
    # check n_max and related descriptors (expected values are computed symbolically)
    np.testing.assert_equal(model.n_max, float('inf'))
    np.testing.assert_almost_equal(model.energy(model.n_max), -9.33333333, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(model.n_max), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(model.n_max, 2), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(model.n_max, 3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.electrophilicity, 2.33970276, decimal=6)
    np.testing.assert_almost_equal(model.nucleofugality, 2.099047619, decimal=6)
    np.testing.assert_almost_equal(model.electrofugality, 2.64268585, decimal=6)


def test_global_general_quadratic():
    # E(N) = 31.0 - 28.0 * N + 4.0 * N^2
    n, n0, a, b, c = sp.symbols('n, n0, a, b, c')
    expr = a + b * n + c * (n**2)
    model = GeneralGlobalTool(expr, 3.45, {2.1:-10.16, 2.5:-14.0, 4.3:-15.44}, n, n0)
    np.testing.assert_almost_equal(model._params[a], 31.0, decimal=6)
    np.testing.assert_almost_equal(model._params[b], -28.0, decimal=6)
    np.testing.assert_almost_equal(model._params[c], 4.0, decimal=6)
    np.testing.assert_almost_equal(model.n0, 3.45, decimal=6)
    #np.testing.assert_almost_equal(model.n_max, 12.5, decimal=6) # <--------
    # check E(N)
    energy = lambda(n): 31.0 - 28.0*n + 4.0*(n**2)
    np.testing.assert_almost_equal(model.energy(5.23), energy(5.23), decimal=6)
    np.testing.assert_almost_equal(model.energy(3.45), energy(3.45), decimal=6)
    np.testing.assert_almost_equal(model.energy(3.00), energy(3.0), decimal=6)
    # check dE(N)
    deriv = lambda(n): -28.0 + 8.0*n
    np.testing.assert_almost_equal(model.energy_derivative(6.30), deriv(6.30), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(3.45), deriv(3.45), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(1.70), deriv(1.70), decimal=6)
    # check d2E(N)
    np.testing.assert_almost_equal(model.energy_derivative(0.55, 2), 8.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(3.45, 2), 8.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(16.5, 2), 8.0, decimal=6)
    # check d^nE(N) for n > 2
    np.testing.assert_almost_equal(model.energy_derivative(9.20, 3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(3.45, 4), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(1.00, 5), 0.0, decimal=6)
    # check ionization potential and electron affinity
    ip = energy(2.45) - energy(3.45)
    ea = energy(3.45) - energy(4.45)
    np.testing.assert_almost_equal(model.ionization_potential, ip, decimal=6)
    np.testing.assert_almost_equal(model.electron_affinity, ea, decimal=6)
    np.testing.assert_almost_equal(model.ip, ip, decimal=6)
    np.testing.assert_almost_equal(model.ea, ea, decimal=6)
    np.testing.assert_almost_equal(model.electronegativity, 0.5 * (ip + ea), decimal=6)
    # electrophil = (-0.5 * (ip + ea))**2 / (2 * (ip - ea))
    # np.testing.assert_almost_equal(model.electrophilicity, electrophil, decimal=6)
    # nucleofugal = (ip - 3 * ea)**2 / (8 * (ip - ea))
    # np.testing.assert_almost_equal(model.nucleofugality, nucleofugal, decimal=6)
    # electrofugal = (3 * ip - ea)**2 / (8 * (ip - ea))
    # np.testing.assert_almost_equal(model.electrofugality, electrofugal, decimal=6)
    # check chemical potential, chemical hardness, and related tools
    np.testing.assert_almost_equal(model.chemical_potential, -0.5 * (ip + ea), decimal=6)
    np.testing.assert_almost_equal(model.chemical_hardness, ip - ea, decimal=6)
    np.testing.assert_almost_equal(model.mu, -0.5 * (ip + ea), decimal=6)
    np.testing.assert_almost_equal(model.eta, ip - ea, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(2), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(3), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(4), 0.0, decimal=6)
    np.testing.assert_almost_equal(model.softness, 1.0 / (ip - ea), decimal=6)
    #np.testing.assert_almost_equal(model.hyper_softness(2), 0.0, decimal=6)
    # check grand potential
    grand = lambda n: energy(n) + 0.5 * (ip + ea) * n
    np.testing.assert_almost_equal(model.grand_potential(15), grand(15), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(10), grand(10), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(20), grand(20), decimal=6)
    # check derivative of grand potential


def test_global_general_exponential():
    # E(N) = 6.91 * exp(-0.25 * (N - 7.0)) + 2.74
    n, n0, a, b, gamma = sp.symbols('n, n0, A, B, gamma')
    expr = a * sp.exp(- gamma * (n - 7.0)) + b
    model = GeneralGlobalTool(expr, 7.0, {7.5:8.838053596859556, 1.25:31.832186639954763, 3.6:18.906959746808596}, n, n0)
    print model._params
    np.testing.assert_almost_equal(model._params[a], 6.91, decimal=6)
    np.testing.assert_almost_equal(model._params[b], 2.74, decimal=6)
    np.testing.assert_almost_equal(model._params[gamma], 0.25, decimal=6)
    np.testing.assert_almost_equal(model.n0, 7, decimal=6)
    # np.testing.assert_almost_equal(model.n_max, 0.0, decimal=6)   # <-------------
    # check E(N)
    energy = lambda n: 6.91 * math.exp(-0.25 * (n - 7.0)) + 2.74
    np.testing.assert_almost_equal(model.energy(20), energy(20), decimal=6)
    np.testing.assert_almost_equal(model.energy(10), energy(10), decimal=6)
    np.testing.assert_almost_equal(model.energy(8), energy(8), decimal=6)
    np.testing.assert_almost_equal(model.energy(16.5), energy(16.5), decimal=6)
    # check dE(N)
    dE = lambda n, r: 6.91 * math.pow(-0.25, r) * math.exp(-0.25 * (n - 7))
    np.testing.assert_almost_equal(model.energy_derivative(18.1), dE(18.1, 1), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10), dE(10, 1), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(8.5), dE(8.5, 1), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(12.25), dE(12.25, 1), decimal=6)
    # # check d2E(N)
    np.testing.assert_almost_equal(model.energy_derivative(17.3, 2), dE(17.3, 2), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10, 2), dE(10, 2), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(9.1, 2), dE(9.1, 2), decimal=6)
    # check d^nE(N) for n > 2
    np.testing.assert_almost_equal(model.energy_derivative(13.7, 3), dE(13.7, 3), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(10, 4), dE(10, 4), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(4.5, 5), dE(4.5, 5), decimal=6)
    np.testing.assert_almost_equal(model.energy_derivative(6.5, 10), dE(6.5, 10), decimal=6)
    # check ionization potential and electron affinity
    ip = energy(6) - energy(7)
    ea = energy(7) - energy(8)
    np.testing.assert_almost_equal(model.ionization_potential, ip, decimal=6)
    np.testing.assert_almost_equal(model.electron_affinity, ea, decimal=6)
    np.testing.assert_almost_equal(model.ip, ip, decimal=6)
    np.testing.assert_almost_equal(model.ea, ea, decimal=6)
    np.testing.assert_almost_equal(model.electronegativity, -dE(7, 1), decimal=6)
    # electrophil = (-0.5 * (ip + ea))**2 / (2 * (ip - ea))
    # np.testing.assert_almost_equal(model.electrophilicity, electrophil, decimal=6)
    # nucleofugal = (ip - 3 * ea)**2 / (8 * (ip - ea))
    # np.testing.assert_almost_equal(model.nucleofugality, nucleofugal, decimal=6)
    # electrofugal = (3 * ip - ea)**2 / (8 * (ip - ea))
    # np.testing.assert_almost_equal(model.electrofugality, electrofugal, decimal=6)
    # check chemical potential, chemical hardness, and related tools
    np.testing.assert_almost_equal(model.chemical_potential, dE(7, 1), decimal=6)
    np.testing.assert_almost_equal(model.chemical_hardness, dE(7, 2), decimal=6)
    np.testing.assert_almost_equal(model.mu, dE(7, 1), decimal=6)
    np.testing.assert_almost_equal(model.eta, dE(7, 2), decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(2), dE(7, 3), decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(3), dE(7, 4), decimal=6)
    np.testing.assert_almost_equal(model.hyper_hardness(4), dE(7, 5), decimal=6)
    np.testing.assert_almost_equal(model.softness, 1.0 / dE(7, 2), decimal=6)
    #np.testing.assert_almost_equal(model.hyper_softness(2), 0.0, decimal=6)
    # check grand potential
    grand = lambda n: energy(n) - dE(7, 1) * n
    np.testing.assert_almost_equal(model.grand_potential(15), grand(15), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(10), grand(10), decimal=6)
    np.testing.assert_almost_equal(model.grand_potential(20), grand(20), decimal=6)
    # check derivative of grand potential


def test_global_general_rational():
    pass


def test_global_general_morse():
    # # E(N) = 4.01 * exp(-0.17 * (N - 17.0) + 0.32) + 6.95
    # n, n0, a, b, gamma, delta = sp.symbols('n, n0, A, B, gamma, delta')
    # expr = a * sp.exp(- gamma * (n - 4.0) + delta) + b
    # #energies = {1.0: 16.146208148459372, 4.0:12.472282334987188, 5.9:10.947988026968526, 7.7:9.894064887805316}
    # energies = {0.5:98.21717932504218, 4.2:55.606783873132294, 5.9:43.39452499661585, 7.7:33.787260559941295}
    # model = GeneralGlobalTool(expr, 17.0, energies, n, n0)
    # print model._params
    # np.testing.assert_almost_equal(model._params[a], 4.01, decimal=6)
    # np.testing.assert_almost_equal(model._params[b], 6.95, decimal=6)
    # np.testing.assert_almost_equal(model._params[gamma], 0.17, decimal=6)
    # np.testing.assert_almost_equal(model._params[delta], 0.32, decimal=6)
    # np.testing.assert_almost_equal(model.n0, 7, decimal=6)
    # assert 5 == 6
    pass
