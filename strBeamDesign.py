import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from Functions import *

# Set the width of the layout
st.html("""
    <style>
        .stMainBlockContainer {
            max-width:58rem;
        }
    </style>
    """
)

st.title("Beam Design")

st.sidebar.header("Material Properties")

f_c = st.sidebar.number_input("$f_c$, MPa", value=(28.0))
f_yl = st.sidebar.number_input("$f_{yl}$, MPa", value=(420.0))
f_yt = st.sidebar.number_input("$f_{yt}$, MPa", value=(280.0))

epsilon_y = f_yl/2e5
epsilon_s = 0.005

st.sidebar.header("Beam Dimension")

b = st.sidebar.number_input("Beam Width, b (mm)", placeholder="Insert beam width", value=(250.0))
h = st.sidebar.number_input("Beam Height, h (mm)", placeholder="Insert beam height", value=(350.0))
p = st.sidebar.number_input("Concrete Cover, p (mm)", placeholder="Insert concrete cover", value=(40.0))
dl = st.sidebar.number_input("Longitudinal Bar Diameter, dl (mm)", value=(16.0))
dt = st.sidebar.number_input("Transversal Bar Diameter, dt (mm)", value=(10.0))

# Applied Moment Acting on the beam #

st.sidebar.header("Design Moment")

M_ue = st.sidebar.number_input("Moment at beam ends (kN-m) =", value=(120.0))

if f_c >= 55:
    beta_1 = 0.65
elif f_c < 55 and f_c > 28 :
    beta_1 = np.round(0.85-(0.05*(f_c-28)/7),2)
elif f_c <= 28:
    beta_1 = 0.85

st.subheader("Calculate " r"$\beta_1$")

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

##################################################### 
# Steel Reinforcement Limit
#####################################################

y = dl + 25
d = h-(p + dt + dl/2)
d_prime = (p+dt+dl/2)

A_smin1 = Asmin1(f_c, f_yl, b, d)
A_smin2 = Asmin2(f_yl, b, d)
A_smin = max(A_smin1, A_smin2)

st.subheader("Calculate " r"$A_{s,min}$")

st.write("According to ACI Code, minimum reinforcement shall be calculated as below: ")

MINIMUM_SPACING = 25

st.latex(r'''
    A_{s,min} = \; \text{Greater of} 
        \begin{cases}

            \frac{0.25 \sqrt{f_c'}}{f_y}b_wd \\
            \frac{1.4}{f_y}b_w d

        \end{cases}
    ''')

st.write("We acquire the minimum area value as: ")
st.latex(r" A_{s.min1} = \frac{0.25 \sqrt{"+ str(f_c) +r"}}{"+ str(f_yl) +r"} \cdot "+ str(b) +r" \cdot "+ str(d) +r" = "+ str(round(A_smin1,3)) +r" \; \text{mm}^2 ")
st.latex(r" A_{s,min2} = \frac{1.4}{"+ str(f_yl) +r"} \cdot "+ str(b) +r" \cdot "+ str(d) +r" = "+ str(round(A_smin2,3)) +r" \; \text{mm}^2")

st.write("Therefore the required minimum area of steel is:")
st.latex(r''' A_{s,min} = ''' rf''' {A_smin:.3f} ''' ''' \; \\text{mm}^2 ''') 

st.subheader("Calculate the Required Reinforcement")

# Maximum steel reinforcement

A_sbal = 0.85 * f_c * beta_1 * (0.003/(0.003+epsilon_y))*d
A_smax = 0.75 * A_sbal

