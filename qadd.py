from pyquil.quil import Program
from pyquil.api import QVMConnection
from pyquil.gates import MEASURE
from math import pi
from qft import crotate, qft_core, inv_qft_core
from common import bitlen, prep_qubits

"""
    All circuits are designed for LSB0 endianness.
    Meaning that at 0 index is the bit with the least siginificant digit.
"""


def add_rotations(qubits_a: list, qubits_b: list):
    """
    Generate a quil program to rotate qubits_a controlled by qubits_b.
    
    :param qubits_a: qubits prepared in fourier transformed state
    :param qubits_b: qubits to use as controlls to rotate qubits_a
    
    :returns: a quil program to rotate qubits_a controlled by qubits_b.
    """
    p = Program()
    
    for i, qubit in enumerate(qubits_a):
        start_index = max(i + 1 - len(qubits_b), 0)
        p += crotate(qubit, qubits_b[:i+1], coef=1, start_index=start_index)
    
    return p


def add_qubits(a_qubits: list, b_qubits: list):
    """
    Generate a program to compute sum of numbers a and b using qft.
    
    :param a: first number to add
    :param b: second number to add
    
    :returns: a quil proram to add numbers a and b
    """
    p = Program()
    
    p += qft_core(a_qubits)
       
    p += add_rotations(a_qubits, b_qubits)
    
    p += inv_qft_core(a_qubits)
    
    return p


def add(a: int, b: int):
    qvm = QVMConnection()
    p = Program()
    
    # make sure the first number is the grather
    if a < b:
        t = a
        a = b
        b = t

    # Number of bits needed to store the sum of 
    # numbers a and b for which bitlen(a) <= n and bitlen(b) <= n is n + 1
    bitlen_a = max(bitlen(a), 1) + 1
    bitlen_b = max(bitlen(b), 1)
    
    a_qubits = list(range(0, bitlen_a))
    b_qubits = list(range(bitlen_a, bitlen_a+bitlen_b))
    
    p += prep_qubits(a_qubits, a)
    p += prep_qubits(b_qubits, b)
    
    p += add_qubits(a_qubits, b_qubits)
    
    p.inst([MEASURE(j, i) for i, j in enumerate(a_qubits)])
    
    result, = qvm.run(p, trials=1)    
    return sum([k*2**i for i, k in enumerate(result)])