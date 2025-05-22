import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
from sympy.abc import r, theta
from fpdf import FPDF
import matplotlib.pyplot as plt
import os

# Configurar la página
st.set_page_config(page_title="Calculadora de Integrales Polares", page_icon="📊", layout="wide")

# CSS Responsivo y Footer
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #f9f9f9;
    color: #555;
    text-align: center;
    padding: 10px;
    font-size: 0.8em;
    border-top: 1px solid #ddd;
    z-index: 9999;
}
@media only screen and (max-width: 768px) {
    .stTextInput > div > input {
        font-size: 16px;
    }
    .block-container {
        padding: 1rem 0.5rem;
    }
}
</style>
""", unsafe_allow_html=True)



# Encabezado
st.title(" Calculadora de Integrales Dobles en Coordenadas Polares")
st.markdown("Visualiza y calcula integrales dobles usando cambio de variables a coordenadas polares.")

# Sidebar con ayuda
with st.sidebar:
    st.header("ℹ️ Ayuda")
    st.markdown("""
    1. Ingresa el integrando (ej: `x**2 + y**2`).
    2. Define los límites de `x` y `y`.
    3. Haz clic en **Calcular**.
    """)
    st.divider()
    st.subheader("📚 Ejemplos Rápidos")
    if st.button("Círculo de radio 2 (x² + y²)"):
        st.session_state.integrando = "x**2 + y**2"
        st.session_state.x_lim_inf = "-sqrt(4 - y**2)"
        st.session_state.x_lim_sup = "sqrt(4 - y**2)"
        st.session_state.y_lim_inf = "-2"
        st.session_state.y_lim_sup = "2"

# Inputs
col1, col2 = st.columns(2)
with col1:
    integrando = st.text_input("Integrando (usa `x` e `y`):", key="integrando", value=st.session_state.get("integrando", "x**2 + y**2"))
with col2:
    x_lim_inf = st.text_input("Límite inferior de `x`:", key="x_lim_inf", value=st.session_state.get("x_lim_inf", "0"))
    x_lim_sup = st.text_input("Límite superior de `x`:", key="x_lim_sup", value=st.session_state.get("x_lim_sup", "4"))
    y_lim_inf = st.text_input("Límite inferior de `y`:", key="y_lim_inf", value=st.session_state.get("y_lim_inf", "0"))
    y_lim_sup = st.text_input("Límite superior de `y`:", key="y_lim_sup", value=st.session_state.get("y_lim_sup", "4"))

if st.button("Calcular", type="primary"):
    try:
        x, y = sp.symbols('x y')
        f_expr = sp.sympify(integrando)
        x_inf = sp.sympify(x_lim_inf)
        x_sup = sp.sympify(x_lim_sup)
        y_inf = sp.sympify(y_lim_inf)
        y_sup = sp.sympify(y_lim_sup)

        # Validación de límites
        if x_inf == x_sup or y_inf == y_sup:
            st.error("❌ Los límites de integración no pueden ser iguales.")
            st.stop()

        # Cambio a coordenadas polares
        f_polar = f_expr.subs({x: r*sp.cos(theta), y: r*sp.sin(theta)})
        integrando_polar = f_polar * r

        # Mostrar pasos
        st.subheader("🔍 Paso a Paso")
        st.latex(rf"\text{{1. Integrando original: }} \iint {sp.latex(f_expr)} \,dx\,dy")
        st.latex(r"x = r\cos\theta,\quad y = r\sin\theta")
        st.latex(rf"\text{{2. En polares: }} {sp.latex(f_polar)} \cdot r = {sp.latex(integrando_polar)}")
        st.latex(r"3. Límites: r \in [0,2],\quad \theta \in [0,2\pi]")

        # Intentar resolver integral simbólicamente, si no posible usar evalf
        try:
            resultado = sp.integrate(integrando_polar, (theta, 0, 2*sp.pi), (r, 0, 2))
            if resultado.has(sp.Integral):
                raise ValueError("Integral no resuelta simbólicamente.")
        except:
            resultado = sp.integrate(integrando_polar.evalf(), (theta, 0, 2*sp.pi), (r, 0, 2)).evalf()

        st.success("✅ Resultado final:")
        st.latex(rf"\text{{Forma exacta o aproximada: }} {sp.latex(resultado)}")
        try:
            numeric = float(resultado.evalf())
            st.write(f"**Valor numérico:** {numeric:.4f}")
        except:
            st.write("**Expresión exacta:**", resultado)

        # Gráfico 3D
        st.subheader("📊 Gráfico 3D del Integrando")
        Y_vals = np.linspace(float(y_inf), float(y_sup), 50)
        X_vals = np.linspace(float(x_inf.evalf(subs={y: Y_vals[0]})), float(x_sup.evalf(subs={y: Y_vals[0]})), 50)
        X, Y = np.meshgrid(X_vals, Y_vals)
        Z = np.zeros_like(X)
        f_num = sp.lambdify((x, y), f_expr, "numpy")
        try:
            Z = f_num(X, Y)
        except:
            st.warning("No se pudo graficar correctamente el integrando.")
        fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='viridis')])
        fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='f(x, y)'))
        st.plotly_chart(fig, use_container_width=True)

       
        

        class PDF(FPDF):
            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 10)
                self.cell(0, 10, "Creado por Freddy Eduardo Riscanevo Mendez | Derechos de autor © 2025", 0, 0, "C")

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "Resultado de la integral doble en coordenadas polares:\n")
        pdf.multi_cell(0, 10, f"Integrando: {integrando}\nLímites: x en [{x_inf}, {x_sup}], y en [{y_inf}, {y_sup}]\n")

        pdf.multi_cell(0, 10, f"Resultado: {resultado}")
       

        pdf_path = "/mnt/data/resultado_integral.pdf"
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Descargar resultado en PDF", f, file_name="resultado_integral.pdf")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# Footer
st.markdown('<div class="footer">Creado por Freddy Eduardo Riscanevo Mendez | Derechos de autor © 2025</div>', unsafe_allow_html=True)