st.write("The maximum amount of reinforcment is taken as 75\% of $A_{s,balance}$. which are calculated as:")
st.latex(r"""
         \begin{align*}
         A_{s,balance} &= \frac{1}{f_y} \left(0.85 \cdot f_c' \cdot \beta_1 \cdot \frac{\epsilon_{cu}}{\epsilon_{cu}+\epsilon_y} \cdot d \right) \\
         &= \frac{1}{"""+ str(round(f_yl,3)) +r"""} \cdot \left(0.85 \cdot """+ str(round(f_c)) +r""" \cdot """+ str(round(beta_1,3)) +r""" \cdot \frac{0.003}{0.003+ """+ str(round(epsilon_y,3)) +r"""} \right) \\
         &= """+ str(round(A_smax,3)) +r""" \; \text{mm}^2
         \end{align*}
         """)

##################################################### 
# Design
#####################################################

# Section Design

st.subheader('Nominal Flexural Strength')

st.write('Distance to steel tension reinforcement')
st.latex(r"d = "+ str(round(d,3)) +r" \; \text{mm}")

st.write('Distance to steel compression reinforcement')
st.latex(r"d' = "+ str(round(d_prime,3)) +r" \; \text{mm}")

st.write('Tension reinforcement strain')
st.latex(r" \epsilon_s = "+ str(round(epsilon_s,5)) +r" \longrightarrow \; \text{tension reinforcement has yielded}")

# Assume the value of c
c = d / (epsilon_s+0.003) * 0.003
st.write("Calculate the nominal moment provided by beam with compression reinforcement, assume:")
st.latex(r'c = \frac{d}{\epsilon_s+\epsilon_c} \cdot 0.003 = \frac{'+ str(round(d,3)) +r'}{'+ str(round(epsilon_s,3)) +r' + 0.003} \cdot 0.003 = ' rf'{c:0.2f}' '\; \\text{mm}')

# Calculate a
a = c*beta_1
st.write('Calculate the concrete stress block')
st.latex(r" a = c \cdot \beta_1 = "+ str(round(c,3)) +r" \cdot "+ str(round(beta_1,3)) +r" = "+ str(round(a,3)) +r" \; \text{mm}")

##################################################### 
# Function Assign
#####################################################

# Calculate Cc
Cc = Cconcrete(f_c, b, a)
st.write("Calculate concrete compression")
st.latex(r"""
         \begin{align*}
         C_c &= 0.85 \cdot f_c \cdot b \cdot a \\
         &= 0.85 \cdot """+ str(round(f_c)) +r""" \cdot """+ str(b) +r""" \cdot """+ str(a) +r""" = \; """+ str(round(Cc,3)) +r""" \; \text{N} \\
         \end{align*}
         """)

# Calculate As from Ts
A_s = Cc / f_yl
st.write("Calculate te required steel area:")
st.latex(r"""
        T_s = f_y \cdot A_s \longrightarrow A_s = \frac{T_s}{f_y} \\
        A_s = \frac{"""+ str(round(Cc,3))+r"""}{"""+ str(round(f_yl)) +r"""} = """+ str(round(A_s,3)) +r""" \; \text{mm}^2
        """)

M_n = Cc * (d-a/2)
fM_n = M_n*0.9
st.write("The corresponding nominal moment is: ")
st.latex(r"""
         \begin{align*}
         M_n &= C_c \cdot \left( d - \frac{a}{2} \right)\\
         &= """+ str(round(Cc,3)) +r""" \cdot \left( """+ str(round(d,3)) +r""" - \frac{"""+ str(round(a,3)) +r"""}{2} \right) = """+ str(round(M_n)) +r""" \; \text{N-mm}
         \end{align*}
         """)
st.write("Since the steel reinforcment is in tension, therefore the reduction factor, $\; \phi$, is equal to 0.9, therefore")

st.latex(r"""
         \begin{align*} 
         \phi M_n &= 0.9 \cdot """+ str(round(M_n,3)) +r""" = """+ str(round(fM_n,3)) +r""" \; \text{Nmm} \\
         &= """+ str(round(fM_n/1e6,3)) +r""" \; \text{kNm}
         \end{align*}
         """)

