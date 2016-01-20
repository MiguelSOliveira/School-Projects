.data:
	x3: .word
	y3: .word
	h: .word
	z2: .word
	_ret: .word

.text:
main:
	li $t0, 2
	sw $t0, x3
	li $t0, 1
	sw $t0, y3
	li $t1, 6
	addi $t0, $t1, 5
	sw $t0, z2
