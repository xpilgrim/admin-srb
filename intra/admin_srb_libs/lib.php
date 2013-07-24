<?php

/** 
* library for non-db-functions 
*
* PHP version 5
*
* @category Intranetsite
* @package  Admin-SRB
* @author   Joerg Sorge <joergsorge@googel.com>
* @license  http://www.gnu.org/copyleft/gpl.html GNU General Public License
* @link     http://srb.fm
*/

/**
* get_date_format_deutsch
*
* @param c_date $c_date datum sql
* 
* @return Datum deutsch
*
*/	
function get_date_format_deutsch( $c_date )
{
	$c_date_year = substr($c_date, 0, 4);
	$c_date_month = substr($c_date, 5, 2);
	$c_date_day = substr($c_date, 8, 2);
	$c_date_deutsch = $c_date_day.".".$c_date_month.".".$c_date_year;
	return $c_date_deutsch;
}

/**
* get_date_format_sql
*
* @param c_date $c_date datum deutsch
* 
* @return Datum sql
*
*/
function get_date_format_sql( $c_date )
{
	$c_date_year = substr($c_date, 6, 4);
	$c_date_month = substr($c_date, 3, 2);
	$c_date_day = substr($c_date, 0, 2);
	$c_date_sql = $c_date_year."-".$c_date_month."-".$c_date_day;
	return $c_date_sql;
}

/**
* get_german_day_name
*
* @param c_day_name $c_day_name enlischer Name des Tages
* 
* @return deutscher Name des Tages
*
*/
function get_german_day_name( $c_day_name )
{
	switch ( $c_day_name ) {
	case "Sunday":
		return "Sonntag";
		break;
	case "Monday":
		return "Montag";
		break;
	case "Tuesday":
		return "Dienstag";
		break;
	case "Wednesday":
		return "Mittwoch";
		break;
	case "Thursday":
		return "Donnerstag";
		break;
	case "Friday":
		return "Freitag";
		break;
	case "Saturday":
		return "Sonnabend";
		break;
	default:
		return $c_day_name;
		//endswitch;
	}
}

/**
* get_german_day_name_a
*
* @param c_date_sql $c_date_sql sql-Datum
* 
* @return deutscher Name des Tages
*
*/
function get_german_day_name_a( $c_date_sql )
{
	$j = substr($c_date_sql, 0, 4);
	$m = substr($c_date_sql, 5, 2);
	$d = substr($c_date_sql, 8, 2);
	$c_day_name = date('l', mktime(0, 0, 0, $m, $d, $j));
	switch ( $c_day_name ) {
	case "Sunday":
		return "Sonntag";
		break;
	case "Monday":
		return "Montag";
		break;
	case "Tuesday":
		return "Dienstag";
		break;
	case "Wednesday":
		return "Mittwoch";
		break;
	case "Thursday":
		return "Donnerstag";
		break;
	case "Friday":
		return "Freitag";
		break;
	case "Saturday":
		return "Sonnabend";
		break;
	default:
		return $c_day_name;
		//endswitch;
	}
}

/**
* get_german_day_name_short
*
* @param c_day_name $c_day_name engl Short-Name
* 
* @return deutscher Kurz-Name des Tages
*
*/
function get_german_day_name_short( $c_day_name )
{
	switch ( $c_day_name ) {
	case "Sun":
		return "So";
		break;
	case "Mon":
		return "Mo";
		break;
	case "Tue":
		return "Di";
		break;
	case "Wed":
		return "Mi";
		break;
	case "Thu":
		return "Do";
		break;
	case "Fri":
		return "Fr";
		break;
	case "Sat":
		return "Sa";
		break;
	default:
		return $c_day_name;
		//endswitch;
	}
}

/**
* get_time_in_hms
*
* @param s $s engl Sekunden
* 
* @return Zeit in hh:mm:ss
*
*/
function get_time_in_hms( $s )
{
	//	$s = 124;
	$h = floor($s / 3600);
	$s -= $h * 3600;
	$m = floor($s / 60);
	$s -= $m * 60;

	$hms = sprintf("%02d:%02d:%02d", $h, $m, $s);  
	return $hms;
}	

/**
* get_seconds_from_hms
*
* @param hms $hms hh:mm:ss
* 
* @return Sekunden
*
*/
function get_seconds_from_hms( $hms )
{
	$h = substr($hms, 0, 2);
	$h_m = floor($h * 60);
	$m = substr($hms, 3, 2);
	$s = substr($hms, 6, 2);
          
	$m += $h_m;
	$m_s = floor($m * 60);
	$s += $m_s ;
	return $s;
}
         
/**
* replace_umlaute_klein_gross
*
* @param x $x String 
* 
* @return String mit grossen Umlauten
*
*/
function replace_umlaute_klein_gross( $x )
{
	$k1=array('ä', 'ö', 'ü');
	$k2=array('Ä', 'Ö', 'Ü');
	for ($i='0';$i<'3';$i++) {
		$x = str_replace($k1[$i], $k2[$i], $x);
	}
	return $x;
}

/**
* replace_umlaute_gross_klein
*
* @param x $x String 
* 
* @return String mit kleinen Umlauten
*
*/        
function replace_umlaute_gross_klein( $x )
{
	$k2=array('ä', 'ö', 'ü');
	$k1=array('Ä', 'Ö', 'Ü');
	for ($i='0';$i<'3';$i++) {
		$x = str_replace($k1[$i], $k2[$i], $x);
	}
	return $x;
}

