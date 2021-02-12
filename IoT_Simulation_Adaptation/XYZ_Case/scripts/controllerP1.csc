set p1Counter 0
set counter 0
loop
wait
read var
rdata $var sender val
if($sender==s34)
	plus p1Counter $p1Counter $val
	if($p1Counter>=200)
		send N 35
	else
		send A 35
	end
end
if($sender==s33)
	minus p1Counter $p1Counter $val
	if($p1Counter<200)
		send A 35
	else
		send N 35
	end
end
data p p1 $var
plus counter $counter 1
if ($counter>=2)
	set counter 0
	send $p 11
end