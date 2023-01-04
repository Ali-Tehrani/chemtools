# -*- coding: utf-8 -*-
# ChemTools is a collection of interpretive chemical tools for
# analyzing outputs of the quantum chemistry calculations.
#
# Copyright (C) 2016-2019 The ChemTools Development Team
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
import numpy as np

from scipy.integrate import solve_ivp
from scipy.interpolate import LSQSphereBivariateSpline, SmoothSphereBivariateSpline
from scipy.optimize import root_scalar
from scipy.spatial import ConvexHull, Voronoi
from scipy.spatial.distance import cdist

from scipy.sparse import lil_matrix

from grid.atomgrid import AtomGrid
from grid.cubic import UniformGrid, _HyperRectangleGrid
from grid.lebedev import AngularGrid
from grid.utils import convert_cart_to_sph

import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits import mplot3d




def normalized_gradient(pt, grad_func):
    grad = grad_func(np.array([pt]))[0].T
    return grad / np.linalg.norm(grad)


def _project_pt_on_line(pt, ray_pt1, ray_pt2):
    r"""Project point onto a line defined by maxima, point on sphere and radial points."""
    ap = pt - ray_pt1
    ab = ray_pt2 - ray_pt1
    return ray_pt1 + np.dot(ap, ab) / np.dot(ab, ab) * ab


class SurfaceQTAIM():
    def __init__(self, r_func, rad_grids, angular_degs, maximas, oas, ias, basins_ias,
                 refined_ang=None):
        self._r_func = r_func
        self._maximas = maximas
        self._rad_grids = rad_grids
        self._angular_degs = angular_degs
        self._oas = oas
        self._ias = ias
        self._basins_ias = basins_ias
        self._refined_ang = refined_ang

    @property
    def r_func(self):
        # List[M, np.ndarray(N_i,)] ::math:`r_j(\theta_i, \phi_i)` for each M basins and N_i angular points.
        return self._r_func

    @property
    def oas(self):
        # List[List[int]] : First list is over basins, second over indices of points of outeratomic surface.
        return self._oas

    @property
    def ias(self):
        # List[List[int]] : First list is over basins, second over indices of points of interatomic surface.
        return self._ias

    @property
    def maximas(self):
        # ndarray(M, 3) : The maxima of each basin.
        return self._maximas

    @property
    def angular_degs(self):
        # int or List[int] : List of angular degrees over each basin.
        return self._angular_degs

    @property
    def rad_grids(self):
        # List[OneDGrids] : List of M OneDGrids for integrating over radial component in [0, \inty).
        return self._rad_grids

    @property
    def basins_ias(self):
        return self._basins_ias

    @property
    def refined_ang(self):
        # List[M, np.ndarray(N_i, 2)] : Additional Angular points to append to the angular grid
        return self._refined_ang

    def generate_angular_grid_of_basin(self, i_basin):
        # Note this doesn't include the extra angular points generated by refinement.
        deg = self.angular_degs
        deg = deg[i_basin] if isinstance(deg, list) else deg
        return AngularGrid(degree=deg)

    def generate_angular_pts_of_basin(self, i_basin):
        angular_grid = self.generate_angular_grid_of_basin(i_basin)
        points = angular_grid.points
        if self.refined_ang is not None:
            points = np.vstack((points, self.refined_ang[i_basin]))
        return points

    def get_atom_grid_over_basin(self, i_basin):
        # integrate over a basin.
        deg = self.angular_degs
        deg = deg[i_basin] if isinstance(deg, list) else deg
        atom_grid = AtomGrid(self.rad_grids[i_basin], degrees=[deg], center=self.maximas[i_basin])

        # Go through each spherical point and get the r(theta_i, phi_i) limit
        for i_sph in range(atom_grid.get_shell_grid(0).size):
            r_limit = self.r_func[i_basin, i_sph]
            # Go through each radial point and see if it is larger than the limit.
            for i_rad in range(atom_grid.rgrid.size):
                if atom_grid.rgrid.points[i_rad] > r_limit:
                    # Find where (r_{ij}, theta_i, phi_i) is and set the weights to zero.
                    i_start, i_final = atom_grid.indices[i_rad], atom_grid.indices[i_rad + 1]
                    atom_grid.weights[i_start + i_sph] = 0.0
        # atom_grid.weights[inequality] = 0.0
        return atom_grid

    def generate_pts_on_surface(self, i_basin):
        sph_pts = self.generate_angular_pts_of_basin(i_basin)
        return self.maximas[i_basin] + self.r_func[i_basin][:, None] * sph_pts

    def get_ias_pts_of_basin(self, i_basin):
        ias = self.ias[i_basin]
        sph_pts = self.generate_angular_pts_of_basin(i_basin)
        return self.maximas[i_basin] + self.r_func[i_basin][ias, None] * sph_pts[ias]

    def get_oas_pts_of_basin(self, i_basin):
        oas = self.oas[i_basin]
        sph_pts = self.generate_angular_pts_of_basin(i_basin)
        return self.maximas[i_basin] + self.r_func[i_basin][oas, None] * sph_pts[oas]

    def interpolate_radial_func(self, method="smooth", ias=False, oas=False):
        # if method not in ["smooth", ]
        if ias and oas:
           raise ValueError(f"Both {ias} and {oas} cannot be true.")
        if ias:
            #TODO
            pass
        raise NotImplementedError(f"Not implemented yet.")


