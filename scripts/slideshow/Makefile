json.gif: JSON.key
	open JSON.key
	sleep 4
	osascript export.scpt
	mv ~/Pictures/JSON*/* .
	rm -fr ~/Pictures/JSON*
	convert -delay 1500 -loop 0 *.png json2.gif 
	convert json2.gif json.gif
	rm json2.gif
	rm -f *.png

clean:
	rm -f *.gif *.png
