set mod 0
loop
if($mod==0)
	areadsensor var
	rdata $var t x sensorVal1
	data p s20 $sensorVal1
	send $p 50 
	while($sensorVal1<5.0)
		areadsensor var
		rdata $var t x sensorVal1
		data p s20 $sensorVal1
		send $p 50
		function y myf v2ExNorm,100,10
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
		data p s20 $sensorVal1
		send $p 50
		function y myf v2ExCrit,100,10
		delay $y
	end
	if($sensorVal1<5.0)
		set mod 0
	end
end