def construct_points_between_ias_and_oas(
    ias: list, oas: int, angular_pts: np.ndarray, r_func_max: np.ndarray, maxima: np.ndarray
):
    r"""
    Construct points between the inner atomic surface and outer atomic surface.

    This is done by constructed a convex hull between IAS and OAS, seperetely.
    Each point on the IAS, the two closest points are found on the OAS, then
    a triangle is constructed.  Seven points are constructed within this triangle
    and the Cartesian coordinates of the sphere centered at the maxima is solved
    for each of these seven points.

    Parameters
    -----------
    ias : List[int]
        List of integers of `angular_pts` that are part of the inner atomic surface (IAS).
    oas : List[int]
        List of integers of `angular_pts` that are part of the outer atomic surface (OAS).
    angular_pts : np.ndarray
        Angular Points around the maxima for which rays are propgated from.
    r_func_max : np.ndarray
        The radial component for each angular point in `angular_pts` that either gives
        the radial value that intersects the OAS or the IAS.
    maxima : np.ndarray
        Maxima of the basin.

    Returns
    -------
    ndarray(K * 7, 3)
        Cartesian coordinates of :math:`K` points on the sphere centered at `maxima` such that
        they correspond to the seven points constructed above, where :math:`K` is the number
        of points on the IAS of `maxima`.

    """
    # Take a convex hull of both IAS and OAS seperately.
    ias_pts = maxima + r_func_max[ias, None] * angular_pts[ias, :]
    oas_pts = maxima + r_func_max[oas, None] * angular_pts[oas, :]
    ias_hull = ConvexHull(ias_pts)
    oas_hull = ConvexHull(oas_pts)
    ias_bnd = ias_hull.points[ias_hull.vertices]
    oas_bnd = oas_hull.points[oas_hull.vertices]

    # Compute the distance matrix
    dist_mat = cdist(ias_bnd, oas_bnd)
    # for each point in say ias take the closest two points in oas.
    new_ang_pts = np.zeros((len(ias_bnd) * 7, 3))  # 7 points per ias boundary are added.
    for i_ias, pt_ias in enumerate(ias_bnd):
        two_indices = dist_mat[i_ias].argsort()[:2]
        pt1, pt2 = oas_bnd[two_indices[0]], oas_bnd[two_indices[1]]

        # Take the center and midpoint between each line of the triangle (pt_ias, pt1, pt2)
        midpoint = (pt1 + pt2 + pt_ias) / 3.0
        line_pt1 = (pt1 + pt_ias) / 2.0
        line_pt2 = (pt2 + pt_ias) / 2.0
        line_pt3 = (pt1 + pt2) / 2.0

        # The triangle with the center can be split into three polygons, take the center of each.
        poly_pt1 = (midpoint + line_pt1 + line_pt2 + pt_ias) / 4.0
        poly_pt2 = (midpoint + line_pt1 + line_pt3 + pt1) / 4.0
        poly_pt3 = (midpoint + line_pt2 + line_pt3 + pt2) / 4.0

        new_pts = np.array([midpoint, line_pt1, line_pt2, line_pt3, poly_pt1, poly_pt2, poly_pt3])
        # Solve for the Cartesian angular coordinates of these 7 points by solving
        #  r = m + t direction, where m is the maxima, direction has norm one, r is each of
        #  these points
        direction = new_pts - maxima
        t = np.linalg.norm(direction, axis=1)
        direction = direction / t[:, None]
        new_ang_pts[i_ias * 7:(i_ias + 1) * 7] = direction
    return new_ang_pts


