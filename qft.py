from pyquil.quil import Program
from pyquil.gates import H, CPHASE, SWAP
from math import pi

"""
    All circuits are designed for LSB0 endianness.
    Meaning that at 0 index is the bit with the least siginificant digit.
"""

def reverse_qubits(qubits, order=1):
    """
    Generates a quil programm to reverse given qubits.
    
    :param qubits: List of qubits indexes to do reversal with.
    :param order: Specifies the ordering of instractions. 
                Set dir=1 for normal ordering and -1 for reverse.
    
    :returns: A quil program to do a bit reversal of given qubits.
    """
    p = Program()
    l = len(qubits)
    for i in range(l / 2)[::order]:
        p.inst(SWAP(qubits[i], qubits[-i-1]))
    
    return p


def crotate(qubit, controls, coef=1, start_index=0):
    """
    Generates the a circuit to make conditional rotations
    on the `qubit` using `controls` as control qubits.

    :param qubit: the qubit to apply the rotation on.
    :param controls: the control qubits to use for rotation.
    :param coeff: A modifier for the angle used in rotations (-1 for inverse
                 QFT, 1 for QFT)
    :param start_index: index of the controls[0] q indicating from which digit are the control qubits given.
    :return: A Quil program to compute the conditional rotation
           on the `qubit` using `controls` as control qubits
    """
    instructions = []
    for index, cqubit in enumerate(controls[::-1]):
        angle = pi/2**(index + start_index)
        instructions.append(CPHASE(coef * angle, cqubit, qubit))
    
    return instructions


def qft_core(qubits, coef=1):
    """
    Generates a quil programm that performs 
    quantum fourier transform on given qubits 
    without swaping qubits at the end.
    
    :param qubits: A list of qubit indexes.
    :param coeff: A modifier for the angle used in rotations (-1 for inverse
                 QFT, 1 for QFT)
    :return: A Quil program to compute the QFT of the given qubits without swapping.
    """
    p = Program()
    
    # Iterate over qubits starting from the most significant
    for i, qubit in enumerate(qubits[::-1]):
        p.inst(H(qubit))
        
        # Add controlled rotations R_i for i in 1 .. n-1
        # using all qubits right to current
        p.inst(crotate(qubit, qubits[:-i-1], coef=coef, start_index=1))
    return p


def inv_qft_core(qubits):
    """
    Generates a quil programm that performs 
    inverse quantum fourier transform on given qubits 
    without swaping qubits at the end.
    
    :param qubits: A list of qubit indexes.
    :return: A Quil program to compute the invese QFT of the given qubits without swapping.
    """    
    qft_quil = Program.inst(qft_core(qubits, coef=-1))
    inv_qft_quil = Program()

    while(len(qft_quil) > 0):
        inst = qft_quil.pop()
        inv_qft_quil.inst(inst)

    return inv_qft_quil


def qft(qubits, coeff=1):
    """
    Generates a quil programm that performs 
    quantum fourier transform on given qubits.
    
    :param qubits: A list of qubit indexes.
    :return: A Quil program to compute the QFT of the given qubits.
    """
    return qft_core(qubits, coeff=coeff)+reverse_qubits(qubits)


def inv_qft(qubits):
    """
    Generates a quil programm that performs 
    inverse quantum fourier transform on given qubits.
    
    :param qubits: A list of qubit indexes.
    :return: A Quil program to compute the inverse QFT of the given qubits.
    """
    return reverse_qubits(qubits, order=-1)+inv_qft_core(qubits)
