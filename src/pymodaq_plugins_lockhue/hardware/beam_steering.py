# -*- coding: utf-8 -*-
"""
Created the 24/10/2022

@author: Sebastien Weber
"""
import numpy as np
from pymodaq_plugins_mock.hardware.wrapper import ActuatorWrapperWithTauMultiAxes



class IniBeam:
    def __init__(self):
        self._theta_in_x = 0.
        self._theta_in_y = 0.

        self._delta_x = 0.
        self._delta_y = 0.

    @property
    def delta_x(self):
        """ Get/set the beam offset on first mirror in mm"""
        return self._delta_x

    @delta_x.setter
    def delta_x(self, delta_x: float):
        self._delta_x = delta_x

    @property
    def delta_y(self):
        """ Get/set the beam offset on first mirror in mm"""
        return self._delta_x

    @delta_y.setter
    def delta_y(self, delta_y: float):
        self._delta_y = delta_y

    @property
    def theta_in_x(self):
        """ Get/set the beam incidence angle on first mirror in °"""
        return self._theta_in_x

    @theta_in_x.setter
    def theta_in_x(self, theta_in_x: float):
        self._theta_in_x = theta_in_x

    @property
    def theta_in_y(self):
        """ Get/set the beam incidence angle on first mirror in °"""
        return self._theta_in_y

    @theta_in_y.setter
    def theta_in_y(self, theta_in_y: float):
        self._theta_in_y = theta_in_y

class Setup():
    def __init__(self):
        # The lengths based on measured values
        self.L_0 = 70
        self.L_MM = 50
        self.L_BS = 80
        self.L_1 = 60
        self.L_2 = 170

class Matrix(): #Refaire
    def __init__(self, setup: Setup):
        # Propagating matrices
        """
        # Without mirrors
        self.mat_0 = [[1, 0, setup.L_0, 0], [0, 0, 1, 0]]
        self.mat_MM = [[1, 0, setup.L_MM, 0], [0, 0, 1, 0]]
        self.mat_BS = [[1, 0, setup.L_BS, 0], [0, 0, 1, 0]]
        self.mat_C1 = [[1, 0, setup.L_1, 0], [0, 0, 1, 0]]
        self.mat_C2 = [[1, 0, setup.L_2, 0], [0, 0, 1, 0]]

        # Mirror effects
        self.mat_M = 2 * [[-setup.L_0, 0, -setup.L_MM - setup.L_0, 0], [0, -setup.L_0, 0, -setup.L_MM - setup.L_0]]
        #WARNING:
        """

        self.matInit1 = [[1, 0, setup.L_0 + setup.L_MM + setup.L_BS + setup.L_1, 0],
                   [0, 1, 0, setup.L_0 + setup.L_MM + setup.L_BS + setup.L_1]]
        self.matInit2 = [[1, 0, setup.L_0 + setup.L_MM + setup.L_BS + setup.L_2, 0],
                    [0, 1, 0, setup.L_0 + setup.L_MM + setup.L_BS + setup.L_2]]

        self.matSetup1 = [[setup.L_MM + setup.L_BS + setup.L_1, 0, setup.L_BS + setup.L_1, 0],
                    [0, setup.L_MM + setup.L_BS + setup.L_1, 0, setup.L_BS + setup.L_1]]
        self.matSetup2 = [[setup.L_MM + setup.L_BS + setup.L_2, 0, setup.L_BS + setup.L_2, 0],
                     [0, setup.L_MM + setup.L_BS + setup.L_2, 0, setup.L_BS + setup.L_2]]

class BeamSteeringActuators(ActuatorWrapperWithTauMultiAxes):
    axes = ['M1tx', 'M1ty', 'M2tx', 'M2ty']
    units = ['', '', '', '']
    _units = units
    _epsilon = 0.1
    _tau = 0.01  # s

    def __init__(self):
        super().__init__()

        self._current_values = [0., 0., 0., 0.]


class Camera:
    Nx = 256
    Ny = 256
    amp = 20
    x0 = 128
    y0 = 128
    _dx = 20
    _dy = 10
    _n = 1
    _angle = 0
    amp_noise = 1

    def __init__(self):
        super().__init__()
        self._image: np.ndarray = None
        self.x_axis = np.linspace(0, self.Nx, self.Nx, endpoint=False) - self.Nx / 2
        self.y_axis = np.linspace(0, self.Ny, self.Ny, endpoint=False) - self.Ny / 2

    @property
    def dx(self):
        return self._dx

    @dx.setter
    def dx(self, new_dx: float):
        self._dx = new_dx

    @property
    def dy(self):
        return self._dy

    @dy.setter
    def dy(self, new_dy: float):
        self._dy = new_dy

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, new_n: int):
        self._n = new_n

    def get_data(self, beam_controller: BeamSteeringActuators,
                 ini_beam: IniBeam, setup: Setup) -> np.ndarray:
        """
         to be reimplemented with real matrix propagator
        """
        raise NotImplementedError


class Camera1(Camera):

    def get_data(self, beam_controller: BeamSteeringActuators,
                 ini_beam: IniBeam, setup: Setup) -> np.ndarray:
        mat = Matrix(setup)
        input = [ini_beam.delta_x, ini_beam.delta_y, ini_beam.theta_in_x, ini_beam.theta_in_y] #Can we make it more compact?
        mirror_angles = [setup.get_value(axis for axis in setup.axes)]

        image = np.dot(mat.matInit1, input) + np.dot(mat.matSetup1, mirror_angles)
        return image


class Camera2(Camera):

    def get_data(self, beam_controller: BeamSteeringActuators,
                 ini_beam: IniBeam, setup: Setup) -> np.ndarray:
        mat = Matrix(setup)
        input = [ini_beam.delta_x, ini_beam.delta_y, ini_beam.theta_in_x, ini_beam.theta_in_y]
        mirror_angles = [setup.get_value(axis for axis in setup.axes)]

        image = np.dot(mat.matInit2, input) + np.dot(mat.matSetup2, mirror_angles)
        return image


class BeamSteering:
    _tau = BeamSteeringActuators._tau

    def __init__(self):
        self.ini_beam = IniBeam()
        self.setup = Setup()
        self.actuators = BeamSteeringActuators()
        self.cameras = [Camera1(), Camera2()]
        for cam in self.cameras:
            cam.fringes = False

    @property
    def tau(self):
        """
        fetch the characteristic decay time in s
        Returns
        -------
        float: the current characteristic decay time value

        """
        return self.actuators.tau

    @tau.setter
    def tau(self, value: float):
        """
        Set the characteristic decay time value in s
        Parameters
        ----------
        value: (float) a strictly positive characteristic decay time
        """
        self.actuators.tau = value

    def move_at(self, value: float, axis: str):
        """
        """
        if axis in BeamSteeringActuators.axes:
            self.actuators.move_at(value, axis)

    def stop(self, axis: str):
        self.actuators.stop(axis)

    def get_value(self, axis: str):
        """
        Get the current actuator value
        Returns
        -------
        float: The current value
        """
        return self.actuators.get_value(axis)

    def get_camera_data(self, index: int) -> np.ndarray:
        return self.cameras[index].get_data(self.actuators,
                                            self.ini_beam,
                                            self.setup)