def gradient_path(pt, grad_func, t_span=(0, 1000), method="LSODA", max_step=100, t_inc=200,
                  max_tries=10, first_step=1e-3, beta_sphere_maxima=-np.inf, maxima=None):
    # TODO: If the density value is low, gradient low and trying ODE did not move much, then
    #  an option is to turn max_step tp np.inf and change t_span to 10,000.
    is_converged = False
    y0 = pt.copy()
    numb_times = 0
    while not is_converged and numb_times < max_tries:
        sol = solve_ivp(
            lambda t, x: grad_func(np.array([x]))[0].T,
            y0=y0,
            t_span=t_span,
            method=method,
            max_step=max_step,
            first_step=first_step,
        )
        # print(sol)
        assert sol["success"], "ODE was not successful."
        convergence = np.abs(sol["y"][:, -2] - sol["y"][:, -1])
        if np.all(convergence < 0.01):
            return sol["y"][:, -1]
        elif beta_sphere_maxima != -np.inf:
            # If the point converged to the beta sphere of the maxima, then we stop.
            radial = np.linalg.norm(sol["y"][:, -1] - maxima)
            if radial < beta_sphere_maxima:
                print("Close to beta sphere.")
                return sol["y"][:, -1]
        else:
            # This isn't good for finding isosurfaces, because it would keep on going longer than expected.
            # Also I can do the beta sphere trick here for convegence rather than going all the towards.
            print(sol["y"][:, -1], t_span)
            t_span = (t_span[1], t_span[1] + t_inc)
            y0 = sol["y"][:, -1]
            numb_times += 1
    if numb_times == max_tries:
        raise RuntimeError(f"No convergence in gradient path pt {pt},"
                           f" solution {sol['y'][:, -1]}, t_span {t_span}")


def solve_for_isosurface_pt(index_iso, rad_pts, maxima, cart_sphere_pt, density_func,
                            iso_val, iso_err):
    # Given a series of points based on a maxima defined by angles `cart_sphere_pt` with
    #  radial pts `rad_pts`.   The `index_iso` tells us where on these points to construct another
    #  refined grid from finding l_bnd and u_bnd.  This assumes the lower bound and upper bound
    #  contains the isosurface point.  This point is solved using a root-finding algorithm to
    #  solve for the root of the density function.
    print(rad_pts, index_iso)
    l_bnd = rad_pts[index_iso - 1] if index_iso >= 0 else rad_pts[index_iso] / 2.0
    u_bnd = rad_pts[index_iso + 1] if index_iso + 1 < len(rad_pts) else rad_pts[index_iso] * 2.0
    dens_l_bnd = density_func(np.array([maxima + l_bnd * cart_sphere_pt]))
    dens_u_bnd = density_func(np.array([maxima + u_bnd * cart_sphere_pt]))
    if iso_val < dens_u_bnd or dens_l_bnd < iso_val:
        raise ValueError(f"Radial grid {l_bnd, u_bnd} did not bound {dens_l_bnd, dens_u_bnd} "
                         f"the isosurface value {iso_val}. Use larger radial grid.")

    # Use Root-finding algorithm to find the isosurface point.
    root_func = lambda t: density_func(np.array([maxima + t * cart_sphere_pt]))[0] - iso_val
    from scipy.optimize import root_scalar
    sol = root_scalar(root_func, method="toms748", bracket=(l_bnd, u_bnd), xtol=iso_err)
    print(sol)
    assert sol.converged, f"Root function did not converge {sol}."
    bnd_pt = maxima + sol.root * cart_sphere_pt
    print(bnd_pt, density_func(np.array([bnd_pt])))
    return bnd_pt


