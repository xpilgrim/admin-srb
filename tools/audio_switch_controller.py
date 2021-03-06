#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103

"""
Controller Audio Switch
Autor: Joerg Sorge, based on SKS-Server from Jenz Loeffler
Org: SRB - Das Buergerradio
www.srb.fm

Distributed under the terms of GNU GPL version 2 or later
Copyright (C) Joerg Sorge
2015-10-26

Dieses Script ermittelt den Status und schaltet den Audio-Switche


Dateiname Script: audio_switch_controlle.py
Schluesselwort fuer Einstellungen: audio_switch
Benoetigt: lib_common.py im gleichen Verzeichnis
Bezieht Daten aus: Firebird-Datenbank
Arbeitet zusammen mit: audio_switch_controller.php auf dem Webserver

Fehlerliste:
E 0 Parameter-Typ oder Inhalt stimmt nicht
E 1 Fehler bei Parameteruebergabe an Script
E 2 Fehler beim Push
E 3 Fehler beim Fade

Parameterliste:
Param 1: Serial Port Server A
Param 2: Serial Port Server B
Param 3: Serial baudrate
Param 4: Serial bytesize
Param 5: Serial parity
Param 6: Serial stopbits
Param 7: Serial timeout

Dieses Script wird durch das Intra-Web-Frontend aufgerufen
oder auf der Kommandozeile bediehnt


"""

import sys
import getopt
import time
import lib_common_1 as lib_cm
import lib_serial as lib_ser


class app_config(object):
    """Application-Config"""
    def __init__(self):
        """Settings"""
        # app_config
        self.app_id = "023"
        self.app_desc = "Audio_Switch_Controller"
        self.app_errorfile = "error_audio_switch_controller.log"
        # key for config in db
        self.app_config = "audio_switch"
        # amount parameter
        self.app_config_params_range = 7
        # params-type-list
        self.app_params_type_list = []
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_int")
        self.app_params_type_list.append("p_int")
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_int")
        self.app_params_type_list.append("p_int")
        # errorlist
        self.app_errorslist = []
        self.app_errorslist.append("Parameter-Typ oder Inhalt stimmt nicht ")
        self.app_errorslist.append("Fehler bei Parameteruebergabe an Script ")
        self.app_errorslist.append("Fehler beim Push ")
        self.app_errorslist.append("Fehler beim Fade ")
        # using develop-params
        self.app_develop = "no"
        # display debugmessages on console yes or no: "no"
        # for normal usage set to no!!!!!!
        self.app_debug_mod = "no"
        # settings serial port


def usage_help():
    """pull out some help"""
    print "controller for audioswitch"
    print "usage:"
    print "controller_audio_switch.py -option value"
    print "valid options are:"
    print "-h --help"
    print "-s --status to display status"
    print "-a --read active audio input"
    print "-l n --level n to display level for input n"
    print "-p n --push n to switch to input n"
    print "-f n --fade n to fade to input n"
    print "-g n --gain n to set gain to 0dB for input n"


def load_extended_params():
    """load extended params"""
    ext_params_ok = True
    # extern tools
    ext_params_ok = lib_cm.params_provide_server_settings(ac, db)
    if ext_params_ok is None:
        return None
    lib_cm.set_server(ac, db)
    return ext_params_ok


def read_audio_input(check_resp_pattern):
    """read audio input"""
    switch_status = ser.get_status(ac, db, "I", "I")
    if not switch_status:
        return
    # pattern value of audio input respond depends on previous cmd
    # so switch here
    if check_resp_pattern:
        status_audio = ser.read_switch_respond(ac, db, switch_status)
        log_message = "Audio Input active: " + status_audio
    else:
        log_message = "Audio Input active: " + switch_status[0]
    print log_message
    db.write_log_to_db_a(ac, log_message, "p",
                                                "write_also_to_console")


def push_switch(param):
    """push switch"""
    port = ser.set_port(ac, db)
    if not port:
        return
    switch_status = ser.get_status(ac, db, "I", "I")
    if not switch_status:
        return
    switch_cmd = param + "!"
    try:
        port.write(switch_cmd)
        time.sleep(0.1)
        #read_audio_input(True)
        db.write_log_to_db_a(ac, "Switch to Input " + param, "e",
                                                "write_also_to_console")
        print "Switch to Input " + param
        port.close
    except Exception as e:
        db.write_log_to_db_a(ac, ac.app_errorslist[2] + str(e), "x",
            "write_also_to_console")
        port.close


