#!/usr/bin/perl
use CGI::Carp qw(fatalsToBrowser);
use CGI;
use strict;
use warnings;

my $cgi = CGI->new;
print $cgi->header('text/html');

# Get the setting_id from the query string
my $setting_id = $cgi->param('setting_id') || '';

# Define the directory path and construct the file name
my $dir = '/EXP/RIBF/TRIP/2024/AUTUMN/USR/default/JSR/LISE/ROOT/';
my $file = "${setting_id}.root";

# Output the HTML
print << "HTML";
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Read a ROOT file</title>
    <link rel="shortcut icon" href="img/RootIcon.ico"/>
    <script type="text/javascript" src="/JSROOT/scripts/JSRootCore.js?gui"></script>
</head>
<body>
    <div id="simpleGUI" path="$dir" files="$file"></div>
    <p>Opening file: $file</p>
</body>
</html>
HTML