def solve_for_basin_bnd_pt(
    dens_cutoff, maxima, radial, cart_sphere_pt, density_func, grad_func, other_maximas, bnd_err,
    iso_val, beta_sphere_maxima, beta_sphere_others
):
    # Construct the ray and compute its density values based on a maxima defined by angles
    #  `cart_sphere_pt` with radial pts `rad_pts`.    It goes through each point on the ray
    #   if the ray density value is greater than dens_cutoff, then it is likely this ray
    #   tends towards infinity and has no basin boundary.  If density value is larger, then
    #   it solves for the gradient path via solving gradient ode.  If this ode solution,
    #   is close to other basins, then we found when it switched basins.  Then we take
    #  the two points where it switches basin and compute the distance, if this distance
    #  is less than `bnd_err`, then we take the midpoint to be the boundary point on the ray
    #  that intersects the ias.  If not, then we construct a new ray with different l_bnd
    #  and u_bnd and reduce the step-size further and repeat this process.
    rad_pts = radial.copy()
    ss_ray = np.mean(np.diff(rad_pts))   # Stay with a coarse ray then refine further.
    index_iso = None  # Needed to refine if the ray tends towards infinity.
    bnd_pt = None  # Boundary or Isosurface Point
    is_ray_to_inf = False  # Does this ray instead go towards infinity

    # TODO: Consider increase upper bound if it fails.
    # TODO: doing the last point first to see if it is a ray that goes to infinity. THe problem
    #   is if it isn't a ray that goes to infinity, then you need to do all of them anyways.
    #   this is going to be heavy refactor for this function.
    found_watershed_on_ray = False
    basin_id = None
    while not found_watershed_on_ray:
        ray = maxima + rad_pts[:, None] * cart_sphere_pt
        ray_density = density_func(ray)
        print("Start of Ray ", ray[0], " Cartesian pt of Sphere ", cart_sphere_pt, "Final Ray Pt: ",
              ray[-1])

        # Compute the boundary point
        for i_ray, pt in enumerate(ray):
            if ray_density[i_ray] > dens_cutoff:
                # Multiply the integration span by the radial component so it scales.
                # Make the first step proportional to the step-size of the ray
                y_val = gradient_path(pt, grad_func,
                                      t_span=(0, max(1000 * rad_pts[i_ray], 75)),
                                      max_step=50,
                                      beta_sphere_maxima=beta_sphere_maxima,
                                      maxima=maxima)#, first_step=ss_ray / 10)

                print("Pt ", pt, "Y ", y_val, "Maxima ", maxima)
                # If the next point is closer to other maximas or in beta spheres
                dist_maxima = np.linalg.norm(y_val - other_maximas, axis=1)
                if np.any(dist_maxima < 1e-1) or np.any(dist_maxima < beta_sphere_others):
                    print("Close to other maxima")
                    # If dist between the basin switch is less than boundary err
                    dist = np.linalg.norm(ray[i_ray] - ray[i_ray - 1])
                    if dist < bnd_err:
                        # Take the midpoint to be the boundary point.
                        found_watershed_on_ray = True
                        bnd_pt = (ray[i_ray] + ray[i_ray - 1]) / 2.0
                        basin_id = np.where(dist_maxima < 1e-1)[0][0] + 1  # basins starts at 1
                        print("Found the Watershed point ", bnd_pt, basin_id)
                    else:
                        # Refine Grid Further
                        l_bnd = np.linalg.norm(ray[i_ray - 1] - maxima) if i_ray != 0 else 1e-3
                        u_bnd = np.linalg.norm(ray[i_ray] - maxima)
                        ss_ray /= 10.0
                        rad_pts = np.arange(l_bnd, u_bnd + ss_ray, ss_ray)
                        print("Refine the ray further with l_bnd, u_bnd, ss: ", l_bnd, u_bnd,
                              ss_ray)
                    break  # break out of this ray and either quit or do refined ray.
            else:
                # The density values became less than the isosurface cut-off
                print("Stop: Density value is less than isosurface cut-off.")
                is_ray_to_inf = True
                index_iso = i_ray
                break  # break out of ray loop
            is_ray_to_inf = True if i_ray == len(ray) - 1 else is_ray_to_inf

        if is_ray_to_inf:
            index_iso = np.argsort(np.abs(ray_density - iso_val))[0]
            print("Ray to infinity with index ", index_iso)
            break
    return bnd_pt, is_ray_to_inf, index_iso, found_watershed_on_ray, basin_id


