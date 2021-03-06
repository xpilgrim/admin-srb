<?php

/** 
* Inventar PDF-Listen zusammenstellen 
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

?>	
	
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
	<title>Admin-SRB-Inventar finden</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8" >
	<style type="text/css">	@import url("../parts/style/style_srb_2.css");   </style>
	<style type="text/css">	@import url("../parts/style/style_srb_jq_2.css");</style>
	<style type="text/css"> @import url("../parts/jquery/jquery_ui_1_8_16/css/jquery-ui-1.8.16.custom.css");    </style>
	<style type="text/css"> @import url("../parts/colorbox/colorbox.css");  </style>
	
	<script type="text/javascript" src="../parts/jquery/jquery_1_7_1/jquery.min.js"></script>
	<script type="text/javascript" src="../parts/jquery/jquery_ui_1_8_16/jquery-ui-1.8.16.custom.min.js"></script>
	<script type="text/javascript" src="../parts/jquery/jquery_tools/jq_tools.js"></script>
	<script type="text/javascript" src="../parts/colorbox/jquery.colorbox.js"></script>	
	<script type="text/javascript" src="../parts/jquery/jquery_my_tools/jq_my_tools_2.js"></script>
	
	<script type="text/javascript">
	
	function chk_formular () {
		cEingabe = document.form1.form_iv_eigentuemer.value + document.form1.iv_typ.value + document.form1.iv_hersteller.value + document.form1.iv_rechnung.value + document.form1.iv_id.value

  		if ( cEingabe == "") {		  
	    	alert("Es wurden keine Suchbegriffe eingegeben!");
    		document.form1.form_iv_eigentuemer.focus();
			return false;}
		}
	</script>

</head>
<body>
<?php
echo "<div class='main'>";
	 
include "../parts/site_elements/header_srb_2.inc";
include "../parts/menu/menu_srb_root_1_eb_1.inc";
echo "<div class='column_left'>";
include "parts/iv_menu.inc";
user_display();
echo "</div> <!--class=column_left-->";
echo "<div class='column_right'>";
echo "<div class='head_item_right'>";
echo "Inventar als pdf exportieren";
echo "</div>";
include "parts/iv_toolbar.inc";

echo "<div class='content'>";
		
$user_rights = user_rights_1($_SERVER['PHP_SELF'], rawurlencode($_SERVER['QUERY_STRING']), "B");
if ( $user_rights == "yes" ) { 	
	echo "<form name='form1' action='iv_pdf_list.php' method='POST' onsubmit='return chk_formular()' enctype='application/x-www-form-urlencoded'>";
	echo "<div><input type='hidden' name='action' value='find'></div>";
	echo "<div><input type='hidden' name='find_option_1' value='from_prev_form'></div>";
	echo "<table>";	
	echo "<tr><td>Eigentümer</td><td>".html_dropdown_from_table_1("IV_EIGENTUEMER", "IV_EIG_DESC", "form_iv_eigentuemer", "text_2", "")."(Wenn nicht benötigt: Keine Zuordnung einstellen)</td></tr>";
	echo "<tr><td>Sponsor</td><td><input type='TEXT' name='form_iv_sponsor' value='' size='60' maxlength='100'></td></tr>";
	echo "<tr><td> </td></tr>";
	echo "<tr><td>Optionen für Suche</td><td><input type='radio' name='find_option' value='begin' checked='checked' > Anfang <input type='radio' name='find_option' value='in'> Innerhalb <input type='radio' name='find_option' value='exact'> Exakte Übereinstimmung</td></tr>";
	echo "<tr><td><br>&nbsp;<br></td><td><br>&nbsp;<br><input type='SUBMIT' name='submit' value='pdf erzeugen'> <input type='RESET' name='reset' value='Zurücksetzen'></td></tr>";
	echo "</table>";
	echo "</form>";
} // user_rights
echo "</div>";
echo "</div>";
echo "</div>";
echo "<script type='text/javascript'>";
echo "document.form1.iv_objekt.focus();";
echo "</script>";
?>
</body>
</html>
