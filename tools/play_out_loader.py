#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Play Out Loader
Autor: Joerg Sorge
Org: SRB - Das Buergerradio
www.srb.fm

Distributed under the terms of GNU GPL version 2 or later
Copyright (C) Joerg Sorge joergsorge at googell
2013-06-30

Dieses Script ist Hauptbestandteil der Sendeabwicklung.
Es erzeugt die noetigen Playlisten zum Ausspielen
und stellt die Werte fur die Audiofreischaltung
der Sendequellen bereit.

Dateiname Script: play_out_loader.py
Schluesselwort fuer Einstellungen: PO_Loader
Benoetigt: lib_common.py im gleichen Verzeichnis
Bezieht Daten aus: Firebird-Datenbank

Fuer Ausfuehrung via Intranet muessen die Ausfuehrungsrechte erweitert werden:
chmod o+x srb-tools/play_out_loader.py

Parameterliste:
Von PO_Loader:
P1 Zeitansage on/off
P2 Jingle on/off
P3 Jingle senden wenn InfoTime-Beitraege vorhanden sind ? on/off
P4 Infotime on/off
P5 Instrumental on/off
P6 Magazin on/off
P7 Fader on/off
P8 mAirlist-Playlist schreiben on/off

Extern Parameters:
PO_Playlists:
Param_1: Pfad Playlist mpd Infotime
Param_2: Pfad Playlist mpd Sendung
Param_3: Pfad Playlist mpd Rotation Instrumentals
Param_4: Pfad Playlist mpd Jingles
Param_5: LW:\Pfad\Dateiname - Playlist für mAirList Server A
Param_6: LW:\Pfad\Dateiname - Playlist für mAirList Server B
Param_7: Pfad mAirlist_IT fuer mAirlist
Param_8: Pfad mAirlist Sendung fuer mAirlist
Param_9: Pfad mAirlist Instrumentals fuer mAirlist
Param_10: Pfad mAirlist Jingles fuer mAirlist
Param_11: Sub-Path Instrumentals from server to folder play-out-rotation

PO_Time_Config:
Param 1: Beginn Tagesstunde Infotime und Magazin
Param 2: Ende Tagesstunde Infotime und Magazin
Param 3: Beginn normale Sendung 1 oder Beginn Info-Time
(kann in der Regel nur 00 sein!!!)
Param 4: Beginn normale Sendung 2 (Ende Info-Time)
Param 5: Beginne normale Sendung 3
Param 6: Interval (Abstand) der Magazin-Beitraege in Minuten (zweistellig)
Param 7: Beginn Infotime Serie B (stunde zweistellig)
Param 8: Interval (Abstand) der Infotime-Beitraege in Sekunden (zweistellig)

PO_Zeitansage_Config:
Param 1: Datei mit Stille zum faden
Param 2: Pfad von mpd zu Zeitansagen-Audios
Param 3: Pfad - Files - Zeitansagen von mAirList zu Audios

PO_Switch_Broadcast_Config:
Param 1: ON/Off-Switch
Param 2: Pfad\Dateiname Sendeumschalterdatei Server A
Param 3: Pfad\Dateiname Sendeumschalterdatei Server B

server_settings
server_settings_paths_a
server_settings_paths_b

Fehlerliste:
Error 000 Parameter-Typ oder Inhalt stimmt nicht
Error 001 beim Lesen Parameter mAirlist
Error 002 beim Lesen Parameter InfoTime Pfade
Error 003 beim Lesen Parameter Times
Error 004 beim Lesen Parameter Zeitansage
Error 005 beim Lesen Parameter Audioswitch
Error 006 beim Loeschen der Playlist
Error 007 beim Schreiben der Playlist
Error 008 beim Schreiben der Audio-Switch Steuerdatei
Error 009 beim Lesen der Zeitansage
Error 010 beim Lesen des Jingles
Error 011 beim Lesen des Instrumentals
Error 012 beim Lesen der Laenge von Instrumentals
Error 013 beim Loeschen der Magazin-Playlist
Error 014 Instrumental-Playlist Erstellung abgebrochen

Funktionsweise
1. Bereitstellen der vorgesehenen "normalen" Sendungen
2. Loeschen der alten Playlisten
3. Bereitstellen der "Schaltpunkte" fuer Audioquellenswitch
4. Bereitstellen von Infotime-Sendungen wenn vorgesehen
5. Bereitstellen von Magazin-Sendungen wenn vorgesehen

This script is preparing all audios for playing out.
Times and filenames are registerd for play-out-scheduler.
It writes a control file for audioswitch.

Dieses Script wird zeitgesteuert (crontab)
kurz vor der vollen Stunde vor der Ausstrahlung ausgefuehrt.
In der Regel also z.B. ca. 11:56 Uhr