def _optimize_centers(centers, grad_func):
    maximas = np.array(
        [gradient_path(x, grad_func, t_span=(0, 10), method="Radau",
                       first_step=1e-9, max_step=1e-2) for x in centers],
        dtype=np.float64
    )
    print("New maximas: \n ", maximas)
    # Check duplicates
    distance = cdist(maximas, maximas)
    distance[np.diag_indices(len(maximas))] = 1.0  # Set diagonal elements to one
    if np.any(distance < 1e-8):
        raise RuntimeError(f"Optimized maximas contains duplicates: \n {maximas}.")
    return maximas


def qtaim_surface(rgrids, angular, centers, density_func, grad_func, iso_val=0.001,
                  dens_cutoff=1e-5, bnd_err=1e-4, iso_err=1e-6,
                  beta_sphere=None, optimize_centers=True, refine=False):
    r"""
    Find the outer atomic and inner atomic surface based on QTAIM.

    For each maxima, a sphere is determined based on `angular` and a ray is propogated
    based on the radial grid `rgrids`.  The ray is then determines to either
    go to infinity and cross the isosurface of the electron density or the ray
    intersects the inner-atomic surface of another basin.  This is determined for
    each point on the sphere.

    Parameters
    ----------
    rgrids: list[OneDGrid]
        List of one dimensional grids for each centers.
    angular: List[int] or ndarray(N, 3)
        Either integer specifying the degree to construct angular/Lebedev grid around each maxima
        or array of points on the sphere in Cartesian coordinates.
    centers: ndarray(M,3)
        List of local maximas of the density.
    density_func: Callable(ndarray(N,3) ->  ndarray(N,))
        The density function.
    grad_func: Callable(ndarray(N,3) -> ndarray(N,3))
        The gradient of the density function.
    iso_val: float
        The isosurface value of the outer atomic surface.
    dens_cutoff: float
        Points on the ray whose density is less than this cutoff are ignored.
    bnd_err: float
        This determines the accuracy of points on the inner atomic surface (IAS) by controlling
        the step-size of the ray that cross the IAS.
    iso_err: float
        The error associated to points on the OAS and how close they are to the isosurface value.
    beta_sphere : list[float]
        List of size `M` of radius of the sphere centered at each maxima. It avoids backtracing
        of points within the circle. If None is provided, then it doesn't use beta sphere
        for that maxima.
    optimize_centers: bool
        If true, then it will optimize the centers/maximas to get the exact local maximas.
    refine : (bool, int)
        If true, then additional points between the IAS and OAS are constructed, added and
        solved for whether it is on the IAS or OAS.

    Returns
    -------
    SurfaceQTAIM
        Class that contains the inner-atomic surface, outer-atomic surface for each maxima.

    Notes
    -----
    - It is possible for a Ray to intersect the zero-flux surface but this algorihtm will
        classify it as a ray to infinity because the points on the other side of the basin have
        density values so small that the ode doesn't converge to the maxima of the other basin.
        In this scenario it might be worthwhile to have a denser radial grid with less points
        away from infinity or have a smaller density cut-off.  Alternative for the developer,
        is to implement highly accurate ode solver at the expense of computation time.

    """
    if not isinstance(refine, (bool, int)):
        raise TypeError(f"Refine {type(refine)} should be either boolean or integer.")
    if dens_cutoff > iso_val:
        raise ValueError(f"Density cutoff {dens_cutoff} is greater than isosurface val {iso_val}.")
    if beta_sphere is not None and len(centers) != len(beta_sphere):
        raise ValueError(
            f"Beta sphere length {len(beta_sphere)} should match the"
            f" number of centers {len(centers)}"
        )

    maximas = centers
    if optimize_centers:
        # Using ODE solver to refine the maximas further.
        maximas = _optimize_centers(maximas, grad_func)

    numb_maximas = len(maximas)
    angular_pts = AngularGrid(degree=angular).points if isinstance(angular, int) else angular
    r, thetas, phis = convert_cart_to_sph(angular_pts).T
    numb_ang_pts = len(thetas)

    r_func = [np.zeros((numb_ang_pts,), dtype=np.float64) for _ in range(numb_maximas)]
    oas = [[] for _ in range(numb_maximas)]  # outer atomic surface
    ias = [[] for _ in range(numb_maximas)]  # inner atomic surface.
    basin_ias = [[] for _ in range(numb_maximas)]  # basin ids for inner atomic surface.
    refined_ang = [] if refine else None
    maxima_to_do = range(0, numb_maximas) if type(refine) == type(True) else [refine]  # for refinement
    for i_maxima, maxima in enumerate(maximas):
        # Maximas aren't usually large, so doing this is okay. Quick fix to use refinement without
        #  re-writing this function into seperate functions.
        if i_maxima in maxima_to_do:
            print("Start: Maxima ", maxima)
            other_maximas = np.delete(maximas, i_maxima, axis=0)
            other_beta_sph = -np.inf  # Infinity so that the if-statement holds true
            beta_sph_max = -np.inf
            if beta_sphere is not None:
                beta_sph_max = beta_sphere[i_maxima]
                other_beta_sph = [beta_sphere[i] for i in range(0, numb_maximas) if i != i_maxima]

            for i_ang in range(0, numb_ang_pts):  # Go through each point of the sphere
                print("I_ang ", i_ang)
                cart_sphere_pt, theta, phi = angular_pts[i_ang], thetas[i_ang], phis[i_ang]

                # Do backtracing on the ray
                radial = rgrids.points
                radial = radial if beta_sphere is None else radial[radial > beta_sphere[i_maxima]]

                bnd_pt, is_ray_to_inf, i_iso, found_watershed_on_ray, basin_id = solve_for_basin_bnd_pt(
                    dens_cutoff,maxima, radial, cart_sphere_pt, density_func, grad_func,
                    other_maximas, bnd_err, iso_val, beta_sph_max, other_beta_sph
                )
                # If the ray tends towards infinity instead, solve for the isosurface value.
                if is_ray_to_inf:
                    bnd_pt = solve_for_isosurface_pt(
                        i_iso, radial, maxima, cart_sphere_pt, density_func, iso_val,
                        iso_err
                    )

                r_func[i_maxima][i_ang] = np.linalg.norm(bnd_pt - maxima)
                if is_ray_to_inf:
                    oas[i_maxima].append(i_ang)
                elif found_watershed_on_ray:
                    ias[i_maxima].append(i_ang)
                    basin_ias[i_maxima].append(basin_id)

                print("")

            if type(refine) == type(True) and refine:  # refine can be integer, so this ignores it.
                # Take convex hull between ias and oas and construct additional points in that region.
                #  `new_pts` is concatenated to angular grids and is in cartesian coordinates.
                print("IAS ", ias[i_maxima])
                print("OAS", oas[i_maxima])
                new_pts = construct_points_between_ias_and_oas(
                    ias[i_maxima], oas[i_maxima], angular_pts, r_func[i_maxima], maxima
                )
                print("new pts ", new_pts, np.linalg.norm(new_pts, axis=1))
                # Re-do this qtaim algortihm only on this center
                refined_qtaim = qtaim_surface(rgrids, new_pts, maximas, density_func,
                                              grad_func, iso_val, dens_cutoff,
                                              bnd_err, iso_err, beta_sphere=beta_sphere,
                                              optimize_centers=False, refine=i_maxima)
                print("Refined", refined_qtaim.ias, refined_qtaim.oas)
                # Update this basin's result from the refined, + numb_ang_pts: corrects indices
                ias[i_maxima] += [x + numb_ang_pts for x in refined_qtaim.ias[i_maxima]]
                oas[i_maxima] += [x + numb_ang_pts for x in refined_qtaim.oas[i_maxima]]
                basin_ias[i_maxima] += refined_qtaim.basins_ias[i_maxima]
                refined_ang.append(new_pts)
                print(refined_qtaim.r_func, r_func[i_maxima].shape)
                r_func[i_maxima] = np.hstack((r_func[i_maxima], refined_qtaim.r_func[i_maxima]))
                # input("Why")

    print("\n")
    return SurfaceQTAIM(r_func, [rgrids], angular, maximas, oas, ias, basin_ias, refined_ang)
