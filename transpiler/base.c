#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

#define COLOUR_ERROR "\x1B[31m"
#define COLOUR_RESET "\x1B[0m"

#define MAX_STACK_SIZE 0xffff
#define STACK_DATA_TYPE long double
#define STACK_INT_DATA_TYPE intmax_t
#define STACK_DATA_TYPE_FORMATTER "%Lf"

#ifdef _WIN32
    #define NOCOLOUR
#endif



//PMLO Fatal Error
void PMLO_Fatal(char* reason) {
#ifndef NOCOLOUR
    printf(COLOUR_ERROR);
#endif
    printf("\n--- PMLO RUNTIME ERROR ---\n%s\n\n",reason);
#ifndef NOCOLOUR
    printf(COLOUR_RESET);
#endif
    exit(1);
}


//PMLO Stack
typedef struct PMLO_Stack {
    STACK_DATA_TYPE items[MAX_STACK_SIZE];
    uint16_t stack_size;
    int32_t top;
} PMLO_Stack;

void PMLO_Stack_new(PMLO_Stack *s) {
    s->top = -1;
    s->stack_size = 0;
}

// Core functions

uint8_t PMLO_Stack_core_isFull(PMLO_Stack *s) {
    return s->top == MAX_STACK_SIZE - 1;
}

uint8_t PMLO_Stack_core_isEmpty(PMLO_Stack *s) {
    return s->top == -1;
}

uint8_t PMLO_Stack_core_isLength(PMLO_Stack *s,STACK_DATA_TYPE len) {
    return s->top == (len - 1);
}

void PMLO_Stack_core_push(PMLO_Stack *s, STACK_DATA_TYPE newItem) {
    if (PMLO_Stack_core_isFull(s)) {
        PMLO_Fatal("Stack is full: can't push any more items.");
    }
    s->top++;
    s->items[s->top] = newItem;
    s->stack_size++;
}

STACK_DATA_TYPE PMLO_Stack_core_pop(PMLO_Stack *s) {
    if (PMLO_Stack_core_isEmpty(s)) {
        PMLO_Fatal("Stack is empty: can't be popped.");
    }
    STACK_DATA_TYPE tmp = s->items[s->top];
    s->top--;
    s->stack_size--;
    return tmp;
}
STACK_DATA_TYPE PMLO_Stack_core_getTop(PMLO_Stack *s) {
    if (PMLO_Stack_core_isEmpty(s)) {
        PMLO_Fatal("Stack is empty: can't get top value.");
    }
    return s->items[s->top];
}
void PMLO_Stack_core_reverse(PMLO_Stack *s) {
    STACK_DATA_TYPE tmp;
    uint16_t start = 0;
    int32_t end = s->top;
    while (start < end) {
        tmp = s->items[start];
        s->items[start] = s->items[end];
        s->items[end] = tmp;
        start++;
        end--;
    }
}
void PMLO_Stack_core_append(PMLO_Stack *s1, PMLO_Stack *s_to_append) {
    PMLO_Stack_core_reverse(s_to_append);
    while (!PMLO_Stack_core_isEmpty(s_to_append)) {
        PMLO_Stack_core_push(s1, PMLO_Stack_core_pop(s_to_append));
    }
}
// End base functions




// Output functions
void PMLO_Stack_output_dumpStack(PMLO_Stack *s) {
    printf("[");
    for (int i = s->stack_size - 1; i > -1; i--) {
        printf(STACK_DATA_TYPE_FORMATTER, s->items[i]);
        if (i != 0){
            printf(", ");
        }
    }
    printf("]\n");
}

void PMLO_Stack_output_dumpVal(PMLO_Stack *s){
    printf(STACK_DATA_TYPE_FORMATTER"\n",PMLO_Stack_core_getTop(s));
}
void PMLO_Stack_output_dumpValStr(PMLO_Stack *s){
    putchar(PMLO_Stack_core_getTop(s));
}

