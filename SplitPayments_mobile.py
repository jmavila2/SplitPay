import streamlit as st
from typing import List, Dict, Tuple

def split_amount_cents_fair(amount_cents: int, participants: List[str]) -> Dict[str, int]:
    n = len(participants)
    base = amount_cents // n
    rem = amount_cents % n
    sorted_participants = sorted(participants, key=lambda x: x.lower())
    shares = {p: base for p in participants}
    for i in range(rem):
        shares[sorted_participants[i]] += 1
    return shares

def compute_balances(names, expenses):
    balances = {n: 0 for n in names}
    paid_total = {n: 0 for n in names}
    owed_total = {n: 0 for n in names}

    for exp in expenses:
        payer = exp["payer"]
        amount = exp["amount_cents"]
        part_list = exp["participants"]
        shares = split_amount_cents_fair(amount, part_list)

        balances[payer] += amount
        paid_total[payer] += amount

        for person, share in shares.items():
            balances[person] -= share
            owed_total[person] += share

    return balances, paid_total, owed_total

def minimize_cash_flow(balances):
    debtors = []
    creditors = []

    for name, bal in balances.items():
        if bal < 0:
            debtors.append([name, -bal])
        elif bal > 0:
            creditors.append([name, bal])

    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    transfers = []
    i, j = 0, 0

    while i < len(debtors) and j < len(creditors):
        d_name, d_amt = debtors[i]
        c_name, c_amt = creditors[j]
        pay = min(d_amt, c_amt)
        transfers.append((d_name, c_name, pay))

        debtors[i][1] -= pay
        creditors[j][1] -= pay

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return transfers

def format_cents(cents):
    return f"${cents / 100:.2f}"

# ---------- Streamlit UI ----------

st.title("💸 Group Expense Split Tool")

# Participants
st.header("Participants")
participants_input = st.text_input(
    "Enter participant names separated by commas",
    placeholder="Jesus, Mike, Anna, Chris"
)

if participants_input:
    names = [n.strip() for n in participants_input.split(",") if n.strip()]
else:
    names = []

# Expenses
st.header("Add Expense")

if "expenses" not in st.session_state:
    st.session_state.expenses = []

if names:
    payer = st.selectbox("Who paid?", names)
    amount = st.number_input("Amount", min_value=0.01, step=0.01)
    participants = st.multiselect("Who participated?", names, default=names)

    if st.button("Add Expense"):
        st.session_state.expenses.append({
            "payer": payer,
            "amount_cents": int(round(amount * 100)),
            "participants": participants
        })
        st.success("Expense added!")

# Show expenses
if st.session_state.expenses:
    st.header("Recorded Expenses")
    for e in st.session_state.expenses:
        st.write(f"{e['payer']} paid {format_cents(e['amount_cents'])} for {', '.join(e['participants'])}")

    if st.button("Calculate Settlement"):
        balances, paid_total, owed_total = compute_balances(names, st.session_state.expenses)
        transfers = minimize_cash_flow(balances)

        st.header("Settlement Transfers")
        if not transfers:
            st.success("Everyone is settled up!")
        else:
            for d, c, amt in transfers:
                st.write(f"**{d} → {c}: {format_cents(amt)}**")


