#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys
import os

os.chdir(r"c:\Users\HP\Music\classifies-students")
result = subprocess.run([
    r"c:/Users/HP/Music/classifies-students/.venv/Scripts/python.exe",
    "generate_word_doc.py"
], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print(f"Return code: {result.returncode}")
