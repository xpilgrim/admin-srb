<?php

/** 
* sendung details anzeigen 
*
* PHP version 5
*
* @category Intranetsite
* @package  Admin-SRB
* @author   Joerg Sorge <joergsorge@googel.com>
* @license  http://www.gnu.org/copyleft/gpl.html GNU General Public License
* @link     http://srb.fm
*/

require "../../cgi-bin/admin_srb_libs/lib_db.php";
require "../../cgi-bin/admin_srb_libs/lib.php";
require "../../cgi-bin/admin_srb_libs/lib_sess.php";
$message = "";
$error_message = "";
$manuskript_vorhanden = false;
if ( isset( $_GET['message'] ) ) { 
	$message .= $_GET['message'];
}
if ( isset( $_POST['message'] ) ) { 
	$message .= $_POST['message'];
}
if ( isset( $_GET['error_message'] ) ) { 
	$error_message .= $_GET['error_message'];
}
if ( isset( $_POST['error_message'] ) ) { 
	$error_message .= $_POST['error_message'];
}
if ( isset( $_GET['po_filename'] ) ) { 
	$po_filename = $_GET['po_filename'];
}
if ( isset( $_GET['po_it'] ) ) { 
	$po_it = $_GET['po_it'];
}
if ( isset( $_GET['po_mg'] ) ) { 
	$po_mg = $_GET['po_mg'];
}

$action_ok = "no";
// Dateipruefung ja/nein
$file_exist_check = "yes";
	
// action pruefen	
if ( isset( $_GET['action'] ) ) {
	$action = $_GET['action'];	
	$action_ok = "yes";
}
if ( isset( $_POST['action'] ) ) { 
	$action = $_POST['action'];
	$action_ok = "yes";
}
			
