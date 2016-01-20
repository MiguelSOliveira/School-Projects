.data:
	x: .word
	y: .word
	h: .word
	z: .word
	ahah: .word
	jk: .word
	sdasgdgashgdhas: .word
	avc: .word
	abc: .word
	d: .word
	r: .word
	chavetas: .word
	_ret: .word

.text:
main:
	li $t0, 1
	sw $t0, x
	li $t0, 2
	sw $t0, y
	li $t3, 1
	mul $t2, $t3, 5
	li $t3, 2
	div $t1, $t3, 4
	add $t0, $t1, $t2
	sw $t0, z
	li $t0, 1
	sw $t0, jk
	li $t0, 1231
	sw $t0, sdasgdgashgdhas
	li $t0, 1
	sw $t0, abc
	lw $t0, x
	li $t1, 5
	bgt $t0, $t1, L1
	li $t0, 1
	sw $t0, d
	li $t0, 2
	sw $t0, r

L1:
L2:	li $t0, 0
	beq $t0, 0, L3
	li $t0, 1
	sw $t0, chavetas
	j L2
L3:	lw $t1, d
	lw $t2, d
	mul $t0, $t1, $t2
	sw $t0, d
	li $t3, 4
	mul $t2, $t3, 5
	div $t1, $t2, 7
	addi $t0, $t1, 0
	sw $t0, _ret
