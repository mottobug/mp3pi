#!/bin/bash

# partly from http://askubuntu.com/questions/159064/switch-between-speaker-bluetooth-stereo-bluetooth-mono

# pactl list short sinks
#0  alsa_output.pci-0000_00_1b.0.analog-stereo  module-alsa-card.c  s16le 2ch 48000Hz SUSPENDED
#12  bluez_sink.0C_A6_94_E3_76_DA  module-bluez5-device.c  s16le 2ch 44100Hz SUSPENDED


SINK=$( pacmd list-cards | grep -B 1 bluez )
INDEX=${SINK:10:2}

echo "Bluetooth Card is at $INDEX"

SINK=$( pacmd list-cards | grep bluez )
MAC=${SINK:19:17}

echo "Bluetooth device $MAC"

BT_SINK="bluez_sink.$MAC"
#BT_SOURCE="bluez_source.$MAC"

echo $BT_SINK

echo pacmd set-card-profile $INDEX a2dp
pacmd set-card-profile $INDEX a2dp_sink

echo pacmd set-default-sink $BT_SINK
pacmd set-default-sink $BT_SINK
#pacmd set-default-source $BT_SOURCE

# howto move streams while not playing anything?
pactl list short sink-inputs|while read stream; do
  streamId=$(echo $stream|cut '-d ' -f1)
  echo pactl move-sink-input "$streamId" $BT_SINK
  pactl move-sink-input "$streamId" $BT_SINK
done
