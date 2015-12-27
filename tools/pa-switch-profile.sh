#!/bin/bash

SINK=$( pacmd list-cards | grep -B 1 bluez )
INDEX=${SINK:10:2}

echo "Bluetooth Card is at $INDEX"

SINK=$( pacmd list-cards | grep bluez )
MAC=${SINK:19:17}

echo "Bluetooth device $MAC"

BT_SINK="bluez_sink.$MAC"

echo $BT_SINK

echo pacmd set-card-profile $INDEX a2dp
pacmd set-card-profile $INDEX a2dp_sink

echo pacmd set-default-sink $BT_SINK
pacmd set-default-sink $BT_SINK

