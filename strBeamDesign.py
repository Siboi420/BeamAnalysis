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
# Beam Reinforcement Limit
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

n_min = np.ceil(A_smin * 4 / (np.pi * dl**2))

rho_bal = (0.85*beta_1*f_c/f_yl)*(600/(600+f_yl)) 
rho_max = 0.75*rho_bal
A_smax = rho_max * b * d
rho_min = A_smin/(b * d)

##################################################### 
# Beam Section Parameter
#####################################################
epsilon_s = 0.005

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

# # Calculating Required A_s

# st.latex(r''' A_{s,req} = \frac{0.85 f_c' b}{f_y} \cdot \left( d - \sqrt{d^2 - \frac{2M_u/\phi}{0.85 f_c' b}} \right) ''')
# st.latex(r" A_{s,req} =  \frac{0.85 \cdot "+ str(round(f_c,None)) +r" \cdot "+ str(b) +r"}{"+ str(round(f_yl,None)) +r"} \cdot \left( "+ str(d) +r" - \sqrt{"+ str(d) +r"^2 - \frac{2 \cdot "+ str(round(M_ue,None)) +r" \cdot 10^6 / 0.9}{0.85 \cdot "+ str(round(f_c,None)) +r" \cdot "+ str(b) +r"}} \right) = "+ str(round(A_s,3)) +r" \; \text{mm}^2 ")

# if A_s < A_smin:
#     st.latex("\\text{Since }" r"A_{s,req} < A_{s,min} \; \therefore \; A_s = A_{s,min}")
# elif A_s > A_smin:
#     st.latex("\\text{Since }" r"A_{s,req} > A_{s,min} \; \therefore \; A_s = A_{s,req}")

# # Amount of Bars required

# st.write('The amount of bar used')
# st.latex(r'n = \frac{A_s \cdot 4}{\pi \cdot d_l^2} \approx \;' rf'{n:.0f}' '\; \\text{bars}')
# st.latex(r" A_{s,use} = n \cdot \frac{1}{4} \cdot \pi \cdot d_l^2 = "+ str(round(n)) +r" \cdot \frac{1}{4} \cdot "+ str(round(dl)) +r" = "+ str(round(A_suse,3)) +r" \; \text{mm}^2 ")

# # Assume amount of compression bar

# st.write(r'Assume for compression steel is equal to')
# st.latex(r"A_s' \geq 0.5A_s = \; " rf"{A_s_prime:0.3f}" "\; \\text{mm}^2")
# st.latex(r"\text{number of compression bar, } n' = "+ str(round(n_prime)) +r" ")


##################################################### 
# Design
#####################################################
# Section Design

st.subheader('Nominal Flexural Strength')

st.write('Distance to steel tension reinforcement')
st.latex(r"d = "+ str(round(d,3)) +r" \; \text{mm}")

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
# Calculate Cc
Cc = Cconcrete(f_c, b, a)
st.write("Calculate concrete compression")
st.latex(r"C_c = 0.85 \cdot f_c \cdot b \cdot \beta_1 \cdot c = \; 0.85 \cdot "+ str(round(f_c)) +r" \cdot "+ str(b) +r" \cdot "+ str(round(beta_1,2)) +r" \cdot "+ str(c) +r" = \; "+ str(round(Cc,3)) +r" \; \text{N} ")

# Calculate steel compression strain
epsilon_s_prime = epsilonPrime(c, d_prime)
st.write("Calculate compression steel strain")
st.latex(r" \epsilon_s' = \frac{c-d'}{c} \cdot 0.003 = \frac{"+ str(c) +r" - "+ str(round(d_prime,2))+r"}{"+ str(round(c)) +r"} \cdot 0.003 = "+ str(round(epsilon_s_prime,5)) +r" ")

# Calculate compression steel yield strength
f_s_prime = fPrime(f_yl, epsilon_s_prime)
st.write("Calculate compression steel yield strength")
st.latex(r"f_s' = \epsilon_s' \cdot 200000 = \; "+ str(round(epsilon_s_prime,5)) +r" \cdot 200000 = "+ str(round(f_s_prime,3)) +r" \; \text{MPa} " )

# Calculate Cs
Cs = M_ue*1e6/0.9/(d-d_prime)
st.write("Calculate compression steel")
st.write("Cs =",Cs)

# Calculate Ts
A_s = Cc / f_yl
st.write("As =",A_s, "mm2")

M_n = Cc * (d-a/2)
fM_n = M_n*phi
st.write("fMn =", fM_n/1e6)

if fM_n > M_ue*1e6:
    st.write("The section is safe")
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
    A_s_p = Cs / (f_s_prime-0.85*f_c)
    st.write("Asp =", A_s_p)
    Ts = Cc + Cs
    st.write(Ts)
    A_s = Ts/f_yl
    st.write(A_s)



