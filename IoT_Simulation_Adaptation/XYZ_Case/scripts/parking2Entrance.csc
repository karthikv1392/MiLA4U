set mod 0
loop
if($mod==0)
	areadsensor var
	rdata $var t x sensorVal1
	data p s42 $sensorVal1
	send $p 48
	while($sensorVal1<12.0)
		areadsensor var
		rdata $var t x sensorVal1
		data p s42 $sensorVal1
		send $p 48
		function y myf p2EnNorm,100,10
		delay $y
	end
	if($sensorVal1>=12.0)
		set mod 1
	end
end
if($mod==1)
	while($sensorVal1>=12.0)
		areadsensor var
		rdata $var t x sensorVal1	
		data p s42 $sensorVal1
		send $p 48
		function y myf p2EnCrit,100,10
		delay $y
	end
	if($sensorVal1<12.0)
		set mod 0
	end
end