def fade_switch(param):
    """fade_switch"""
    switch_status = ser.get_status(ac, db, "-s", "I")
    if switch_status is None:
        return
    switch_imput_old = ser.read_switch_respond(ac, db, switch_status)
    switch_imput_new = param
    switch_fade_out = switch_imput_old + "-G"
    switch_fade_in = switch_imput_new + "+G"
    switch_to_input = switch_imput_new + "!"
    port = ser.set_port(ac, db)
    if not port:
        return
    try:
        log_message = ("Fade from Input " + switch_imput_old
                        + " to Input " + switch_imput_new)
        db.write_log_to_db_a(ac, log_message, "e", "write_also_to_console")
        # fade old input out
        x = 1
        for x in range(18):
            port.write(switch_fade_out)
            time.sleep(0.1)
        #print "gain switch_imput_old"
        ser.get_status(ac, db, switch_imput_old, "V" + switch_imput_old + "G")
        time.sleep(0.1)
        # reduce gain for new input
        port.write(switch_imput_new + "*-18g")
        time.sleep(0.1)
        #print "gain switch_imput_new"
        ser.get_status(ac, db, switch_imput_new, "V" + switch_imput_new + "G")
        # switch to new input
        port.write(switch_to_input)
        time.sleep(0.1)
        # fade new input in
        x = 1
        for x in range(18):
            port.write(switch_fade_in)
            time.sleep(0.1)
        # reset old input to 0dB
        ser.reset_gain(ac, db, switch_imput_old)
        time.sleep(0.2)
        port.close
        print "Faded to Input " + switch_to_input
    except Exception as e:
        db.write_log_to_db_a(ac, ac.app_errorslist[3] + str(e), "x",
            "write_also_to_console")
        port.close


def lets_rock(argv):
    """main function """
    load_extended_params_ok = load_extended_params()
    if load_extended_params_ok is None:
        return
    # check if serial port is a port number or an string
    if ac.server_active == "A":
        if db.ac_config_1[1].isdigit():
            ac.ser_port = int(db.ac_config_1[1])
        else:
            ac.ser_port = db.ac_config_1[1]
    if ac.server_active == "B":
        if db.ac_config_1[2].isdigit():
            ac.ser_port = int(db.ac_config_1[2])
        else:
            ac.ser_port = db.ac_config_1[2]

    valid_param = None

    try:
        opts, args = getopt.getopt(argv, "hsal:p:f:g:",
            ["help", "status", "audio", "level=", "push=", "fade=", "gain="])
    except getopt.GetoptError:
        usage_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            valid_param = True
            usage_help()
            sys.exit()

        elif opt in ("-s", "--status"):
            valid_param = True
            switch_status = ser.get_status(ac, db, arg, "I")
            if switch_status:
                log_message = "Status: " + ', '.join(switch_status)
                print log_message
                db.write_log_to_db_a(ac, log_message, "p",
                                             "write_also_to_console")

        elif opt in ("-a", "--audio"):
            valid_param = True
            read_audio_input(True)

        elif opt in ("-l", "--level="):
            if arg != "":
                valid_param = True
                switch_status = ser.get_status(ac, db, arg, "V" + arg + "G")
                if switch_status:
                    log_message = "Level for Input: " + arg
                    db.write_log_to_db_a(ac, log_message, "t",
                                                "write_also_to_console")
                    print log_message

        elif opt in ("-p", "--push"):
            if arg != "":
                valid_param = True
                push_switch(arg)

        elif opt in ("-f", "--fade="):
            if arg != "":
                valid_param = True
                fade_switch(arg)

        elif opt in ("-g", "--gain="):
            if arg != "":
                valid_param = True
                switch_status = ser.reset_gain(ac, db, arg)
                if switch_status:
                    log_message = "Gain for Input: " + ', '.join(switch_status)
                    print log_message
                    db.write_log_to_db_a(ac, log_message, "p",
                                                "write_also_to_console")
    # it seems, that no valid arg is given
    if valid_param is None:
        db.write_log_to_db_a(ac, ac.app_errorslist[1], "x",
            "write_also_to_console")
        usage_help()


if __name__ == "__main__":
    db = lib_cm.dbase()
    ac = app_config()
    ser = lib_ser.mySERIAL()
    log_message = ac.app_desc + " gestartet"
    db.write_log_to_db_a(ac, log_message, "r", "write_also_to_console")
    # Config_Params 1
    db.ac_config_1 = db.params_load_1(ac, db)
    if db.ac_config_1 is not None:
        param_check = lib_cm.params_check_1(ac, db)
         # alles ok: weiter
        if param_check is not None:
            # losgehts
            lets_rock(sys.argv[1:])

    # fertsch
    log_message = ac.app_desc + " gestoppt"
    db.write_log_to_db_a(ac, log_message, "s", "write_also_to_console")
    sys.exit()
