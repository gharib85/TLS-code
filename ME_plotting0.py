from qutip import ket, mesolve, qeye, tensor, thermal_dm, destroy, steadystate
import matplotlib.pyplot as plt
import numpy as np
import UD_liouv as RC
import driving_liouv as EM
import ME_checking as check
import scipy as sp
reload(RC)
reload(EM)
reload(check)
plt.style.use('ggplot')


def plot_RC_pop(ax):

    #ax.title(r"$\omega_0=$""%i"r"$cm^{-1}$, $\alpha_{ph}=$""%f"r"$cm^{-1}$, $T_{EM}=$""%i K" %(w0, alpha_ph, T_EM))
    #ax.plot(timelist, 1-DATA_nrwa.expect[0], label='nrwa', color='y')
    ax.plot(timelist, DATA_ns.expect[2].real, label='Non-secular', color='g')
    #ax.plot(timelist, DATA_s.expect[2].real, label='Vib. Lindblad', color='b')
    #ax.plot(timelist, DATA_naive.expect[2].real, label='Simple Lindblad', color='r')
    ax.set_ylabel("Reaction-Coordinate "r"$\langle n\rangle$")
    ax.set_xlabel("Time (cm)")
    ax.legend()

def plot_RC_disp(ax):

    #ax.title(r"$\omega_0=$""%i"r"$cm^{-1}$, $\alpha_{ph}=$""%f"r"$cm^{-1}$, $T_{EM}=$""%i K" %(w0, alpha_ph, T_EM))
    #ax.plot(timelist, 1-DATA_nrwa.expect[0], label='nrwa', color='y')
    ax.plot(timelist, DATA_ns.expect[3].real, label='Non-secular', color='g')
    #ax.plot(timelist, DATA_s.expect[3].real, label='Vib. Lindblad', color='b')
    #ax.plot(timelist, DATA_naive.expect[3].real, label='Simple Lindblad', color='r')
    ax.set_ylabel("Reaction-Coordinate displacement")
    ax.set_xlabel("Time (cm)")
    ax.legend()

def plot_dynamics(ax):
    """
    #if T_EM>0.0: # No need to plot SS for T=0
    ss_ns = steadystate(H, [L_RC+L_ns]).ptrace(0)
    ss_v = steadystate(H, [L_RC+L_s]).ptrace(0)
    ss_n = steadystate(H, [L_RC+L_naive]).ptrace(0)
    ss_g_ns = ss_ns.matrix_element(G.dag(), G)
    ss_g_v = ss_v.matrix_element(G.dag(), G)
    ss_g_n = ss_n.matrix_element(G.dag(), G)
    ax.axhline(1-ss_g_v.real, color='b', ls='--')
    ax.axhline(1-ss_g_ns.real, color='g', ls='--')
    ax.axhline(1-ss_g_n.real, color='r', ls='--')
    """
    #ax.title(r"$\omega_0=$""%i"r"$cm^{-1}$, $\alpha_{ph}=$""%f"r"$cm^{-1}$, $T_{EM}=$""%i K" %(w0, alpha_ph, T_EM))
    #ax.plot(timelist, 1-DATA_nrwa.expect[0], label='nrwa', color='y')
    ax.plot(timelist, 1-DATA_ns.expect[0].real, label='Non-secular', color='g')
    #ax.plot(timelist, 1-DATA_s.expect[0].real, label='Vib. Lindblad', color='b')
    #ax.plot(timelist, 1-DATA_naive.expect[0].real, label='Simple Lindblad', color='r')
    ax.set_ylabel("Excited state population")
    ax.set_xlabel("Time (cm)")
    ax.legend()
    #p_file_name = "Notes/Images/Dynamics/Pop_a{:d}_Tph{:d}_Tem{:d}_w0{:d}.pdf".format(int(alpha_ph), int(T_ph), int(T_EM), int(w0))
    #pl.savefig(p_file_name)
    #plt.close()