if fM_n > M_ue*1e6:
    n = np.ceil(A_smin / (dl**2 * np.pi / 4)) # Rely on the concrete strength, Cc, instead of the steel reinf.
    n_prime = np.ceil(max(n/2, A_smin / (dl**2 * np.pi / 4), 2))
    A_s = n * dl**2 * np.pi /4
    A_sp = n_prime * dl**2 * np.pi / 4

    st.write("The design capacity ratio is:")

    st.latex(r"""
    \begin{align*}
    \phi M_n &= """+ str(round(fM_n/1e6,3)) +r""" \; \text{kN-m} \\
    M_u &= """+ str(round(M_ue,3)) +r""" \; \text{kN-m} \\
    DCR &= \frac{M_u}{\phi M_n} = \frac{"""+ str(round(M_ue,3)) +r"""}{"""+ str(round(fM_n/1e6,3)) +r"""} = """+ str(round(M_ue/(fM_n/1e6),3)) +r"""
    \end{align*}
    """)

elif fM_n < M_ue*1e6:
    st.latex(r"""
    \begin{align*}
    \phi M_n &= """+ str(round(fM_n/1e6,3)) +r""" \; \text{kN-m} \\
    M_u &= """+ str(round(M_ue,3)) +r""" \; \text{kN-m}
    \end{align*}
    """)
    st.latex(r"\phi M_n < M_u")
    st.write("Since the nominal moment is insufficient, compression reinforcement is required to increse the amount of tension reinforcement " \
    "enough to achieve sufficient strength required")

    M_ns = M_ue/0.9 - M_n/1e6

    st.latex(r"""
             \begin{align*}
             M_{ns'} &= M_u/0.9 - M_n\\
             &= """+ str(round(M_ue/0.9,3)) +r""" - """+ str(round(M_n/1e6,3)) +r""" \\
             &= """+ str(round(M_ns,3))+r""" \; \text{kN-m}
             \end{align*}
             """)
    
    Cs = M_ns*1e6/(d-d_prime)
    st.latex(r"""
             \begin{align*}
             M_{ns}' &= C_s \cdot (d-d') \longrightarrow C_s = \frac{M_{ns}'}{d-d'} \\
             C_s &= \frac{"""+ str(round(M_ns,3)) +r""" \cdot 10^6}{"""+ str(round(d,3)) +r""" - """+ str(round(d_prime,3)) +r"""} = """+ str(round(Cs,3)) +r""" \; \text{N} \\
             \end{align*}
             """)

    # Calculate steel compression strain
    epsilon_s_prime = epsilonPrime(c, d_prime)
    st.write("Calculate compression steel strain")
    st.latex(r" \epsilon_s' = \frac{c-d'}{c} \cdot 0.003 = \frac{"+ str(c) +r" - "+ str(round(d_prime,2))+r"}{"+ str(round(c)) +r"} \cdot 0.003 = "+ str(round(epsilon_s_prime,5)) +r" ")

    # Calculate compression steel yield strength
    f_s_prime = min(fPrime(f_yl, epsilon_s_prime),f_yl)
    st.write("Calculate compression steel yield strength")
    st.latex(r"f_s' = \epsilon_s' \cdot 200000 = \; "+ str(round(epsilon_s_prime,5)) +r" \cdot 200000 = "+ str(round(f_s_prime,3)) +r" \; \text{MPa} " )

    A_sp = round((Cs / (f_s_prime-0.85*f_c)),3)
    st.latex(r"""
             \begin{align*}
             C_s = (f_s' - 0.85 \cdot f_c) \cdot A_s' \longrightarrow A_s' = \frac{C_s}{f_s'-0.85 \cdot f_c} \\
             A_s'= \frac{"""+ str(round(Cs,3)) +r"""}{"""+ str(round(f_s_prime,3)) +r""" - 0.85 \cdot """+ str(round(f_c,3)) +r"""} = """+ str(A_sp) +r""" \; \text{mm}^2
             \end{align*}
             """)

    Ts = Cc + Cs
    st.latex(r"""
             \begin{align*}
             T_s &= C_c + C_s = """+ str(round(Cc,3)) +r""" + """+ str(round(Cs,3)) +r""" = """+ str(round(Ts,3)) +r""" \; \text{N} \\
             \end{align*}
             """)

    A_s = round((Ts/f_yl),3)
    st.latex(r"""A_s = \frac{T_s}{f_y} = \frac{"""+ str(round(Ts,3)) +r"""}{"""+ str(round(f_yl,3)) +r"""} = """+ str(round(A_s,3)) +r""" \; \text{mm}^2""") 

    st.write("Therefore the amount of tension reinforcement required is ", str(A_s), "$\\text{mm}^2$ and for the compression reinforcement is ", str(A_sp), "$\\text{mm}^2$")

    n = np.ceil(A_s / (dl**2*np.pi/4))
    n_prime = np.ceil(max(((A_sp / (dl**2*np.pi/4))),n/2))

    M_n = Cc * (d-a/2) + Cs * (d-d_prime)
    fM_n = 0.9 * M_n

    st.latex(r"""
    \begin{align*}
    M_n &= C_c \cdot \left( d - \frac{a}{2} \right) + C_s \cdot (d-d') \\
    M_n &= """+str(round(Cc,3))+r""" \cdot \left( """+str(round(d,3))+r""" - \frac{"""+str(round(a,3))+r"""}{2} \right) + """+str(round(Cs,3))+r""" \cdot ("""+str(round(d,3))+r""" - """+str(round(d_prime,3))+r""") = """+str(round(M_n,3))+r""" \; \text{N-mm}\\
    &= """+str(round(M_n/1e6,3))+r""" \; \text{kN-m}\\
    \phi M_n &= 0.9 * """+str(round(M_n/1e6,3))+r""" = """+ str(round(fM_n/1e6,3)) +r"""\; \text{kN-m} \\
    M_u &= """+ str(round(M_ue,3)) +r""" \; \text{kN-m} \\
    DCR &= \frac{M_u}{\phi M_n} =\frac{"""+ str(round(M_ue,3)) +r"""}{"""+ str(round(fM_n/1e6,3)) +r"""} = """+ str(round(M_ue/(fM_n/1e6),3)) +r"""
    \end{align*}
    """)

