#!/bin/bash
#
# This script is for starting mpd and tools
# to stop mpd and tools use play_out_stop.sh
#
# Prerequisite is a correct running jack/Qjackctrl
#
# Author: Joerg Sorge
# Distributed under the terms of GNU GPL version 2 or later
# Copyright (C) Joerg Sorge joergsorge at gmail.com
# 2014-11-18
#

#TODO: if using jamin, reconnect mpd-out to jamin-in

# config:
jack_source_mpd_1='Music Player Daemon:left'
jack_source_mpd_2='Music Player Daemon:right'
ebumeter="j"
meterbridge="n"
jamin="n"
calffx="j"

## do not edit below this line

function f_check_package () {
        package_install=$1
        if dpkg-query -s $1 2>/dev/null|grep -q installed; then
                echo "$package_install installiert"
        else
                zenity --error --text="Package:\n$package_install\nnot installt, please install it first!"
		./stream-stop.sh &
                exit
        fi
}

function f_check_fx () {
	if [ "$jamin" != "n" ] && [ "$calffx" != "n" ]; 
	then
		message="# Pleas choose either Jamin OR Calf as FX-Module in teh conffigfile!\n Let's let down..."
		echo $message
		sleep 5
		exit
	fi
}

function f_start_play_out () {
	message="$message Starting Play-Out..\n"
	echo $message
	f_check_package "mpd"
	sleep 1
	mpd ~/srb-mpd/mpd.conf &
}

function f_start_mixer () {
	message="$message Starting Mixer..\n"
	echo $message
	f_check_package "jack-mixer"
	sleep 1
	jack_mixer &
}

function f_start_scheduler () {
	message="$message Starting Play-Out-Scheduler..\n"
	echo $message
	sleep 1
	cd ~/srb-tools/
	./play_out_scheduler.py &
}

function f_start_logging () {
	message="$message Starting Play-Out-Logging..\n"
	echo $message
	sleep 1
	cd ~/srb-tools/
	./play_out_logging.py &
}

function f_start_meterbridge () {
	message="#$message Starting Meterbridge..\n"
	echo $message
	f_check_package "meterbridge"
	sleep 1
	meterbridge -t dpm -n stream-bridge x x &
	message="#$message Connecting Meterbridge..\n"
	echo $message
	sleep 2
	jack_connect $jack_source_1 stream-bridge:meter_1 &
	jack_connect $jack_source_2 stream-bridge:meter_2 &
}

function f_start_ebumeter () {
	message="$message Starting EBU Meter..\n"
	echo $message
	f_check_package "ebumeter"
	sleep 1
	ebumeter &
	message="#$message Connecting EBU Meter..\n"
	echo $message
	sleep 2
	jack_connect "$jack_source_mpd_1" ebumeter:in.L &
	jack_connect "$jack_source_mpd_2" ebumeter:in.R &
}

function f_check_jack () {
	message="$message Checking Jack..\n"
	echo $message
	sleep 1
	jack_pid=$(ps aux | grep '[q]jackctl' | awk '{print $2}')
	if [ "$jack_pid" == "" ]; then
		zenity --error --text="Qjackctl is not running!\n Please start it befor running this script!\n Let's lay down.."
		exit		
	fi
}

function f_check_jamin () {
	message="$message Check Jamin..\n"
	echo $message
	sleep 1
	jamin_pid=$(ps aux | grep '[j]amin' | awk '{print $2}')
	if [ "$jamin_pid" != "" ]; then
		zenity --error --text="Jamin is alraedy running!\n Please kill it befor using this script.."
		exit
	fi
}

function f_start_jamin () {
	message="$message Starting Jamin..\n"
	echo $message
	f_check_package "jamin"
	sleep 1
	jamin &
}

function f_connect_jamin () {
	message="$message Connect Jamin..\n"
	echo $message
	sleep 3
	jack_connect $jack_source_mpd_1 jamin:in_L &
	jack_connect $jack_source_mpd_1 jamin:in_R &
}

function f_connect_ebumeter_jamin () {
	message="$message Connect EBU-Meter..\n"
	echo $message
	sleep 1
	jack_disconnect $jack_source_1 ebumeter:in.L &
	jack_disconnect $jack_source_2 ebumeter:in.R &
	jack_connect jamin:out_L ebumeter:in.L &
	jack_connect jamin:out_R ebumeter:in.R &
}

function f_start_calfjackhost () {
	message="$message Starting Calf..\n"
	echo $message
	#f_check_package "calfjackhost"
	# its not installed via deb
	if [ -e /usr/bin/calfjackhost ]; then
		sleep 1
		calfjackhost ! multibandcompressor:Standard ! multibandlimiter:Standard ! &
	else
		zenity --error --text="Package:\nCalf\nnot installed, please install it first!"
		exit
	fi
}


echo "Starting Play-Out and Jack-Apps..."

(	echo "10"
	message="# Starting Tools..\n"
	f_check_jack
	f_check_fx

	if [ "$jamin" != "n" ]; then
		f_check_jamin
	fi

	f_start_play_out
	#f_start_mixer

	if [ "$meterbridge" != "n" ]; then
		f_start_meterbridge
	fi

	if [ "$ebumeter" != "n" ]; then
		f_start_ebumeter
	fi

	if [ "$jamin" != "n" ]; then
		f_start_jamin
		f_connect_jamin
	fi

	if [ "$jamin" != "n" ]; then
		if [ "$ebumeter" != "n" ]; then
			f_connect_ebumeter_jamin
		fi
	fi

	if [ "$calffx" != "n" ]; then
		f_start_calfjackhost
		#f_connect_jamin
	fi

	f_start_scheduler
	sleep 1	
	f_start_logging
	sleep 1
	echo "100"
	
)| zenity --progress \
           --title="Play-Out" --text="starten..." --width=500 --pulsate --auto-close

