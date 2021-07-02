import logging
from os import PathLike
from pathlib import Path
from typing import Any, Iterable, Tuple
from unittest.mock import patch

import numpy as np
import pytest
import xarray as xr
from basic_modeling_interface import Bmi
from numpy.testing import assert_array_equal

from ewatercycle import CFG
from ewatercycle.config import DEFAULT_CONFIG
from ewatercycle.models.abstract import AbstractModel
from ewatercycle.parameter_sets import ParameterSet


@pytest.fixture
def setup_config(tmp_path):
    CFG['parameterset_dir'] = tmp_path
    CFG['ewatercycle_config'] = tmp_path / 'ewatercycle.yaml'
    yield CFG
    CFG['ewatercycle_config'] = DEFAULT_CONFIG
    CFG.reload()


class MockedModel(AbstractModel):
    available_versions = ('0.4.2',)

    def __init__(self, version: str = '0.4.2', parameter_set: ParameterSet = None):
        super().__init__(version, parameter_set)

    def setup(self, *args, **kwargs) -> Tuple[PathLike, PathLike]:
        if 'bmi' in kwargs:
            # sub-class of AbstractModel should construct bmi
            # using grpc4bmi Docker or Singularity client
            self.bmi = kwargs['bmi']
        return Path('foobar.cfg'), Path('.')

    def get_value_as_xarray(self, name: str) -> xr.DataArray:
        return xr.DataArray(
            data=[[1.0, 2.0], [3.0, 4.0]],
            coords={
                "latitude": [42.25, 42.21],
                "longitude": [-99.83, -99.32],
                "time": '2014-09-06'},
            dims=["longitude", "latitude"],
            name='Temperature',
            attrs=dict(units="degC"),
        )

    def _coords_to_indices(self, name: str, lat: Iterable[float], lon: Iterable[float]) -> Tuple[
        Iterable[int], Iterable[float], Iterable[float]]:
        return np.array([0]), np.array([-99.83]), np.array([42.25])

    @property
    def parameters(self) -> Iterable[Tuple[str, Any]]:
        return [('area', 42)]


@pytest.fixture
@patch('basic_modeling_interface.Bmi')
def bmi(MockedBmi):
    return MockedBmi()


@pytest.fixture
def model(bmi: Bmi):
    m = MockedModel()
    m.setup(bmi=bmi)
    return m


def test_construct():
    with pytest.raises(TypeError) as excinfo:
        AbstractModel(version='0.4.2')
    msg = str(excinfo.value)
    assert "Can't instantiate abstract class" in msg
    assert 'setup' in msg
    assert 'parameters' in msg


def test_construct_with_unsupported_version():
    with pytest.raises(ValueError) as excinfo:
        MockedModel(version='1.2.3')

    assert "Supplied version 1.2.3 is not supported by this model. Available versions are ('0.4.2',)." in str(excinfo.value)


def test_setup(model):
    result = model.setup()

    expected = Path('foobar.cfg'), Path('.')
    assert result == expected


def test_initialize(model: MockedModel, bmi):
    config_file = 'foobar.cfg'
    model.initialize(config_file)

    bmi.initialize.assert_called_once_with(config_file)


def test_finalize(model: MockedModel, bmi):
    model.finalize()

    bmi.finalize.assert_called_once_with()


def test_update(model: MockedModel, bmi):
    model.update()

    bmi.update.assert_called_once_with()


def test_get_value(bmi, model: MockedModel):
    expected = np.array([[1.0, 2.0], [3.0, 4.0]])
    bmi.get_value.return_value = expected

    value = model.get_value('discharge')

    assert_array_equal(value, expected)


def test_get_value_at_coords(bmi, model: MockedModel):
    expected = np.array([1.0])
    bmi.get_value_at_indices.return_value = expected

    value = model.get_value_at_coords('discharge', [-99.83], [42.25])

    assert_array_equal(value, expected)


def test_set_value(model: MockedModel, bmi):
    value = np.array([1.0, 2.0])
    model.set_value('precipitation', value)

    bmi.set_value.assert_called_once_with('precipitation', value)


def test_set_value_at_coords(model: MockedModel, bmi):
    value = np.array([1.0])
    model.set_value_at_coords('precipitation', [-99.83], [42.25], value)

    bmi.set_value_at_indices.assert_called_once_with('precipitation', [0], value)


def test_start_time(bmi, model: MockedModel):
    bmi.get_start_time.return_value = 42.0

    time = model.start_time

    assert time == pytest.approx(42.0)


def test_end_time(bmi, model: MockedModel):
    bmi.get_end_time.return_value = 42.0

    time = model.end_time

    assert time == pytest.approx(42.0)


def test_time(bmi, model: MockedModel):
    bmi.get_current_time.return_value = 42.0

    time = model.time

    assert time == pytest.approx(42.0)


def test_time_units(bmi, model: MockedModel):
    bmi.get_time_units.return_value = 'd'

    units = model.time_units

    assert units == 'd'


def test_time_step(bmi, model: MockedModel):
    bmi.get_time_step.return_value = 1.0

    step = model.time_step

    assert step == pytest.approx(1.0)


def test_output_var_names(bmi, model: MockedModel):
    bmi.get_output_var_names.return_value = ('discharge',)

    names = model.output_var_names

    assert names == ('discharge',)


def test_get_value_as_xarray(model: MockedModel):
    expected = xr.DataArray(
        data=[[1.0, 2.0], [3.0, 4.0]],
        coords={
            "latitude": [42.25, 42.21],
            "longitude": [-99.83, -99.32],
            "time": '2014-09-06'},
        dims=["longitude", "latitude"],
        name='Temperature',
        attrs=dict(units="degC"),
    )

    dataarray = model.get_value_as_xarray("Temperature")

    xr.testing.assert_equal(dataarray, expected)


class TestCheckParameterSet:
    def test_correct_version(self, setup_config):
        ps = ParameterSet(
            name='justatest',
            directory='justatest',
            config='justatest/config.ini',
            target_model='mockedmodel',  # == lowered class name
            supported_model_versions={'0.4.2'}
        )
        m = MockedModel(parameter_set=ps)
        assert m.parameter_set == ps

    def test_wrong_model(self, setup_config):
        ps = ParameterSet(
            name='justatest',
            directory='justatest',
            config='justatest/config.ini',
            target_model='wrongmodel',
            supported_model_versions={'0.4.2'}
        )
        with pytest.raises(ValueError) as excinfo:
            MockedModel(parameter_set=ps)

        expected = 'Parameter set has wrong target model'
        assert expected in str(excinfo.value)

    def test_any_version(self, caplog, setup_config):
        ps = ParameterSet(
            name='justatest',
            directory='justatest',
            config='justatest/config.ini',
            target_model='mockedmodel',  # == lowered class name
            supported_model_versions=set()
        )
        with caplog.at_level(logging.INFO):
            MockedModel(parameter_set=ps)

        expected = 'is not explicitly listed in the supported model versions'
        assert expected in caplog.text

    def test_unsupported_version(self, setup_config):
        ps = ParameterSet(
            name='justatest',
            directory='justatest',
            config='justatest/config.ini',
            target_model='mockedmodel',
            supported_model_versions={'1.2.3'}
        )
        with pytest.raises(ValueError) as excinfo:
            MockedModel(parameter_set=ps)

        expected = 'Parameter set is not compatible with version'
        assert expected in str(excinfo.value)