if ( $action_ok == "yes" ) {
	if ( isset( $_GET['sg_id'] ) ) {	
		$id = $_GET['sg_id'];
	}
	if ( isset( $_POST['sg_id'] ) ) {
		$id = $_POST['sg_id'];
	}
		
	// Audiodatei pruefen oder nicht (nach Neuaufnahme nicht pruefen, da ja noch keine da sein kann)
	if ( isset( $_GET['check_file'] ) ) {	
		$file_exist_check = $_GET['check_file'];
	}
			
	// action switchen
	if ( $id !="" ) { 
		switch ( $action ) {
		case "display":
			$message .= "Sendung-Details anzeigen. ";
			break;

		case "show_dubs":		
			$message .= "Sendung-Details und Wiederholungen anzeigen. ";
			break;
				
		case "check_delete":		
			$message .= "Sendung löschen? ";
			// erstsendung und wh pruefen!!!!!!!!!!!
			$tbl_row_sg_check_delete = db_query_sg_display_item_1($id);
			if ( !$tbl_row_sg_check_delete ) { 
				$message .= "Fehler bei Abfrage Sendung!"; 
				$action_ok = "no";
			} else { 
				if ( rtrim($tbl_row_sg_check_delete->SG_HF_FIRST_SG) == "F" ) { 
					// WH, kann geloescht werden
					//header( "Location: sg_hf_detail.php?action=delete&sg_id=".$id."&kill_wh=T" );
					header("Location: sg_hf_detail.php?action=delete&sg_id=".$id."&kill_wh=T&kill_possible=T");
				} else {	
					// ist ES, pruefen ob WH vorhanden
					$c_query_condition_sg_wh = " SG_HF_CONTENT_ID =".$tbl_row_sg_check_delete->SG_HF_CONTENT_ID;
					$db_result_sg_wh = db_query_list_items_1("SG_HF_CONTENT_ID", "SG_HF_MAIN", $c_query_condition_sg_wh);
					$z = 0;
					foreach ( $db_result_sg_wh as $item_wh ) {
						$z += 1;
					}

					if ( $z > 1 ) {
						//$message .= "Wiederholungen vorhanden, löschen nicht möglich!";
						header("Location: sg_hf_detail.php?action=delete&sg_id=".$id."&kill_possible=F");
					} else {
						// pruefen ob Manuskript vorhanden
						//$tbl_row_sg->SG_HF_CONT_ID
						$tbl_row_mk = db_query_display_item_1("SG_MANUSKRIPT", "SG_MK_SG_CONT_ID = ".$tbl_row_sg_check_delete->SG_HF_CONTENT_ID);
						if ( isset($tbl_row_mk->SG_MK_ID )) { 
							//zur Sendung ist ein Manuskript vorhanden, loeschen nicht moeglich
							header("Location: sg_hf_detail.php?action=delete&sg_id=".$id."&kill_possible=F");
						} else {
							header("Location: sg_hf_detail.php?action=delete&sg_id=".$id."&kill_es=T&kill_possible=T");
						}
					}
				}
			}
			break;

		case "delete":		
			$message .= "Sendung wirklich löschen? ";
			if ( isset( $_GET['kill_possible'] ) ) { 
				$kill_possible = $_GET['kill_possible'];
			}
			break;

		case "kill_wh":		
			$message .= "Sendung löschen. ";
			// pruefen ob bestaetigung passt
			$c_kill = db_query_load_item("USER_SECURITY", 0);

			if ( $_POST['form_kill_code'] == trim($c_kill) ) {
				$_ok = db_query_delete_item("SG_HF_MAIN", "SG_HF_ID", $id);
				if ( $_ok == "true" ) {
					$message = "Sendung gelöscht!";
					$action_ok = "no";
					//$kill_possible = "F";
				} else { 
					$message .= "Löschen fehlgeschlagen";
				}
			} else { 
				$message .= "Keine Löschberechtigung!";
			}
			break;
				
		case "kill_es":		
			$message .= "Erstsendung löschen. ";
			// pruefen ob bestaetigung passt
			$c_kill = db_query_load_item("USER_SECURITY", 0);

			if ( $_POST['form_kill_code'] == trim($c_kill) ) {
				$_ok_a = db_query_delete_item("SG_HF_MAIN", "SG_HF_ID", $id);
				$_ok_b = db_query_delete_item("SG_HF_CONTENT", "SG_HF_CONT_SG_ID", $id);
				if ( $_ok_a == "true" ) {
					$action_ok = "no" ;// damit geloeschte Sendung nicht aufgrufen wird;	
					if ( $_ok_b == "true" ) {
						$message = "Erstsendung gelöscht!";
						$action_ok = "no" ;// damit geloeschte Sendung nicht aufgrufen wird;	
					} else { 
						$message .= "Content löschen fehlgeschlagen";
					}
				} else { 
					$message .= "Main löschen fehlgeschlagen";
				}
			} else { 
				$message .= "Keine Löschberechtigung!";
			}
			break;

		case "play_out":
			$message .= "Sendung ausspielen? ";
			$play_now = "T";
			break;
		
		case "play_now":
			// pruefen ob bestaetigung passt
			$c_play = db_query_load_item("USER_SECURITY", 0);

			if ( $_POST['form_play_code'] == trim($c_play) ) {
				if ( isset( $_POST['po_filename'] ) ) { 
					$po_filename = $_POST['po_filename'];
				}
			
				$message .= "Sendung ausspielen... ";
				// choose play-out-path
				$po_path = "Play_Out_Sendung"; 
				if ( $po_it == "T" or $po_mg == "T" ) {
					$po_path = "Play_Out_Infotime";
				}
				// load access mpc
				$tbl_row_mpd_config = db_query_display_item_1("USER_SPECIALS", "USER_SP_SPECIAL = 'PO_Scheduler_Config'");
				$cmd = $tbl_row_mpd_config->USER_SP_PARAM_2." -h ".$tbl_row_mpd_config->USER_SP_PARAM_4."@".$tbl_row_mpd_config->USER_SP_PARAM_3." add ".$po_path."/".$po_filename;
				$message .= shell_exec($cmd); 
			} else {
				$message .= "Keine Playberechtigung!";
			}
			break;
		
		}//endswitch;
	}
} else {
	$message .= "Keine Anweisung. Nichts zu tun..... "; 
}

// Ende $action_ok == "yes" 
// $action_ok kann auf "no" gesetzt worden sein, deshalb weiter mit neuer Prüfung
		
