import streamlit as st
import time
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="SimVerse: Water Pollution Control Simulator",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stSlider > div > div > div > div {
        color: #1f77b4;
    }
    .metric-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4db6ac;
    }
    .metric-label {
        font-size: 1rem;
        color: #8b949e;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'day' not in st.session_state:
    st.session_state.day = 1
    st.session_state.pollution_level = 10.0  # Initial baseline pollution
    st.session_state.dissolved_oxygen = 8.0 # mg/L (Good health)
    st.session_state.aquatic_health = 100.0 # Percentage
    st.session_state.history = {
        'Day': [1],
        'Pollution': [10.0],
        'Oxygen': [8.0],
        'Health': [100.0]
    }
    st.session_state.policies = {
        'Treatment Plant': False,
        'Regulation': False,
        'Cleanup Drive': False
    }
    st.session_state.started = False  # Track if user has seen instructions

# --- SIMULATION ENGINE ---
def run_simulation_step(factory_input, farm_input):
    # INCREASED SENSITIVITY: Base pollution generated per day
    daily_pollution = (factory_input * 1.5) + (farm_input * 1.0) 
    
    # Natural decay/purification (constant but lower relative to input)
    natural_recovery = 2.0 
    
    # Policy Effects
    if st.session_state.policies['Treatment Plant']:
        daily_pollution *= 0.3 # 70% reduction
    if st.session_state.policies['Regulation']:
        daily_pollution *= 0.6 # 40% reduction
        
    decay_booster = 1.0
    if st.session_state.policies['Cleanup Drive']:
        decay_booster = 2.5 # Significant recovery boost
        
    # Update Pollution State
    net_pollution = daily_pollution - (natural_recovery * decay_booster)
    st.session_state.pollution_level = max(0, st.session_state.pollution_level + net_pollution)
    
    # Update Oxygen level (More sensitive)
    # Target DO = 8.0 minus 15% of pollution level, floor at 0.5
    target_do = max(0.5, 8.0 - (st.session_state.pollution_level * 0.15))
    st.session_state.dissolved_oxygen += (target_do - st.session_state.dissolved_oxygen) * 0.4
    
    # Update Aquatic Health (More dynamic)
    # Direct impact from pollution + sensitive oxygen threshold
    health_impact = 0
    
    # DO impact
    if st.session_state.dissolved_oxygen < 6.0:
        health_impact -= (6.0 - st.session_state.dissolved_oxygen) * 2.5
        
    # Pollution direct impact (Toxicity)
    if st.session_state.pollution_level > 20:
        health_impact -= (st.session_state.pollution_level - 20) * 0.5
        
    # Recovery if conditions are clean
    if st.session_state.dissolved_oxygen > 6.0 and st.session_state.pollution_level < 20:
        base_recovery = 3.0
        # Policy boost for recovery
        if st.session_state.policies['Cleanup Drive']:
            base_recovery += 5.0
        health_impact += base_recovery
        
    st.session_state.aquatic_health = np.clip(st.session_state.aquatic_health + health_impact, 0, 100)
    
    # Update History
    st.session_state.day += 1
    st.session_state.history['Day'].append(st.session_state.day)
    st.session_state.history['Pollution'].append(st.session_state.pollution_level)
    st.session_state.history['Oxygen'].append(st.session_state.dissolved_oxygen)
    st.session_state.history['Health'].append(st.session_state.aquatic_health)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🕹️ Simulation Controls")
    st.image("https://img.icons8.com/isometric/100/factory.png", width=50)
    factory_val = st.slider("Industrial Discharge (Factories)", 0, 10, 5, help="High discharge increases pollution rapidly.")
    
    st.image("https://img.icons8.com/isometric/100/farm.png", width=50)
    farm_val = st.slider("Agricultural Runoff (Farms)", 0, 10, 3, help="Fertilizer runoff causes nutrient pollution.")
    
    st.markdown("---")
    st.subheader("🛡️ Policy Interventions")
    st.session_state.policies['Treatment Plant'] = st.checkbox("Build Treatment Plant", value=st.session_state.policies['Treatment Plant'])
    st.session_state.policies['Regulation'] = st.checkbox("Enforce Strict Regulation", value=st.session_state.policies['Regulation'])
    st.session_state.policies['Cleanup Drive'] = st.checkbox("Launch Cleanup Drive", value=st.session_state.policies['Cleanup Drive'])
    
    st.markdown("---")
    
    # Check if game is over
    game_over = st.session_state.day >= 30
    
    if not game_over:
        if st.button("▶️ Next Day", type="primary"):
            run_simulation_step(factory_val, farm_val)
            st.rerun()
    else:
        st.success("✅ Simulation Campaign Complete!")
        
    if st.button("🔄 Reset Simulation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- MAIN DASHBOARD / WELCOME ---
if not st.session_state.started:
    st.title("🌟 Welcome to SimVerse")
    st.markdown("""
    ### 🌊 Water Pollution Control Simulator: Instructions
    
    In this simulation, you are the **Environmental Commissioner** of the River Everglade Basin. Your goal is to keep the ecosystem healthy for 30 days.
    
    #### 🕹️ How to Operate:
    1.  **Manage Sources**: Use the sliders in the sidebar to control **Factory Discharge** and **Farm Runoff**. Lower is better for the river!
    2.  **Implement Policies**: Activate infrastructure projects like **Treatment Plants** or **Regulations** to reduce the net impact of pollution.
    3.  **Advance Time**: Click **'Next Day'** to see the results of your actions.
    4.  **Monitor Metrics**:
        *   **Pollution Index**: Keep it low (below 20).
        *   **Dissolved Oxygen**: Must stay above 4.0 mg/L for fish to survive!
        *   **Aquatic Health**: This represents the overall thriving of life. If it drops to 0, the ecosystem collapses.
    5.  **Recovery**: If the water gets polluted, you can restore health by closing sources and launching **Cleanup Drives**.
    
    *Are you ready to protect the river?*
    """)
    if st.button("🚀 Start Simulation", type="primary"):
        st.session_state.started = True
        st.rerun()
    st.stop() # Prevent dashboard from showing until started

st.title("🌊 SimVerse: Water Pollution Control Simulator")
st.markdown(f"**Current Day: {st.session_state.day} / 30** | Location: River Everglade Basin")

if st.session_state.day >= 30:
    st.markdown("---")
    st.header("📋 Final Sustainability Report")
    
    avg_health = np.mean(st.session_state.history['Health'])
    final_pollution = st.session_state.pollution_level
    
    # Calculate Grade
    if avg_health > 90 and final_pollution < 5:
        grade = "A+"
        desc = "Environmental Champion! You've successfully restored the ecosystem."
        color = "#4db6ac"
    elif avg_health > 70:
        grade = "B"
        desc = "Sustainable Manager. The river is healthy, but there's room for improvement."
        color = "#ffcc00"
    elif avg_health > 40:
        grade = "C"
        desc = "Warning: Critical Stress. The ecosystem is struggling to survive."
        color = "#ff9800"
    else:
        grade = "F"
        desc = "Ecological Collapse. Immediate intervention was failed."
        color = "#ff5252"
        
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown(f'''<div style="background: {color}; color: white; border-radius: 50%; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; font-size: 3rem; font-weight: bold; margin: auto;">{grade}</div>''', unsafe_allow_html=True)
    with c2:
        st.subheader(f"Status: {desc}")
        st.write(f"**Average Aquatic Health:** {avg_health:.1f}%")
        st.write(f"**Final Pollution index:** {final_pollution:.1f}")
        
    st.balloons()
    st.markdown("---")

# Top row metrics
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'''<div class="metric-card"><div class="metric-label">Pollution Index</div><div class="metric-value" style="color: {'#ff5252' if st.session_state.pollution_level > 50 else '#ffcc00' if st.session_state.pollution_level > 20 else '#4db6ac'}">{st.session_state.pollution_level:.1f}</div></div>''', unsafe_allow_html=True)
with m2:
    st.markdown(f'''<div class="metric-card"><div class="metric-label">Dissolved Oxygen (DO)</div><div class="metric-value" style="color: {'#4db6ac' if st.session_state.dissolved_oxygen > 6 else '#ffcc00' if st.session_state.dissolved_oxygen > 4 else '#ff5252'}">{st.session_state.dissolved_oxygen:.2f} mg/L</div></div>''', unsafe_allow_html=True)
with m3:
    st.markdown(f'''<div class="metric-card"><div class="metric-label">Aquatic Health</div><div class="metric-value" style="color: {'#4db6ac' if st.session_state.aquatic_health > 80 else '#ffcc00' if st.session_state.aquatic_health > 50 else '#ff5252'}">{st.session_state.aquatic_health:.1f}%</div></div>''', unsafe_allow_html=True)

st.markdown("---")

# Visual Simulation
st.subheader("🖼️ Interactive Ecosystem View")

# Calculate visual factors
# Water color: Blue (200) to Murky Brown (40)
hue = max(40, 200 - (st.session_state.pollution_level * 1.6))
saturation = min(80, 40 + (st.session_state.pollution_level * 0.4))
lightness = max(20, 40 - (st.session_state.pollution_level * 0.2))

# Scum opacity based on pollution
scum_opacity = min(0.8, st.session_state.pollution_level / 100.0)

# Fish count based on health
# We want 0-8 fish depending on health index
fish_count = int((st.session_state.aquatic_health / 100.0) * 8)

river_html = f"""
<div style="width: 100%; height: 400px; background: #1a1c24; border-radius: 20px; position: relative; overflow: hidden; border: 2px solid #30363d; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <!-- SVG Ecosystem -->
    <svg width="100%" height="100%" viewBox="0 0 800 400" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
        <!-- Sky Gradient -->
        <defs>
            <linearGradient id="skyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#1e3c72;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#2a5298;stop-opacity:1" />
            </linearGradient>
            
            <linearGradient id="waterGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:hsl({hue}, {saturation}%, {lightness + 20}%);stop-opacity:1" />
                <stop offset="100%" style="stop-color:hsl({hue}, {saturation}%, {lightness}%);stop-opacity:1" />
            </linearGradient>
            
            <filter id="glow">
                <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>

        <!-- Background Sky -->
        <rect width="800" height="400" fill="url(#skyGradient)" />
        
        <!-- Sun/Moon -->
        <circle cx="700" cy="80" r="30" fill="#ffd700" filter="url(#glow)">
            <animate attributeName="opacity" values="0.8;1;0.8" dur="4s" repeatCount="indefinite" />
        </circle>

        <!-- Far Mountains -->
        <path d="M0 250 L150 150 L300 250 L450 100 L600 250 L800 180 L800 400 L0 400 Z" fill="#16213e" opacity="0.5" />
        
        <!-- River Body -->
        <path id="river" d="M0 280 Q 200 250 400 280 T 800 280 L 800 400 L 0 400 Z" fill="url(#waterGradient)">
             <animate attributeName="d" 
                values="M0 280 Q 200 250 400 280 T 800 280 L 800 400 L 0 400 Z;
                        M0 280 Q 200 310 400 280 T 800 280 L 800 400 L 0 400 Z;
                        M0 280 Q 200 250 400 280 T 800 280 L 800 400 L 0 400 Z" 
                dur="5s" repeatCount="indefinite" />
        </path>
        
        <!-- Scum Layer (Pollution) -->
        <path d="M0 280 Q 200 250 400 280 T 800 280 L 800 400 L 0 400 Z" fill="#5d4037" opacity="{scum_opacity}">
             <animate attributeName="d" 
                values="M0 280 Q 200 250 400 280 T 800 280 L 800 400 L 0 400 Z;
                        M0 280 Q 200 310 400 280 T 800 280 L 800 400 L 0 400 Z;
                        M0 280 Q 200 250 400 280 T 800 280 L 800 400 L 0 400 Z" 
                dur="5.2s" repeatCount="indefinite" />
        </path>

        <!-- Fish Group -->
        <g id="fish-group">
            {"".join([f'''
            <g transform="translate({100 + i*80}, {320 + (i*17)%40})">
                <text font-size="20" opacity="{"1" if i < fish_count else "0"}" style="transition: opacity 2s ease;">
                    {"🐟" if i%2==0 else "🐠"}
                    <animateTransform attributeName="transform" type="translate" values="0,0; 20,0; 0,0" dur="{3+i%3}s" repeatCount="indefinite" />
                </text>
            </g>
            ''' for i in range(8)])}
        </g>
        
        <!-- Bubbles for Oxygen (Inverse to pollution) -->
        <g id="oxygen-bubbles">
            {"".join([f'''
            <circle cx="{50 + i*70}" cy="380" r="2" fill="white" opacity="{max(0, (st.session_state.dissolved_oxygen - 2)/10)}">
                <animate attributeName="cy" from="380" to="280" dur="{2+i%2}s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.5;0" dur="{2+i%2}s" repeatCount="indefinite" />
            </circle>
            ''' for i in range(10)])}
        </g>
    </svg>
    
    <!-- UI Overlay for current status -->
    <div style="position: absolute; top: 15px; left: 15px; background: rgba(0,0,0,0.4); padding: 5px 15px; border-radius: 20px; font-family: sans-serif; font-size: 14px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(5px);">
        📍 River Health: <span style="color: {'#4db6ac' if st.session_state.aquatic_health > 80 else '#ffcc00' if st.session_state.aquatic_health > 50 else '#ff5252'}">{st.session_state.aquatic_health:.1f}%</span>
    </div>
</div>
"""
components.html(river_html, height=420)

# Charts
st.markdown("---")
st.subheader("📊 Historical Trends")
history_df = pd.DataFrame(st.session_state.history)

c1, c2 = st.columns(2)
with c1:
    st.write("**Pollution vs Oxygen**")
    st.line_chart(history_df.set_index('Day')[['Pollution', 'Oxygen']])
with c2:
    st.write("**Aquatic Health Index (%)**")
    st.line_chart(history_df.set_index('Day')[['Health']])

# Instructions / Context
with st.expander("ℹ️ About This Simulator"):
    st.write("""
    **SimVerse: Water Pollution Control Simulator** is an educational tool designed to show the impact of industrial and agricultural activities on local water bodies.
    - **Industrial Discharge**: High levels lead to rapid chemical pollution.
    - **Agricultural Runoff**: Causes nutrient overload, reducing Dissolved Oxygen.
    - **Oxygen (DO)**: If it drops below 4.0 mg/L, the ecosystem enters 'Hypoxia', killing fish.
    - **Policies**: Investing in infrastructure and regulation is key to long-term sustainability.
    """)
