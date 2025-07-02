from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List
from typing import Dict, Set, List
import streamlit as st
INF = float('inf')
import io
import sys


class User(ABC):
    def __init__(self,name_: str,email_: str)-> None:
        self.name=name_
        self.email=email_
    @abstractmethod
    def update(self, d: dict) -> None:
        pass




# STRATEGY METHOD FOR SPLITSTRATEGY



# ===== STRATEGY INTERFACE =====
class SplitStrategy(ABC):
    @abstractmethod
    def makeSplit(self, names: set[User], amt: int)->dict:
        pass

# ===== CONCRETE STRATEGY1 =====
class EqualSplit(SplitStrategy):
    def makeSplit(self, names: set[User], amt: int) -> dict:
        l=len(names)
        shares={}
        share=amt/l
        for name in names:
            shares[name]=share
        return shares

# ===== CONTEXT =====
class Context:
    def __init__(self, strategy_: SplitStrategy=None)->None:
        self.strategy=strategy_
    def setStrategy(self,strategy_:SplitStrategy)->None:
        self.strategy=strategy_
    def executeStrategy(self,names: set[User], amt: int)->dict:
        if(not self.strategy):
            print("There is no splitStrategy specified")
            return {}
        else:
            return self.strategy.makeSplit(names,amt)



# BEHAVIOUR METHOD



# ===== Observer Interface =====
# class Observer(ABC):
#     @abstractmethod
#     def update(self, d: dict) -> None:
#         pass


# ===== Subject  =====
class ExpenseManager:
    def __init__(self,strat: SplitStrategy) -> None:
        self.users=set()

        self.balanceSheet=defaultdict(float)
        self.context=Context()
        self.context.setStrategy(strat)


    def register_observer(self, e: User) -> None:
        if e not in self.users:
            self.users.add(e)


    def remove_observer(self, e: User) -> None:
        if e in self.users:
            self.users.discard(e)



    def _notify_observers(self) -> None:
        for e in self.users:
            e.update(self.balanceSheet)

    def addExpense(self, e1: User, amt: int) -> None:
        d=self.context.executeStrategy(self.users,amt)
        for key,value in d.items():
            if(key==e1):
                continue
            else:
                if(key in self.balanceSheet):
                    self.balanceSheet[key]-=value
                else:
                    self.balanceSheet[key]=-value
                if(e1 in self.balanceSheet):
                    self.balanceSheet[e1]+=value
                else:
                    self.balanceSheet[e1]=value
        self._notify_observers()

    def simplify(self)->dict:
        temp=[]
        corresponding_user=[]
        for key,value in self.balanceSheet.items():
            if(value!=0):
                temp.append(value)
                corresponding_user.append(key)
        
        z=len(temp)
        dp=[INF]*(1<<z)
        dp[0]=0
        parent={}
        for i in range(1,(1<<z)):
            s=0
            for k in range(z):
                if(bool(i&(1<<k))==True):
                    s+=temp[k]
            
            if(s==0):
                dp[i]=i.bit_count()

                for j in range(i):
                    val=(i|j)
                    if(val!=i):
                        continue
                    ss=0
                    for k in range(z):
                        if(i&(1<<k) and j&(1<<k)):
                            ss+=temp[k]
                    
                    if(ss==0):
                        if(dp[i]>dp[j]+dp[i-j]):
                            parent[i]=[i,j]
                            dp[i]=dp[j]+dp[i-j]
                    
        result={}
        def dfs(u:int)->None:
            if(u in parent):
                dfs(parent[u][0])
                dfs(parent[u][1])
            else:
                s=0
                ind=[]
                for k in range(z):
                    if(u&(1<<k)):
                        ind.append(k)
                zz=len(ind)
                s=0
                for i in range(zz-1):
                    s+=temp[ind[i]]
                    result[corresponding_user[ind[i]]]=[corresponding_user[ind[i+1]],s]
        # CALL DFS
        dfs((1<<z)-1)
        
        return result
    

# ===== Concrete Observer =====
class UserBalanceView(User):
    def __init__(self, name: str, email: str) -> None:
        super().__init__(name, email)

    def update(self, d: dict) -> None:
        amt = d.get(self, 0.0)
        print(f"name: {self.name}, email: {self.email}, balance: {amt}")






# WITHOUT UI SPLIWIZE RUNNING
        
# if __name__ == "__main__":
#     # Group1=ExpenseManager(EqualSplit())
#     # user1=UserBalanceView("vaibhav","vaibhav327@gmail.com")
#     # user2=UserBalanceView("karan","karan1230deep@gmail.com")
#     # user3=UserBalanceView("shubham","jassijha@gmail.com")
#     # Group1.register_observer(user1)
#     # Group1.register_observer(user2)
#     # Group1.register_observer(user3)
#     # Group1.addExpense(user1,150)
#     # Group1.addExpense(user2,90)
#     # Group1.addExpense(user3,60)
#     # Group1.simplify()




# ==== Streamlit UI ====

st.title("🔀 SplitwiZe Group Expense Manager")

# 1) Init session state
if "groups" not in st.session_state:
    st.session_state.groups = {}
    st.session_state.group_users = {}
    st.session_state.notifications = []

# Ensure widget keys exist
st.session_state.setdefault("new_group_name", "")
st.session_state.setdefault("user_name", "")
st.session_state.setdefault("user_email", "")
st.session_state.setdefault("expense_amount", 1)

# --- Callbacks ---

def create_group():
    name = st.session_state.new_group_name.strip()
    if name and name not in st.session_state.groups:
        mgr = ExpenseManager(EqualSplit())
        st.session_state.groups[name]      = mgr
        st.session_state.group_users[name] = {}
        st.session_state.notifications.append((f"✔️ Created group '{name}'", "success"))
    else:
        st.session_state.notifications.append(("❌ Invalid or duplicate group name", "error"))
    # clear the text_input
    st.session_state.new_group_name = ""

def add_user():
    grp   = st.session_state.selected_group
    name  = st.session_state.user_name.strip()
    email = st.session_state.user_email.strip()
    mgr   = st.session_state.groups[grp]
    users = st.session_state.group_users[grp]
    if name and email and name not in users:
        view = UserBalanceView(name, email)
        mgr.register_observer(view)
        users[name] = view
        st.session_state.notifications.append((f"✔️ Added user '{name}'", "success"))
    else:
        st.session_state.notifications.append(("❌ Invalid or duplicate user", "error"))
    # clear the text_inputs
    st.session_state.user_name  = ""
    st.session_state.user_email = ""

def record_expense():
    grp   = st.session_state.selected_group
    mgr   = st.session_state.groups[grp]
    users = st.session_state.group_users[grp]
    payer = st.session_state.payer_select
    amt   = st.session_state.expense_amount
    if payer in users:
        mgr.addExpense(users[payer], int(amt))
        st.session_state.notifications.append((f"✔️ {payer} paid {amt}", "success"))
    else:
        st.session_state.notifications.append(("❌ Select a valid payer", "error"))
    # reset the number_input
    st.session_state.payer_select = ""
    st.session_state.expense_amount = 1

# --- UI ---

# Sidebar: create/select group
with st.sidebar.expander("➕ Create New Group", expanded=True):
    st.text_input("Group Name", key="new_group_name")
    st.button("Create Group", on_click=create_group)

group = st.sidebar.selectbox(
    "Select Group",
    options=list(st.session_state.groups.keys()),
    key="selected_group"
)

if group:
    mgr = st.session_state.groups[group]
    users_dict = st.session_state.group_users[group]

    st.header(f"Group: {group}")

    # Add User
    with st.expander("➕ Add User"):
        st.text_input("User Name",  key="user_name")
        st.text_input("User Email", key="user_email")
        st.button("Add User", on_click=add_user)

    # Add Expense
    with st.expander("💸 Add Expense"):
        st.selectbox(
            "Payer",
            options=list(users_dict.keys()),
            key="payer_select",
            disabled=not users_dict
        )
        st.number_input(
            "Amount",
            min_value=1,
            step=1,
            key="expense_amount",
            disabled=not users_dict
        )
        st.button("Record Expense", on_click=record_expense, disabled=not users_dict)

    # View Balances
    st.subheader("Current Balances")
    for uname, user in users_dict.items():
        bal = mgr.balanceSheet.get(user, 0.0)
        st.write(f"- **{uname}**: {bal:.2f}")

    # Simplify Balances
    with st.expander("🔄 Simplify Balances"):
        if st.button("Show Simplification", on_click=None, disabled=not users_dict):
            result = mgr.simplify()
            for key,value in result.items():
                if value[1] > 0:
                    st.write(f"{value[0].name} owes {key.name} amount {value[1]}")
                else:
                    st.write(f"{key.name} owes {value[0].name} amount {-value[1]}")

# Render notifications in sidebar
                    
import time
notif_slot = st.sidebar.empty()

if st.session_state.notifications:
    msg, kind = st.session_state.notifications[-1]

    # 1) Show
    if kind == "success":
        notif_slot.success(msg)
    else:
        notif_slot.error(msg)

    # 2) Wait
    time.sleep(1)

    # 3) Clear
    notif_slot.empty()

    # And drop it from our list so we don't re-show on next rerun
    st.session_state.notifications.clear()