import datetime
import importlib.util
import pathlib
import sys
import types

import pytest


@pytest.fixture(scope="module")
def co2_module():
    script_path = pathlib.Path(__file__).resolve().parents[1] / "co2-mqtt.py"
    module_name = "co2_mqtt_module_under_test"

    mh_z19_stub = types.ModuleType("mh_z19")
    setattr(mh_z19_stub, "read_all", lambda serial_console_untouched=True: {"co2": 400})
    sys.modules["mh_z19"] = mh_z19_stub

    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_read_from_sensors_uses_last_value_when_sensor_returns_none(
    co2_module, monkeypatch
):
    control = co2_module.Control()
    control.co2_last_value = 450

    monkeypatch.setattr(
        co2_module.mh_z19, "read_all", lambda serial_console_untouched=True: None
    )

    control.read_from_sensors()

    assert control.co2s[-1] == 450
    assert control.co2_last_value == 450


def test_read_from_sensors_updates_last_value_on_valid_data(co2_module, monkeypatch):
    control = co2_module.Control()

    monkeypatch.setattr(
        co2_module.mh_z19,
        "read_all",
        lambda serial_console_untouched=True: {"co2": 700},
    )

    control.read_from_sensors()

    assert control.co2s[-1] == 700
    assert control.co2_last_value == 700


def test_smooth_data_ignores_zeros(co2_module):
    reader = co2_module.CO2Reader.__new__(co2_module.CO2Reader)

    result = reader._smooth_data([0, 400, 0, 500, 600])

    assert result == 500


def test_process_samples_returns_payload_and_clears_buffer(co2_module):
    reader = co2_module.CO2Reader.__new__(co2_module.CO2Reader)
    reader.control = co2_module.Control()
    reader.control.co2s = [0, 500, 550, 0]

    payload = reader.process_samples()

    assert len(payload) == 1
    assert payload[0]["fields"]["co2"] == 525
    assert isinstance(payload[0]["fields"]["timestamp"], str)
    datetime.datetime.strptime(payload[0]["fields"]["timestamp"], "%d/%m/%Y, %H:%M:%S")
    assert reader.control.co2s == []


def test_config_reads_values_from_environment(co2_module, monkeypatch):
    monkeypatch.setenv("MQTT_SERVER_IP", "127.0.0.1")
    monkeypatch.setenv("MQTT_SERVER_PORT", "1883")
    monkeypatch.setenv("MQTT_SERVER_USER", "user")
    monkeypatch.setenv("MQTT_SERVER_PASSWORD", "pass")
    monkeypatch.setenv("MQTT_SERVER_TOPIC", "homeassistant/co2")

    config = co2_module.Config()

    assert config.mqtt_server_ip == "127.0.0.1"
    assert config.mqtt_server_port == 1883
    assert config.mqtt_server_user == "user"
    assert config.mqtt_server_password == "pass"
    assert config.mqtt_server_topic == "homeassistant/co2"


def test_setup_mqtt_creates_and_configures_client(co2_module):
    reader = co2_module.CO2Reader.__new__(co2_module.CO2Reader)
    reader.config = types.SimpleNamespace(
        mqtt_server_ip="127.0.0.1",
        mqtt_server_port=1883,
        mqtt_server_user="user",
        mqtt_server_password="pass",
    )

    class FakeClient:
        def __init__(self):
            self.credentials = None
            self.connection = None
            self.loop_started = False

        def username_pw_set(self, user, password):
            self.credentials = (user, password)

        def connect(self, ip, port):
            self.connection = (ip, port)

        def loop_start(self):
            self.loop_started = True

    fake_client = FakeClient()
    original_client_ctor = co2_module.mqtt.Client
    co2_module.mqtt.Client = lambda *_args, **_kwargs: fake_client

    try:
        reader._setup_mqtt()
    finally:
        co2_module.mqtt.Client = original_client_ctor

    assert reader.client is fake_client
    assert fake_client.credentials == ("user", "pass")
    assert fake_client.connection == ("127.0.0.1", 1883)
    assert fake_client.loop_started is True


def test_start_sensor_thread_starts_daemon_thread(co2_module):
    reader = co2_module.CO2Reader.__new__(co2_module.CO2Reader)
    reader._sample = lambda: None

    called = {}

    class FakeThread:
        def __init__(self, target, daemon):
            called["target"] = target
            called["daemon"] = daemon
            called["started"] = False

        def start(self):
            called["started"] = True

    original_thread_ctor = co2_module.threading.Thread
    co2_module.threading.Thread = FakeThread

    try:
        reader._start_sensor_thread()
    finally:
        co2_module.threading.Thread = original_thread_ctor

    assert called["target"] is reader._sample
    assert called["daemon"] is True
    assert called["started"] is True
