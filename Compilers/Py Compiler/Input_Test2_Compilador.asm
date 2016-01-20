.data:
	ahah: .word
	jk: .word
	akb: .word
	lol: .word
	asd: .word
	LOLNiceOne: .word
	abc: .word
	avc: .word
	x: .word
	h: .word
	j: .word
	_ret: .word

.text:
main:
	li $t0, 1
	sw $t0, jk
	li $t0, 1231
	sw $t0, akb
	li $t0, 12
	sw $t0, lol
	li $t2, 3
	mul $t1, $t2, 5
	subi $t0, $t1, 2
	sw $t0, asd
	li $t0, 0
	sw $t0, LOLNiceOne
	li $t0, 1
	sw $t0, abc

L1:	li $t0, 10
	lw $t1, x
	beq $t0, $t1, L2
	li $t0, 1
	sw $t0, x
	j L1
L2:	lw $t0, x
	li $t1, 10
	bne $t0, $t1, L3
	li $t0, 3
	sw $t0, h
	li $t0, 1
	sw $t0, x

L3: