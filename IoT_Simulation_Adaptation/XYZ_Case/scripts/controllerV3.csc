set v3Counter 0
set counter 0
loop
wait
read var
rdata $var sender val
if($sender==s24)
	plus v3Counter $v3Counter $val
	if($v3Counter>=300)
		send N 26
	else
		send A 26
	end
end
if($sender==s25)
	minus v3Counter $v3Counter $val
	if($v3Counter<300)
		send A 26
	else
		send N 26
	end
end
plus counter $counter 1
if($counter>=3)
	data p v3 $var
	set counter 0
	send $p 11
end