if ( $action_ok == "yes" ) {
	$tbl_row_sg = db_query_sg_display_item_1($id);
	if ( !$tbl_row_sg ) { 
		$message .= "Fehler bei Abfrage Sendung!"; 
		$action_ok = "no";
	} else {
		$tbl_row_ad = db_query_display_item_1("AD_MAIN", "AD_ID = " .$tbl_row_sg->SG_HF_CONT_AD_ID);
		if ( ! isset( $tbl_row_ad->AD_ID )) {
			$message .= "Fehler bei Abfrage Adresse!"; 
			$action_ok = "no";
		}
				
		$tbl_row_mk = db_query_display_item_1("SG_MANUSKRIPT", "SG_MK_SG_CONT_ID = " .$tbl_row_sg->SG_HF_CONT_ID);
		if ( isset( $tbl_row_mk->SG_MK_ID )) { 
			$manuskript_vorhanden = true;
		}
			
	}
	// Pfade fuer flashplayer-audios etc. aus einstellungen
	$tbl_row_config = db_query_display_item_1("USER_SPECIALS", "USER_SP_SPECIAL = 'INTRA_Sendung_HF_1'");
}
?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<head>
	<title>Admin-SRB-Sendung</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8" >
	<meta http-equiv="expires" content="0">
	<style type="text/css">	@import url("../parts/style/style_srb_2.css");    </style>
	<style type="text/css"> @import url("../parts/style/style_srb_jq_2.css");  </style>
	<style type="text/css"> @import url("../parts/jquery/jquery_ui_1_8_16/css/jquery-ui-1.8.16.custom.css");    </style>
	<link href="../parts/jPlayer-2.9.2/dist/skin/blue.monday/css/jplayer.blue.monday.css" rel="stylesheet" type="text/css" />
	
	<script type="text/javascript" src="../parts/jquery/jquery_1_7_1/jquery.min.js"></script>
	<script type="text/javascript" src="../parts/jquery/jquery_ui_1_8_16/jquery-ui-1.8.16.custom.min.js"></script>
	<script type="text/javascript" src="../parts/jquery/jquery_tools/jq_tools.js"></script>
	<script type="text/javascript" src="../parts/jquery/jquery_my_tools/jq_my_tools_3.js"></script>	
	<script type="text/javascript" src="../parts/jPlayer-2.9.2/dist/jplayer/jquery.jplayer.min.js"></script>
	<script type="text/javascript" src="../parts/jPlayer-2.9.2/dist/add-on/jquery.jplayer.inspector.min.js"></script>
	
	
	<script type="text/javascript" src="parts/audio-player/audio-player.js"></script>  
   <script type="text/javascript">  
             AudioPlayer.setup("parts/audio-player/player.swf", {  
                 width: 675,
				 transparentpagebg: "yes",
				 checkpolicy: "yes"
             });  
    </script>  
	
</head>
<body>
<?php
echo "<div class='column_right'>";
echo "<div class='head_item_right'>";
echo $message; 
if ( $action_ok == "yes" ) { 
	html_sg_state(rtrim($tbl_row_sg->SG_HF_FIRST_SG), rtrim($tbl_row_sg->SG_HF_ON_AIR), rtrim($tbl_row_sg->SG_HF_CONT_FILENAME));
}
echo "</div>\n";
echo "<div class='content'>\n";
if ( $action_ok == "no" ) { 
	return;
}

