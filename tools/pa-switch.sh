#!/bin/bash

pacmd list-sinks | grep -A1  index | grep name

#pacmd "set-default-sink bluez_sink.0C_A6_94_E3_76_DA"
