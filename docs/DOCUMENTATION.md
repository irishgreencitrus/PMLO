# Pomelo Programming Language (PMLO)
## Table of contents
  * [What is PMLO?](#what-is-pmlo)
  * [Documentation Features](#documentation-features)
    + [Stack Notation](#stack-notation)
    + [REPL Notation](#repl-notation)
  * [The Language Explained](#the-language-explained)
    + [Comments](#comments)
    + [Pushing to the stack](#pushing-to-the-stack)
      - [Pushing Numbers to the stack](#pushing-numbers-to-the-stack)
      - [Pushing 'strings' to the stack](#pushing-strings-to-the-stack)
      - [Pushing Numbers to the stack: part 2](#pushing-numbers-to-the-stack-part-2)
    + [Functions](#functions)
    + [Labels](#labels)
    + [Label Functions](#label-functions)
    + [Registers](#registers)
    + [Scopes and Pomelo's multiple stacks.](#scopes-and-pomelos-multiple-stacks)
    + [Stack functions](#stack-functions)
      - [Specifically moving values from the current scope.](#specifically-moving-values-from-the-current-scope)
  * [List of builtins](#list-of-builtins)
    + [Builtin functions](#builtin-functions)
    + [Scope control](#scope-control)
    + [Literals](#literals)
    + [Labels](#labels-1)
    + [Label Functions](#label-functions-1)
    + [Register Functions](#register-functions)
    + [Stack Functions](#stack-functions)
## What is PMLO?
Pomelo is a stack-based language.
It's designed to be different.
There are no traditional loops or if statements or mathematical expressions.
Every function manipulates the stack.
A functions only input can be the top values on the stack, and its outputs are placed onto the stack.

There is an interpreter written in Python, and a transpiler which transpiles to C.
You can find the interpreter in `pmlo_executor.py` and the transpiler in `pmlo_transpiler.py`.
I aim to make both implementations have complete parity, but I may implement features in the interpreter first.
## Documentation Features
Some things in Pomelo are a bit eccentric, so helpers are used to explain things.
### Stack Notation
This is stack notation:
```pmlo
[5, 4, 3, 2]
```
The leftmost item is the top of the stack, the rightmost is the bottom.
I decided to do it this way because the top of the stack is the most important thing in PMLO.
You can't really do anything with the bottom of the stack at all, so it is rightmost.
### REPL Notation
This is REPL notation.
> I have plans to implement a repl exactly like this, however it hasn't been done yet. Soon(TM)
```pmlorepl
PMLO ==> 1 2 +
3
```
This is a way to show the output of functions, assuming the repl is clear at the start of the code block.
## The Language Explained
### Comments
First, and maybe least important, a line which starts with a `@` symbol is a comment.
I have nothing else to say about them. Use comments or don't, completely your choice.
### Pushing to the stack
#### Pushing Numbers to the stack
Want to push a number to the stack? Just write the number.
Currently, only positive integers are supported to be pushed like this,
however all numbers can be put on the stack in other ways.
```pmlo
2 3 4 5
```

The stack now looks like this:
`[5, 4, 3, 2]`

You can use `$` to print the top value of the stack. This will print `5`. It doesn't remove this value from the stack.
If you want it to, just use `-$` which directly pops the value off the stack to print it, discarding it in the process.
#### Pushing 'strings' to the stack

What about other datatypes on the stack? Sorry, that can't be done. There are no strings in PMLO.
It's up for the user to decide what data holds what in the stack.

This: 
```pmlo
"Hello World"
```
is equivalent to writing this:
```pmlo
72 101 108 108 111 32 87 111 114 108 100
```
They both result in the stack being this:
```pmlo
[100, 108, 114, 111, 87, 32, 111, 108, 108, 101, 72]
```
Strings are obviously easier to type for some things, but there is no technical advantage to them.
#### Pushing Numbers to the stack: part 2
```pmlo
1..100
```
This is a range. It pushes everything in the range to the stack.
```pmlo
1..10
```
is functionally equivalent to:
```pmlo
1 2 3 4 5 6 7 8 9 10
```
> Tip: for big ranges, it is more efficient to use range notation.
> You should never write out numbers if you can write them in a range.
> Mostly for your sanity

I don't have much more to say here, because it is just shorthand.
This feature is more for developer sanity compared to any functional usage
### Functions
```pmlorepl
PMLO => 1 2 +
3
```
That's doesn't look like your usual addition, so what's going on here?
I'll explain.

The stack starts out looking like this.
```pmlo
[2, 1]
```
Then the addition function does this.
1) Pop the last value off of the stack (removing it) and store it in a temporary variable `a`. In this example, `a` would be `2` 
2) Pop the last value off of the stack (removing it) and store it in a temporary variable `b`. In this example, `b` would be `1`
3) Append the value of `a + b` to the stack
4) In this example, the topmost value of the stack would now be 3.

This is effectively the way all functions work in PMLO.
Not that hard to understand for something like addition, but for something like subtraction, where the order of things on the stack matter.
Sometimes this means that PMLO can feel very counterintuitive.

```pmlorepl
PMLO => 3 4 -
1
```

This may seem very weird. Because it could seem like the order of operations is wrong here. I assure you, it isn't.
First, we're pushing `3 4` to the stack. So the topmost value of the stack is `4`. (The entire stack is `[4,3]`). And the function is technically `(topmost value of stack - second topmost value of the stack)`.
leading to `1` and not, as some of you may have been expecting `-1`
### Labels
This is a label.
```pmlo
::HELLO_WORLD
```
Labels have strict syntax. They start with two colons,
and are succeeded by a name which is only allowed to contain uppercase letters, and underscores.
You can jump to labels with label functions.
### Label Functions
So what can you do with labels? Use label functions with them.

This is a label function:
```pmlo
jump:HELLO_WORLD
```
This unconditionally jumps to labels, and can jump backwards or forwards through the code.
The interpreter will throw an error if you try to jump to a label which doesn't exist, even if the requirement was false.
Label functions can be used to replace loops, and if statements.
You can find a list of label functions later in this document.
### Registers
There aren't really variables in PMLO.
However, you are allowed one character variables, only containing lowercase letters (no underscores), called "Registers".
You can set a register using a register function.
```pmlo
3 pop_into<x>
```
This code will mean that the `x` register now has the value `3`.
This function is destructive, meaning the stack is now empty `[]`.

If you want a non-destructive alternative of this function, you can use this
```pmlo
3 copy_into<x>
```
The `x` register will have the value `3` now.
However, since the function is non-destructive, the stack is still `[3]`.

If you want to take a value out of `x`, you can do this
```pmlo
pull_from<x>
```
Assuming the value of `x` was `3`, like in the previous example, this will append `3` to the stack.
This operation is non-destructive, as I don't see why you would ever want to clear a register.
You can always overwrite a register anyway.

### Scopes and Pomelo's multiple stacks.
You can open a scope by using the square brackets.

`[` Opens a scope

`]` Closes a scope

Scopes have their own private stacks, which are independent of other stacks.
All functions, label functions, and register functions will only see the stack owned by the current scope.
When you open a scope, the new stack will start out empty;
When the scope closes, the stack will be appended to the stack you're changing to.

For example:
```pmlo
3000
[
    1..100
]
```
The main stack now has the value of 
```
[100, 99, ...(skipped for brevity) , 3000]
```
This would hold no matter how many scopes you opened.
```pmlo
3000
[
    [
        [
            1..100
        ]
    ]
]
```
You still get the same stack value of
```
[100, 99, ...(skipped for brevity) , 3000]
```
The scope where the range function is cannot see the `3000` at the end of the stack. 

That is the reason why you need scopes.
### Stack functions

However, what if you want to explicitly do something in a scope.
Like bringing in a value from another scoped stack, the main stack, or moving a value from one stack to the current one.

Stack functions are the answer.

They have the same syntax as for register functions, but they use a number instead of a letter.
This number denotes the id of the scoped stack you want to do something with.
> Tip: Stack `0` is always accessible and is the main stack / program stack.

```pmlo
3000
[
    pull_from<0>
]
```
When you execute `pull_from<0>`, it takes the value at the top of the main stack, and appends it to your scoped stack.
This means the scoped stack now equals `[3000]`.
However, crucially, the main stack no longer has `3000` at the top of the stack.
In this example, we actually leave the main stack empty until the scope closes, where it returns to the original value of `[3000]`.

#### Specifically moving values from the current scope.
When a scope closes, it will automatically append all values to the previous stack,
however what happens if you want to explicitly move the value from the top of the current stack to a different one?

> You can't move values into a scope in the future! This can only move values backwards.
> This may change in the future, allowing you to use temporary stacks with imaginary numbers.

You can use `pop_into<0>`.

In the examples directory you'll find a use case for this.
Since the label function `jump_if_stack_not_empty` only sees the current scope, it can effectively loop through the current stack,
do something with it, and then 'return' the result back to the main stack.
It'll keep doing this until it sees the current stack as empty, where it will now not jump, and just continue on normally.
## List of builtins
### Builtin functions
`+` Add the top two values on the stack

`-` Subtract the top two values on the stack

`*` Multiply the top two values on the stack

`pow` Raise the top value on the stack to the next top value on the stack

`/` Divide the top two values on the stack

`%` Modulo the top two values on the stack

`++` Increment the top value on the stack

`--` Decrement the top value on the stack

`!!` Reverses the stack. The top value is now the bottom value etc.

`$` Outputs the top value on the stack as a number

`-$` Outputs the top value on the stack as a number AND removes it

`$$` Outputs the top value on the stack as a letter

`-$$` Outputs the top value on the stack as a letter AND removes it

`$!` Outputs the entire stack as a list of numbers. Top value is leftmost etc.

`$$!` Outputs the entire stack as a string. Top value is leftmost etc.

`/$` Allows the user to input a number. Not currently implemented when transpiled to C

`||` Boolean OR of the top two values on the stack.

`&&` Boolean AND of the top two values on the stack.

`!` Boolean NOT of the top value on the stack.
### Scope control
`[` Opens a new scope
`]` Closes the current scope
### Literals
`<number>` eg. `3000` Pushes the value to the top of the stack.

`"<string>"` eg. `"Hello World"` Pushes each character of the string as ASCII to the top of the stack.

`<start>..<end>` eg. `1..100` Pushes each number to the top of the stack, on after another.
### Labels
`:IDENTIFIER` eg. `:POSITION_A` A label you can jump to with a label function. The identifier must be UPPERCASE, and can contain underscores.
### Label Functions
`jump:LABEL` Unconditionally jumps to the label.

`jump_if_not_zero:LABEL` Only jumps to the label if the value on the top of the stack is not zero.

`jump_if_zero:LABEL` Only jumps to the label if the value on the top of the stack is not zero.

`jump_if_stack_not_empty:LABEL` Only jumps to the label if the stacks' length is not zero (empty).

`jump_if_stack_empty:LABEL` Only jumps to the label if the stacks' length is zero (empty).

`jump_if_stack_one:LABEL` Only jumps to the label if the stacks' length is one.

`jump_if_stack_not_one:LABEL` Only jumps to the label if the stack's length is not one.
### Register Functions
`pop_into<a>` Pops the value off of the top of the stack into the register `a`, removing it.

`copy_into<a>` Copies the value off of the top of the stack into the register `a`, keeping it in the stack.

`pull_from<a>` Takes the value from register `a` and puts it on the top of the stack. This does not clear the register.

`print<a>` Prints the value in register `a` as an integer.
### Stack Functions
`pop_into<0>` Pops the value off of the current stack and puts it into the stack mentioned, removing it from the current stack. Stack `0` is always the main stack (unscoped).

`copy_into<0>` Copies the value off of the current stack and puts it into the stack mentioned, keeping it in the current stack.

`pull_from<0>` Pops the value off of the mentioned stack, and puts it into the current stack, removing it from the mentioned stack.

`print<0>` Prints the stack mentioned. 

> Warning: This language is very, very much not complete.
> Anything may change at anytime and it may take a while to be updated in the documentation.
> If in doubt, read the source.