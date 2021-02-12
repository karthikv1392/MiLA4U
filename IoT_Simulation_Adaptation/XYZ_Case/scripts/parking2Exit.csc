set mod 0
loop
if($mod==0)
	areadsensor var
	rdata $var t x sensorVal1
	data p s41 $sensorVal1
	send $p 48
	while($sensorVal1<5.0)
		areadsensor var
		rdata $var t x sensorVal1
		data p s41 $sensorVal1
		send $p 48
		function y myf p2ExNorm,100,10
		delay $y
	end
	if($sensorVal1>=5.0)
		set mod 1
	end
end
if($mod==1)
	while($sensorVal1>=5.0)
		areadsensor var
		rdata $var t x sensorVal1
		data p s41 $sensorVal1
		send $p 48
		function y myf p2ExCrit,100,10
		delay $y
	end
	if($sensorVal1<5.0)
		set mod 0
	end
end
