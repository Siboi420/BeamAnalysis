import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from Functions import *

# Set the width of the layout
st.html("""
    <style>
        .stMainBlockContainer {
            max-width:58rem;
            max-height:10rem;
        }
    </style>
    """
)

st.title("Beam Design")

st.sidebar.header("Material Properties")

f_c = st.sidebar.number_input("$f_c$, MPa", value=float(28))
f_yl = st.sidebar.number_input("$f_{yl}$, MPa", value=float(420))
f_yt = st.sidebar.number_input("$f_{yt}$, MPa", value=float(280))
epsilon_y = f_yl/2e5

st.sidebar.header("Beam Dimension")

b = st.sidebar.number_input("Beam Width, b (mm)", placeholder="Insert beam width", value=float(250))
h = st.sidebar.number_input("Beam Height, h (mm)", placeholder="Insert beam height", value=float(350))
p = st.sidebar.number_input("Concrete Cover, p (mm)", placeholder="Insert concrete cover", value=float(40))
dl = st.sidebar.number_input("Longitudinal Bar Diameter, dl (mm)", value=float(19))
dt = st.sidebar.number_input("Transversal Bar Diameter, dt (mm)", value=float(10))

# Applied Moment Acting on the beam #

st.sidebar.header("Design Moment")

M_ue = st.sidebar.number_input("Moment at beam ends (kN-m) =", value=float(120))

