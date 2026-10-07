; UBER256 - a 256-byte DOS/VGA intro: smooth rainbow palette + two interfering
; ring families (moire) that drift apart, in well under 256 bytes.
; NASM: nasm -f bin intro256.asm -o UBER256.COM        Target: DOS/DOSBox, VGA, 386+
BITS 16
ORG 100h

start:
    mov ax,13h
    int 10h
    push word 0A000h
    pop es
    in al,21h
    push ax                      ; save PIC mask (restored before exit)
    or al,2                      ; mask IRQ1: our own 60h/64h poll owns Esc
    out 21h,al

    ; Palette: three phase-shifted triangle waves = a seamless rainbow loop.
    mov dx,3C8h
    xor ax,ax
    out dx,al
    inc dx
    xor bx,bx
.pal:
    mov al,bl
    call tri
    out dx,al
    mov al,bl
    add al,85
    call tri
    out dx,al
    mov al,bl
    add al,170
    call tri
    out dx,al
    inc bl
    jnz .pal                     ; BX = 0 again: the frame/phase counter

frame:
    mov al,bl                    ; the second ring centre orbits the first
    call tri
    sub al,32
    cbw
    imul ax,ax,3
    add ax,160
    mov [ocx],ax
    mov al,bl
    add al,64                    ; quarter turn later: a circular path
    call tri
    sub al,32
    cbw
    add ax,ax
    add ax,100
    mov [ocy],ax
    xor di,di
    mov dx,200                   ; y (counts down)
.y:
    mov cx,320                   ; x (counts down)
.x:
    mov ax,cx
    sub ax,160
    imul ax,ax                   ; (x-160)^2
    mov si,ax
    mov ax,dx
    sub ax,100
    imul ax,ax                   ; (y-100)^2
    add ax,si                    ; r^2 from the screen centre
    shr ax,5
    call tri                     ; fold into a ring profile (0..63)
    mov si,ax                    ; first ring family
    mov ax,cx
    sub ax,[ocx]
    imul ax,ax
    mov bp,ax
    mov ax,dx
    sub ax,[ocy]
    imul ax,ax
    add ax,bp                    ; r^2 from the orbiting centre
    shr ax,5
    call tri                     ; second family
    add ax,si                    ; the moire is where the two profiles add
    shl al,1                     ; stretch 0..126 over the palette
    add al,bl                    ; and the palette rolls over time
    stosb
    loop .x
    dec dx
    jnz .y

    inc bx
    in al,64h                    ; 8042 status: wait for real scancode data
    test al,1
    jz frame
    in al,60h
    dec al                       ; Esc scancode 1 => zero
    jnz frame

    pop ax
    out 21h,al                   ; restore BIOS IRQ1 keyboard servicing
    mov ax,3
    int 10h
    ret

tri:                             ; AL = triangle(AL): 0..63
    sub al,128
    cbw
    xor al,ah
    shr al,1
    ret

ocx dw 0
ocy dw 0
