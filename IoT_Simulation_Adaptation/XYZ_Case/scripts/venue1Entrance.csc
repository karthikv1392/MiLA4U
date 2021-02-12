set mod 0
loop
if($mod==0)
	areadsensor var
	rdata $var t x sensorVal1
	data p s1 $sensorVal1
	send $p 49
	while($sensorVal1<15.0)
		areadsensor var
		rdata $var t x sensorVal1
		data p s1 $sensorVal1
		send $p 49
		function y myf v1EnNorm,100,10
		delay $y
	end
	if($sensorVal1>=15.0)
		set mod 1
	end
end
if($mod==1)
	while($sensorVal1>=15.0)
		areadsensor var
		rdata $var t x sensorVal1
		data p s1 $sensorVal1
		send $p 49
		function y myf v1EnCrit,100,10
		delay $y
	end
	if($sensorVal1<15.0)
		set mod 0
	end
end