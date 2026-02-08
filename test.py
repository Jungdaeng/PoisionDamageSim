import streamlit as st
import matplotlib.pyplot as plt
import math

# =========================
# Matplotlib config
# =========================
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["axes.formatter.useoffset"] = False
plt.rcParams["axes.formatter.use_mathtext"] = False

# =========================
# UI
# =========================
st.title("모비노기 도적 독 시뮬레이션")
st.markdown("독 종류에 따른 감쇠 모델 적용 v1.3 by 정댕/던컨")
st.markdown("설정한 주기로 독이 지속적으로 들어갔다는 가정을하며, 평타독은 배제하여 오차가 존재합니다.")
st.sidebar.header("Parameters")

A_input = st.sidebar.number_input(
    "4번 스킬 DoT",
    value=18000,
    step=500
)
st.sidebar.caption("모든 독 배제, 4번 스킬 1회 사용 후 유지되는 DoT")

B_input = st.sidebar.number_input(
    "독사 무기 DoT",
    value=19000,
    step=500
)
st.sidebar.caption("모든 독 배제, 독사 무기 1회 타격 후 유지되는 DoT")

C_input = st.sidebar.number_input(
    "독성 DoT",
    value=8000,
    step=500
)
st.sidebar.caption("모든 독 배제, 독성 1회 발동 시 유지되는 DoT")

T_c_input = st.sidebar.number_input(
    "4번 스킬 주기 (초)",
    value=12,
    min_value=1
)

T_toxic = st.sidebar.number_input(
    "독성 시전 주기 (초), 3차징",
    value=15,
    min_value=1
)

t_max = st.sidebar.slider("시뮬레이션 시간 범위 (초)", 10, 300, 120)

use_mist = st.sidebar.checkbox("4번 스킬 활성화", value=True)
mist_is_poison = st.sidebar.checkbox("독무 사용 여부", value=True)
use_snake = st.sidebar.checkbox("독사 무기 활성화", value=True)
use_toxic = st.sidebar.checkbox("독성 활성화", value=True)

# =========================
# Internal parameters
# =========================
T_c = max(T_c_input, 7)

A = A_input * 30
B = B_input * 30
C = C_input * 30

L_m = 30 if mist_is_poison else 60
L_s = 30
L_t = 30

# =========================
# Helper functions
# =========================
def i_m(t):
    r = t % T_c
    return 1 if 1 <= r <= 7 else 0

def i_s(t):
    return 1 if t % 10 == 0 else 0

def i_t(t):
    return 1 if t % T_toxic == 0 else 0

def r_k_m(t):
    if t < 8:
        return 0
    return 7 + T_c * math.floor((t - 7) / T_c)

def r_k_s(t):
    return t - (t % 10)

def r_k_t(t):
    return t - (t % T_toxic)

# =========================
# State initialization
# =========================
P_m = [0.0] * (t_max + 1)
P_s = [0.0] * (t_max + 1)
P_t = [0.0] * (t_max + 1)

if use_snake:
    P_s[0] = B
if use_toxic:
    P_t[0] = C

# =========================
# Simulation
# =========================
for t in range(1, t_max + 1):

    # 4번 스킬
    if use_mist:
        add = (A / 7) * i_m(t)
        ref = max(0, min(t - 1, r_k_m(t)))
        P_m[t] = P_m[t - 1] + add - P_m[ref] / L_m
    else:
        P_m[t] = 0.0

    # 독사
    if use_snake:
        add = B * i_s(t)
        ref = max(0, min(t - 1, r_k_s(t)))
        P_s[t] = P_s[t - 1] + add - P_s[ref] / L_s
    else:
        P_s[t] = 0.0

    # 독성
    if use_toxic:
        add = C * i_t(t)
        ref = max(0, min(t - 1, r_k_t(t)))
        P_t[t] = P_t[t - 1] + add - P_t[ref] / L_t
    else:
        P_t[t] = 0.0

# =========================
# DoT (instant)
# =========================
DoT = [
    (P_m[t] / 30 if use_mist else 0) +
    (P_s[t] / 30 if use_snake else 0) +
    (P_t[t] / 30 if use_toxic else 0)
    for t in range(t_max + 1)
]

# =========================
# Held DoT
# =========================
DoT_held = [0.0] * (t_max + 1)
last = DoT[0]

for t in range(t_max + 1):
    if (use_mist and i_m(t)) or (use_snake and i_s(t)) or (use_toxic and i_t(t)):
        last = DoT[t]
    DoT_held[t] = last

# =========================
# Plot: Accumulated Poison
# =========================
st.subheader("축적된 독의 양")

fig, ax = plt.subplots()
ax.plot(P_m, label="4nd skill")
ax.plot(P_s, label="posion snake")
ax.plot(P_t, label="toxic", color="darkgreen")

ax.set_xlabel("Time (sec)")
ax.set_ylabel("Accumulated Poison")
ax.set_xticks(range(0, t_max + 1, 10))
ax.ticklabel_format(style="plain", axis="y")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()
st.pyplot(fig)

# =========================
# Plot: DoT
# =========================
st.subheader("DoT 데미지")

fig2, ax2 = plt.subplots()
ax2.plot(DoT, label="Instant DoT", color="red")
ax2.plot(DoT_held, label="Held DoT", color="blue", linestyle="--")

ax2.set_xlabel("Time (sec)")
ax2.set_ylabel("Damage per Second")
ax2.set_xticks(range(0, t_max + 1, 10))
ax2.ticklabel_format(style="plain", axis="y")
ax2.grid(True, linestyle="--", alpha=0.5)
ax2.legend()
st.pyplot(fig2)

# =========================
# Final values
# =========================
final_held_dot = DoT_held[-1]
final_held_poison = final_held_dot * 30
st.subheader("최종 결과")
st.subheader("최종 결과 (체감 기준)")
st.write(f"최종 Held DoT: {final_held_dot:,.0f}")
st.write(f"최종 누적 독 환산값 (×30): {final_held_poison:,.0f}")

