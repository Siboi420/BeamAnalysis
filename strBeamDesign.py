import numpy as np
import pandas as pd
import streamlit as st
from Functions import CheckBeamDesign, CheckBeamDouble, Asmin1, Asmin2


st.sidebar.title("Beam Design")

st.sidebar.header("Material Properties")

f_c = st.sidebar.number_input("f_c =", value=float(28))
f_yl = st.sidebar.number_input("f_yl =", value=float(420))
f_yt = st.sidebar.number_input("f_yt =", value=float(280))
epsilon_y = f_yl/2e5

st.sidebar.header("Beam Dimension")

b = st.sidebar.number_input("Beam Width, b", placeholder="Insert beam width", value=float(250))
h = st.sidebar.number_input("Beam Height, h", placeholder="Insert beam height", value=float(350))
p = st.sidebar.number_input("Concrete Cover, p", placeholder="Insert concrete cover", value=float(40))
dl = st.sidebar.number_input("Longitudinal Bar Diameter, dl", value=float(19))
dt = st.sidebar.number_input("Transversal Bar Diameter, dt", value=float(10))

# Applied Moment Acting on the beam #

st.sidebar.header("Design Moment")

M_ue = st.sidebar.number_input("Moment at beam ends (kN-m) =", value=float(120))

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
    A_smin = A_smin,
    b = b,
    beta_1 = beta_1)
    if utilisation < 0.03:
        print(c)

beamDesign = CheckBeamDesign(
    c = c,
    f_yl = f_yl,
    f_c = f_c,
    A_s = A_suse,
    A_smin = A_smin,
    b = b,
    h = h,
    dl = dl,
    dt = dt,
    cover = p,
    beta_1 = beta_1)
    

##################################################### 
# Strealit Configuration
#####################################################

st.subheader("Calculating " r"$\beta_1$")

if f_c >= 55:
    st.latex(r"""
             f_c' \geq 55 \; \therefore \; \beta_1 = 0.65
             """)
elif f_c < 55 and f_c > 28 :
    st.latex(r"""
             28 < f_c' < 55 \; \therefore \; \beta_1 = 0.85 - \frac{0.05 \cdot (f_c'-28)}{7}\\
             \beta_1 =""" +rf""" {beta_1} """ )
elif f_c <= 28:
    st.latex(r"""
             16 \leq f_c' \leq 28 \; \therefore \; \beta_1 = 0.85\\
             """)
    

st.subheader("Calculating " r"$A_{s,min}$")

st.text("According to ACI Code, minimum reinforcement shall be calculated as below: ")

r'''
$$
A_{s,min} = \; \text{Greater of} 
\begin{cases}

\frac{0.25 \sqrt{f_c'}}{f_y}b_wd \\
\frac{1.4}{f_y}b_w d

\end{cases}
$$
'''

st.text("We acquire the minimum area value as: ")
r'''$$ A_{s.min1} = $$''' rf'''{A_smin1:.03f}''' ''' $$\; \\text{mm}^2 $$'''
r'''$$ A_{s.min2} = $$''' rf'''{A_smin2:.03f}''' ''' $$\; \\text{mm}^2 $$'''

st.text("Therefore the required minimum area of steel is:")
st.latex(r''' A_{s,min} = ''' rf''' {A_smin:.3f} ''' ''' \; \\text{mm}^2 ''') 

st.subheader("Calculate the Required Reinforcement")
st.text('To calculate the required area of reinforcement steel:')

st.latex(r''' A_{s,req} = \frac{0.85 f_c' b}{f_y} \cdot \left( d - \sqrt{d^2 - \frac{2M_u/\phi}{0.85 f_c' b}} \right) =''' rf''' {A_s:0.3f} ''' ''' \; \\text{mm}^2 ''')


if A_s < A_smin:
    st.latex("\\text{Since }" r"A_{s,req} < A_{s,min} \; \therefore \; A_s = A_{s,min}")
elif A_s > A_smin:
    st.latex("\\text{Since }" r"A_{s,req} > A_{s,min} \; \therefore \; A_s = A_{s,req}")

st.text('The amount of bar used')
st.latex(r'n = \frac{A_s \cdot 4}{\pi \cdot d_l^2} \approx \;' rf'{n:.0f}' '\; \\text{bars}')
st.latex(r'A_{s,use} = n \cdot \frac{1}{4} \cdot \pi \cdot d_l^2  =' rf'{A_suse:0.3f}' '\; \\text{mm}^2')
st.text(r'Assume for compression steel is equal to')
st.latex(r"A_s' \geq 0.5A_s")

st.subheader('Section Design Parameter')

st.text('Calculate the concrete stress block')
st.latex(r''' a = \frac{A_s \cdot f_y}{0.85 \cdot f_c \cdot b} = \;''' rf'''{a:.3f}''' ''' \; \\text{mm} ''')


st.text('Calculate the section neutral axis')
st.latex(r'''c = \frac{a}{\beta_1} = \;''' rf'''{c1:0.3f}''' ''' \; \\text{mm} ''')

st.text('Calculate the steel strain')
st.latex(r'\epsilon_s = \frac{d-c}{c} \cdot 0.003 = \;' rf'{epsilon_s:0.5f}')

st.text("Calculate the nominal moment provided by beam with compression reinforcement, assume:")
st.latex(r'c = \;' rf'{c}' '\; \\text{mm}')

st.text("Calculate compression steel strain")
st.latex(r""" \epsilon_s' = \frac{c-d'}{c} \cdot 0.003 =""" rf"""{((c-d_prime)/c*0.003):0.5f} """)

st.text("Calculate compression steel yield strength")
st.latex(r"f_s' = \epsilon_s' \cdot 200000 = \;" rf"{min(f_yl, ((c-d_prime)/c*0.003) * 2e5):0.3f}" "\; \\text{MPa}" )

# st.text("Calculate compression steel")
# st.latex(r"C_s = A_s' \cdot (f_s'-0.85 \cdot f_c) = \;")

st.latex(r"M_n = C_c \cdot (d - a/2) + C_s \cdot (d-d') = \;" rf"{beamDesign/1e6:0.3f}" "\; \\text{kN-m}")

