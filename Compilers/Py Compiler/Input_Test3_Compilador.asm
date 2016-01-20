.data:
	x: .word
	d: .word
	e: .word
	f: .word
	_ret: .word

.text:
main:
	li $t0, 1
	sw $t0, d
	li $t0, 2
	sw $t0, e
	li $t1, 1
	addi $t0, $t1, 2
	sw $t0, d
