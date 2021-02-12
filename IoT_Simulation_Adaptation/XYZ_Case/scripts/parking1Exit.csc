set mod 0
loop
if($mod==0)
	areadsensor var
	rdata $var t x sensorVal1
	data p s33 $sensorVal1
	send $p 47
	while($sensorVal1<5.0)
		areadsensor var
		rdata $var t x sensorVal1
		data p s33 $sensorVal1
		send $p 47
		function y myf p1ExNorm,100,10
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
		data p s33 $sensorVal1
		send $p 47
		function y myf p1ExCrit,100,10
		delay $y
	end
	if($sensorVal1<5.0)
		set mod 0
	end
end
