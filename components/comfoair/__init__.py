import math
import esphome.codegen as cg
import esphome.cpp_generator as cppg
import esphome.config_validation as cv
from esphome import pins
from esphome.core import ID
from esphome.util import Registry
from esphome.const import CONF_ID, CONF_VERSION, CONF_NAME, UNIT_PERCENT, CONF_RX_PIN, CONF_TX_PIN
from esphome.components import text_sensor, binary_sensor, sensor
from enum import Enum

CONF_GLOBAL_FILTERS = "global_filters"

AUTO_LOAD = ["text_sensor", "binary_sensor", "sensor", "climate"]
MULTI_CONF = True

CONF_HUB_ID = 'comfoair'

empty_sensor_hub_ns = cg.esphome_ns.namespace('comfoair')

Comfoair = empty_sensor_hub_ns.class_('Comfoair', cg.Component)
ComfoairClimate = empty_sensor_hub_ns.class_('ComfoairClimate', cg.Component)
class ComfoNumConvs(Enum):
    UINT8 = 0,
    UINT16 = 1,
    UINT32 = 2,
    INT16 = 3

FILTER_REGISTRY = Registry()
validate_filters = cv.validate_registry("filter", FILTER_REGISTRY)
sensors = {
    "fan_speed":          {"unit": "", "PDO": 65, "CONV": ComfoNumConvs.UINT8},
    "next_fan_change":    {"unit": "s", "PDO": 81, "CONV": ComfoNumConvs.UINT32},
    "next_bypass_change": {"unit": "s", "PDO": 82, "CONV": ComfoNumConvs.UINT32},
    "next_supply_change": {"unit": "s", "PDO": 86, "CONV": ComfoNumConvs.UINT32},
    "next_exhaust_change": {"unit": "s", "PDO": 87, "CONV": ComfoNumConvs.UINT32},

    "exhaust_fan_duty":  {"unit":"%",    "PDO": 117, "CONV": ComfoNumConvs.UINT8 },
    "supply_fan_duty":   {"unit":"%",    "PDO": 118, "CONV": ComfoNumConvs.UINT8 },
    "exhaust_fan_flow":  {"unit":"m³/h", "PDO": 119, "CONV": ComfoNumConvs.UINT16},
    "supply_fan_flow":   {"unit":"m³/h", "PDO": 120, "CONV": ComfoNumConvs.UINT16},
    "exhaust_fan_speed": {"unit":"rpm",  "PDO": 121, "CONV": ComfoNumConvs.UINT16},
    "supply_fan_speed":  {"unit":"rpm",  "PDO": 122, "CONV": ComfoNumConvs.UINT16},

    "power_consumption_current":      {"unit": "W",   "PDO": 128, "CONV": ComfoNumConvs.UINT16},
    "energy_consumption_ytd":         {"unit": "kWh", "PDO": 129, "CONV": ComfoNumConvs.UINT16},
    "energy_consumption_since_start": {"unit": "kWh", "PDO": 130, "CONV": ComfoNumConvs.UINT16},

    "days_remaining_filter": {"unit": "days", "PDO": 192, "CONV": ComfoNumConvs.UINT16},

    "avoided_heating_actual": {"unit": "W", "PDO": 213, "CONV": ComfoNumConvs.UINT16},
    "avoided_heating_ytd":    {"unit": "kWh", "PDO": 214, "CONV": ComfoNumConvs.UINT16},
    "avoided_heating_total":  {"unit": "kWh", "PDO": 215, "CONV": ComfoNumConvs.UINT16},

    "avoided_cooling_actual": {"unit": "W", "PDO": 216, "CONV": ComfoNumConvs.UINT16},
    "avoided_cooling_ytd":    {"unit": "kWh", "PDO": 217, "CONV": ComfoNumConvs.UINT16},
    "avoided_cooling_total":  {"unit": "kWh", "PDO": 218, "CONV": ComfoNumConvs.UINT16},

    "bypass_state":  {"unit": "%", "PDO": 227, "CONV": ComfoNumConvs.UINT8},

    # temps
    "rmot":                     {"unit": "°C", "PDO": 209, "CONV": ComfoNumConvs.INT16, "div": 10},
    "target_temp":              {"unit": "°C", "PDO": 212, "CONV": ComfoNumConvs.UINT16, "div": 10},
    "pre_heater_temp_before":   {"unit": "°C", "PDO": 220, "CONV": ComfoNumConvs.INT16, "div": 10},
    "post_heater_temp_before":  {"unit": "°C", "PDO": 221, "CONV": ComfoNumConvs.INT16, "div": 10},
    "extract_air_temp":         {"unit": "°C", "PDO": 274, "CONV": ComfoNumConvs.INT16, "div": 10},
    "exhaust_air_temp":         {"unit": "°C", "PDO": 275, "CONV": ComfoNumConvs.INT16, "div": 10},
    "outdoor_air_temp":         {"unit": "°C", "PDO": 276, "CONV": ComfoNumConvs.INT16, "div": 10},

    "pre_heater_temp_after":    {"unit": "°C", "PDO": 277, "CONV": ComfoNumConvs.INT16, "div": 10},
    "post_heater_temp_after":   {"unit": "°C", "PDO": 278, "CONV": ComfoNumConvs.INT16, "div": 10},

    # humidity
    "extract_air_humidity":   {"unit": "%", "PDO": 290, "CONV": ComfoNumConvs.UINT8},
    "exhaust_air_humidity":   {"unit": "%", "PDO": 291, "CONV": ComfoNumConvs.UINT8},
    "outdoor_air_humidity":   {"unit": "%", "PDO": 292, "CONV": ComfoNumConvs.UINT8},
    "pre_heater_hum_after":   {"unit": "%", "PDO": 293, "CONV": ComfoNumConvs.UINT8},
    "supply_air_humidity":    {"unit": "%", "PDO": 294, "CONV": ComfoNumConvs.UINT8},


    # analog ports
    "analog_input_0_10v_1":   {"unit": "V", "PDO": 369, "CONV": ComfoNumConvs.UINT8, "div": 10},
    "analog_input_0_10v_2":   {"unit": "V", "PDO": 370, "CONV": ComfoNumConvs.UINT8, "div": 10},
    "analog_input_0_10v_3":   {"unit": "V", "PDO": 371, "CONV": ComfoNumConvs.UINT8, "div": 10},
    "analog_input_0_10v_4":   {"unit": "V", "PDO": 372, "CONV": ComfoNumConvs.UINT8, "div": 10},

}

