#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys

result = subprocess.run([
    sys.executable, 
    "scripts/extend_word_to_40_pages.py"
], cwd="c:\\Users\\HP\\Music\\classifies-students")

sys.exit(result.returncode)