if A_s >= A_smax:
    st.error("The reinforcement area $A_s = "+ str(round(A_s)) +r" \; \text{mm}^2$, exceed the maximum of $A_{s,max} = "+ str(round(A_smax)) +r" \; \text{mm}^2$. Increase the section dimension!")
else: 
    st.write("The section is safe")
    st.subheader("Reinforcement Limits")
    st.write("Tension bar check")
    st.write("$A_s = "+str(round(A_s,3))+r" \; \text{mm}^2 < A_{s,max} = "+str(round(A_smax,3))+r" \; \text{mm}^2 \rightarrow$ The reinforcement is not overcrowded \
              $A_s = "+str(round(A_s,3))+r" \; \text{mm}^2 > A_{s,min} = "+str(round(A_smin,3))+r" \; \text{mm}^2 \rightarrow$ The reinforcement is sufficient")
    st.write("Compression bar check")
    if A_sp < 0.5*A_s:
        st.write("$A_s' = "+str(round(A_sp,3))+r" \; \text{mm}^2 < 0.5A_s = "+str(round(0.5*A_s,3))+r" \; \text{mm}^2 \rightarrow A_{s,used}' = 0.5A_s = "+str(round(0.5*A_s,3))+r" \; \text{mm}^2$")
    elif A_sp > 0.5*A_s:
        st.write("$A_s' = "+str(round(A_sp,3))+r" > 0.5A_s \rightarrow $ The compression bar is sufficient")

    # Section Drawing

    st.subheader("Section Preview")

    # Calculate rebar positions and handle layering
    xx_dis = (b - 2 * p - dt * 2 - dl) / (n - 1) if n > 1 else 0  # Distance between tension bars
    layering_required = xx_dis < MINIMUM_SPACING if n > 1 else False

    tension_bars_layer1 = []
    tension_bars_layer2 = []
    yy_tension1 = []
    yy_tension2 = []

    # Compression Bars
    compression_bars = np.linspace((p+dt+dl/2), (b-(p+dt+dl/2)), int(n_prime)).tolist()
    yy_compression = np.repeat((h-d_prime), int(n_prime))

    first_bar_position = p + dt + dl/2
    last_bar_position = b - (p + dt + dl/2)
    first_layer_spacing = (last_bar_position - first_bar_position)/(np.ceil(n/2)-1) if np.ceil(n/2)>1 else 0 #Spacing of the top bar is dependent on the amount of tension needed.

    if layering_required:
        num_bars_layer1 = int(np.ceil(n / 2)-1) #Number of Bars in Top layer
        num_bars_layer2 = int(n - num_bars_layer1)  # Correctly calculates the remaining bars
        
        #Layer 1 linspace has same starting position as compression bar
        xx1 = np.linspace(first_bar_position, last_bar_position, num_bars_layer1) #layer 1 uses a single linspace call

        #Bottom layer uses a linear space, but has correct # of bars and positions within its space.
        xx2 = np.linspace(first_bar_position,(b - (p + dt + dl / 2)),num_bars_layer2) if num_bars_layer2 >0 else [] #Bottom Layer's left most side will have same first bar position as compression
        xx2_dis=(b - ((2*p) + (dt*2) + dl))/(num_bars_layer2-1)

        #Convert values to List
        tension_bars_layer1 = xx1.tolist()
        tension_bars_layer2 = xx2.tolist()

        #create repeating List
        yy_tension1= np.repeat((h-d + dl + 25), len(tension_bars_layer1)) if len(tension_bars_layer1) > 0 else []
        yy_tension2 = np.repeat((h-d), len(tension_bars_layer2)) if len(tension_bars_layer2) > 0 else [] #20 mm assumed here

    else: #NO Layering
        xx = np.linspace((p+dt+dl/2), (b-(p+dt+dl/2)), int(n))
        tension_bars_layer1 = xx.tolist()
        yy_tension1 = np.repeat((h-d), int(n)) #yy_tension can just equal to n since it does not affect the length of another tensor

    fig, ax = plt.subplots(figsize=(3,3))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.plot(
        [0, b, b, 0, 0],
        [0, 0, h ,h, 0])

    # Plot compression bars with positions that don't change
    ax.scatter(compression_bars, yy_compression, label=r"Compression bar") # Plot Compression

    # Plot tension bars based on layering strategy
    if layering_required:
        ax.scatter(tension_bars_layer1, yy_tension1, label=r"Tension bar Layer 2") #Plot layer 1. tension bars (list).
        ax.scatter(tension_bars_layer2, yy_tension2, label=r"Tension bar Layer 1")
    else:
        ax.scatter(tension_bars_layer1, yy_tension1, label=r"Tension bar") #Plot tension bars layer 1
    ax.set_xlim(-100, b+50)
    ax.set_ylim(-100, h+50)
    ax.legend(loc='lower left', fontsize=5, markerscale=0.5)
    st.pyplot(fig, use_container_width=False)

    if layering_required:
        st.write("The distance between tension bar is", str(round(xx2_dis,3)), "$\\text{mm}$")
    else:
        st.write(r"The distance between tension bar is", str(round(xx_dis,3)),  "$\\text{mm}$") 

    xxp_dis = (b-2*p - dt*2 - dl) / (n_prime-1)


    st.write("The distance between compression bar is =", str(round(xxp_dis,3)), "$\\text{mm}$")
    st.write("Number of tension reinforcement =", str(round(n)))
    st.write("Number of compression reinforcement =", str(round(n_prime)))