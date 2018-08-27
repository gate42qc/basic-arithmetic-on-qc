from pyquil.quil import Program
from pyquil.gates import I, X
from math import pi

"""
    All circuits are designed for LSB0 endianness.
    Meaning that at 0 index is the bit with the least siginificant digit.
"""


def bitlen(n: int):
    """
    Calculate bitlength of a given number n.
    
    :param n: number for which to calculute the bithlength
    
    :returns: bithlength of the number n.
    """
    l = 0
    while n > 0:
        n = int(n/2)
        l += 1
    return l


def prep_qubits(qubits: list, n: int):
    """
    Generate a quil program which prepares given qubits in a state representing number n.

    :param n: the number to write
    :param qubits: qubit indexes to write the number n

    :return: circuit to write number n on given qubits.
    """
    p = Program()

    for qubit in qubits:
        if n % 2 == 1:
            p.inst(X(qubit))
        else:
            p.inst(I(qubit))
        n = int(n/2)
    
    return p
