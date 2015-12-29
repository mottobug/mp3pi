#!/bin/bash

pactl list short sinks | awk '{print $2}'


