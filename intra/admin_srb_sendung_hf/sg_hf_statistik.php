<?php

/** 
* Sendung - Statistik
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
require "../../cgi-bin/admin_srb_libs/lib_statistik.php";
require "../../cgi-bin/admin_srb_libs/lib_sess.php";
$message = "";

// check action
$action_ok = false;
if ( isset($_GET['action']) ) {
	$action = $_GET['action'];	
	$action_ok = true;
}
		
if ( $action_ok == true ) {	
	switch ( $action ):
	case "display": 
		$message .= "Statistik Sendung"; 
		break;
	endswitch;
} else {
	$message = "Keine Anweisung. Nichts zu tun..... "; 
}
$a_statistik_sg = statistik_sg();


?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<head>
	<title>Admin-SRB-Sendung</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8" >
   <style type="text/css">	@import url("../parts/style/style_srb_3.css");    </style>
	<style type="text/css"> @import url("../parts/jquery/jquery_ui_1_8_16/css/jquery-ui-1.8.16.custom.css");    </style>
	<style type="text/css">	@import url("../parts/style/style_srb_jq_2.css");    </style>

	<script type="text/javascript" src="../parts/jquery/jquery_1_7_1/jquery.min.js"></script>
	<script type="text/javascript" src="../parts/jquery/jquery_ui_1_8_16/jquery-ui-1.8.16.custom.min.js"></script>
	<script type="text/javascript" src="../parts/jquery/jquery_tools/jq_tools.js"></script>
	<script type="text/javascript" src="../parts/jquery/jquery_my_tools/jq_my_tools_2.js"></script>
</head>
<body>
 
<?php 
echo "<div class='column_right_1'>";
echo "<div class='head_item_right'>";
echo $message."\n";
echo "</div>";
	
if ( $action_ok == false ) { 
	return;
} 
$user_rights = user_rights_1($_SERVER['PHP_SELF'], rawurlencode($_SERVER['QUERY_STRING']), "B");
if ( $user_rights == "yes" ) { 	
	echo "<div class='content'>Gesamtübersicht Sendungen</div>";	
	echo "<div class='content' id='jq_slide_by_click'>";
	$z = 0;
	foreach ( $a_statistik_sg[0] as $item => $item_count ) {
		$z +=1;
		// Listcolors					
		if ( $z % 2 != 0 ) { 
			echo "<div class='content_row_a_4'>"; 
		} else {	
			echo "<div class='content_row_b_4'>";
		}
		echo "<div class='content_column_1'>".$item."</div><div class='content_column_6'>".$item_count."</div>";
		echo "</div>\n"; 			
	} 			//foreach			
	echo "</div>\n";
	
	echo "<div class='content'>Sendungen (ES und WH) nach Jahren und Quartalen (ES in Klammern)</div>";
	echo "<div class='content' id='jq_slide_by_click'>";
	$z = 0;		
	foreach ( $a_statistik_sg[1] as $item_year => $item_value ) {
		$z +=1;
		// Listcolors					
		if ( $z % 2 != 0 ) { 
			echo "<div class='content_row_a_4'>"; 
		} else {	
			echo "<div class='content_row_b_4'>";
		}
		echo "<div class='content_column_1'>Im Jahr ".$item_year. "</div> <div class='content_column_6'>".$item_value."</div>\n";
		echo "</div>\n";
		echo "<div class='content_row_toggle_head_3'><img src='../parts/pict/form.gif' title='Mehr anzeigen' alt='Zusatz'></div>";
		echo "<div class='content_row_toggle_body_3'>";
	
		foreach ( $a_statistik_sg[2] as $item_quartal => $item_value ) {
			// Listcolors					
			if (substr($item_quartal, 0, 4) == 	$item_year ) {			
				echo "<div class='content_column_1'>Quartal ".$item_quartal."</div> <div class='content_column_6'>".$item_value."</div>\n";
			}
		}
		echo "</div>\n";
	}
	echo "</div>\n";
	
	echo "<div class='content'>Max. gleichzeitige Webstreamhörer nach Jahren</div>";
	echo "<div class='content' id='jq_slide_by_click'>";
	$z =0;
	foreach ( $a_statistik_sg[3] as $item_year => $item_value ) {
		$z +=1;
		// Listcolors					
		if ( $z % 2 != 0 ) { 
			echo "<div class='content_row_a_4'>"; 
		} else {	
			echo "<div class='content_row_b_4'>";
		}
		echo "<div class='content_column_1'>Im Jahr ".$item_year. "</div> <div class='content_column_6'>".$item_value."</div>\n";
 		echo "</div>\n";
	}
	echo "</div>\n";
	
	echo "<br><div class='space_line'> </div>\n ";	
} // user_rights
echo "</div> <!--class=column_right-->";
echo "</div> <!--class=content-->";
?>
</body>
</html>