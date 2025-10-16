@echo off
cd /d G:\CodingStuff\AnkiLeetCode\leetcode-anki-cli

:: Option A - pass tag on CLI:
python -m src.anki.review 

:: Option B - set environment variable for this run (alternative):
:: set "BORED_TAG=two pointers"
:: python -m src.anki.review

pause