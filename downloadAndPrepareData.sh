#!/bin/bash
echo "This script will download and prepare the stackoverflow data. You will need ~100gb disc space during the process."



mkdir data
mkdir models
mkdir topics
mkdir rawdata
cd rawdata

if [ ! -f "stackoverflow.com-Posts.7z" ]; then
	echo "Downloading stackoverflow file (10gb), this might take a while"
	#wget -c https://archive.org/download/stackexchange/stackoverflow.com-Posts.7z
fi 

if [ ! -f "Posts.xml" ]; then
	echo "Extracting stackoverflow file, this will take even longer"
	echo "NB: this will result in one 50gb file, make sure you have enough disc space!"
	#7za x stackoverflow.com-Posts.7z
fi

echo "Will now extract all posts from 2013 and 2014 using precalculated line numbers."
# These numbers are based on a version of the dump file donwloaded on April 5th, 2017.
Y2013=11799341
Y2014=17237115
END2013=`expr $Y2014 - 1`
Y2015=22653753
END2014=`expr $Y2015 - 1`

F2013="2013.Posts.xml"
F2014="2014.Posts.xml"

if [ ! -f $F2013 ]; then
	awk 'NR=='$Y2013', NR=='$END2013'-1; NR=='$END2013' {print; exit}' Posts.xml > $F2013
fi
if [ ! -f $F2013 ]; then
	awk 'NR=='$Y2014', NR=='$END2015'-1; NR=='$END2014' {print; exit}' Posts.xml > $F2014
fi

echo "splitting files"
M201301=`awk '/CreationDate=\"2013-01/ {print NR; exit}' 2013.Posts.xml`
M201302=`awk '/CreationDate=\"2013-02/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201302 - 1`
awk 'NR=='$M201301', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-01.Posts.xml
echo "2013-01 done"

M201303=`awk '/CreationDate=\"2013-03/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201303 - 1`
awk 'NR=='$M201302', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-02.Posts.xml
echo "2013-02 done"

M201304=`awk '/CreationDate=\"2013-04/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201304 - 1`
awk 'NR=='$M201303', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-03.Posts.xml
echo "2013-03 done"

M201305=`awk '/CreationDate=\"2013-05/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201305 - 1`
awk 'NR=='$M201304', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-04.Posts.xml
echo "2013-04 done"

M201306=`awk '/CreationDate=\"2013-06/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201306 - 1`
awk 'NR=='$M201305', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-05.Posts.xml
echo "2013-05 done"

M201307=`awk '/CreationDate=\"2013-07/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201307 - 1`
awk 'NR=='$M201306', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-06.Posts.xml
echo "2013-06 done"

M201308=`awk '/CreationDate=\"2013-08/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201308 - 1`
awk 'NR=='$M201307', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-07.Posts.xml
echo "2013-07 done"

M201309=`awk '/CreationDate=\"2013-09/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201309 - 1`
awk 'NR=='$M201308', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-08.Posts.xml
echo "2013-08 done"

M201310=`awk '/CreationDate=\"2013-10/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201310 - 1`
awk 'NR=='$M201309', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-09.Posts.xml
echo "2013-09 done"

M201311=`awk '/CreationDate=\"2013-11/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201311 - 1`
awk 'NR=='$M201310', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-10.Posts.xml
echo "2013-10 done"

M201312=`awk '/CreationDate=\"2013-12/ {print NR; exit}' 2013.Posts.xml`
LAST=`expr $M201312 - 1`
awk 'NR=='$M201311', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2013.Posts.xml > 2013-11.Posts.xml
echo "2013-11 done"

awk 'NR>='$M201312 2013.Posts.xml > 2013-12.Posts.xml
echo "2013-12 done"

M201401=`awk '/CreationDate=\"2014-01/ {print NR; exit}' 2014.Posts.xml`
M201402=`awk '/CreationDate=\"2014-02/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201402 - 1`
awk 'NR=='$M201401', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-01.Posts.xml
echo "2014-01 done"

M201403=`awk '/CreationDate=\"2014-03/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201403 - 1`
awk 'NR=='$M201402', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-02.Posts.xml
echo "2014-02 done"

M201404=`awk '/CreationDate=\"2014-04/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201404 - 1`
awk 'NR=='$M201403', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-03.Posts.xml
echo "2014-03 done"

M201405=`awk '/CreationDate=\"2014-05/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201405 - 1`
awk 'NR=='$M201404', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-04.Posts.xml
echo "2014-04 done"

M201406=`awk '/CreationDate=\"2014-06/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201406 - 1`
awk 'NR=='$M201405', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-05.Posts.xml
echo "2014-05 done"

M201407=`awk '/CreationDate=\"2014-07/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201407 - 1`
awk 'NR=='$M201406', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-06.Posts.xml
echo "2014-06 done"

M201408=`awk '/CreationDate=\"2014-08/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201408 - 1`
awk 'NR=='$M201407', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-07.Posts.xml
echo "2014-07 done"

M201409=`awk '/CreationDate=\"2014-09/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201409 - 1`
awk 'NR=='$M201408', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-08.Posts.xml
echo "2014-08 done"

M201410=`awk '/CreationDate=\"2014-10/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201410 - 1`
awk 'NR=='$M201409', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-09.Posts.xml
echo "2014-09 done"

M201411=`awk '/CreationDate=\"2014-11/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201411 - 1`
awk 'NR=='$M201410', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-10.Posts.xml
echo "2014-10 done"

M201412=`awk '/CreationDate=\"2014-12/ {print NR; exit}' 2014.Posts.xml`
LAST=`expr $M201412 - 1`
awk 'NR=='$M201411', NR=='$LAST'-1; NR=='$LAST' {print; exit}' 2014.Posts.xml > 2014-11.Posts.xml
echo "2014-11 done"

awk 'NR>='$M201412 2014.Posts.xml > 2014-12.Posts.xml
echo "2014-12 done"

echo "Done extracting 2013 and 2014 data. Continuing to parse and clean."

cd ..

python SOParser.py

