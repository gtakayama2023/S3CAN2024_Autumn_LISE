#!/usr/bin/perl
use CGI::Carp qw(fatalsToBrowser);
use CGI qw/:standard/;
use strict;
use warnings;

# URLからdefaultの部分を抽出
my $url = $ENV{'REQUEST_URI'} || '';
my ($default) = $url =~ m|/USR/([^/]+)/JSR/|;
$default ||= 'default';  # デフォルト値を設定

# setting_idを取得
my ($setting_id) = $url =~ /setting_id=(\d+)/;

# Content-Typeヘッダーを出力
print "Content-type: text/html\n\n";

# HTMLの開始部分を出力
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
HTML

# div要素を出力 (抽出したdefaultを使用)
print qq{     <div id="simpleGUI" path="/EXP/RIBF/TRIP/2024/AUTUMN/USR/$default/JSR/LISE/ROOT/" files="};

# ファイル一覧を取得して出力 ( サーバー上の絶対/相対パス )
my $dir = '../ROOT/';
opendir(DIR, $dir) or die "Cannot open directory: $!";
my @files;
while (my $file = readdir(DIR)) {
    if ($file =~ /\.root$/) {  # .root 拡張子のファイルのみを対象とする場合
        push @files, $file;
    }
}
closedir(DIR);

# ファイル名を降順でソートして出力
foreach my $file (sort { $b cmp $a } @files) {
    print "$file;";
}

# div要素の終了部分を出力
print '"></div>';
print " hello ";

# HTMLの終了部分を出力
print << "HTML";
</body>
</html>
HTML
