import numpy as np

def epsilonPrime(
        c: float,
        d_prime: float):
    epsilon_s_prime = ((c-d_prime)/c*0.003)
    
    return epsilon_s_prime

def fPrime(
        f_yl: float,
        epsilon_s_prime: float):
    f_s_prime = min(f_yl, epsilon_s_prime * 2e5)

    return f_s_prime

def Csteel(
        A_smin: float,
        A_s_prime: float,
        f_s_prime: float,
        f_c: float):
    
    Cs = max(A_smin, A_s_prime) * (f_s_prime-0.85*f_c)

    return Cs

def Cconcrete(
        f_c: float,
        b: float,
        a: float):
    Cc = 0.85 * f_c * b * a

    return Cc

def Tsteel(
        A_s: float,
        f_yl: float):
    T = A_s * f_yl

    return T

def CheckBeamDouble(
        c : float,
        d_prime: float,
        f_yl: float,
        f_c: float,
        A_s: float,
        A_s_prime: float,
        A_smin: float,
        b: float,
        beta_1: float):

    epsilon_s_prime = ((c-d_prime)/c*0.003)
    f_s_prime = min(f_yl, epsilon_s_prime*2e5)
    Cs = max(A_s_prime, A_smin) * (f_s_prime-0.85*f_c)
    Cc = 0.85 * f_c * b * beta_1 * c
    T = A_s * f_yl
    percent = (max((Cs+Cc), T) - min((Cs+Cc), T)) / max((Cs+Cc), T)

    return percent


def CheckBeamDesign(
        c : float,
        f_yl: float,
        f_c: float,
        A_s: float,
        A_s_prime: float,
        A_smin: float,
        b: float,
        h: float,
        dl: float,
        dt: float,
        cover: float,
        beta_1: float):
    
    a = A_s * f_yl / (0.85*f_c*b)
    d = h - (cover + dt + dl/2)
    d_prime = cover + dt + dl/2
    epsilon_s_prime = ((c-d_prime)/c*0.003)
    f_s_prime = min(f_yl, epsilon_s_prime*2e5)
    Cs = max(A_s_prime, A_smin) * (f_s_prime-0.85*f_c)
    Cc = 0.85 * f_c * b * beta_1 * c
    Mn = Cc*(d-a/2) + Cs*(d-d_prime)

    return Mn

def Asmin1(
        f_c : float,
        f_yl : float,
        b : float,
        d : float):
    A_smin1 = 0.25 * np.sqrt(f_c) / f_yl * b * d
    return A_smin1

def Asmin2(
        f_yl: float,
        b: float,
        d: float):
    A_smin2 = 1.4/f_yl * b * d
    return A_smin2