if st.sidebar.button("Calculate"):
    if f_c <= 0 or f_yl <= 0 or f_yt <= 0 or f_yt <= 0 or b <= 0 or h <= 0 or p <= 0 or dl <= 0 or dt <= 0:
        st.error("The input value must no be zero!")
    else:   
        if f_c >= 55:
            beta_1 = 0.65
        elif f_c < 55 and f_c > 28 :
            beta_1 = np.round(0.85-(0.05*(f_c-28)/7),2)
        elif f_c <= 28:
            beta_1 = 0.85

        ##################################################### 
        # Beam Reinforcement Limit
        #####################################################

        y = dl + 25
        d = h-(p + dt + dl/2)
        d_prime = (p+dt+dl/2)

        A_smin1 = Asmin1(f_c, f_yl, b, d)
        A_smin2 = Asmin2(f_yl, b, d)
        A_smin = max(A_smin1, A_smin2)

        n_min = np.ceil(A_smin * 4 / (np.pi * dl**2))

        rho_bal = (0.85*beta_1*f_c/f_yl)*(600/(600+f_yl)) 
        rho_max = 0.75*rho_bal
        A_smax = rho_max * b * d
        rho_min = A_smin/(b * d)

        ##################################################### 
        # Beam Section Parameter
        #####################################################

        a = d - np.sqrt(d**2 - ((2*M_ue*1e6)/(0.85*f_c*0.9*b)))
        c1 = a/beta_1
        epsilon_s = ((d-c1) / c1) *0.003

        c_max = 0.003 / (0.003 +(epsilon_y + 0.003)) * d
        a_max = beta_1 * c_max
        A_s = 0.85 * f_c * b / f_yl * (d - np.sqrt(d**2 - (2*M_ue*1e6/0.9)/(0.85*f_c*b)))

        if A_s < A_smin:
            A_s = A_smin
        elif A_s > A_smin:
            A_s = A_s

        if epsilon_s > epsilon_y + 0.003:
            phi = 0.9
        elif epsilon_s < epsilon_y + 0.003 and epsilon_s > epsilon_y:
            phi = 0.65+0.25*(epsilon_s-epsilon_y)/0.003
        elif epsilon_s <= epsilon_y:
            phi = 0.65

        n = np.ceil(A_s * 4 / (np.pi * dl**2))
        A_suse = n * np.pi * dl**2 * 0.25

        n_prime = np.ceil(n/2)
        A_s_prime = n_prime * np.pi * dl**2 * 0.25

        ##################################################### 
        # Design
        #####################################################

        c = 1

        utilisation = CheckBeamDouble(
            c = c,
            d_prime = d_prime,
            f_yl = f_yl,
            f_c = f_c,
            A_s = A_suse,
            A_s_prime = A_s_prime,
            A_smin = A_smin,
            b = b,
            beta_1 = beta_1)

        while utilisation > 0.03:
            c += 1
            utilisation = CheckBeamDouble(
            c = c,
            d_prime = d_prime,
            f_yl = f_yl,
            f_c = f_c,
            A_s = A_suse,
            A_s_prime = A_s_prime,
            A_smin = A_smin,
            b = b,
            beta_1 = beta_1)
            if utilisation < 0.03:
                break

        beamDesign = CheckBeamDesign(
            c = c,
            f_yl = f_yl,
            f_c = f_c,
            A_s = A_suse,
            A_s_prime = A_s_prime,
            A_smin = A_smin,
            b = b,
            h = h,
            dl = dl,
            dt = dt,
            cover = p,
            beta_1 = beta_1)

        ##################################################### 
        # Function Assign
        #####################################################

        epsilon_s_prime = epsilonPrime(c, d_prime)

        f_s_prime = fPrime(f_yl, epsilon_s_prime)

        Cs = Csteel(A_s, A_smin, f_s_prime, f_c)

        Cc = Cconcrete(f_c, b, beta_1, c)

        T = Tsteel(A_s, f_yl)

        ##################################################### 
        # Strealit Configuration
        #####################################################

        st.subheader("Calculating " r"$\beta_1$")

        if f_c >= 55:
            st.latex(r"""
                    f_c' \geq 55 \; \therefore \; \beta_1 = 0.65
                    """)
        elif f_c > 28 and f_c < 55:
            st.latex(r" 28 < f_c' < 55 \; \therefore \; \beta_1 = 0.85 - \frac{0.05 \cdot (f_c'-28)}{7} ")
            st.latex(r" \beta_1 = \; 0.85 - \frac{0.05 \cdot (" + str(f_c) + r" - 28)}{7} = "+ str(beta_1) +r" ")
        elif f_c <= 28:
            st.latex(r"""
                    16 \leq f_c' \leq 28 \; \therefore \; \beta_1 = 0.85\\
                    """)
            

        st.subheader("Calculating " r"$A_{s,min}$")

        st.write("According to ACI Code, minimum reinforcement shall be calculated as below: ")

        r'''
        $$
        A_{s,min} = \; \text{Greater of} 
        \begin{cases}

        \frac{0.25 \sqrt{f_c'}}{f_y}b_wd \\
        \frac{1.4}{f_y}b_w d

        \end{cases}
        $$
        '''

        st.write("We acquire the minimum area value as: ")
        st.latex(r" A_{s.min1} = \frac{0.25 \sqrt{"+ str(f_c) +r"}}{"+ str(f_yl) +r"} \cdot "+ str(b) +r" \cdot "+ str(d) +r" = "+ str(round(A_smin1,3)) +r" \; \text{mm}^2 ")
        st.latex(r" A_{s,min2} = \frac{1.4}{"+ str(f_yl) +r"} \cdot "+ str(b) +r" \cdot "+ str(d) +r" = "+ str(round(A_smin2,3)) +r" \; \text{mm}^2")

        st.write("Therefore the required minimum area of steel is:")
        st.latex(r''' A_{s,min} = ''' rf''' {A_smin:.3f} ''' ''' \; \\text{mm}^2 ''') 

        st.subheader("Calculate the Required Reinforcement")
        st.write('To calculate the required area of reinforcement steel:')

        # Calculating Required A_s

        st.latex(r''' A_{s,req} = \frac{0.85 f_c' b}{f_y} \cdot \left( d - \sqrt{d^2 - \frac{2M_u/\phi}{0.85 f_c' b}} \right) ''')
        st.latex(r" A_{s,req} =  \frac{0.85 \cdot "+ str(round(f_c,None)) +r" \cdot "+ str(b) +r"}{"+ str(round(f_yl,None)) +r"} \cdot \left( "+ str(d) +r" - \sqrt{"+ str(d) +r"^2 - \frac{2 \cdot "+ str(round(M_ue,None)) +r" \cdot 10^6 / 0.9}{0.85 \cdot "+ str(round(f_c,None)) +r" \cdot "+ str(b) +r"}} \right) = "+ str(round(A_s,3)) +r" \; \text{mm}^2 ")

        if A_s < A_smin:
            st.latex("\\text{Since }" r"A_{s,req} < A_{s,min} \; \therefore \; A_s = A_{s,min}")
        elif A_s > A_smin:
            st.latex("\\text{Since }" r"A_{s,req} > A_{s,min} \; \therefore \; A_s = A_{s,req}")

        # Amount of Bars required

        st.write('The amount of bar used')
        st.latex(r'n = \frac{A_s \cdot 4}{\pi \cdot d_l^2} \approx \;' rf'{n:.0f}' '\; \\text{bars}')
        st.latex(r" A_{s,use} = n \cdot \frac{1}{4} \cdot \pi \cdot d_l^2 = "+ str(round(n)) +r" \cdot \frac{1}{4} \cdot "+ str(round(dl)) +r" = "+ str(round(A_suse,3)) +r" \; \text{mm}^2 ")

        # Assume amount of compression bar

        st.write(r'Assume for compression steel is equal to')
        st.latex(r"A_s' \geq 0.5A_s = \; " rf"{A_s_prime:0.3f}" "\; \\text{mm}^2")
        st.latex(r"\text{number of compression bar, } n' = "+ str(round(n_prime)) +r" ")

        # Section Design

        st.subheader('Section Design Parameter')

        # Calculate a

        st.write('Calculate the concrete stress block')
        st.latex(r" a = \frac{A_s \cdot f_y}{0.85 \cdot f_c \cdot b} = \left( \frac{"+ str(round(A_s,3)) +r" \cdot "+ str(round(f_yl)) +r"}{0.85 \cdot "+ str(round(f_c)) +r" \cdot "+ str(b) +r"} \right)= "+ str(round(a,3)) +r"\; \text{mm} ")

        # Calculate c

        st.write('Calculate the section neutral axis')
        st.latex(r"c = \frac{a}{\beta_1} = \frac{"+ str(round(a,3)) +r"}{"+ str(beta_1) +r"} = \; "+ str(round(c1,3)) +r" \; \text{mm}")

        # Calculate steel strain

        st.write('Calculate the steel strain')
        st.latex(r"d = "+ str(round(d,3)) +r" \; \text{mm}")
        st.latex(r" \epsilon_s = \frac{d-c}{c} \cdot 0.003 = \frac{"+ str(d) +r" - "+ str(round(c1,3))+r"}{"+ str(round(c1,3)) +r"} \cdot 0.003 = "+ str(round(epsilon_s,5)) +r"")

        # Assume the value of c

        st.write("Calculate the nominal moment provided by beam with compression reinforcement, assume:")
        st.latex(r'c = \;' rf'{c:0.2f}' '\; \\text{mm}')

        # Calculate steel compression strain

        st.write("Calculate compression steel strain")
        st.latex(r" \epsilon_s' = \frac{c-d'}{c} \cdot 0.003 = \frac{"+ str(c) +r" - "+ str(round(d_prime,2))+r"}{"+ str(round(c)) +r"} \cdot 0.003 = "+ str(round(epsilon_s_prime,5)) +r" ")

        # Calculate compression steel yield strength

        st.write("Calculate compression steel yield strength")
        st.latex(r"f_s' = \epsilon_s' \cdot 200000 = \; "+ str(round(epsilon_s_prime,5)) +r" \cdot 200000 = "+ str(round(f_s_prime,3)) +r" \; \text{MPa} " )

        # Calculate Cs

        st.write("Calculate compression steel")
        st.latex(r"C_s = A_s' \cdot f_s' - 0.85 \cdot f_c = \; "+ str(round(A_s_prime,3))+r" \cdot "+ str(round(f_s_prime,3)) +r" - 0.85 \cdot "+ str(round(f_c)) +r" = "+ str(round(Cs,3)) +r" \; \text{N} ")

        # Calculate Cc

        st.write("Calculate concrete compression")
        st.latex(r"C_c = 0.85 \cdot f_c \cdot b \cdot \beta_1 \cdot c = \; 0.85 \cdot "+ str(round(f_c)) +r" \cdot "+ str(b) +r" \cdot "+ str(round(beta_1,2)) +r" \cdot "+ str(c) +r" = \; "+ str(round(Cc,3)) +r" \; \text{N} ")

        # Calculate Ts

        st.write("Calculate steel tension")
        st.latex(r"T = A_s \cdot f_y = \; "+ str(round(A_s,3)) +r" \cdot "+ str(f_yl) +r" = \; "+ str(round(T,3)) +r" \; \text{N} ")

        # Verify Cs + Cc and T

        st.write("Verify the difference of " r"$(C_s + C_c) \; \text{and} \; T \;$" " is less than 3%")
        st.latex(r"""
        \begin{align*}
        \text{difference} &= \left| \frac{(C_s + C_c) - T}{T} \right| \cdot 100\% < 3\% \\ 
        &= \left| \frac{("""+ str(round(Cs)) +r""" + """+ str(round(Cs)) +r""") - """+ str(round(T)) +r"""}{"""+ str(round(T)) +r"""} \right| \cdot 100\% = \; """+ str(round(utilisation*100,2))+r"""\% < 3 \% \therefore \text{OK}
        \end{align*}
        """)

        # Nominal Moment Design

        st.write("Calculate nominal beam strength:")
        st.latex(r""" 
        \begin{align*}
        M_n &= C_c \cdot (d - a/2) + C_s \cdot (d-d') \\
        &= """+ str(round(Cc)) +r""" \cdot ("""+ str(d) +r""" - """+ str(round(a,3)) +r"""/2) + """+ str(round(Cs))+r""" \cdot ("""+ str(d) +r""" - """+ str(d_prime) +r""") = \; """+ str(round(beamDesign/1e6)) +r""" \; \text{kN-m} 
        \end{align*}
        """)

        st.write("For $\epsilon_s =$ " rf"{epsilon_s:0.5f}" ", $\; \phi =" rf"{phi:0.2f}$")
        st.latex("\phi M_n = " rf"{round(phi * beamDesign/1e6)}" "\; \\text{kN-m}")

        st.write("The design capacity ration is:")

        DCR = M_ue / (phi * beamDesign/1e6)

        st.latex(r"DCR = \frac{M_u}{\phi M_n} = \;" rf"{DCR:0.3f}")

        if DCR >= 1:
            st.error("The section is needs to be upgraded")
        elif DCR < 1:
            st.write("The section is safe")

        # Section Drawing

        st.write("Section Preview")

        xx = np.linspace((p+dt+dl/2), (b-(p+dt+dl/2)), int(n))
        yy = np.repeat((h-d), n)

        xx_p = np.linspace((p+dt+dl/2), (b-(p+dt+dl/2)), int(n_prime))
        yy_p = np.repeat((h-d_prime), n_prime)

        fig, ax = plt.subplots(figsize=(3,3))
        ax.set_xticks([])
        ax.set_yticks([])
        ax.plot(
            [0, b, b, 0, 0],
            [0, 0, h ,h, 0])
        ax.scatter(xx_p, yy_p, label=r"Compression bar")
        ax.scatter(xx, yy, label=r"Tension bar")
        ax.set_xlim(-100, b+50)
        ax.set_ylim(-100, h+50)
        ax.legend(loc='lower left', fontsize=5, markerscale=0.5)

        st.pyplot(fig, use_container_width=False)

        xx_dis = (b-2*p - dt*2 - dl) / (n-1)
        xxp_dis = (b-2*p - dt*2 - dl) / (n_prime-1)

        st.latex(r"\text{The distance between tension bar is } = "+ str(round(xx_dis,3)) +r" \text{mm}")
        st.latex(r"\text{The distance between compression bar is } = "+ str(round(xxp_dis,3)) +r" \text{mm}")

        st.latex(r"\text{Number of tension reinforcement = } "+ str(round(n)) +r" ")
        st.latex(r"\text{Number of compression reinforcement = } "+ str(round(n_prime)) +r" ")
