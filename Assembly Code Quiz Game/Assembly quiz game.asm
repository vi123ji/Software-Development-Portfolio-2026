;Assembly quiz game

section .data
    welcomeMsg db "Welcome to the True or False Game", 10
    welcomeLen equ $-welcomeMsg

    q1 db "Is learning assembly code hard? (T/F): ", 10
    q1Len equ $-q1
    a1 db 'T'

    q2 db "Is computer science cool? (T/F): ", 10
    q2Len equ $-q2
    a2 db 'T'

    q3 db "Assembly code is a high level programming language (T/F): ", 10
    q3Len equ $-q3
    a3 db 'F'

    q4 db "Assembly language is easier to read than Python (T/F): ", 10
    q4Len equ $-q4
    a4 db 'F'

    q5 db "Linux is an operating system? (T/F): ", 10
    q5Len equ $-q5
    a5 db 'T'

    correctMsg db "Correct", 10
    correctLen equ $-correctMsg

    wrongMsg db "Wrong, you have lost a life", 10
    wrongLen equ $-wrongMsg

    lifeMsg db "Lives remaining: ", 10
    lifeLen equ $-lifeMsg

    gameOverMsg db "You have run out of lives. Game Over", 10
    gameOverLen equ $-gameOverMsg

    finalScoreMsg db "Your final score is: ", 10
    finalScoreLen equ $-finalScoreMsg

    newline db 10
    newlineLen equ $-newline

section .bss
    userInput resb 1
    score resb 1
    lives resb 1

section .text
    global _start

_start:
    ; Initialize score and lives
    mov byte [score], 0
    mov byte [lives], 3

    ; Display welcome message
    mov edx, welcomeLen
    mov ecx, welcomeMsg
    mov ebx, 1
    mov eax, 4
    int 80h

    call ask_q1
    call check_game_over
    call ask_q2
    call check_game_over
    call ask_q3
    call check_game_over
    call ask_q4
    call check_game_over
    call ask_q5
    call check_game_over

    call show_final_score
    jmp end_program

; Function to ask a question and check answer
ask_q1:
    mov edx, q1Len
    mov ecx, q1
    call ask_question
    mov al, [a1]
    call check_answer
    ret

ask_q2:
    mov edx, q2Len
    mov ecx, q2
    call ask_question
    mov al, [a2]
    call check_answer
    ret

ask_q3:
    mov edx, q3Len
    mov ecx, q3
    call ask_question
    mov al, [a3]
    call check_answer
    ret

ask_q4:
    mov edx, q4Len
    mov ecx, q4
    call ask_question
    mov al, [a4]
    call check_answer
    ret

ask_q5:
    mov edx, q5Len
    mov ecx, q5
    call ask_question
    mov al, [a5]
    call check_answer
    ret

ask_question:
    ; Print question
    mov ebx, 1
    mov eax, 4
    int 80h

    ; Read user input properly
    mov edx, 1
    mov ecx, userInput
    mov ebx, 0
    mov eax, 3
    int 80h

    ; Clear input buffer to avoid skipping questions
    mov edx, 1
    mov ecx, userInput
    mov ebx, 0
    mov eax, 3
    int 80h
    ret

check_answer:
    mov bl, [userInput]
    cmp bl, al

    jne wrong_response

correct_response:
    inc byte [score]
    mov edx, correctLen
    mov ecx, correctMsg
    call print_message
    ret

wrong_response:
    dec byte [lives]
    mov edx, wrongLen
    mov ecx, wrongMsg
    call print_message

    ; Show remaining lives
    mov edx, lifeLen
    mov ecx, lifeMsg
    call print_message

    mov al, [lives]
    add al, '0'
    mov [userInput], al

    mov edx, 1
    mov ecx, userInput
    call print_message

    ; Print newline so the next question doesn't appear on the same line
    mov edx, newlineLen
    mov ecx, newline
    call print_message
    ret

check_game_over:
    cmp byte [lives], 0
    jne continue_game
    mov edx, gameOverLen
    mov ecx, gameOverMsg
    call print_message
    jmp end_program

continue_game:
    ret

show_final_score:
    mov edx, finalScoreLen
    mov ecx, finalScoreMsg
    call print_message

    mov al, [score]
    add al, '0'
    mov [userInput], al

    mov edx, 1
    mov ecx, userInput
    call print_message
    ret

print_message:
    mov ebx, 1
    mov eax, 4
    int 80h
    ret

end_program:
    mov eax, 1
    int 80h
