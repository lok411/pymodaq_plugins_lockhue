# -*- coding: utf-8 -*-
"""
Created the 24/10/2022

@author: Sebastien Weber
"""
import numpy as np
from pymodaq_plugins_mock.hardware.wrapper import ActuatorWrapperWithTauMultiAxes


class BeamSteeringActuators(ActuatorWrapperWithTauMultiAxes):
    axes = ['M1tx', 'M1ty', 'M2tx', 'M2ty']
    units = ['', '', '', '']
    _units = units
    _epsilon = 0.1
    _tau = 0.01  # s

    def __init__(self):
        super().__init__()

        self._current_values = [0., 0., 0., 0.]

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

    def get_data(self, beam_controller: BeamSteeringActuators) -> np.ndarray:
        """ to be reimplemented with real matrix propagator

        """
        raise NotImplementedError


class Camera1(Camera):


    def get_data(self, beam_controller: BeamSteeringActuators) -> np.ndarray:
        ...
        return self._image


class Camera2(Camera):

    def get_data(self, beam_controller: BeamSteeringActuators) -> np.ndarray:
        ...
        return self._image


class BeamSteering:
    _tau = BeamSteeringActuators._tau

    def __init__(self):

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
        return self.cameras[index].get_data(self.actuators)