def plot_coherences(ax):
    #plt.title(r"$\alpha_{ph}=$""%i"r"$cm^{-1}$, $T_{EM}=$""%i K" %(alpha_ph, T_EM))
    #ax.plot(timelist, DATA_s.expect[1].real, label='Vib. Lindblad', color='b')
    ax.plot(timelist, DATA_ns.expect[1].real, label='Non-secular', color='g',alpha=0.7)
    #ax.plot(timelist, DATA_naive.expect[1].real, label='Simple Lindblad', color='r',alpha=0.4)
    ax.legend()
    ax.set_ylabel("Coherence")
    ax.set_xlabel("Time (cm)")
    ax.set_xlim(0,2)
    file_name = "Notes/Images/Dynamics/Coh_a{:d}_Tph{:d}_Tem{:d}_w0{:d}.pdf".format(int(alpha_ph), int(T_ph), int(T_EM), int(w0))
    #plt.savefig(file_name)
    #print "File saved: ", file_name
    #plt.close()

def plot_dynamics_spec(DAT_ns, DAT_s, DAT_n,  t):
    DAT_list, lab_list = [DAT_ns, DAT_s, DAT_n,], [r'$|S_ns|$', r'$|S_s|$', r'$|S_n|$']
    plt.figure()
    for DAT, lab in zip(DAT_list, lab_list):
        dyn = 1-DAT.expect[1]
        ss = dyn[-1]
        gg = dyn-ss
        spec = np.fft.fft(gg)
        freq = np.fft.fftfreq(t.shape[-1])
        plt.plot(freq, abs(spec), label=lab)
    #plt.plot(freq, abs(spec), linestyle='dotted')
    plt.title("Frequency spectrum of vibronic TLS coherence")
    plt.legend()
    plt.ylabel("Magnitude" )
    plt.xlabel(r"Frequency- $\epsilon$ ($cm^{-1}$)")
    p_file_name = "Notes/Images/Spectra/Coh_spec_a{:d}_Tph{:d}_Tem{:d}_w0{:d}.pdf".format(int(alpha_ph), int(T_ph), int(T_EM), int(w0))
    #plt.xlim(-0.2, 0.5)
    plt.savefig(p_file_name)
    d_file_name = "DATA/Spectra/Coh_spec_a{:d}_Tph{:d}_TEM{:d}_w0{:d}.txt".format(int(alpha_ph), int(T_ph), int(T_EM), int(w0))
    np.savetxt(d_file_name, np.array([spec, freq]), delimiter = ',', newline= '\n')
    plt.close()

def plot_manifolds(ax, H):
    eigs = H.eigenenergies()
    p_title = "Vibronic manifolds: " + r"$\alpha_{ph}$="+"{:d}".format(int(alpha_ph))+ "$\epsilon$={:d}, $\omega_0=${:d}".format(int(eps), int(w0))
    #ax.title(p_title)
    plt.ylabel(r"Energy ($cm^{-1}$)")
    j = 0
    for i in eigs:
        col = 'b'
        """
        if j<H.shape[0]/2:
            col = 'b'
        else:
            col = 'r'
        """
        ax.axhline(i, color = col)
        j+=1
    #p_file_name = "Notes/Images/Spectra/Manifolds_a{:d}_Tph{:d}_Tem{:d}_w0{:d}_eps{:d}.pdf".format(int(alpha_ph), int(T_ph), int(T_EM), int(w0), int(eps))
    #plt.savefig(p_file_name)
    #print "Plot saved: ", p_file_name
    #plt.show()


def plot_nonsec(ax, TD, dipoles):
    ax.scatter(TD, dipoles)
    ax.grid()
    #ax.title(r"Non-secularity check: $\epsilon=$""%i"%eps)
    ax.set_xlabel(r"$\varphi_{ij}-\varphi_{kl}$")
    ax.set_ylabel(r"Down rate weighted by dipole of transitions $A_{ij}A_{kl}$")