textSensors = {
    "operating_mode": {
        "PDO": 49,
        "code": '''
return vals[0] == 1 ? "limited_manual": (vals[0] == 0xff ? "auto": "unlimited_manual");
'''
    },
    "bypass_activation_mode": {
        "PDO": 66,
        "code": '''
return  vals[0] == 0 ? "auto": (vals[0] == 1 ? "activated": "deactivated");
'''
    },
    "temp_profile": {
        "PDO": 67,
        "code": '''
return vals[0] == 0 ? "auto": (vals[0] == 1 ? "cold": "warm");
'''
    },

}

binarySensors = {
    # summer/winter mode
    "heating_season":   {
        "unit": "",
        "PDO": 210,
        "code": '''
return vals[0] == 1;
        '''
    },
    "cooling_season":   {
        "unit": "",
        "PDO": 211,
        "code": '''
return vals[0] == 1;
        '''
    },
    "manual_mode": {
        "PDO": 56,
        "code": '''
return vals[0] == 1;
        '''
    },
    "away": {
        "PDO": 16,
        "code": '''
return vals[0] == 0x08;
        '''
    },

    "fan_supply_only": {
        "PDO": 70,
        "code": '''
return vals[0] != 0;
        '''
    },
    "fan_exhaust_only": {
        "PDO": 71,
        "code": '''
return vals[0] != 0;
        '''
    },
}
GEN_SENSORS_SCHEMA = {
    cv.Optional(key, default=key): cv.maybe_simple_value(
        sensor.sensor_schema(unit_of_measurement=value['unit'], accuracy_decimals=math.trunc(math.log10(value['div'])) if 'div' in value else 0), key=CONF_NAME, accuracy_decimals=2 )
    for key, value in sensors.items()
}

GEN_TEXTSENSORS_SCHEMA = {
    cv.Optional(key, default=key): cv.maybe_simple_value(
        text_sensor.text_sensor_schema(), key=CONF_NAME, accuracy_decimals=2 )
    for key, value in textSensors.items()
}

GEN_BINARYSENSORS_SCHEMA = {
    cv.Optional(key, default=key): cv.maybe_simple_value(
        binary_sensor.binary_sensor_schema(), key=CONF_NAME)
    for key, value in binarySensors.items()
}

CONFIG_SCHEMA = cv.All(
    cv.Schema({
        cv.GenerateID(): cv.declare_id(Comfoair),
        cv.Optional(CONF_RX_PIN, default=21): pins.internal_gpio_input_pin_number,
        cv.Optional(CONF_TX_PIN, default=25): pins.internal_gpio_output_pin_number,
        cv.Optional(CONF_GLOBAL_FILTERS): sensor.validate_filters,
    })
    .extend(GEN_SENSORS_SCHEMA)
    .extend(GEN_TEXTSENSORS_SCHEMA)
    .extend(GEN_BINARYSENSORS_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA),
    )



async def to_code(config):
    cg.add_library("SPI", "2.0.0")
    cg.add_library("can_common", None, "https://github.com/collin80/can_common.git#07605a2a9f4963ee68a9ecf7790d38b22f6d2cdf")
    cg.add_library("esp32_can", None, "https://github.com/thom_ek/esp32_can.git")


    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    cg.add(var.set_rx(config[CONF_RX_PIN]))
    cg.add(var.set_tx(config[CONF_TX_PIN]))
    for key, value in sensors.items():
        sens = await sensor.new_sensor(config[key])

        if (config.get(CONF_GLOBAL_FILTERS)):
            newconf = []
            for filter in config[CONF_GLOBAL_FILTERS]:
                tmp = filter.copy()
                tmp['type_id'] = ID(tmp['type_id'].id + key, type=tmp['type_id'].type)
                newconf.append(tmp)
            filters = await sensor.build_filters(newconf)
            cg.add(sens.set_filters(filters))
        cg.add(var.register_sensor(sens, key, value['PDO'], value['CONV'].value, value['div'] if 'div' in value else 1))

    for key, value in textSensors.items():
        sens = await text_sensor.new_text_sensor(config[key])
        lamda = cppg.RawExpression(f'''
[](uint8_t *vals) -> std::string {{ 
    {value['code']}
}}
''')
        cg.add(var.register_textSensor(sens, key, value['PDO'], lamda))

    for key, value in binarySensors.items():
        sens = await binary_sensor.new_binary_sensor(config[key])
        lamda = cppg.RawExpression(f'''
[](uint8_t *vals) -> bool {{ 
    {value['code']}
}}
''')
        cg.add(var.register_binarySensor(sens, key, value['PDO'], lamda))

    cg.add(cg.App.register_climate(var))