"""

import sys
import codecs
import string
import datetime
import ntpath
from mutagen.mp3 import MP3
import lib_common_1 as lib_cm


class app_config(object):
    """Application-Config"""
    def __init__(self):
        """Settings"""
        # app_config
        self.app_id = "009"
        self.app_desc = "play_out_loader"
        # Developmod (other parameter, e.g. paths)
        self.app_develop = "no"
        # debug-mod
        # must set to "no" if running per chronjob!
        self.app_debug_mod = "no"
        # this sript is running under Windows
        self.app_windows = "no"
        # key of config in db
        self.app_config = "PO_Loader"
        self.app_config_develop = "PO_Loader"
        self.app_errorfile = "error_play_out_loader.log"
        self.app_config_params_range = 8
        # params-type-list
        self.app_params_type_list = []
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_string")
        self.app_params_type_list.append("p_string")
        # errorlist
        self.app_errorslist = []
        self.app_errorslist.append(self.app_desc +
            " Parameter-Typ oder Inhalt stimmt nicht")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Lesen Parameter mAirlist")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Lesen Parameter InfoTime Pfade")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Lesen Parameter Times")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Lesen Parameter Zeitansage")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Lesen Parameter Audioswitch")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Loeschen der Playlist")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Schreiben der Playlist")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Schreiben der Audio-Switch Steuerdatei")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Lesen der Zeitansage")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Lesen des Jingles")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Lesen des Instrumentals")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Lesen der Laenge von Instrumentals")
        self.app_errorslist.append(self.app_desc +
            " Fehler beim Loeschen der Magazin-Playlist")
        self.app_errorslist.append(self.app_desc +
            " Fehler bei Instrumental-Playlist-Erstellung")
        self.random_file_error = 0
        # mAirlist-Playlist is running under Windows
        self.pl_win_mairlist = "yes"
        # mpd-Playlist is running under Windows
        self.pl_win_mpd = "no"
        # transmitt IT
        self.po_it = None
        # Magazines play-out
        self.po_mg = []
        self.po_mg.append(True)
        self.po_mg.append(True)
        self.po_mg.append(True)
        # transmitt Instrumental
        self.po_instrumental = None
        # Switch switchpoints
        self.po_switch = []
        self.po_switch.append("03")
        self.po_switch.append("03")
        self.po_switch.append("03")
        # List for mAirlist-playlist Infotime-Items
        self.po_it_pl = []
        # List for mpd-playlist Infotime-Items
        self.po_it_pl_mpd = []
        # Duration of InfoTime
        self.po_it_duration = 0
        # for now
        #self.time_target = datetime.datetime.now()
        # for comming hour
        self.time_target = datetime.datetime.now() + datetime.timedelta(hours=1)


def load_extended_params():
    """load extended params"""
    # paths playlists etc
    db.ac_config_playlist = db.params_load_1a(ac, db, "PO_Playlists")
    if db.ac_config_playlist is not None:
        # Set additionaly Params
        app_params_type_list_playlist = []
        # Types of Params
        app_params_type_list_playlist.append("p_string")
        app_params_type_list_playlist.append("p_string")
        app_params_type_list_playlist.append("p_string")
        app_params_type_list_playlist.append("p_string")
        app_params_type_list_playlist.append("p_string")
        app_params_type_list_playlist.append("p_string")
        app_params_type_list_playlist.append("p_string")
        app_params_type_list_playlist.append("p_string")
        app_params_type_list_playlist.append("p_string")
        app_params_type_list_playlist.append("p_string")
        app_params_type_list_playlist.append("p_string")
        # Check types
        param_check_mairlist = lib_cm.params_check_a(
                        ac, db, 11,
                        app_params_type_list_playlist,
                        db.ac_config_playlist)
        if param_check_mairlist is None:
            db.write_log_to_db_a(ac, ac.app_errorslist[1], "x",
            "write_also_to_console")
            return None

    # Times
    db.ac_config_times = db.params_load_1a(
                            ac, db, "PO_Time_Config_1")
    if db.ac_config_times is not None:
        # Set additionaly Params
        app_params_type_list_times = []
        # Types of Params
        app_params_type_list_times.append("p_string")
        app_params_type_list_times.append("p_string")
        app_params_type_list_times.append("p_string")
        app_params_type_list_times.append("p_string")
        app_params_type_list_times.append("p_string")
        app_params_type_list_times.append("p_string")
        app_params_type_list_times.append("p_string")
        app_params_type_list_times.append("p_string")
        # Check types
        param_check_times = lib_cm.params_check_a(
                        ac, db, 8,
                        app_params_type_list_times,
                        db.ac_config_times)
        if param_check_times is None:
            db.write_log_to_db_a(ac, ac.app_errorslist[3], "x",
            "write_also_to_console")
            return None

    # Zeitansage
    db.ac_config_zeitansage = db.params_load_1a(
                            ac, db, "PO_Zeitansage_Config")
    if db.ac_config_zeitansage is not None:
        # Set additionaly Params
        app_params_type_list_zeitansage = []
        # Types of Params
        app_params_type_list_zeitansage.append("p_string")
        app_params_type_list_zeitansage.append("p_string")
        app_params_type_list_zeitansage.append("p_string")
        app_params_type_list_zeitansage.append("p_string")

        # Check types
        param_check_zeitansage = lib_cm.params_check_a(
                        ac, db, 4,
                        app_params_type_list_zeitansage,
                        db.ac_config_zeitansage)
        if param_check_zeitansage is None:
            db.write_log_to_db_a(ac, ac.app_errorslist[4], "x",
            "write_also_to_console")
            return None

    # Audioswitch
    db.ac_config_audioswitch = db.params_load_1a(
                            ac, db, "PO_Switch_Broadcast_Config")
    if db.ac_config_audioswitch is not None:
        # Set additionaly Params
        app_params_type_list_audioswitch = []
        # Types of Params
        app_params_type_list_audioswitch.append("p_string")
        app_params_type_list_audioswitch.append("p_string")
        app_params_type_list_audioswitch.append("p_string")
        # Check types
        param_check_audioswitch = lib_cm.params_check_a(
                        ac, db, 3,
                        app_params_type_list_audioswitch,
                        db.ac_config_audioswitch)
        if param_check_audioswitch is None:
            db.write_log_to_db_a(ac, ac.app_errorslist[5], "x",
            "write_also_to_console")
            return None

    # extern tools, server-settings
    ext_params_ok = True
    ext_params_ok = lib_cm.params_provide_tools(ac, db)
    if ext_params_ok is None:
        return None
    ext_params_ok = lib_cm.params_provide_server_settings(ac, db)
    if ext_params_ok is None:
        return None
    lib_cm.set_server(ac, db)
    ext_params_ok = lib_cm.params_provide_server_paths_a(ac, db,
                                                        ac.server_active)
    if ext_params_ok is None:
        return None
    ext_params_ok = lib_cm.params_provide_server_paths_b(ac, db,
                                                        ac.server_active)
    return ext_params_ok


def load_broadcast(minute_start, minute_end):
    """load shows from db"""
    list_sendung_filename = []
    list_sendung_duration = []
    list_sendung_source = []
    int_sum_duration = 0
    list_sendung_title = []

    db_tbl_condition = ("A.SG_HF_ON_AIR = 'T' AND "
            "SUBSTRING(A.SG_HF_TIME FROM 1 FOR 10) = '"
            + str(ac.time_target.date()) + "' "
            "AND SUBSTRING(A.SG_HF_TIME FROM 12 FOR 2) = '"
            + str(ac.time_target.hour).zfill(2) + "' "
            "AND SUBSTRING(A.SG_HF_TIME FROM 15 FOR 2) >= '"
            + minute_start + "' "
            "AND SUBSTRING(A.SG_HF_TIME FROM 15 FOR 2) <= '"
            + minute_end + "' "
            "AND A.SG_HF_INFOTIME='F' AND A.SG_HF_MAGAZINE='F' ")
    sendung_data = db.read_tbl_rows_sg_cont_ad_with_cond(ac,
                                            db, db_tbl_condition)

    if sendung_data is None:
        log_message = (u"Keine Sendungen für: " + str(ac.time_target.date())
                     + " " + str(ac.time_target.hour) + ":" + minute_start)
        db.write_log_to_db_a(ac, log_message, "t", "write_also_to_console")
        list_sendung_filename.append("nix")
        list_sendung_source.append("nix")
        list_result = [list_sendung_filename, int_sum_duration,
                            list_sendung_source]
        lib_cm.message_write_to_console(ac, "load_broadcast list_result: ")
        lib_cm.message_write_to_console(ac, list_result)
        return list_result

    # write in list
    log_message = (u"Sendungen vorhanden für: " + str(ac.time_target.date())
                     + " " + str(ac.time_target.hour) + ":" + minute_start)
    db.write_log_to_db_a(ac, log_message, "t", "write_also_to_console")

    for row in sendung_data:
        hh = row[3][0:2]
        mm = row[3][3:5]
        ss = row[3][6:8]

        int_sum_duration = (int(hh) * 60 * 60) + (int(mm) * 60) + int(ss)
        # list with filename and seconds
        list_sendung_filename.append(row[12])
        list_sendung_source.append(row[7])
        list_sendung_duration.append(int_sum_duration)
        list_sendung_title.append(row[11])

    int_sum_duration = int_sum_duration / 60
    list_result = [list_sendung_filename, list_sendung_duration,
         int_sum_duration, list_sendung_source, list_sendung_title]
    lib_cm.message_write_to_console(ac, "load_broadcast list_result: ")
    lib_cm.message_write_to_console(ac, list_result)
    return list_result


def load_infotime(sende_stunde_start):
    """load InfoTime-reports from db"""
    list_sendung_filename = []
    list_sendung_duration = []
    int_sum_duration = 0

    db_tbl_condition = ("A.SG_HF_ON_AIR = 'T' AND "
            "SUBSTRING(A.SG_HF_TIME FROM 1 FOR 10) = '"
            + str(ac.time_target.date()) + "' "
            "AND SUBSTRING(A.SG_HF_TIME FROM 12 FOR 2) = '"
            + sende_stunde_start + "' "
            "AND A.SG_HF_INFOTIME='T' AND A.SG_HF_MAGAZINE='F' ")
    sendung_data = db.read_tbl_rows_sg_cont_ad_with_cond(ac,
                                                 db, db_tbl_condition)

    if sendung_data is None:
        log_message = (u"Keine IT-Sendungen für: "
                 + str(ac.time_target.date()) + " " + str(ac.time_target.hour))
        db.write_log_to_db_a(ac, log_message, "t", "write_also_to_console")
        list_sendung_filename.append("nix")
        #list_result with lenght IT 0 minutes:
        list_result = [list_sendung_filename, 0, int_sum_duration]
        lib_cm.message_write_to_console(ac, "load_infotime list_result: ")
        lib_cm.message_write_to_console(ac, list_result)
        return list_result

    # write in list
    log_message = (u"IT-Sendungen vorhanden für: " + str(ac.time_target.date())
                     + " " + str(ac.time_target.hour))
    db.write_log_to_db_a(ac, log_message, "t", "write_also_to_console")

    for row in sendung_data:
        hh = row[3][0:2]
        mm = row[3][3:5]
        ss = row[3][6:8]

        int_sum_duration = (int(hh) * 60 * 60) + (int(mm) * 60) + int(ss)
        # list with filename and seconds
        list_sendung_filename.append(row[12])
        list_sendung_duration.append(int_sum_duration)

    int_sum_duration = int_sum_duration / 60
    list_result = [list_sendung_filename, list_sendung_duration,
         int_sum_duration]
    lib_cm.message_write_to_console(ac, "load_infotime list_result: ")
    lib_cm.message_write_to_console(ac, list_result)
    return list_result


def rock_sendung(minute_start, minute_end):
    """collect shows"""
    # load broadcast from db
    lib_cm.message_write_to_console(ac, minute_start + minute_end)
    list_result = load_broadcast(minute_start, minute_end)
    # Infotime ist in app-config deaktiviert
    # Wenn Keine Sendungen, dann IT aktivieren
    # Magazin ist in app-config aktiviert
    # Wenn Keine oder kurze Sendungen dann entspr. Mags aktivieren

    if minute_start == "00":
        if list_result[0][0] == "nix":
            # KEINE Sendungen vorhanden
            # Volle Stunde entscheidet ueber IT
            # Wenn keine Sendungen vorhanden, dann IT!
            ac.po_it = True
            log_message = "Infotime vorsehen!"
            db.write_log_to_db_a(ac, log_message, "p", "write_also_to_console")
        else:
            log_message = "Infotime wird nicht gesendet!"
            db.write_log_to_db_a(ac, log_message, "e", "write_also_to_console")
            # Quelle fuer Switch einstellen
            # Quelle befindet sich an Postition 0
            # der vierten liste [3] innerhalb der liste 'list_result'
            ac.po_switch[0] = list_result[3][0][:2]
            ac.po_switch[1] = list_result[3][0][:2]
            ac.po_switch[2] = list_result[3][0][:2]
            # Magazin nur in Abhaegigkeit der Laenge der Sendungen
            if list_result[2] > 5:
                ac.po_mg[0] = None
            if list_result[2] > 25:
                ac.po_mg[1] = None
            if list_result[2] > 35:
                ac.po_mg[2] = None

    if minute_start > "00" and minute_start < "30":
        if list_result[0][0] != "nix":
            # Sendungen vorhanden
            # Quelle fuer Switch 2 und 3 einstellen
            # Quelle befindet sich an Postition 0
            # der vierten liste [3] innerhalb der liste 'list_result'
            ac.po_switch[1] = list_result[3][0][:2]
            ac.po_switch[2] = list_result[3][0][:2]
            # Instrumental nach IT senden
            ac.po_instrumental = True
            # In Abhaegigkeit der Laenge der Sendungen
            # Magazin 1
            if list_result[2] > 5:
                ac.po_mg[0] = None
            # Magazin 2
            if list_result[2] > 20:
                ac.po_mg[1] = None
            if list_result[2] > 35:
                ac.po_mg[2] = None

    if minute_start == "30":
        if list_result[0][0] != "nix":
            # Sendungen vorhanden
            # Quelle fuer Switch 3 einstellen
            # Quelle befindet sich an Postition 0
            # der vierten liste [3] innerhalb der liste 'list_result'
            ac.po_switch[2] = list_result[3][0][:2]
            # Magazin 2 nicht senden
            ac.po_mg[1] = None
            # Magazin 3 nur in Abhaegigkeit der Laenge der Sendungen
            if list_result[2] > 5:
                ac.po_mg[2] = None
    # PL schreiben
    prepare_pl_broadcast(minute_start, list_result)


def prepare_pl_broadcast(minute_start, list_result):
    """Playlist fuer Sendungen schreiben"""

    if minute_start == "00":
        nZ_po_switch = 0
        if ac.server_active == "A":
            path_filename = db.ac_config_playlist[5] + "_00.m3u"
        if ac.server_active == "B":
            path_filename = db.ac_config_playlist[6] + "_00.m3u"
    if minute_start > "00" and minute_start < "30":
        nZ_po_switch = 1
        if ac.server_active == "A":
            path_filename = (db.ac_config_playlist[5] + "_"
                                + minute_start + ".m3u")
        if ac.server_active == "B":
            path_filename = (db.ac_config_playlist[6] + "_"
                                + minute_start + ".m3u")
    if minute_start == "30":
        nZ_po_switch = 2
        if ac.server_active == "A":
            path_filename = db.ac_config_playlist[5] + "_30.m3u"
        if ac.server_active == "B":
            path_filename = db.ac_config_playlist[6] + "_30.m3u"

    # delete mAirlist-Playlist
    if db.ac_config_1[8].strip() == "on":
        lib_cm.message_write_to_console(ac, path_filename)
        delete_pl_ok = lib_cm.erase_file_a(ac, db, path_filename,
            u"Playlist geloescht ")
        if delete_pl_ok is None:
            db.write_log_to_db_a(ac, ac.app_errorslist[6], "x",
                                             "write_also_to_console")
    if list_result[0][0] == "nix":
        log_message = "Keine normale Sendung, keine PL schreiben!"
        lib_cm.message_write_to_console(ac, log_message)
        return

    # PL write only if necessary
    if len(list_result[0]) == 1 and ac.po_switch[nZ_po_switch] != "03":
        log_message = (u"Sendung nicht via Play-Out,"
                " keine PL geschrieben: " + "".join(list_result[4]))
        db.write_log_to_db_a(ac, log_message, "e", "write_also_to_console")
        db.write_log_to_db(ac, "Sendung live: " + "".join(list_result[4]), "i")
    else:
        write_playlist(
            path_filename, list_result[0], list_result[1], minute_start)


def write_playlist(
    path_filename, list_sendung_filename, list_sendung_duration, minute_start):
    """
    Write Playlist
    mpd will take t from logging-db,
    mairlist from file
    """
    path_mediafile_mpd = lib_cm.check_slashes_a(ac,
                             db.ac_config_playlist[2], ac.pl_win_mpd)
    z = 0
    action_msg = ""
    log_message_pl = ""
    for item in list_sendung_filename:
        if item[0:7] == "http://":
            action_msg = "Sendung: " + item[8:-1]
            log_message_pl = ("Playlist Sendung " + str(minute_start) + ": "
                    + item)
        else:
            action_msg = "Sendung: " + item
            log_message_pl = ("Playlist Sendung " + str(minute_start) + ": "
                    + path_mediafile_mpd + item)

        log_message = "Sendung " + str(minute_start) + ": " + item
        db.write_log_to_db(ac, action_msg, "i")
        db.write_log_to_db(ac, log_message_pl, "k")
        z += 1

    # mAirlist
    if db.ac_config_1[8].strip() != "on":
        log_message = ("mAirlist-Playlist ist deaktiviert.."
                            + "keine Playlist geschrieben!")
        db.write_log_to_db(ac, log_message, "e")
        return

    try:
        if (ac.app_windows == "yes"):
            f_playlist = codecs.open(path_filename, 'w', "iso-8859-1")
        else:
            f_playlist = codecs.open(path_filename, 'w', "utf-8")

    except IOError as (errno, strerror):
        log_message = ("write_to_file_playlist_broadcast: I/O error({0}): {1}"
        .format(errno, strerror) + ": "
         + path_filename.encode('ascii', 'ignore'))
        db.write_log_to_db_a(ac, log_message, "x", "write_also_to_console")
        db.write_log_to_db_a(ac, ac.app_errorslist[7], "x",
                                             "write_also_to_console")
        return

    path_mediafile = lib_cm.check_slashes_a(ac,
                             db.ac_config_playlist[8], ac.pl_win_mairlist)
    z = 0
    action_msg = ""
    log_message_pl = ""
    for item in list_sendung_filename:
        if item[0:7] == "http://":
            f_playlist.write("#mAirList STREAM "
                 + str(list_sendung_duration[z]) + " [] " + item + "\r\n")
        else:
            # pfad voranstellen
            f_playlist.write(path_mediafile + item + "\r\n")
        z += 1
    f_playlist.close


def write_playlist_it(path_filename):
    """Write Playlist InfoTime"""
    # mpd
    action_msg = ""
    for item in ac.po_it_pl_mpd:
        action_msg = "Infotime: " + ntpath.basename(item)

        log_message = "Playlist Infotime: " + item
        db.write_log_to_db(ac, log_message, "k")

        # Einige Eintraege fuer Info-Meldung uebergehen
        waste = None
        if string.find(action_msg, "Zeitansage") != -1:
            waste = True
        if string.find(action_msg, "SRB_Jingles") != -1:
            waste = True
        if string.find(action_msg, "Instrumental") != -1:
            waste = True
        if waste is None:
            db.write_log_to_db(ac, action_msg, "i")

    if db.ac_config_1[8].strip() != "on":
        log_message = ("mAirlist-Playlist ist deaktiviert.."
                            + "keine Playlist geschrieben!")
        db.write_log_to_db(ac, log_message, "e")
        return
    try:
        if (ac.app_windows == "yes"):
            f_playlist = codecs.open(path_filename, 'w', "iso-8859-1")
        else:
            f_playlist = codecs.open(path_filename, 'w', "utf-8")

    except IOError as (errno, strerror):
        log_message = ("write_to_file_playlist_infotime: I/O error({0}): {1}"
        .format(errno, strerror) + ": "
         + path_filename.encode('ascii', 'ignore'))
        db.write_log_to_db_a(ac, log_message, "x", "write_also_to_console")
        db.write_log_to_db_a(ac, ac.app_errorslist[7], "x",
                                             "write_also_to_console")
        return

    # mairlist
    for item in ac.po_it_pl:
        # Win Zeilenumbruch hinten dran
        f_playlist.write(item + "\r\n")

    f_playlist.close


def write_playlist_mg(path_file_pl, file_mg, mg_number):
    """write Playlist Magazine"""
    path_mg_mpd = lib_cm.check_slashes_a(ac,
                         db.ac_config_playlist[1], ac.pl_win_mpd)
    log_message = ("Playlist Magazin " + str(mg_number) + ": "
                                    + path_mg_mpd + file_mg)
    db.write_log_to_db_a(ac, log_message, "k", "write_also_to_console")
    log_message = "Magazin: " + file_mg
    db.write_log_to_db_a(ac, log_message, "i", "write_also_to_console")

    if db.ac_config_1[8].strip() != "on":
        log_message = ("mAirlist-Playlist ist deaktiviert.."
                            + "keine Playlist geschrieben!")
        db.write_log_to_db(ac, log_message, "e")
        return

    try:
        if (ac.app_windows == "yes"):
            f_playlist = codecs.open(path_file_pl, 'w', "iso-8859-1")
        else:
            f_playlist = codecs.open(path_file_pl, 'w', "utf-8")

    except IOError as (errno, strerror):
        log_message = ("write_to_file_playlist_magazin: I/O error({0}): {1}"
        .format(errno, strerror) + ": "
         + path_file_pl.encode('ascii', 'ignore'))
        db.write_log_to_db_a(ac, log_message, "x", "write_also_to_console")
        db.write_log_to_db_a(ac, ac.app_errorslist[7], "x",
                                             "write_also_to_console")
        return

    path_mg = lib_cm.check_slashes_a(ac,
                         db.ac_config_playlist[7], ac.pl_win_mairlist)

    path_file_mg = path_mg + file_mg
    f_playlist.write(path_file_mg + "\r\n")
    f_playlist.close


def write_to_file_switch_params():
    """Switch Steuerdatei schreiben"""
    # WICHTIG: der log_text wird von play_out_logging gesucht
    # um die audio_switch_prameter zu finden
    ac.action_summary = (u"Sendequellen: "
                 + ac.po_switch[0] + ac.po_switch[1] + ac.po_switch[2])
    db.write_log_to_db(ac, ac.action_summary, "i")
    #log_message = ("Switch 1-3: " + ac.po_switch[0]
    #                     + ac.po_switch[1] + ac.po_switch[2])
    #db.write_log_to_db_a(ac, log_message, "t", "write_also_to_console")

    # on/off switch from params for writing file
    if db.ac_config_audioswitch[1].strip() == "off":
        db.write_log_to_db_a(ac,
                    "Schreiben der Datei fuer Sendeschalter ist deaktiviert",
                                     "e", "write_also_to_console")
        return

    if ac.server_active == "A":
        file_audio_switch = db.ac_config_audioswitch[2]
    if ac.server_active == "B":
        file_audio_switch = db.ac_config_audioswitch[3]
    #print "ausioswitch" + file_audio_switch
    data_audio_switch = read_from_file_lines_in_list(file_audio_switch)
    #print data_audio_switch
    if data_audio_switch is None:
        log_message = (u"Datei für Sendequellenumschalter "
                    "kann nicht gelesen werden: " + file_audio_switch)
        db.write_log_to_db_a(ac, log_message, "x", "write_also_to_console")
        return

    try:
        f_switch = open(file_audio_switch, 'w')
    except IOError as (errno, strerror):
        log_message = ("write_to_file_switch_params: I/O error({0}): {1}"
                        .format(errno, strerror) + ": " + file_audio_switch)
        db.write_log_to_db(ac, log_message, "x")
        db.write_log_to_db_a(ac, ac.app_errorslist[8], "x",
                                             "write_also_to_console")
    else:
        f_switch.write(str(ac.time_target.hour).zfill(2)
                                 + ":00 #" + ac.po_switch[0] + "\r\n")
        minute_zweiter_schaltpunkt = db.ac_config_times[4]
        f_switch.write(str(ac.time_target.hour).zfill(2)
        + ":" + minute_zweiter_schaltpunkt + " #" + ac.po_switch[1] + "\r\n")
        f_switch.write(str(ac.time_target.hour).zfill(2)
                                 + ":30 #" + ac.po_switch[2] + "\r\n")
        f_switch.write(data_audio_switch[0])
        f_switch.write(data_audio_switch[1])
        f_switch.write(data_audio_switch[2])
        f_switch.write("Parameter fuer Sendequellenumschalter:"
                                        " hh:mm #Quell-Nr. am Switch\r\n")
        f_switch.close

        log_message = (u"Datei für Sendequellenumschalter geschrieben: "
                 + ac.po_switch[0] + ac.po_switch[1] + ac.po_switch[2])
        db.write_log_to_db_a(ac, log_message, "k", "write_also_to_console")


def read_zeitansage():
    """Zeitansage abarbeiten"""
    # path from von play_out_loader to Zeitansage
    path_zeitansage = (lib_cm.check_slashes(ac, db.ac_config_servpath_a[12])
                    + str(ac.time_target.hour).zfill(2))
    # path from mAirlist to Zeitansage
    path_zeitansage_po = (lib_cm.check_slashes_a(ac,
                         db.ac_config_zeitansage[3], ac.pl_win_mairlist)
                    + str(ac.time_target.hour).zfill(2))
    path_zeitansage_po = (lib_cm.check_slashes_a(ac,
                             path_zeitansage_po, ac.pl_win_mairlist))
    # path from mpd to Zeitansage
    path_zeitansage_po_mpd = (lib_cm.check_slashes_a(ac,
                         db.ac_config_zeitansage[2], ac.pl_win_mpd)
                    + str(ac.time_target.hour).zfill(2))
    path_zeitansage_po_mpd = (lib_cm.check_slashes_a(ac,
                             path_zeitansage_po_mpd, ac.pl_win_mpd))
    # Zeitansage zu passender Zeit per Zufall aus Pool holen
    file_zeitansage = lib_cm.read_random_file_from_dir(ac, db, path_zeitansage)
    if file_zeitansage is None:
        db.write_log_to_db_a(ac, ac.app_errorslist[9], "x",
                                             "write_also_to_console")
    else:
        # mairlist
        ac.po_it_pl.append(path_zeitansage_po + file_zeitansage)
        lib_cm.message_write_to_console(ac, ac.po_it_pl)
        # mpd
        ac.po_it_pl_mpd.append(path_zeitansage_po_mpd + file_zeitansage)
        lib_cm.message_write_to_console(ac, ac.po_it_pl_mpd)


def read_jingle():
    """work on Jingles"""
    # path from play_out_loader to Jingles
    path_jingle = (lib_cm.check_slashes(ac, db.ac_config_servpath_a[11]))
    # path from mAirlist to Jingle
    path_jingle_po = (lib_cm.check_slashes_a(ac,
                         db.ac_config_playlist[10], ac.pl_win_mairlist))
    #path_jingle_po = (lib_cm.check_slashes_a(ac,
    #                                 path_jingle_po, ac.pl_win_mairlist))
    # Pfad von mpd zu Jingle
    path_jingle_po_mpd = (lib_cm.check_slashes_a(ac,
                         db.ac_config_playlist[4], ac.pl_win_mpd))
    #path_jingle_po_mpd = (lib_cm.check_slashes_a(ac,
    #                                 path_jingle_po_mpd, ac.pl_win_mpd))
    # random jingle
    file_jingle = lib_cm.read_random_file_from_dir(ac, db, path_jingle)
    if file_jingle is None:
        db.write_log_to_db_a(ac, ac.app_errorslist[10], "x",
                                             "write_also_to_console")
    else:
        if db.ac_config_1[1].strip() == "on":
            # if Zeitansage, jingle after zeitansage
            # mairlist
            ac.po_it_pl.insert(1, path_jingle_po + file_jingle)
            # mpd
            ac.po_it_pl_mpd.insert(1, path_jingle_po_mpd + file_jingle)
        else:
            # mairlsit
            ac.po_it_pl.insert(0, path_jingle_po + file_jingle)
            # mpd
            ac.po_it_pl_mpd.insert(0, path_jingle_po_mpd + file_jingle)
        lib_cm.message_write_to_console(ac, ac.po_it_pl_mpd)


def read_infotime():
    """InfoTime-Beitraege sammeln"""
    # Zeitfenster fuer InfoTime
    if (str(ac.time_target.hour).zfill(2) >= db.ac_config_times[1]
        and str(ac.time_target.hour).zfill(2) < db.ac_config_times[2]):
        # Im Zeifenster!
        # erst auf feste (kommende) Stunde gebuchte IT suchen
        time_target_start = (datetime.datetime.now()
                                 + datetime.timedelta(hours=+1))
        list_result = load_infotime(time_target_start.strftime("%H"))
        # keine feste IT Buchung, normale nehmen
        if list_result[0][0] == "nix":
            db.write_log_to_db_a(ac,
                "Keine fest gebuchte Info-Time-Sendung vorhanden fuer: "
                                     + str(ac.time_target.hour),
                                     "e", "write_also_to_console")
            if ac.time_target.hour > 0 and ac.time_target.hour % 2 != 0:
                db.write_log_to_db_a(ac, "IT: ungerade Stunde pruefen",
                                     "p", "write_also_to_console")
                list_result = load_infotime(db.ac_config_times[7])
            else:
                db.write_log_to_db_a(ac, "IT: gerade Stunde pruefen",
                                     "p", "write_also_to_console")
                list_result = load_infotime(db.ac_config_times[1])
    else:
        db.write_log_to_db_a(ac, "Ausserhalb des InfoTime Zeitfensters!",
                                     "e", "write_also_to_console")
        return None

    if list_result[0][0] == "nix":
        db.write_log_to_db_a(ac, "Keine InfoTime Sendungen vorhanden",
                                     "e", "write_also_to_console")
        return None

    # Laenge fuer Instrumentals
    ac.po_it_duration = list_result[2]

    # path from mAirlist to InfoTime
    path_it_po = lib_cm.check_slashes_a(ac,
                             db.ac_config_playlist[7], ac.pl_win_mairlist)
    # path from mpd to InfoTime
    path_it_po_mpd = lib_cm.check_slashes_a(ac,
                             db.ac_config_playlist[1], ac.pl_win_mpd)
    # Filenames mit Path in List
    for item in list_result[0]:
        # mairlist
        ac.po_it_pl.append(path_it_po + item)
        # mpd
        ac.po_it_pl_mpd.append(path_it_po_mpd + item)
    return True


def read_instrumental():
    """collect Instrumentals"""
    # path from play_out_loader to Instrumentals
    path_rotation = lib_cm.check_slashes(ac, db.ac_config_servpath_a[4])
    path_instrumental = (path_rotation
                    + lib_cm.check_slashes(ac, db.ac_config_playlist[11]))
    # path from mAirlist to Instrumentals
    path_instrumental_po = (lib_cm.check_slashes_a(ac,
                             db.ac_config_playlist[9], ac.pl_win_mairlist))
    # path from mpd to Instrumentals
    path_instrumental_po_mpd = (lib_cm.check_slashes_a(ac,
                             db.ac_config_playlist[3], ac.pl_win_mpd))
    # for summary length
    duration_minute_instr = 0
    duration_minute_target = int(db.ac_config_times[4]) - ac.po_it_duration
    lib_cm.message_write_to_console(ac, "Duration in Minuten")
    lib_cm.message_write_to_console(ac, str(ac.po_it_duration))

    # Instrumentals sammeln bis erforderliche Gesamtlaenge erreicht
    while (duration_minute_instr < duration_minute_target):
        if ac.random_file_error >= 5:
            db.write_log_to_db(ac, ac.app_errorslist[14], "x")
            ac.random_file_error = 0
            return
        file_instrumental = lib_cm.read_random_file_from_dir(ac,
                                         db, path_instrumental)
        if file_instrumental is None:
            db.write_log_to_db_a(ac, ac.app_errorslist[11], "x",
                                             "write_also_to_console")
            ac.random_file_error += 1
            continue
        else:
            # mairlist
            ac.po_it_pl.append(path_instrumental_po + file_instrumental)
            lib_cm.message_write_to_console(ac, ac.po_it_pl)
            # mpd
            ac.po_it_pl_mpd.append(path_instrumental_po_mpd + file_instrumental)
            lib_cm.message_write_to_console(ac, ac.po_it_pl_mpd)
        try:
            audio_instrumental = MP3(path_instrumental + file_instrumental)
            duration_minute_instr += audio_instrumental.info.length / 60
        except Exception, e:
            err_message = "Error by reading duration: %s" % str(e)
            lib_cm.message_write_to_console(ac, err_message)
            db.write_log_to_db_a(ac, ac.app_errorslist[12], "x",
                                             "write_also_to_console")
            db.write_log_to_db_a(ac, path_instrumental, "x",
                                             "write_also_to_console")
            ac.random_file_error += 1
        lib_cm.message_write_to_console(ac, "Duration Instrumental")
        #lib_cm.message_write_to_console(ac, str(audio_instrumental.info.length))
        lib_cm.message_write_to_console(ac, str(duration_minute_instr))


def load_magazin():
    """Magazin-Beitraege aus db holen"""
    list_sendung_filename = []
    list_sendung_duration = []
    int_sum_duration = 0

    db_tbl_condition = ("A.SG_HF_ON_AIR = 'T' AND "
            "SUBSTRING(A.SG_HF_TIME FROM 1 FOR 10) = '"
            + str(ac.time_target.date()) + "' "
            "AND A.SG_HF_INFOTIME='F' AND A.SG_HF_MAGAZINE='T' ")
    sendung_data = db.read_tbl_rows_sg_cont_ad_with_cond(ac,
                                                 db, db_tbl_condition)

    if sendung_data is None:
        log_message = (u"Keine Magazin-Sendungen für: "
                 + str(ac.time_target.date()) + " " + str(ac.time_target.hour))
        db.write_log_to_db_a(ac, log_message, "t", "write_also_to_console")
        list_sendung_filename.append("nix")
        #list_result mit Laenge IT 0 Minuten:
        list_result = [list_sendung_filename, 0, int_sum_duration]
        lib_cm.message_write_to_console(ac, "load_infotime list_result: ")
        lib_cm.message_write_to_console(ac, list_result)
        return list_result

    # in List schreiben
    log_message = (u"Magazin-Sendungen vorhanden für: "
                     + str(ac.time_target.date())
                     + " " + str(ac.time_target.hour))
    db.write_log_to_db_a(ac, log_message, "t", "write_also_to_console")

    for row in sendung_data:
        #print row
        hh = row[3][0:2]
        mm = row[3][3:5]
        ss = row[3][6:8]

        int_sum_duration = (int(hh) * 60 * 60) + (int(mm) * 60) + int(ss)
        # list mit filename und sekunden
        list_sendung_filename.append(row[12])
        list_sendung_duration.append(int_sum_duration)

    int_sum_duration = int_sum_duration / 60
    list_result = [list_sendung_filename, list_sendung_duration,
         int_sum_duration]
    lib_cm.message_write_to_console(ac, "load_magazin list_result: ")
    lib_cm.message_write_to_console(ac, list_result)
    return list_result


def prepare_pl_infotime():
    """Playlist InfoTime vorbereiten"""
    # Fader on top
    # fader prepaere here and not in read_zeitansage,
    # because it can added also when no Zeitansage

    # if fader is set to on
    if db.ac_config_1[7].strip() == "on":
        # mairlist
        path_fader = lib_cm.check_slashes_a(ac,
                             db.ac_config_zeitansage[3], ac.pl_win_mairlist)
        path_file_fader = path_fader + db.ac_config_zeitansage[1]
        ac.po_it_pl.insert(0, path_file_fader)
        # mpd
        path_fader_mpd = lib_cm.check_slashes_a(ac,
                             db.ac_config_zeitansage[2], ac.pl_win_mpd)
        path_file_fader_mpd = path_fader_mpd + db.ac_config_zeitansage[1]
        ac.po_it_pl_mpd.insert(0, path_file_fader_mpd)
    else:
        db.write_log_to_db_a(ac, "Fader ist deaktiviert",
                                     "e", "write_also_to_console")
    lib_cm.message_write_to_console(ac, ac.po_it_pl)
    if ac.server_active == "A":
        path_filename = db.ac_config_playlist[5] + "_00.m3u"
    if ac.server_active == "B":
        path_filename = db.ac_config_playlist[6] + "_00.m3u"
    write_playlist_it(path_filename)


def rock_infotime():
    """Infotime abarbeiten"""
    if db.ac_config_1[1].strip() == "on":
        read_zeitansage()
    else:
        db.write_log_to_db_a(ac, "Zeitansage ist deaktiviert",
                                     "e", "write_also_to_console")
    if db.ac_config_1[4].strip() == "on":
        transmit_it = read_infotime()
    else:
        db.write_log_to_db_a(ac, "InfoTime ist deaktiviert",
                                     "e", "write_also_to_console")
    if db.ac_config_1[2].strip() == "on":
        # Jingle aktiviert
        if db.ac_config_1[3].strip() == "on":
            # Jingle auch bei IT-Beitraegen aktiviert
            read_jingle()
        else:
            if transmit_it is None:
                # Jingle doch wenn keine IT-Betraege vorhanden
                # oder ausserhalb IT-Zeit
                read_jingle()
            else:
                db.write_log_to_db_a(ac, "Jingle bei IT-Sendungen deaktiviert",
                                     "e", "write_also_to_console")

    else:
        db.write_log_to_db_a(ac, "Jingle ist deaktiviert",
                                     "e", "write_also_to_console")

    if db.ac_config_1[5].strip() == "on" and ac.po_instrumental is True:
        read_instrumental()
    else:
        db.write_log_to_db_a(ac, "Instrumental ist deaktiviert "
                    "oder nicht noetig", "e", "write_also_to_console")

    prepare_pl_infotime()


def rock_magazin():
    """Magazin abarbeiten"""
    # Alle PL loeschen
    if db.ac_config_1[8].strip() == "on":
        mag_z = [1, 2, 3]
        for i in mag_z:
            if ac.server_active == "A":
                path_pl_file = (db.ac_config_playlist[5]
                                + "_magazine_0" + str(i) + ".m3u")
            if ac.server_active == "B":
                path_pl_file = (db.ac_config_playlist[6]
                                + "_magazine_0" + str(i) + ".m3u")
            lib_cm.message_write_to_console(ac, path_pl_file)
            delete_pl_ok = lib_cm.erase_file_a(ac, db, path_pl_file,
                                        u"Playlist geloescht ")
            if delete_pl_ok is None:
                db.write_log_to_db_a(ac, ac.app_errorslist[13], "x",
                                             "write_also_to_console")
    # Einstellungen
    if db.ac_config_1[6].strip() == "off":
        db.write_log_to_db_a(ac, "Magazin ist deaktiviert ",
                                     "e", "write_also_to_console")
        return
    # Sendung oder Magazin
    if (ac.po_mg[0] is None and ac.po_mg[1] is None and
                                    ac.po_mg[2] is None):
        db.write_log_to_db_a(ac, "Magazin wird nicht gesendet",
                                     "e", "write_also_to_console")
        return

    # Zeitfenster fuer InfoTime
    if (str(ac.time_target.hour).zfill(2) >= db.ac_config_times[1]
        and str(ac.time_target.hour).zfill(2) < db.ac_config_times[2]):
        list_result = load_magazin()
    else:
        db.write_log_to_db_a(ac,
             "Ausserhalb des InfoTime/ Magazin Zeitfensters!",
                                    "e", "write_also_to_console")
        return

    if list_result[0][0] == "nix":
        db.write_log_to_db_a(ac, "Keine Magazin Sendungen vorhanden",
                                     "e", "write_also_to_console")
        return

    # Anzahl
    nZ_Magazins = len(list_result[0])
    log_message = u"Anzahl Magazinbeitraege: " + str(nZ_Magazins)
    db.write_log_to_db_a(ac, log_message, "t", "write_also_to_console")

    # Bis 3 Stueck
    if nZ_Magazins <= 3:
        zz = 1
        for item in list_result[0]:
            #sendung = item
            if ac.po_mg[zz - 1] is True:
                if ac.server_active == "A":
                    path_file_pl = (db.ac_config_playlist[5]
                                    + "_magazine_0" + str(zz) + ".m3u")
                if ac.server_active == "B":
                    path_file_pl = (db.ac_config_playlist[6]
                                    + "_magazine_0" + str(zz) + ".m3u")
                write_playlist_mg(path_file_pl, item, zz)
            else:
                log_message = (u"Magazinbeitrag "
                     + str(zz) + u" fällt wegen Normalsendung aus")
                db.write_log_to_db_a(ac, log_message, "t",
                                             "write_also_to_console")
            zz += 1

    # Bis 6 Stueck
    if nZ_Magazins > 3 and nZ_Magazins <= 6:
        zz = 1
        mag_hour = ac.time_target.hour
        list_sendung = list_result[0]
        if mag_hour > 0 and mag_hour % 2 == 0:
            # gerade Stunde
            log_message = u"Magazin Serie A geht auf Sendung"
            db.write_log_to_db_a(ac, log_message, "p", "write_also_to_console")

            for index, item in enumerate(list_sendung):
                if index < 3:
                    if ac.po_mg[zz - 1] is True:
                        if ac.server_active == "A":
                            path_file_pl = (db.ac_config_playlist[5]
                                    + "_magazine_0" + str(zz) + ".m3u")
                        if ac.server_active == "B":
                            path_file_pl = (db.ac_config_playlist[6]
                                    + "_magazine_0" + str(zz) + ".m3u")
                        write_playlist_mg(path_file_pl, item, zz)
                    else:
                        log_message = (u"Magazinbeitrag "
                                 + str(zz) + u" fällt wegen Normalsendung aus")
                        db.write_log_to_db_a(ac, log_message, "t",
                                             "write_also_to_console")
                    zz += 1
        else:
            # ungerade Stunde
            log_message = u"Magazin Serie B geht auf Sendung"
            db.write_log_to_db_a(ac, log_message, "p", "write_also_to_console")
            for index, item in enumerate(list_sendung):
                if index > 2:
                    if ac.po_mg[zz - 1] is True:
                        if ac.server_active == "A":
                            path_file_pl = (db.ac_config_playlist[5]
                                    + "_magazine_0" + str(zz) + ".m3u")
                        if ac.server_active == "B":
                            path_file_pl = (db.ac_config_playlist[6]
                                    + "_magazine_0" + str(zz) + ".m3u")
                        write_playlist_mg(path_file_pl, item, zz)
                    else:
                        log_message = (u"Magazinbeitrag "
                                 + str(zz) + u" fällt wegen Normalsendung aus")
                        db.write_log_to_db_a(ac, log_message, "t",
                                             "write_also_to_console")
                    zz += 1

    # up to 9 items
    if nZ_Magazins > 6:
        zz = 1
        list_sendung = list_result[0]
        # diese liste enthaelt 24 items,
        # jedes item enthaelt die startnr der 3 mags,
        # die gesendet werden sollen (1.=0/4.=3/6.=5)
        list_index_sendung_hour = [0, 0, 0, 0, 0, 0, 0, 3, 6, 0, 3, 6, 0,
                                             3, 6, 0, 3, 6, 0, 3, 6, 0, 3, 6]
        # aus list_sendung die 3 mag_sendungen rausholen
        # die in der stunde gesendet werden sollen
        list_sendung_mag = (list_sendung[
                   list_index_sendung_hour[ac.time_target.hour]:
                   list_index_sendung_hour[ac.time_target.hour] + 3])
         # Serie ermitteln und loggen
        n_mag_serie = list_index_sendung_hour[ac.time_target.hour]
        if n_mag_serie == 0:
            log_message = u"Magazin Serie A geht auf Sendung"
        if n_mag_serie == 3:
            log_message = u"Magazin Serie B geht auf Sendung"
        if n_mag_serie == 6:
            log_message = u"Magazin Serie C geht auf Sendung"
        db.write_log_to_db_a(ac, log_message, "p",
                                             "write_also_to_console")
        for index, item in enumerate(list_sendung_mag):
            if ac.po_mg[zz - 1] is True:
                if ac.server_active == "A":
                    path_file_pl = (db.ac_config_playlist[5]
                                    + "_magazine_0" + str(zz) + ".m3u")
                if ac.server_active == "B":
                    path_file_pl = (db.ac_config_playlist[6]
                                    + "_magazine_0" + str(zz) + ".m3u")
                write_playlist_mg(path_file_pl, item, zz)
            else:
                log_message = (u"Magazinbeitrag "
                                 + str(zz) + u" fällt wegen Normalsendung aus")
                db.write_log_to_db_a(ac, log_message, "t",
                                             "write_also_to_console")
            zz += 1


def read_from_file_lines_in_list(filename):
    """write rows from file in list"""
    try:
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
    except IOError as (errno, strerror):
        lines = None
        log_message = ("read_from_file_lines_in_list - I/O error({0}): {1}"
                        .format(errno, strerror) + ": " + filename)
        db.write_log_to_db_a(ac, log_message, "x", "write_also_to_console")
    return lines


def lets_rock():
    print "lets_rock "
    # ext params
    load_extended_params_ok = load_extended_params()
    if load_extended_params_ok is None:
        return
    # Shows 1. startpoint (top of the hour)
    # Minute Start, Minute Ende
    # Minute Ende ist Minute Anfang des naechsten Punktes -1, zw. 59
    minute_start = db.ac_config_times[3]
    minute_end = str(int(db.ac_config_times[4]) - 1).zfill(2)
    rock_sendung(minute_start, minute_end)

    # Shows 2. startpoint
    minute_start = db.ac_config_times[4]
    minute_end = str(int(db.ac_config_times[5]) - 1).zfill(2)
    rock_sendung(minute_start, minute_end)

    # Shows 3. startpoint
    minute_start = db.ac_config_times[5]
    minute_end = "59"
    rock_sendung(minute_start, minute_end)

    # Audioswitch
    write_to_file_switch_params()
    # InfoTime
    if ac.po_it is not None:
        rock_infotime()
    # Magazine
    rock_magazin()


if __name__ == "__main__":
    db = lib_cm.dbase()
    ac = app_config()
    print  "lets_work: " + ac.app_desc
    db.write_log_to_db(ac, ac.app_desc + " gestartet", "a")
    # Config_Params 1
    db.ac_config_1 = db.params_load_1(ac, db)
    if db.ac_config_1 is not None:
        param_check = lib_cm.params_check_1(ac, db)
        # alles ok: weiter
        if param_check is not None:
            lets_rock()

    # fertsch
    db.write_log_to_db(ac, ac.app_desc + " gestoppt", "s")
    print "lets_lay_down"
    sys.exit()