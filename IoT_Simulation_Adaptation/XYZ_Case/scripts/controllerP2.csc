set p2Counter 0
set counter 0
loop
wait
read var
rdata $var sender val
if($sender==s42)
	print $val
	plus p2Counter $p2Counter $val
	if($p2Counter>=300)
		send N 43
	else
		send A 43
	end
end
if($sender==s41)
	minus p2Counter $p2Counter $val
	if($p2Counter<300)
		send A 43
	else
		send N 43
	end
end
data p p2 $var
plus counter $counter 1
if ($counter>=2)
	set counter 0
	send $p 11
end