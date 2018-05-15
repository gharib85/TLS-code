"""
In this script we have four methods.
1) Ham_RC builds the RC-frame Hamiltonian and system operators for both bath interactions.
    It takes in the system splitting, the RC frequency, system-RC coupling and the Hilbert space dimension.

2) RCME_operators builds the collapse operators for the RCME. It takes as input the
    Hamiltonian, system operator for phonon interaction, RC-residual coupling strength and beta (inv. T).

3) liouvillian_build... builds the RCME Liouvillian. Taking RC-residual coupling, RC-freq. and Temperature (for beta).
    It also takes a default parameter time_units which is set 'cm', giving frequencies in inverse cm.
    Can be set to 'ps' for inv. picoseconds.

4) RC_function_UD dresses up the Liouvillian with all the mapped RC frame parameters.
    It calculates these in accordance with Jake's initial paper.
"""
import numpy as np
import scipy as sp
from qutip import destroy, tensor, qeye, spre, spost, sprepost
#from sympy.functions import coth
import utils as UTILS

from utils import beta_f, Coth

def Ham_RC(sigma, eps, Omega, kappa, N, rotating=False):
    """
    Input: System splitting, RC freq., system-RC coupling and Hilbert space dimension
    Output: Hamiltonian, sigma_- and sigma_z in the vibronic Hilbert space
    """
    if rotating:
        eps=0.
    a = destroy(N)
    shift = (kappa**2)/Omega
    H_S = (eps+shift)*tensor(sigma.dag()*sigma, qeye(N)) + kappa*tensor(sigma.dag()*sigma, (a + a.dag()))+tensor(qeye(2),Omega*a.dag()*a)
    A_em = tensor(sigma, qeye(N))
    A_nrwa = tensor(sigma+sigma.dag(), qeye(N))
    A_ph = tensor(qeye(2), (a + a.dag()))
    return H_S, A_em, A_nrwa, A_ph

def RCME_operators(H_0, A, gamma, beta):
    # This function will be passed a TLS-RC hamiltonian, RC operator, spectral density and beta
    # outputs all of the operators needed for the RCME (underdamped)
    dim_ham = H_0.shape[0]
    Chi = 0 # Initiate the operators
    Xi = 0
    eVals, eVecs = H_0.eigenstates()
    ground_list = []
    excited_list = []
    for i in range(len(eVals)):
        is_ground = sum(eVecs[i])[0][0].real == 1.
        if is_ground:
            ground_list.append(i)
        else:
            excited_list.append(i)

    #print H_0
    #ti = time.time()
    for j in range(dim_ham):
        for k in range(dim_ham):
            e_jk = eVals[j] - eVals[k] # eigenvalue difference
            A_jk = A.matrix_element(eVecs[j].dag(), eVecs[k])
            outer_eigen = eVecs[j] * (eVecs[k].dag())
            if sp.absolute(A_jk) > 0:
                if sp.absolute(e_jk) > 0:
                    #print e_jk
                    # If e_jk is zero, coth diverges but J goes to zero so limit taken seperately
                    """
                    if (np.pi*gamma*A_jk/beta) >0:
                        print j, k
                        print j in ground_list, k in ground_list
                        print e_jk"""
                    Chi += 0.5*np.pi*e_jk*gamma * UTILS.Coth(e_jk * beta / 2)*A_jk*outer_eigen # e_jk*gamma is the spectral density
                    Xi += 0.5*np.pi*e_jk*gamma * A_jk * outer_eigen
                else:
                    """
                    if (np.pi*gamma*A_jk/beta) >0:
                        print j, k
                        print j in ground_list, k in ground_list
                        print e_jk"""

                    Chi += (np.pi*gamma*A_jk/beta)*outer_eigen # Just return coefficients which are left over
                    #Xi += 0 #since J_RC goes to zero

    return H_0, A, Chi, Xi

def liouvillian_build(H_0, A, gamma, wRC, T_C):
    # Now this function has to construct the liouvillian so that it can be passed to mesolve
    H_0, A, Chi, Xi = RCME_operators(H_0, A, gamma, beta_f(T_C))
    L = 0
    L-=spre(A*Chi)
    L+=sprepost(A, Chi)
    L+=sprepost(Chi, A)
    L-=spost(Chi*A)

    L+=spre(A*Xi)
    L+=sprepost(A, Xi)
    L-=sprepost(Xi, A)
    L-=spost(Xi*A)

    return L, Chi+Xi

def RC_function_UD(sigma, eps, T_ph, Gamma, wRC, alpha_ph, N, silent=False,
                                            residual_off=False, rotating=False):
    # we define all of the RC parameters by the underdamped spectral density
    gamma = Gamma / (2. * np.pi * wRC)  # coupling between RC and residual bath
    if residual_off:
        gamma=0
    kappa= np.sqrt(np.pi * alpha_ph * wRC / 2.)  # coupling strength between the TLS and RC

    if not silent:
        print "w_RC={} | TLS splitting = {} | RC-res. coupling={:0.2f} | TLS-RC coupling={:0.2f} | Gamma_RC={:0.2f} | alpha_ph={:0.2f} | N={} |".format(wRC, eps, gamma,  kappa, Gamma, alpha_ph, N)
    H, A_em, A_nrwa, A_ph = Ham_RC(sigma, eps, wRC, kappa, N, rotating=rotating)
    L_RC, Z =  liouvillian_build(H, A_ph, gamma, wRC, T_ph)

    return L_RC, H, A_em, A_nrwa, Z, wRC, kappa, Gamma
