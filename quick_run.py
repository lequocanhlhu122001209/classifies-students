#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"c:\Users\HP\Music\classifies-students")

# Import and run
from generate_word_doc import generate_comprehensive_doc

if __name__ == '__main__':
    try:
        generate_comprehensive_doc()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
