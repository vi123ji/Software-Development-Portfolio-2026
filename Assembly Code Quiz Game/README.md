# Assembly True or False Quiz Game

## Overview

This project is an interactive True or False quiz game developed in x86 Assembly Language for Linux. The program demonstrates the use of low-level programming concepts, including user input handling, conditional branching, memory management, procedures, and Linux system calls.

---

## Features

- Interactive command-line True or False quiz.
- Five multiple-choice questions.
- Score tracking throughout the game.
- Three-life system with remaining lives displayed after incorrect answers.
- Game over condition when all lives are lost.
- Displays the final score when the game ends.
- Modular implementation using Assembly procedures.

---

## Repository Structure

### Main Files

| File | Description |
|------|-------------|
| **True or False Game.asm** | Complete source code for the Assembly quiz game, including question handling, answer validation, score tracking, and game logic. |

---

## Technologies Used

- x86 Assembly Language (NASM)
- Linux
- Linux system calls (`int 80h`)

---

## Project Objective

This project aimed to develop an interactive quiz game in x86 Assembly Language while demonstrating core low-level programming concepts, including procedures, conditional branching, memory manipulation, user input handling, and direct interaction with the Linux operating system via system calls.

---

## Results

The completed application successfully presents a series of True or False questions, validates user responses, tracks the player's score and remaining lives, and ends the game either when all questions have been answered or when the player runs out of lives.

---

## Future Improvements

Potential future work includes:

- Supporting multiple difficulty levels.
- Accepting both uppercase and lowercase input.
- Adding coloured terminal output.
- Implementing a high-score system.

---