/**
* replace_umlaute_sonderzeichen
*
* @param x $x String 
* 
* @return String ohne Umlaute und Sonderzeichen
*
*/ 
function replace_umlaute_sonderzeichen( $x )
{
	$k2 = array('Ae', 'ae', 'Oe', 'oe', 'Ue', 'ue', 'ss', 'und', '_');
	$k1 = array('Ä', 'ä', 'Ö', 'ö', 'Ü', 'ü', 'ß', '&', ' ');
	for ($i='0';$i<'8';$i++) {
		$x = str_replace($k1[$i], $k2[$i], $x);
	}
	return $x;
}

/**
* search_forbidden_strings
*
* @param my_string $my_string String 
* 
* @return yes or no
*
*/ 
function search_forbidden_strings( $my_string ) 
{
	$string_ok = "yes"; 
	if (strpos($my_string, "Select")!==false) { 
		$string_ok = "no";
	}
	if (strpos($my_string, "Update")!==false) { 
		$string_ok = "no";
	}
	if (strpos($my_string, "Union")!==false) { 
		$string_ok = "no";
	}
	if (strpos($my_string, "exec")!==false) { 
		$string_ok = "no";
	}
	//echo $string_ok;
	return $string_ok;	
}

/**
* sg_extract_stichwort_for_filename
* Stichwort in Filename Sendung uebernehmen
*
* @param c_stichworte $c_stichworte String 
* 
* @return String
*
*/ 
function sg_extract_stichwort_for_filename( $c_stichworte )
{
	if ( $c_stichworte != "" ) {
		if ( strpos($c_stichworte, ' ') != false ) {
			// Leerzeichen da, also vielleicht mehr als ein Wort, nur das erste Wort nehmen
			$c_filename_stichwort = substr($c_stichworte, 0, strpos($c_stichworte, ' '));
		} else {
			$c_filename_stichwort = trim($c_stichworte);
		}
	} else {
		$c_filename_stichwort = "Sendung_ohne_Stichwort";
	}
        
	return $c_filename_stichwort;
}

/**
* user_login_form
* Form anzeigen
*
* @param website $website URL 
* @param query   $query   Query 
* 
* @return html
*
*/ 
function user_login_form( $website, $query )
{
	echo "<script>";
	echo '$( "#dialog-form" ).dialog( "open" )';
	echo "</script>";
	echo "<div id='dialog-form' title='Bitte anmelden'>";
	echo "<p>Diese Seite kann nur nach LogIn mit folgendem Benutzernamen und Passwort angezeigt werden!</p>";
	//echo "<form action='user_login_1.php' method='GET' enctype='application/x-www-form-urlencoded'>";
	echo "<form action='../admin_srb_user/user_login_1.php' method='GET' enctype='application/x-www-form-urlencoded'>";
	echo "<input type='hidden' name='action' value='LogIn'>";
	echo "<input type='hidden' name='form_log_dir' value='".dirname($website)."'>";	
	echo "<input type='hidden' name='form_log_webseite' value='".$website."?".$query."'>";	
	echo "<input type='input' name='form_log_name' value=''>";	
	echo "<input type='password' name='form_log_pass' value=''>"; 
	echo "<input type='submit' value='LogIn'></form></div>";				
}

/**
* display_message
* Form anzeigen
*
* @param title   $title   URL 
* @param message $message Message 
* 
* @return html
*
*/ 
function display_message( $title, $message )
{
	echo "<script>";
	echo '$( "#dialog-form" ).dialog( "open" )';
	echo "</script>";
	echo "<div id='dialog-form' title='".$title."'>";
	echo "<p>".$message."</p></div>";					
	return;
}

/**
* html_sg_state
*
* @param c_first_sg $c_first_sg T or F 
* @param c_on_air   $c_on_air   T or F  
* @param c_filename $c_filename String
* 
* @return html
*
*/ 
function html_sg_state( $c_first_sg,  $c_on_air, $c_filename )
{
	// noch einbauen: Pruefung File im Archiv   
	echo "<div style='margin-top: -5px; float: right'>";
	if ( $c_first_sg == "T" ) {
		if ( $c_on_air == "T" ) {
			echo "<img src='parts/rectangle_green.png' width='16px' height='16px' alt='Erstsendung'>";
		} else {
			echo "<img src='parts/rectangle_green_x.png' width='16px' height='16px' alt='Erstsendung'>";
		}
	} else { 
		if ( $c_on_air == "T" ) {
			echo "<img src='parts/rectangle_blue.png' width='16px' height='16px' alt='Wiederholung'>";
    	} else {
			echo "<img src='parts/rectangle_blue_x.png' width='16px' height='16px' alt='Wiederholung'>";
		}
	}
	echo "</div>";
	return;
}

/**
* html_sg_state_1
*
* @param c_first_sg $c_first_sg T or F 
* @param c_on_air   $c_on_air   T or F  
* @param c_filename $c_filename String
* 
* @return html
*
*/ 
function html_sg_state_1( $c_first_sg, $c_on_air, $c_filename )
{
    // noch einbauen: Pruefung File im Archiv
	if ( $c_first_sg == "T" ) {
    	if ( $c_on_air == "T" ) {
    		echo "<img src='parts/rectangle_green.png' width='16px' height='16px' alt='Erstsendung'>";
    	} else {
			echo "<img src='parts/rectangle_green_x.png' width='16px' height='16px' alt='Erstsendung'>";
		}
	} else { 
		if ( $c_on_air == "T" ) {
			echo "<img src='parts/rectangle_blue.png' width='16px' height='16px' alt='Wiederholung'>";
		} else {
			echo "<img src='parts/rectangle_blue_x.png' width='16px' height='16px' alt='Wiederholung'>";
		}
	}
	return;
}
	

?>
