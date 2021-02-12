set mod 0
set counter 0
loop
if($mod==0)
	areadsensor var
	rdata $var t x sensorVal1
	plus counter $sensorVal1 $counter
	print $counter
	data p s1 $sensorVal1
	send $p 2 
	while($sensorVal1<5.0)
		areadsensor var
		rdata $var t x sensorVal1
		plus counter $sensorVal1 $counter
		print $counter
		data p s1 $sensorVal1
		send $p 1
		delay 20000
	end
	if($sensorVal1>=5.0)
		set mod 1
	end
end
if($mod==1)
	while($sensorVal1>=5.0)
		areadsensor var
		rdata $var t x sensorVal1
		plus counter $sensorVal1 $counter
		print $counter
		data p s1 $sensorVal1
		send $p 1
		delay 10000
	end
	if($sensorVal1<5.0)
		set mod 0
	end
end