#!/bin/sh

echo Sync Doc to kiwi ...
rsync -av /home/kabe/git/prof/tau/Doxygen/ kiwi:public_html/PARP_doc/
echo Synd Doc Finished.

