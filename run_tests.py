#!/usr/bin/env python
"""
Script para facilitar a execução dos testes.
"""
import sys
import subprocess

def run_tests():
    """Executa os testes com pytest."""
    print("Executando testes unitários...")
    test_command = [
        "pytest", 
        "-xvs", 
        "tests/",
        "--cov=app",
        "--cov-report=term-missing",
    ]
    result = subprocess.run(test_command)
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())
