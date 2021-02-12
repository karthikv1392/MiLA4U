set mod 0
set counter 0
loop
if($mod==0)
	areadsensor var
	rdata $var t x sensorVal1
	plus counter $sensorVal1 $counter
	print $counter
	data p s1 $sensorVal1
	send $p 11
	while($sensorVal1<10.0)
		areadsensor var
		rdata $var t x sensorVal1
		plus counter $sensorVal1 $counter
		print $counter
		if($counter>=500.0)
			send N 7
		else
			send A 7
		end
		data p s1 $sensorVal1
		send $p 11
		delay 20000
	end
	if($sensorVal1>=10.0)
		set mod 1
	end
end
if($mod==1)
	while($sensorVal1>=10.0)
		areadsensor var
		rdata $var t x sensorVal1
		plus counter $sensorVal1 $counter
		print $counter
		if($counter>=500.0)
			send N 7

		else
			send A 7
		end
		data p s1 $sensorVal1
		send $p 11
		delay 10000
	end
	if($sensorVal1<10.0)
		set mod 0
	end
end