#!/bin/sh

UA="Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
python -c "from instalooter.looters import InstaLooter; InstaLooter._cachefs.settext(u'user-agent.txt', u'$UA')"