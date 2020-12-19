.globl strlen
strlen:
    xor %rax,%rax
    xor %rcx,%rcx
    not %rcx
    cld
    repnz scasb
    inc %rcx
    not %rcx
    mov %rcx,%rax
    ret

.globl write
write:
    mov $1,%rax;
    syscall
    ret

.globl read
read:
    mov $0,%rax;
    syscall
    ret

.globl socket
socket:
    mov $41,%rax
    mov $2,%rdi
    mov $1,%rsi
    mov $6,%rdx
    syscall
    ret

.globl bind
bind:
    mov $49,%rax
    syscall
    ret

.globl listen
listen:
    mov $50,%rax
    syscall
    ret

.globl accept
accept:
    mov $43,%rax
    syscall
    ret

.globl close
close:
    mov $3,%rax
    syscall
    ret

.globl fcntl
fcntl:
    mov $72,%rax
    syscall
    ret

.globl exit
exit:
    mov $60,%rax
    syscall
    ret

.globl epoll_create1
epoll_create1:
    mov $291,%rax
    syscall
    ret

.globl epoll_ctl
epoll_ctl:
    mov $233,%rax
    mov %rcx,%r10
    syscall
    ret

.globl epoll_wait
epoll_wait:
    mov $232,%rax
    mov %rcx,%r10
    syscall
    ret

.globl reuseaddr
reuseaddr:
    mov $1,%rax
    push %rax
    mov $54,%rax
    mov $1,%rsi
    mov $2,%rdx
    mov %rsp,%r10
    mov $4,%r8
    syscall
    pop %rdx
    ret

.globl openrw
openrw:
    mov $2,%rax
    mov $66,%rsi
    mov $0600,%rdx
    syscall
    ret