$user_rights = user_rights_1($_SERVER['PHP_SELF'], rawurlencode($_SERVER['QUERY_STRING']), "C");			
if ( $user_rights == "yes" ) { 
	echo "<div class='content_row_a_1'>";
	echo "<div class='content_column_1'>Datum/ Zeit/ Länge</div>";
	echo "<div class='content_column_4'>" .get_date_format_deutsch(substr($tbl_row_sg->SG_HF_TIME, 0, 10))." (".get_german_day_name_a(substr($tbl_row_sg->SG_HF_TIME, 0, 10)).") </div>";
	echo "<div class='content_column_4'>" .substr($tbl_row_sg->SG_HF_TIME, 11, 8). " </div>";
			
	switch ( rtrim($tbl_row_sg->SG_HF_DURATION)) {
	case "00:00:00":
		// Laenge von 0 Minuten hervorheben				
		echo "<div class='content_column_4 blink' title='Bitte Sendedauer ueberpruefen'>" .rtrim($tbl_row_sg->SG_HF_DURATION). " </div>";
		break;

	case "00:01:00":
		// Vorbelegte Laenge von 1 Minute hervorheben				
		echo "<div class='content_column_4 blink' title='Bitte Sendedauer ueberpruefen'>" .rtrim($tbl_row_sg->SG_HF_DURATION). " </div>";
		break;
	
	default:
		echo "<div class='content_column_4'>" .rtrim($tbl_row_sg->SG_HF_DURATION). " </div>";
	}
	echo "</div>\n";

	echo "<div class='content_row_b_1'>";
	echo "<div class='content_column_1'>Titel</div>";
	echo "<div class='content_column_2'>" .$tbl_row_sg->SG_HF_CONT_TITEL. "</div>";
	echo "</div>\n";
	echo "<div class='content_row_a_1'>";
	echo "<div class='content_column_1'>Untertitel</div>";
	echo "<div class='content_column_2'>" .$tbl_row_sg->SG_HF_CONT_UNTERTITEL. "</div>";
	echo "</div>\n";
	echo "<div class='content_row_b_1'>";
	echo "<div class='content_column_1'>Sendeverantwortlich</div>";
	echo "<div class='content_column_2'>" .$tbl_row_ad->AD_VORNAME." " .$tbl_row_ad->AD_NAME.", ".$tbl_row_ad->AD_ORT. "</div>";
	echo "</div>\n";
	echo "<div class='space_line_1'> </div>";
	echo "<div class='content_row_a_1'>";
	echo "<div class='content_column_1'>Stichworte</div>";
	echo "<div class='content_column_2'>" .$tbl_row_sg->SG_HF_CONT_STICHWORTE."</div>" ;
	echo "</div>\n";
	echo "<div class='content_row_b_1'>";
	echo "<div class='content_column_1'>Internet</div>";
	echo "<div class='content_column_2'>" .$tbl_row_sg->SG_HF_CONT_WEB. "</div>";
	echo "</div>\n";
	echo "<div class='content_row_a_1'>";
	echo "<div class=content_column_1>Genre/ Sprache</div>";
	echo "<div class='content_column_3'>" .db_query_load_value_by_id("SG_GENRE", "SG_GENRE_ID", $tbl_row_sg->SG_HF_CONT_GENRE_ID). "</div>";
	echo "<div class='content_column_3'>" .db_query_load_value_by_id("SG_SPEECH", "SG_SPEECH_ID", $tbl_row_sg->SG_HF_CONT_SPEECH_ID). "</div>";
	echo "</div>\n";
	echo "<div class='space_line_1'> </div>";
	echo "<div class='content_row_b_1'>";
	echo "<div class='content_column_1'>Einstellungen</div>";
	echo "<div class='content_column_2'>";
	if ( rtrim($tbl_row_sg->SG_HF_ON_AIR) == "T") {
		echo "<input type='checkbox' name='form_sg_on_air' value='T' checked='checked' title='Wird gesendet'>Auf Sendung ";
	} else { 
		echo "<input type='checkbox' name='form_sg_on_air' value='T' title='Wird NICHT gesendet'>Auf Sendung ";
	}
	if ( rtrim($tbl_row_sg->SG_HF_INFOTIME) == "T") {
		echo "<input type='checkbox' name='form_sg_infotime' value='T' checked='checked' title='InfoTime'>InfoTime ";
	} else { 
		echo "<input type='checkbox' name='form_sg_infotime' value='T' title='InfoTime'>InfoTime ";
	}
	if ( rtrim($tbl_row_sg->SG_HF_MAGAZINE) == "T" ) {
		echo "<input type='checkbox' name='form_sg_magazine' value='T' checked='checked' title='Magazin'>Mag ";
	} else { 
		echo "<input type='checkbox' name='form_sg_magazine' value='T' title='Magazin'>Mag ";
	}
	if ( rtrim($tbl_row_sg->SG_HF_PODCAST) == "T" ) {
		echo "<input type='checkbox' name='form_sg_podcast' value='T' checked='checked' title='Podcast'>Podcast ";
	} else { 
		echo "<input type='checkbox' name='form_sg_podcast' value='T' title='Podcast'>Podcast ";
	}
	if ( rtrim($tbl_row_sg->SG_HF_VP_OUT) == "T" ) {
		echo "<input type='checkbox' name='form_sg_vp_out' value='T' checked='checked' title='VP extern zur Verfügung stellen'>VP-Out ";
	} else { 
		echo "<input type='checkbox' name='form_sg_vp_out' value='T' title='VP extern zur Verfügung stellen'>VP-Out ";
	}
	if ( rtrim($tbl_row_sg->SG_HF_FIRST_SG) != "T" ) {
		if ( rtrim($tbl_row_sg->SG_HF_REPEAT_PROTO) == "T" ) {
			echo "<input type='checkbox' name='form_sg_repeat_proto' value='T' checked='checked' title='Wiederholung von Audio-Protokoll\n Wenn dies aktiv, wird das Audioprotokoll in Play-Out kopiert'>WH Proto ";
		} else { 
			echo "<input type='checkbox' name='form_sg_repeat_proto' value='T' title='Wiederholung von Audio-Protokoll\n Wenn dies aktiv, wird das Audioprotokoll in Play-Out kopiert'>WH Proto ";
		}
	} else {					
		if ( rtrim($tbl_row_sg->SG_HF_LIVE) == "T" ) {
			echo "<input type='checkbox' name='form_sg_live' value='T' checked='checked' title='Livesendung'>Live ";
		} else { 
			echo "<input type='checkbox' name='form_sg_live' value='T' title='Livesendung'>Live ";
		}						
	}
										
	if ( rtrim($tbl_row_sg->SG_HF_CONT_TEAMPRODUCTION) == "T" ) {
		echo "<input type='checkbox' name='form_sg_teamprod' value='T' checked='checked' title='Teamproduktion'> Teamp.";
	} else { 
		echo "<input type='checkbox' name='form_sg_teamprod' value='T' title='Teamproduktion'> Teamp.";
	}
	echo "</div></div>\n";
			
	echo "<div class='content_row_a_1'>";
	echo "<div class=content_column_1>Quelle</div>";
	echo "<div class='content_column_2'>" .db_query_load_value_by_id("SG_HF_SOURCE", "SG_HF_SOURCE_ID", rtrim($tbl_row_sg->SG_HF_SOURCE_ID)). "</div>";
	echo "</div>\n";
	echo "<div class='content_row_b_1'>";
	echo "<div class=content_column_1>Content/ Sendung-Nr</div>";
	echo "<div class='content_column_3'>" .$tbl_row_sg->SG_HF_CONTENT_ID. "</div>";
	echo "<div class='content_column_3'>" .$tbl_row_sg->SG_HF_ID. "</div>";
	echo "</div>\n";
	echo "<div class='content_row_a_1'>"; 
	echo "<div class='content_column_1'>Regieanweisung</div>";
	echo "<div class='content_column_2'>" .$tbl_row_sg->SG_HF_CONT_REGIEANWEISUNG. "</div>";
	echo "</div>\n";
	echo "<div class='content_row_b_1'>";
	echo "<div class='content_column_1'>Dateiname</div>";
	echo "<div class='content_column_2'>" .$tbl_row_sg->SG_HF_CONT_FILENAME. "</div>";
	echo "</div>\n";

	// Pfad + Dateiname audio
	$file_exist = "no";
	$z = 0;
			
	// Datei pruefen oder nicht
	// wird oben schon auf no gesetzt wenn wir von edit-neuaufnahme kommen 			
	if ( $tbl_row_sg->SG_HF_CONT_FILENAME == "Keine_Audiodatei" ) {
		$file_exist_check = "no";
	}

	if ( substr($tbl_row_sg->SG_HF_CONT_FILENAME, 0, 5) == "http:" ) {
		$file_exist_check = "no";
		$file_exist = "yes";
		$remotefilename = $tbl_row_sg->SG_HF_CONT_FILENAME;
	}

	if ( $file_exist_check == "yes" ) {
		$search_in_archiv = $tbl_row_config->USER_SP_PARAM_9;
		// archiv-Jahr
		if ( rtrim($tbl_row_sg->SG_HF_FIRST_SG) == "T" ) {
			$archiv_sg_year = substr($tbl_row_sg->SG_HF_TIME, 0, 4)."/";
		} else {
			$archiv_sg_year = db_query_sg_load_year_by_id($tbl_row_sg->SG_HF_CONT_SG_ID)."/";
		}
				
		// pfad zusammenbauen
		if ( rtrim($tbl_row_sg->SG_HF_MAGAZINE) == "T" or rtrim($tbl_row_sg->SG_HF_INFOTIME) == "T" ) {
			// FLASHPLAYER				
			$remotefilename = "http://".$_SERVER['SERVER_NAME'].$tbl_row_config->USER_SP_PARAM_1.$tbl_row_sg->SG_HF_CONT_FILENAME;
			$remotefilename_archiv = "http://".$_SERVER['SERVER_NAME'].$tbl_row_config->USER_SP_PARAM_2.$archiv_sg_year.$tbl_row_sg->SG_HF_CONT_FILENAME;					
			// php
			$php_remotefilename = $tbl_row_config->USER_SP_PARAM_5.$tbl_row_sg->SG_HF_CONT_FILENAME;
			$php_remotefilename_archiv = $tbl_row_config->USER_SP_PARAM_6.$archiv_sg_year.$tbl_row_sg->SG_HF_CONT_FILENAME;					
		} else {
			// FLASHPLAYER	
			$remotefilename = "http://".$_SERVER['SERVER_NAME'].$tbl_row_config->USER_SP_PARAM_3.$tbl_row_sg->SG_HF_CONT_FILENAME;					
			$remotefilename_archiv = "http://".$_SERVER['SERVER_NAME'].$tbl_row_config->USER_SP_PARAM_4.$archiv_sg_year.$tbl_row_sg->SG_HF_CONT_FILENAME;				
			//php
			$php_remotefilename = $tbl_row_config->USER_SP_PARAM_7.$tbl_row_sg->SG_HF_CONT_FILENAME;
			$php_remotefilename_archiv = $tbl_row_config->USER_SP_PARAM_8.$archiv_sg_year.$tbl_row_sg->SG_HF_CONT_FILENAME;
		}
			
		if ( file_exists($php_remotefilename)) {
			$file_exist = "yes";
		} else {
			if ( $search_in_archiv =="yes" ) {
				if ( file_exists($php_remotefilename_archiv)) {
					$remotefilename = $remotefilename_archiv;
					$file_exist = "yes";
					if ( rtrim($tbl_row_sg->SG_HF_MAGAZINE) == "T" or rtrim($tbl_row_sg->SG_HF_INFOTIME) == "T" ) {
						$error_message .= "Media-Datei befindet sich im Archiv:".$tbl_row_config->USER_SP_PARAM_6.$archiv_sg_year." ! <br>Zum Ausspielen bitte in Play-Out kopieren.";
					} else {
						$error_message .= "Media-Datei befindet sich im Archiv:".$tbl_row_config->USER_SP_PARAM_8.$archiv_sg_year." ! <br>Zum Ausspielen bitte in Play-Out kopieren.";
					}
				} else { 
					$error_message .= "Media-Datei weder in Play-Out noch im Archiv vorhanden!"; 
				}
			} else { 
				$error_message .= "Media-Datei nicht vorhanden oder im Archiv. Archiv-Suche aber deaktiviert!" ; 
			} 				
		}
	} // file_exist_check

			
	if ( $file_exist == "yes" ) {
		//echo "<br><div class='space_line_1'> </div>";
		//echo "<p id='audioplayer_1'>Alternative content</p>";  
		//echo "<script type='text/javascript'>";
		//AudioPlayer.embed("audioplayer_1", {soundFile: "1052854_Sobek_Sommerfest_Sabelschule.mp3"});  
		//echo "AudioPlayer.embed('audioplayer_1', {soundFile: 'http://streamserver.max.fm:80/srb'});";
		//echo "AudioPlayer.embed('audioplayer_1', {soundFile: '".$remotefilename."' });"; 
		//echo "</script>\n  ";
		
		echo '<script type="text/javascript">';
		//echo '//<![CDATA[';
		echo '$(document).ready(function(){';
		echo '	$("#jquery_jplayer_1").jPlayer({';
		echo 'ready: function () {';
		echo '			$(this).jPlayer("setMedia", {';
		echo 'mp3: "'.$remotefilename.'"';
		echo '		});';
		echo '		},';
		echo '		swfPath: "../../dist/jplayer",';
		echo '		supplied: "mp3",';
		echo '		wmode: "window",';
		echo '		useStateClassSkin: true,';
		echo '		autoBlur: false,';
		echo '		smoothPlayBar: true,';
		echo '		keyEnabled: true,';
		echo '		remainingDuration: true,';
		echo '		toggleDuration: true';
		echo '});';
		echo '	$("#jplayer_inspector").jPlayerInspector({jPlayer:$("#jquery_jplayer_1")});';
		echo '});	';

		echo '</script>';

echo '<div id="jquery_jplayer_1" class="jp-jplayer"></div>';
echo '<div id="jp_container_1" class="jp-audio" role="application" aria-label="media player">';
	echo '<div class="jp-type-single">';
		echo '<div class="jp-gui jp-interface">';
			echo '<div class="jp-controls">';
				echo '<button class="jp-play" role="button" tabindex="0">play</button>';
				echo '<button class="jp-stop" role="button" tabindex="0">stop</button>';
			echo '</div>';
			echo '<div class="jp-progress">';
				echo '<div class="jp-seek-bar">';
					echo '<div class="jp-play-bar"></div>';
				echo '</div>';
			echo '</div>';
			echo '<div class="jp-time-holder">';
				echo '<div class="jp-current-time" role="timer" aria-label="time">&nbsp;</div>';
				echo '<div class="jp-duration" role="timer" aria-label="duration">&nbsp;</div>';
			echo '</div>';
		echo '</div>';
		echo '<div class="jp-no-solution">';
			echo '<span>Update Required</span>';
			echo 'To play the media you will need to either update your browser to a recent version or update your <a href="http://get.adobe.com/flashplayer/" target="_blank">Flash plugin</a>.';
		echo '</div>';
	echo '</div>';
echo '</div>';	
//echo '<div id="jplayer_inspector"></div>';		
	}

	echo "<br>\n<span class='error_message'>".$error_message."</span>";
			
	// Loeschen
	if ( $action == "delete" ) { 
		if ( $kill_possible == "F" ) {
			echo "<script>";
			echo '$( "#dialog-form" ).dialog( "open" )';
			echo "</script>";
			echo "<div id='dialog-form' title='Löschen dieser Sendung fehlgeschlagen'>";
			echo "<p>Zu dieser Sendung sind Wiederholungen oder ein Manuskript vorhanden, <br>Sendung kann nicht gelöscht werden!</p></div>";			
		} else {
			echo "<script>";
			echo '$( "#dialog-form" ).dialog( "open" )';
			echo "</script>";
			echo "<div id='dialog-form' title='Löschen dieser Sendung bestätigen'>";
			echo "<p>Diese Sendung kann erst durch Eingabe des Berechtigungscodes gelöscht werden!</p>";
			echo "<form action='sg_hf_detail.php' method='POST' enctype='application/x-www-form-urlencoded'>\n";
			if ( isset( $_GET['kill_wh'] )) { 
				if ( $_GET['kill_wh'] == "T" ) { 
					echo "<input type='hidden' name='action' value='kill_wh'>";
				}
			}
			if ( isset( $_GET['kill_es'] )) { 
				if ( $_GET['kill_es'] == "T" ) { 
					echo "<input type='hidden' name='action' value='kill_es'>";
				}
			}
			echo "<input type='hidden' name='sg_id' value=".$tbl_row_sg->SG_HF_ID.">";	
			echo "<input type='password' name='form_kill_code' class='text_a_1' value=''>"; 
			echo "<input type='submit' class='b_1' value='Jetzt löschen'></form><div class='space_line_1'> </div></div>";
		}
	}
	
	// play-out
	if ( $action == "play_out" ) { 
		if ($play_now == "T" ) {
			echo "<script>";
			echo '$( "#dialog-form" ).dialog( "open" )';
			echo "</script>";
			echo "<div id='dialog-form' title='Play-Out dieser Sendung bestätigen'>";
			echo "Nach Bestätigung durch Berechtigungscode wird die Sendung zur aktuellen Play-Out-Warteschlange zugefügt!<p>";
			echo "<form action='sg_hf_detail.php' method='POST' enctype='application/x-www-form-urlencoded'>\n";
			echo "<input type='hidden' name='action' value='play_now'>";
			echo "<input type='hidden' name='sg_id' value=".$tbl_row_sg->SG_HF_ID.">";	
			echo "<input type='hidden' name='po_filename' value=".rtrim($tbl_row_sg->SG_HF_CONT_FILENAME).">";	
			echo "<input type='password' name='form_play_code' class='text_a_1' value=''>"; 
			echo "<input type='submit' class='b_1' value='Jetzt ausspielen'></form><div class='space_line_1'> </div></div>";
		}
	}

	echo "<br>\n<span> </span>"; // dummy damit warning_div nicht ueberlappt 
				
	echo "<div class='menu_bottom'>";
	echo "<ul class='menu_bottom_list'><li>";
	if ( rtrim($_SESSION["log_rights"]) <= "B" ) {
		echo "<a href='sg_hf_edit.php?action=edit&amp;sg_id=".$tbl_row_sg->SG_HF_ID."&amp;ad_id=".$tbl_row_sg->SG_HF_CONT_AD_ID."&amp;file_exist=".$file_exist."'>Bearbeiten</a> ";
		echo "<a href='sg_hf_edit.php?action=repeat_new&amp;sg_id=".$tbl_row_sg->SG_HF_ID."&amp;ad_id=".$tbl_row_sg->SG_HF_CONT_AD_ID."'>Wiederholen</a> ";			
		echo "<a href='sg_hf_edit.php?action=dublikate_new&amp;sg_id=".$tbl_row_sg->SG_HF_ID."&amp;ad_id=".$tbl_row_sg->SG_HF_CONT_AD_ID."'>Duplizieren</a> ";	
		echo "<a href='../admin_srb_adress/adress_find_extra.php?sg_id=".$tbl_row_sg->SG_HF_ID." ' title='Sendeverantwortlichen ändern'>Sendeverantwortlicher</a> ";
					
		if ( $action == "display" ) { 
			if ( $tbl_row_sg->SG_HF_ID != "0" ) {
				// sendung mit nr 0 darf nicht geloescht werden, ist vorlage fuer neue sendungen
				echo "<a href='sg_hf_detail.php?action=check_delete&amp;sg_id=".$tbl_row_sg->SG_HF_ID."'>Löschen</a> ";
			}
		}
		echo "<a href='sg_hf_reg_form.php?action=print&amp;sg_id=".$tbl_row_sg->SG_HF_ID."&amp;ad_id=".$tbl_row_sg->SG_HF_CONT_AD_ID."' target='_blank'>Drucken</a> ";
		if ( $file_exist == "yes" ) { 
			echo "<a href='sg_hf_detail.php?action=play_out&amp;sg_id=".$tbl_row_sg->SG_HF_ID."&amp;ad_id=".$tbl_row_sg->SG_HF_CONT_AD_ID."&amp;po_it=".rtrim($tbl_row_sg->SG_HF_INFOTIME)."&amp;po_mg=".rtrim($tbl_row_sg->SG_HF_MAGAZINE)."&amp;po_filename=".rtrim($tbl_row_sg->SG_HF_CONT_FILENAME)."' >Play-Out</a> ";
		}
	} else {
		echo "<a title='Keine Berechtigung'>Bearbeiten</a> ";
		echo "<a title='Keine Berechtigung'>Wiederholen</a> ";			
		echo "<a title='Keine Berechtigung'>Duplizieren</a> ";	
		echo "<a title='Keine Berechtigung'>Sendeverantwortlicher</a> ";
		echo "<a title='Keine Berechtigung'>Löschen</a> ";
	}			
	echo "</ul>\n</div>\n<!--menu_bottom-->";  
	echo "<div class='menu_bottom_1'>";
	echo "<ul class='menu_bottom_list'><li>";
	if ( rtrim($tbl_row_sg->SG_HF_FIRST_SG) == "F" ) { 
		echo "<a href='sg_hf_detail.php?action=display&amp;sg_id=".$tbl_row_sg->SG_HF_CONT_SG_ID."'>Erstsendung anzeigen</a> "; 
	}
	if ( rtrim($tbl_row_sg->SG_HF_FIRST_SG) == "T" ) { 
		echo "<a href='sg_hf_detail.php?action=show_dubs&amp;sg_id=".$tbl_row_sg->SG_HF_ID."'>Wiederholungen listen</a> "; 
	}
	echo "<a href='sg_hf_find_list.php?action=list&amp;find_option=show_hour&amp;sg_time=".$tbl_row_sg->SG_HF_TIME."' target='_blank'>Sendungen dieser Stunde in neuem Tab</a> ";	
	if ( $manuskript_vorhanden ) { 
		echo "<a href='sg_hf_manuskript_edit.php?action=edit&amp;sg_id=".$tbl_row_sg->SG_HF_CONT_ID."&amp;sg_mk_id=".$tbl_row_mk->SG_MK_ID."&amp;sg_titel=".$tbl_row_sg->SG_HF_CONT_TITEL."' target='_blank'>Manuskript bearbeiten</a> ";
	} else {
		echo "<a href='sg_hf_manuskript_edit.php?action=new&amp;sg_id=".$tbl_row_sg->SG_HF_CONT_ID."&amp;sg_titel=".$tbl_row_sg->SG_HF_CONT_TITEL."' target='_blank'>Manuskript anlegen</a> ";
	}
			
	echo "</ul>\n</div>\n<!--menu_bottom-->";  
	echo "\n</div><!--content wieder zu-->"; 
			
	// Wiederholungen Anfang
	if ( $action == "show_dubs" ) {
		$c_query_condition_dubs = " SG_HF_CONTENT_ID = ".$tbl_row_sg->SG_HF_CONTENT_ID." AND SG_HF_FIRST_SG = 'F'";
		$db_result_dubs = db_query_list_items_1("SG_HF_ID, SG_HF_TIME, SG_HF_DURATION", "SG_HF_MAIN", $c_query_condition_dubs);
		echo "<div class='content'>Wiederholungen..";
		if ( $db_result_dubs ) { 		
			$z = 0;
			foreach ( $db_result_dubs as $item_dub ) {
				$z += 1;
				if ( $z % 2 != 0 ) {
					echo "<div class='content_row_a'>";	
				} else { 
					echo "<div class='content_row_b'>";
				}
				echo "<a href='sg_hf_detail.php?action=display&amp;sg_id=".$item_dub['SG_HF_ID']."'> ".get_german_day_name_a(substr($item_dub['SG_HF_TIME'], 0, 10))." - ". get_date_format_deutsch(substr($item_dub['SG_HF_TIME'], 0, 10))." - ".substr($item_dub['SG_HF_TIME'], 11, 8)."</a>";
				echo "</div><br>";
			}
		}
		if ( $z == 0 ) { 
			echo "Keine Wiederholungen gefunden...";
		} else {
			echo "<br>&nbsp;<br><span'>Gefunden: ".$z."</span>";
		}
		echo "</div>"; // content wieder zu
	}
			
	// Wiederholungen Ende
	//echo $_SESSION["log_rights"]."x";	
} // user_rights
echo "</div><!--class=column_right-->";
?>
</body>
</html>