if __name__ == "__main__":
    """
    Define all system and environment  parameters
    """
    N = 8
    G = ket([0])
    E = ket([1])
    sigma = G*E.dag() # Definition of a sigma_- operator.

    eps = 2000.*8.066 # TLS splitting

    T_EM = 0. # Optical bath temperature
    #alpha_EM = 0.3 # System-bath strength (optical)
    Gamma_EM = 6.582E-4*8.066 #bare decay of electronic transition in inv. cm
    T_ph = 300. # Phonon bath temperature
    wc = 53. # Ind.-Boson frame phonon cutoff freq
    w0 = 200. # underdamped SD parameter omega_0
    alpha_ph = 100./np.pi # Ind.-Boson frame coupling

    print "eps={:d}, T_EM={:d}, w_0={:d}, alpha_ph={:d}".format(int(eps), int(T_EM), int(w0), int(alpha_ph))
    """
    Now we build the sys-RC Hamiltonian and residual bath Liouvillian as well as generate mapped parameters
    """
    L_RC, H, A_EM, A_nrwa, wRC, kappa, Gamma= RC.RC_function_UD(sigma, eps, T_ph, wc, w0, alpha_ph, N)

    # electromagnetic bath liouvillians

    #L_nrwa = EM.L_nonrwa(H, A_nrwa, eps, Gamma, T_EM) # Ignore this for now as it just doesn't work
    L_ns = EM.L_nonsecular(H, A_EM, eps, Gamma_EM, T_EM, J=EM.J_flat)
    L_s = EM.L_vib_lindblad(H, A_EM, eps, Gamma_EM, T_EM, J=EM.J_flat)
    L_naive = EM.L_EM_lindblad(eps, A_EM, Gamma_EM, T_EM, J=EM.J_flat)

    # Set up the initial density matrix
    n_RC = EM.Occupation(wRC, T_ph)
    initial_sys = G*G.dag()
    #initial_sys = E*E.dag()
    #initial_sys = 0.5*(G+E)*(E.dag()+G.dag())
    rho_0 = tensor(initial_sys, thermal_dm(N, n_RC))
    print (rho_0*tensor(qeye(2), destroy(N).dag()*destroy(N))).tr()

    # Expectation values and time increments needed to calculate the dynamics
    expects = [tensor(G*G.dag(), qeye(N)), tensor(E*G.dag(), qeye(N)), tensor(qeye(2), destroy(N).dag()*destroy(N)), tensor(qeye(2), destroy(N).dag()+destroy(N))]
    timelist = np.linspace(0,10,15000)
    #nonsec_check(eps, H, A_em, N) # Plots a scatter graph representation of non-secularity. Could use nrwa instead.

    # Calculate dynamics
    #DATA_nrwa = mesolve(H, rho_0, timelist, [L_RC+L_nrwa], expects, progress_bar=True)
    #DATA_ns = mesolve(H, rho_0, timelist, [L_RC], expects, progress_bar=True)

    #DATA_s = mesolve(H, rho_0, timelist, [L_RC+L_s], expects, progress_bar=True)
    DATA_ns = mesolve(H, rho_0, timelist, [L_RC+L_naive], expects, progress_bar=True)
    fig = plt.figure(figsize=(12, 6))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    plot_dynamics(ax1)
    plot_manifolds(ax2, H)

    p_file_name = "Notes/Images/Dynamics/Pop_a{:d}_N{:d}_Tem{:d}_w0{:d}_eps{:d}.pdf".format(int(alpha_ph), int(N), int(T_EM), int(w0), int(eps))
    plt.savefig(p_file_name)
    print "Figure saved: ", p_file_name

    fig = plt.figure(figsize=(12, 6))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    plot_RC_pop(ax1)
    plot_RC_disp(ax2)
    p_file_name = "Notes/Images/Phonons/Pop_a{:d}_N{:d}_Tem{:d}_w0{:d}_eps{:d}.pdf".format(int(alpha_ph), int(N), int(T_EM), int(w0), int(eps))
    plt.savefig(p_file_name)

    plt.figure()
    x = np.arange(0,400)
    plt.plot(x, RC.J_UD_SB(x, alpha_ph, w0, Gamma))
    plt.show()
    #plot_dynamics_spec(DATA_ns, DATA_s, DATA_naive, timelist)

    #np.savetxt('DATA/Dynamics/DATA_ns.txt', np.array([1- DATA_ns.expect[0], timelist]), delimiter = ',', newline= '\n')