void PMLO_Stack_output_dumpValDestr(PMLO_Stack *s){
    printf(STACK_DATA_TYPE_FORMATTER"\n",PMLO_Stack_core_pop(s));
}
void PMLO_Stack_output_dumpValStrDestr(PMLO_Stack *s){
    putchar(PMLO_Stack_core_pop(s));
}

void PMLO_Stack_output_dumpStackStr(PMLO_Stack *s) {
    for (int i = s->stack_size - 1; i > -1; i--) {
        putchar(PMLO_Stack_core_getTop(s));
    }
    putchar('\n');
}
// End output functions


// Start mathematical operators
void PMLO_Stack_maths_add(PMLO_Stack *s){
    STACK_DATA_TYPE a = PMLO_Stack_core_pop(s);
    STACK_DATA_TYPE b = PMLO_Stack_core_pop(s);
    PMLO_Stack_core_push(s,a+b);
}
void PMLO_Stack_maths_minus(PMLO_Stack *s){
    STACK_DATA_TYPE a = PMLO_Stack_core_pop(s);
    STACK_DATA_TYPE b = PMLO_Stack_core_pop(s);
    PMLO_Stack_core_push(s,a-b);
}
void PMLO_Stack_maths_multiply(PMLO_Stack *s){
    STACK_DATA_TYPE a = PMLO_Stack_core_pop(s);
    STACK_DATA_TYPE b = PMLO_Stack_core_pop(s);
    PMLO_Stack_core_push(s,a*b);
}
void PMLO_Stack_maths_divide(PMLO_Stack *s){
    STACK_DATA_TYPE a = PMLO_Stack_core_pop(s);
    STACK_DATA_TYPE b = PMLO_Stack_core_pop(s);
    PMLO_Stack_core_push(s,a/b);
}
void PMLO_Stack_maths_modulo(PMLO_Stack *s){
    STACK_INT_DATA_TYPE a = (STACK_INT_DATA_TYPE)PMLO_Stack_core_pop(s);
    STACK_INT_DATA_TYPE b = (STACK_INT_DATA_TYPE)PMLO_Stack_core_pop(s);
    PMLO_Stack_core_push(s,a%b);
}
void PMLO_Stack_maths_power(PMLO_Stack *s){
    STACK_DATA_TYPE a = PMLO_Stack_core_pop(s);
    STACK_DATA_TYPE b = PMLO_Stack_core_pop(s);
#ifdef __TINYC__
    PMLO_Stack_core_push(s,pow(a,b));
#else
    PMLO_Stack_core_push(s,powl(a,b));
#endif
}
void PMLO_Stack_maths_incr(PMLO_Stack *s){
    STACK_DATA_TYPE a = PMLO_Stack_core_pop(s) + 1;
    PMLO_Stack_core_push(s,a);
}
void PMLO_Stack_maths_decr(PMLO_Stack *s){
    STACK_DATA_TYPE a = PMLO_Stack_core_pop(s) - 1;
    PMLO_Stack_core_push(s,a);
}
// End mathematical operators

// Start boolean operators
void PMLO_Stack_bool_or(PMLO_Stack *s){
    STACK_DATA_TYPE a = PMLO_Stack_core_pop(s);
    STACK_DATA_TYPE b = PMLO_Stack_core_pop(s);
    PMLO_Stack_core_push(s,(a||b));
}

void PMLO_Stack_bool_and(PMLO_Stack *s){
    STACK_DATA_TYPE a = PMLO_Stack_core_pop(s);
    STACK_DATA_TYPE b = PMLO_Stack_core_pop(s);
    PMLO_Stack_core_push(s,(a&&b));
}
void PMLO_Stack_bool_not(PMLO_Stack *s){
    STACK_DATA_TYPE a = PMLO_Stack_core_pop(s);
    PMLO_Stack_core_push(s,(!a));
}
// End boolean operators

// START MAIN