# if st.sidebar.button("Calculate"):
#     if f_c <= 0 or f_yl <= 0 or f_yt <= 0 or f_yt <= 0 or b <= 0 or h <= 0 or p <= 0 or dl <= 0 or dt <= 0:
#         st.error("The input value must no be zero!")
#     else:  

# # Section Drawing

# st.write("Section Preview")

# # Calculate rebar positions and handle layering
# xx_dis = (b - 2 * p - dt * 2 - dl) / (n - 1) if n > 1 else 0  # Distance between tension bars
# layering_required = xx_dis < MINIMUM_SPACING if n > 1 else False

# tension_bars_layer1 = []
# tension_bars_layer2 = []
# yy_tension1 = []
# yy_tension2 = []

# # Compression Bars
# compression_bars = np.linspace((p+dt+dl/2), (b-(p+dt+dl/2)), int(n_prime)).tolist()
# yy_compression = np.repeat((h-d_prime), int(n_prime))

# first_bar_position = p + dt + dl/2
# last_bar_position = b - (p + dt + dl/2)
# first_layer_spacing = (last_bar_position - first_bar_position)/(np.ceil(n/2)-1) if np.ceil(n/2)>1 else 0 #Spacing of the top bar is dependent on the amount of tension needed.

# if layering_required:
#     num_bars_layer1 = int(np.ceil(n / 2)-1) #Number of Bars in Top layer
#     num_bars_layer2 = int(n - num_bars_layer1)  # Correctly calculates the remaining bars
    
#     #Layer 1 linspace has same starting position as compression bar
#     xx1 = np.linspace(first_bar_position, last_bar_position, num_bars_layer1) #layer 1 uses a single linspace call

#     #Bottom layer uses a linear space, but has correct # of bars and positions within its space.
#     xx2 = np.linspace(first_bar_position,(b - (p + dt + dl / 2)),num_bars_layer2) if num_bars_layer2 >0 else [] #Bottom Layer's left most side will have same first bar position as compression
#     xx2_dis=(b - ((2*p) + (dt*2) + (dl*num_bars_layer2)))/(num_bars_layer2-1)

#     #Convert values to List
#     tension_bars_layer1 = xx1.tolist()
#     tension_bars_layer2 = xx2.tolist()

#     #create repeating List
#     yy_tension1= np.repeat((h-d + dl + 25), len(tension_bars_layer1)) if len(tension_bars_layer1) > 0 else []
#     yy_tension2 = np.repeat((h-d), len(tension_bars_layer2)) if len(tension_bars_layer2) > 0 else [] #20 mm assumed here

# else: #NO Layering
#     xx = np.linspace((p+dt+dl/2), (b-(p+dt+dl/2)), int(n))
#     tension_bars_layer1 = xx.tolist()
#     yy_tension1 = np.repeat((h-d), int(n)) #yy_tension can just equal to n since it does not affect the length of another tensor

# fig, ax = plt.subplots(figsize=(3,3))
# ax.set_xticks([])
# ax.set_yticks([])
# ax.plot(
#     [0, b, b, 0, 0],
#     [0, 0, h ,h, 0])

# # Plot compression bars with positions that don't change
# ax.scatter(compression_bars, yy_compression, label=r"Compression bar") # Plot Compression

# # Plot tension bars based on layering strategy
# if layering_required:
#     ax.scatter(tension_bars_layer1, yy_tension1, label=r"Tension bar Layer 2") #Plot layer 1. tension bars (list).
#     ax.scatter(tension_bars_layer2, yy_tension2, label=r"Tension bar Layer 1")
# else:
#     ax.scatter(tension_bars_layer1, yy_tension1, label=r"Tension bar") #Plot tension bars layer 1
# ax.set_xlim(-100, b+50)
# ax.set_ylim(-100, h+50)
# ax.legend(loc='lower left', fontsize=5, markerscale=0.5)
# st.pyplot(fig, use_container_width=False)

# if layering_required:
#     st.latex(r"\text{The distance between tension bar is } = "+ str(round(xx2_dis,3)) +r" \text{mm}")
# else:
#     st.latex(r"\text{The distance between tension bar is } = "+ str(round(xx_dis,3)) +r" \text{mm}")

# xxp_dis = (b-2*p - dt*2 - dl) / (n_prime-1)
# st.latex(r"\text{The distance between compression bar is } = "+ str(round(xxp_dis,3)) +r" \text{mm}")
# st.latex(r"\text{Number of tension reinforcement = } "+ str(round(n)) +r" ")
# st.latex(r"\text{Number of compression reinforcement = } "+ str(round(n_prime)) +r" ")