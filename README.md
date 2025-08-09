# 🔀 SplitwiZe – Group Expense Manager

A lightweight Python/Streamlit application that helps groups track shared expenses, view individual balances in real time, and compute the minimal set of payments required to settle up.

---
## 🌐 Live Demo
[Click here to try the app](https://splitwize.streamlit.app/)

## 🚀 Project Overview

- **Create & Manage Multiple Groups**  
- **Register Users** with name & email  
- **Record Expenses** and automatically split equally among participants  
- **Live Balance Display** for each user  
- **Settle Up** with a single click to generate the fewest person-to-person transfers

---

## ⚙️ Tech Stack

- **Language**: Python 3.8+  
- **Web UI**: Streamlit  
- **Core Logic**:  
  - Strategy pattern for pluggable expense-splitting methods  
  - Observer pattern for real-time balance updates  
  - Efficient algorithm for minimal-transaction settlement

---

## 📦 Requirements

- Python 3.8 or higher  
- Streamlit  

```text
streamlit>=1.0
