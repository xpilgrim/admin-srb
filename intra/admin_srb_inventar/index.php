<?php
/** 
* adress-details anzeigen 
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
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">

<html>
<head>
	<title>Admin-SRB-Inventar</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8" >
	<style type="text/css"> @import url("../parts/style/style_srb_2.css");    </style>
	<style type="text/css"> @import url("../parts/style/style_srb_jq_2.css");  </style>
	<style type="text/css"> @import url("../parts/colorbox/colorbox.css");  </style>
	
	<script src="../parts/jquery/jquery_1_7_1/jquery.min.js"></script>
	<script src="../parts/colorbox/jquery.colorbox.js"></script>	
	<script src="../parts/jquery/jquery_my_tools/jq_my_tools_2.js"></script>	

</head>
<body>

<div class="main">
<?php
include "../parts/site_elements/header_srb_2.inc";
include "../parts/menu/menu_srb_root_1_eb_1.inc";
echo "<div class='column_left'>";
include "parts/iv_menu.inc"; 		
user_display();		
echo "</div>";
echo "<div class='column_right'>";
echo "<div class='head_item_right'>";
echo "Inventar anzeigen und bearbeiten";
echo "</div>";
include "parts/iv_toolbar.inc";
echo "</div>";
?>		
</div>
</body>
</html>
