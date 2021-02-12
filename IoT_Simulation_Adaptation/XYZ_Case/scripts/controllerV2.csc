set v2Counter 0
set counter 0
loop
wait
read var
rdata $var sender val
if($sender==s18)
	plus v2Counter $v2Counter $val
	if($v2Counter>=300)
		send N 17
	else
		send A 17
	end
end
if($sender==s20)
	minus v2Counter $v2Counter $val
	if($v2Counter<300)
		send A 17
	else
		send N 17
	end
end
plus counter $counter 1
print $counter
if ($counter>=3)
	data p v2 $var
	set counter 0
	send $p 11
end