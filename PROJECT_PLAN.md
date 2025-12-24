# 🚀 BudgetApp V2 - Project Roadmap

**Last Updated:** December 22, 2025
**Current Phase:** Phase 4 - Polish & Bug Fixes

---

## 📊 Progress Overview

```
Phase 1: Core UI & Transfer System     [████████████████████] 100% ✅
Phase 2: Transactions Tab              [████████████████████] 100% ✅
Phase 3: Reimbursements & Automation   [██████████░░░░░░░░░░]  50% (Reimbursements ✅, Rules 📅 on hold)
Phase 4: Polish & Bug Fixes            [░░░░░░░░░░░░░░░░░░░░]   0% (Starting now)
```

---

<details open>
<summary><h2>✅ Phase 1: Core UI & Transfer System (COMPLETE)</h2></summary>

### 🎯 Goals
Improve core UI organization and implement essential transfer functionality.

### ✅ Completed Features

| Feature | Status | Completion Date |
|---------|--------|-----------------|
| **Transfer Money Dialog** | ✅ Complete | Oct 25, 2024 |
| ├─ Week ↔ Account transfers | ✅ | Oct 25, 2024 |
| ├─ Account ↔ Account transfers | ✅ | Oct 25, 2024 |
| ├─ Real-time balance validation | ✅ | Oct 25, 2024 |
| └─ Auto-updating transaction notes | ✅ | Oct 25, 2024 |
| **Tab-Local Toolbars** | ✅ Complete | Oct 28, 2024 |
| ├─ Bills tab: + Bill button | ✅ | Oct 28, 2024 |
| └─ Savings tab: + Savings button | ✅ | Oct 28, 2024 |
| **Menubar Reorganization** | ✅ Complete | Oct 28, 2024 |
| ├─ File menu (Import/Export/Reset) | ✅ | Oct 28, 2024 |
| ├─ Edit menu (All data modifications) | ✅ | Oct 28, 2024 |
| ├─ View menu (Navigation) | ✅ | Oct 28, 2024 |
| ├─ Tools menu (Hour Calculator) | ✅ | Oct 28, 2024 |
| └─ Help menu (About/Guide/FAQ/Bug) | ✅ | Oct 28, 2024 |
| **Category Color Consistency** | ✅ Complete | Oct 26, 2024 |
| └─ Alphabetical ordering system | ✅ | Oct 26, 2024 |

### 🎓 Key Learnings
- Transfer system uses existing SAVING transaction type with positive/negative amounts
- Week transfers create single transaction (attributed to receiving week)
- Account-to-account transfers create two transactions (linked by description)
- Menubar follows File/Edit/View/Tools/Help convention for user familiarity

### 📝 Documentation
- [x] Transfer dialog documented in ReadMe2.txt
- [x] Menubar structure documented in ReadMe2.txt
- [x] UI organization updated in README.md

</details>

---

<details>
<summary><h2>✅ Phase 2: Transactions Tab (COMPLETE - 100%)</h2></summary>

### 🎯 Goals
Create advanced transaction inspection and debugging interface with 4 sub-tabs.

### ✅ Completed Sub-Phases

| Phase | Feature | Status | Completion Date |
|-------|---------|--------|-----------------|
| **Phase 1** | Settings Toggle | ✅ Complete | Oct 28, 2024 |
| **Phase 2** | Main Tab Structure | ✅ Complete | Oct 28, 2024 |
| ├─ Sub-tabs (Bills/Savings/Paycheck/Spending) | ✅ | Oct 28, 2024 |
| ├─ Search bars for each tab | ✅ | Oct 28, 2024 |
| └─ Delete/Save buttons | ✅ | Oct 28, 2024 |
| **Phase 3** | Table Widget Base | ✅ Complete | Oct 28, 2024 |
| ├─ Sortable columns (▲/▼ indicators) | ✅ | Oct 28, 2024 |
| ├─ Search filtering (real-time) | ✅ | Oct 28, 2024 |
| ├─ Row selection (single + Ctrl multi-select) | ✅ | Oct 28, 2024 |
| ├─ Delete marking (red + strikethrough) | ✅ | Oct 28, 2024 |
| ├─ Locked row styling (gray + 🔒) | ✅ | Oct 28, 2024 |
| ├─ Abnormal checkbox widget | ✅ | Oct 28, 2024 |
| └─ Editable column (fixed width, non-editable) | ✅ | Oct 28, 2024 |
| **Phase 4** | Bills Table (Real Data) | ✅ Complete | Oct 28, 2024 |
| ├─ Load BILL_PAY transactions | ✅ | Oct 28, 2024 |
| ├─ Load SAVING(bill_id) transactions | ✅ | Oct 28, 2024 |
| ├─ Auto-notes generation | ✅ | Oct 28, 2024 |
| └─ Locked row detection | ✅ | Oct 28, 2024 |
| **Phase 5** | Savings Table (Real Data) | ✅ Complete | Nov 1, 2024 |
| ├─ Load SAVING(account_id) via AccountHistory | ✅ | Nov 1, 2024 |
| ├─ Handle deposits & withdrawals | ✅ | Nov 1, 2024 |
| ├─ Auto-notes with payweek info | ✅ | Nov 1, 2024 |
| └─ Locked rollover transactions | ✅ | Nov 1, 2024 |
| **Phase 6** | Paycheck Table (Real Data) | ✅ Complete | Nov 1, 2024 |
| ├─ Load INCOME transactions | ✅ | Nov 1, 2024 |
| ├─ Display earned & start dates | ✅ | Nov 1, 2024 |
| ├─ Auto-notes with date ranges | ✅ | Nov 1, 2024 |
| └─ All rows locked | ✅ | Nov 1, 2024 |
| **Phase 7** | Spending Table (Real Data) | ✅ Complete | Nov 1, 2024 |
| ├─ Load SPENDING & ROLLOVER | ✅ | Nov 1, 2024 |
| ├─ Include week ↔ account transfers | ✅ | Nov 1, 2024 |
| ├─ Auto-notes with category & day | ✅ | Nov 1, 2024 |
| └─ Transfer notes with destinations | ✅ | Nov 1, 2024 |
| **Phase 8** | Save Logic | ✅ Complete | Nov 2, 2024 |
| ├─ Transaction ID tracking | ✅ | Nov 2, 2024 |
| ├─ Edit & delete tracking | ✅ | Nov 2, 2024 |
| ├─ Data validation (dates, amounts) | ✅ | Nov 2, 2024 |
| ├─ Database commit logic | ✅ | Nov 2, 2024 |
| └─ Success/failure dialog | ✅ | Nov 2, 2024 |
| **Phase 9** | Bug Fixes & Polish | ✅ Complete | Nov 3, 2024 |
| ├─ Fixed AccountHistory running_total corruption | ✅ | Nov 3, 2024 |
| ├─ Fixed negative sign flipping for bills | ✅ | Nov 3, 2024 |
| ├─ Added automatic tab refresh on switch | ✅ | Nov 3, 2024 |
| ├─ Theme integration (all colors from theme) | ✅ | Nov 3, 2024 |
| └─ Database recalculation script | ✅ | Nov 3, 2024 |

### 🎓 Key Implementation Details

**Table Widget Features:**
- Smart dollar amount sorting ($1,200.00 handled correctly)
- Multi-select with Ctrl+Click
- Theme-aware styling
- Last 2 columns stretch (for long notes)
- Editable column fixed at 70px width
- Abnormal column as checkbox widget

**Data Loading Pattern:**
```python
# Use AccountHistory for Bills/Savings (correct signs)
history_manager = AccountHistoryManager(db)
history = history_manager.get_account_history(account_id, "savings")
amount = history_entry.change_amount  # Preserves +/- sign

# Query transactions directly for Paycheck/Spending
transactions = get_all_transactions()
filtered = [t for t in transactions if condition]
```

**Auto-Notes Format:**
- Paychecks: `"Manual: Paycheck 30 for 10/21/2024 to 11/03/2024"`
- Spending: `"Manual: Paycheck 30 bought Groceries on Monday"`
- Transfers: `"Manual: Transfer to Emergency Fund"`
- Rollovers: `"Generated: Rollover from payweek 30"`
- Allocations: `"Generated: Savings allocation from payweek 30"`

**Locking Logic:**
- ROLLOVER & INCOME → Always locked
- SAVING with "allocation" or "end-of-period" → Locked (auto-generated)
- SAVING with week_number + account/bill_id → Locked in Spending tab only
- Regular SPENDING → Editable
- Manual BILL_PAY & SAVING → Editable

**Save Functionality:**
- Tracks transaction IDs for each row (all 4 tabs)
- Tracks edited and deleted rows separately
- Clears tracking when switching between sub-tabs
- Validates dates (MM/DD/YYYY format) and amounts (numeric)
- Saves changes transaction-by-transaction with rollback on error
- Shows detailed success/failure dialog with change summary
- Refreshes tables after successful save

---

#### 🔍 **Feature 2.1: Transaction Search/Filter Tab**
**Status:** ✅ **IMPLEMENTED AS TRANSACTIONS TAB**

The Transactions tab provides advanced transaction inspection with 4 sub-tabs (Bills, Savings, Paycheck, Spending) featuring:
- Search bars and sortable columns
- Delete/Save buttons with validation
- Editable and locked rows
- Real-time filtering

See Phase 2 completed sub-phases above for full implementation details.

---

#### 📦 **Feature 2.2: Account Archiving System**
**Priority:** 🟡 Medium | **Status:** 🤔 Architecture Discussion Needed

<details>
<summary>Click to expand details</summary>

**Purpose:** Temporarily deactivate accounts (vacation savings, seasonal bills) without deleting history.

**Use Cases:**
1. **Seasonal Bills:** Summer water bill higher than winter
2. **Temporary Goals:** Vacation fund active for 6 months, then inactive
3. **Income Changes:** Reduce savings when between jobs

**Current Discussion:**

You mentioned tracking with arrays:
```python
auto_save_amounts = [100, 100, 1000, 0, 0, 0]  # History of auto_save settings
is_active_history = [1, 1, 1, 1, 0, 0]         # History of active states
```

**🤔 Architecture Options:**

<table>
<tr>
<th>Option A: Parallel Arrays</th>
<th>Option B: JSON History (Simpler)</th>
</tr>
<tr>
<td>

```python
# Account model
auto_save_amounts = [100, 100, 1000, 0]
is_active_history = [1, 1, 1, 0]
history_dates = ["2024-01-01", "2024-03-01", ...]
```

**Pros:**
- Direct array indexing
- Fast lookups by index

**Cons:**
- Must keep arrays in sync
- Date mapping unclear
- When to add new entry?

</td>
<td>

```python
# Account model
is_active = Column(Boolean, default=True)
activation_history = Column(JSON)

# History format:
[
  {"date": "2024-01-01", "active": true, "auto_save": 100},
  {"date": "2024-03-01", "active": true, "auto_save": 1000},
  {"date": "2024-06-01", "active": false, "auto_save": 0}
]
```

**Pros:**
- Self-contained entries
- Easy to query by date
- Clear structure

**Cons:**
- Need to parse JSON
- Slightly slower lookups

</td>
</tr>
</table>

**❓ Questions to Resolve:**
1. **When does history get updated?**
   - On every paycheck? (automatic snapshot)
   - Only when user changes settings? (manual)
   - Both? (hybrid)

2. **What happens during inactive periods?**
   - Paycheck processor skips inactive accounts? ✅ Recommended
   - Or still deducts $0 and tracks it?

3. **UI for reactivation?**
   - "Activate" button in account editor? ✅ Simple
   - Or automatic reactivation on next paycheck?

**Example Scenario:**
```
Vacation Account Timeline:
├─ Jan-May: Active, $200/paycheck (saving phase)
├─ June: Inactive, took vacation (spending phase)
├─ July-Dec: Active, $100/paycheck (rebuilding phase)
└─ Jan: Inactive, planning next year
```

**Proposed Implementation (Option B):**
```python
class Account(Base):
    is_active = Column(Boolean, default=True)
    activation_history = Column(JSON, default=list)

    def set_active(self, active: bool, auto_save_amount: float = None):
        """Update activation status and log to history"""
        self.is_active = active
        if auto_save_amount is not None:
            self.auto_save_amount = auto_save_amount

        # Add history entry
        if self.activation_history is None:
            self.activation_history = []

        self.activation_history.append({
            "date": datetime.now().isoformat(),
            "active": active,
            "auto_save": self.auto_save_amount
        })
```

**UI Mockup:**
```
┌─────────────────────────────────────┐
│ Account: Vacation Fund              │
├─────────────────────────────────────┤
│ Status: [●] Active  [○] Inactive    │
│ Auto-save: $_____ per paycheck      │
│                                     │
│ 📜 History:                         │
│ ├─ 2024-01-01: Active ($200)       │
│ ├─ 2024-06-01: Inactive ($0)       │
│ └─ 2024-07-01: Active ($100)       │
└─────────────────────────────────────┘
```

**Implementation Steps:**
- [ ] Decide on architecture (Array vs JSON)
- [ ] Add is_active field to Account/Bill models
- [ ] Add activation_history field (if using Option B)
- [ ] Update paycheck processor to skip inactive accounts
- [ ] Add activation UI to account editor dialog
- [ ] Add visual indicator on Bills/Savings tabs (grayed out?)
- [ ] Test reactivation flow

**Estimated Effort:** 🕐 Medium (5-7 hours)

</details>

---

### 🎓 Markdown Tips You're Learning Here
```markdown
<!-- Collapsible sections with <details> -->
<details>
<summary>Click me!</summary>
Hidden content here
</details>

<!-- Tables with alignment -->
| Left | Center | Right |
|:-----|:------:|------:|
| L    |   C    |     R |

<!-- Emojis for visual interest -->
🚀 ✅ 📋 🔥 🎯

<!-- Code blocks with syntax highlighting -->
```python
def example():
    pass
\`\`\`

<!-- Checkboxes for task lists -->
- [x] Done
- [ ] Todo
```

</details>

---

<details>
<summary><h2>🔄 Phase 3: Reimbursements & Automation (IN PROGRESS - 50%)</h2></summary>

### 🎯 Goals
Track work travel expenses and temporary out-of-pocket costs separate from main budget, with future automation features.

### ✅ Completed Features

| Feature | Status | Completion Date |
|---------|--------|-----------------|
| **Reimbursements System** | ✅ Complete | Nov 20, 2025 |
| ├─ Database model (amount, date, state, notes, category, tag) | ✅ | Nov 19, 2025 |
| ├─ ReimbursementManager CRUD service | ✅ | Nov 19, 2025 |
| ├─ Add Transaction dialog integration | ✅ | Nov 19, 2025 |
| ├─ Reimbursements tab with tag filtering | ✅ | Nov 19, 2025 |
| ├─ Weekly view integration (grayed out rows) | ✅ | Nov 19, 2025 |
| ├─ Add button (opens dialog) | ✅ | Nov 19, 2025 |
| ├─ Save button (batch edits with validation) | ✅ | Nov 19, 2025 |
| ├─ Delete button (red text marking) | ✅ | Nov 19, 2025 |
| ├─ Export button (Excel with smart filename) | ✅ | Nov 19, 2025 |
| └─ **Interactive Visualizations** | ✅ | Nov 20, 2025 |
|   ├─ Stats panel (total $ + status pie chart) | ✅ | Nov 20, 2025 |
|   ├─ Progress bars (submitted % & reimbursed %) | ✅ | Nov 20, 2025 |
|   ├─ Dot plot (amount vs age by category, adaptive) | ✅ | Nov 20, 2025 |
|   └─ Tag × Category heatmap (complete overview) | ✅ | Nov 20, 2025 |

### 🎓 Key Implementation Details

**Reimbursements Architecture:**
- **Separate from budget**: NOT included in week spending calculations
- **Bank reconciliation**: Show in weekly view tables (grayed out, italic)
- **5 States**: Pending → Submitted → Reimbursed/Partial/Denied
- **Auto-date updates**: `submitted_date` and `reimbursed_date` set when state changes
- **Dual tagging**: Location/trip tags (e.g., "Whispers25") + category (e.g., "Hotel")

**Table Features:**
- Editable cells with yellow highlight (blended warning color)
- Delete marking with red text
- Sortable columns (click header)
- Multi-row selection (Ctrl+click)
- Tag filtering sidebar ("All", "Other", individual tags)

**Export Format:**
```
Filename: Reimbursements_Whispers25_111925.xlsx
Columns: Amount | Tag | Category | Notes | Status
```

**Use Cases:**
1. Work travel expenses awaiting company reimbursement
2. Friend loans/IOUs (money lent expecting repayment)
3. Temporary out-of-pocket costs

---

### 💡 Planned Features

#### 🔁 **Feature 3.1: Recurring Transaction Templates**
**Priority:** 🟡 Medium | **Status:** 🎨 Concept Phase

<details>
<summary>Click to expand details</summary>

**Purpose:** Save common transactions as templates for quick entry.

**Two Possible Approaches:**

<table>
<tr>
<th>Option A: Simple Templates</th>
<th>Option B: Full Rules Engine</th>
</tr>
<tr>
<td>

**Scope:** Pre-fill only
- User creates template
- "Add from Template" button
- User edits before saving

**UI:**
```
┌─ Templates Tab ─┐
│ ☕ Coffee: $5.50  │
│ ⛽ Gas: $35.00    │
│ 🍔 Lunch: $12.00 │
└──────────────────┘
```

**Pros:**
- Simple to implement
- User has control
- No automation risks

**Effort:** 🕐 Small (2-3 hours)

</td>
<td>

**Scope:** Full automation
- Auto-create transactions
- Pattern detection
- Conditional logic
- Alerts/warnings

**Features:**
1. Templates
2. Auto-categorize
3. Alerts
4. Auto-transactions

**Pros:**
- Very powerful
- Less manual work

**Cons:**
- Complex to build
- Potential bugs
- Need safety checks

**Effort:** 🕐 Large (15-20 hours)

</td>
</tr>
</table>

**Recommendation:** Start with Option A (Simple Templates), expand to Option B later if needed.

**Template Structure:**
```python
class TransactionTemplate(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)  # "Morning Coffee"
    category = Column(String)  # "Coffee"
    amount = Column(Float)  # 5.50
    description = Column(String)  # "Starbucks"
    icon = Column(String)  # "☕" (optional emoji)
```

**UI Integration:**
- Add "Templates" tab next to Transactions tab
- "Add from Template" button in Add Transaction dialog
- Quick-add from dropdown in toolbar

**Implementation Steps:**
- [ ] Create TransactionTemplate model
- [ ] Create templates management UI
- [ ] Add "Add from Template" to transaction dialog
- [ ] Add template quick-select dropdown
- [ ] Allow template editing/deletion

</details>

---

#### 🧠 **Feature 3.2: Smart Category Detection**
**Priority:** 🔵 Low | **Status:** 💭 Ideas Phase

<details>
<summary>Click to expand details</summary>

**Purpose:** Auto-suggest categories based on description patterns.

**Pattern Matching Examples:**
```
"Starbucks" → Coffee
"Shell Gas" → Gas
"Kroger" → Groceries
"Netflix" → Entertainment
```

**Implementation Options:**
1. **Simple Keyword Matching:** Fast, works for most cases
2. **Machine Learning:** Overkill for desktop app
3. **User-Trained Rules:** Best of both worlds

**Proposed Approach:**
```python
# User creates patterns over time
category_patterns = {
    "Coffee": ["starbucks", "dunkin", "coffee"],
    "Gas": ["shell", "bp", "marathon", "gas"],
    "Groceries": ["kroger", "walmart", "target"]
}

def suggest_category(description: str) -> str:
    desc_lower = description.lower()
    for category, keywords in category_patterns.items():
        if any(keyword in desc_lower for keyword in keywords):
            return category
    return "Uncategorized"
```

**UI Flow:**
1. User enters description: "Starbucks Grande Latte"
2. System suggests: "Coffee" (based on "starbucks" match)
3. User can accept or change
4. If changed, ask: "Always categorize 'Starbucks' as X?"

**Implementation Steps:**
- [ ] Create pattern storage (JSON settings file)
- [ ] Add pattern detection logic
- [ ] Add "Learn from this" UI prompt
- [ ] Add pattern management UI (Settings?)
- [ ] Test pattern matching performance

**Estimated Effort:** 🕐 Medium (4-6 hours)

</details>

---

#### 🔔 **Feature 3.3: Rules & Alerts System**
**Priority:** 🔵 Low | **Status:** 💭 Future Consideration

<details>
<summary>Click to expand details</summary>

**Purpose:** Conditional warnings and automation triggers.

**Example Rules:**
```python
# Alert if weekly spending > budget
if week.spent > week.allocated:
    show_alert("Overspending this week!")

# Warn if bill due soon
if bill.days_until_due < 3 and bill.balance < bill.typical_amount:
    show_warning("Internet bill due in 2 days!")

# Suggest transfer when savings goal met
if account.balance >= account.goal_amount:
    suggest_action("Goal reached! Transfer to checking?")
```

**Rule Types:**
- **Budget Alerts:** Spending limits per week/category
- **Bill Reminders:** Due date warnings
- **Goal Tracking:** Savings milestone notifications
- **Anomaly Detection:** Unusual spending patterns

**Implementation Complexity:** 🔥 High
- Needs rule definition language
- Needs rule evaluation engine
- Needs notification system
- Needs rule management UI

**Decision:** Defer to Phase 4 or beyond

</details>

</details>

---

<details open>
<summary><h2>🔧 Phase 4: Polish & Bug Fixes (IN PROGRESS)</h2></summary>

### 🎯 Goals
Quality-of-life improvements, edge case handling, and UI refinements before returning to Phase 3 Rules system.

**Note:** Phase 3 is 50% complete (Reimbursements ✅ done, Rules & Automation 📅 on hold). We're doing Phase 4 polish first, then returning to complete Phase 3 later.

---

### 📋 Active Bug/Polish Overview

| Category | Issue | Priority | Status |
|----------|-------|----------|--------|
| 🐛 **Critical Bugs** | Transactions tab - Editing not saving | 🔴 High | 🔄 In Progress |
| 🐛 **Critical Bugs** | Tax tab scrollbar disappeared | 🔴 High | ✅ Complete |
| 🐛 **Critical Bugs** | Transactions tab - Sign display incorrect | 🔴 High | ✅ Refactored |
| ✨ **Refactoring** | Transactions tab - Sub-tab restructure | 🔴 High | ✅ Complete |
| 🐛 **Critical Bugs** | Scratch Pad - Refresh removes formatting | 🔴 High | 📋 Todo |
| 🐛 **Display Issues** | Week tab - Starting/ending amounts display same | 🟡 Medium | 📋 Todo |
| 🎨 **Theme System** | Theme colors/fonts not updating consistently | 🟡 Medium | 📋 Todo |
| ✨ **Feature Polish** | Categories tab - Include Abnormal checkbox | 🟡 Medium | ✅ Complete |
| ✨ **Feature Polish** | Current Week/Paycheck Highlighting | 🟡 Medium | ✅ Complete |
| ✨ **Feature Polish** | Week tab - Edit transaction dates | 🟡 Medium | 📋 Todo |
| ✨ **Feature Polish** | Tab reordering system | 🟡 Medium | 💭 Design |
| ✨ **Feature Polish** | Scratch Pad - Case-insensitive & advanced paste | 🟡 Medium | 📋 Todo |
| ⚙️ **Settings Overhaul** | Export/Import all data | 🟡 Medium | 💭 Design |
| ⚙️ **Settings Overhaul** | Tab visibility toggles | 🟡 Medium | 📋 Todo |
| 🔧 **Low Priority** | Year tab - Better visualizations for bottom plots | 🟢 Low | 💭 Design |
| 🔧 **Low Priority** | Dashboard dynamic sizing | 🟢 Low | 💭 Design |
| 🔧 **Low Priority** | Other Income transaction type | 🟢 Low | 💭 Design |

---

<details open>
<summary><h3>🐛 Critical Bug Fixes</h3></summary>

#### 🔴 **Bug 4.1: Transactions Tab - Editing Not Persisting**
**Status:** 🔄 In Progress | **Priority:** 🔴 High

**Issue:**
- Edits to transactions not always saving
- Need to implement save logic for all 4 sub-tabs

**Progress (December 2024):**
- ✅ Sub-tabs restructured: Bills+Savings merged → Accounts, Transfers tab added
- ✅ All 4 tabs now query Transaction table directly (consistent pattern)
- ✅ Transaction IDs tracked for each row (ready for save logic)
- ✅ Transfers tab stores tuple `(source_id, dest_id)` for paired transactions
- ✅ Info button added with field descriptions for each sub-tab
- 📋 Next: Implement save handlers for each sub-tab

**See:** `TRANSACTIONS_TAB_ROADMAP.md` for detailed editing rules and implementation steps

---

#### 🔴 **Bug 4.2: Transactions Tab - Sign Display**
**Status:** ✅ Refactored (December 2024) | **Priority:** 🔴 High

**Original Issue:**
- Sign display was confusing - sometimes showing raw values, sometimes absolute

**Resolution - Intentional UX Design:**
Rather than showing raw database signs (which confused users), we implemented a **Movement column** system:

| Tab | Amount Display | Direction Indicator |
|-----|----------------|---------------------|
| Accounts | Always positive | Movement column: Deposit/Withdrawal/Payment |
| Paycheck | Always positive | N/A (always income) |
| Spending | Always positive | N/A (type indicates direction) |
| Transfers | Always positive | From/To columns show direction |

**Movement Types (Accounts Tab):**
- **Deposit**: Money going INTO account from week (was positive amount)
- **Withdrawal**: Money going FROM account TO week (was negative amount)
- **Payment**: Bill payment leaving budget entirely (type=bill_pay)

**Rationale:**
- User-friendly: No confusion about what negative/positive means
- Clear direction: Movement/From/To columns explicitly show money flow
- Consistent: All amounts positive, direction shown via dedicated column

**Files Modified:**
- `views/transactions_view.py` - All 4 `load_*_data()` methods updated

---

#### ✨ **Refactoring 4.2.1: Transactions Tab Sub-Tab Restructure**
**Status:** ✅ Complete (December 2024) | **Priority:** 🔴 High

**Changes Made:**

**1. Sub-Tab Reorganization:**
- OLD: Bills | Savings | Paycheck | Spending
- NEW: Accounts | Paycheck | Spending | Transfers

**2. Accounts Tab (merged Bills + Savings):**
- Shows all Week↔Account transactions
- New columns: `[ID][Locked][Date][Account][Movement][Amount][Type][Week][Manual Notes][Auto Notes]`
- Movement column replaces sign display (Deposit/Withdrawal/Payment)
- Excludes Account↔Account transfers (those go to Transfers tab)
- Now queries Transaction directly (was using AccountHistory indirectly)

**3. Transfers Tab (new):**
- Shows ONLY Account↔Account transfers (where `transfer_group_id` is set)
- Shows ONE row per transfer pair (not both sides)
- Columns: `[ID][Date][Amount][From][To][Week][Locked][Manual Notes][Auto Notes]`
- ID shows "source_id/dest_id" format
- Stores tuple of both IDs for save logic

**4. Spending Tab:**
- Removed "Week Pos" column
- Rollovers now show "First"/"Second" in Category column instead of "Rollover"
- New column order: `[ID][Date][Amount][Category][Type][Abnormal][Paycheck][Week][Locked][Manual Notes][Auto Notes]`

**5. All Tabs:**
- Header changed from "🔒" to "Locked" (emoji stays in cell values)
- All tabs now query Transaction table directly (consistent pattern)

**Database Support:**
- `transfer_group_id` field added to Transaction model (UUID, links paired transfers)
- Migration script: `migrations/add_transfer_group_id.py`

---

#### 🔴 **Bug 4.3: Tax Tab - Scrollbar Disappeared (Again)**
**Status:** ✅ Complete (2025-11-29) | **Priority:** 🔴 High

**Issue:**
- Scrollbar not showing on Tax tab
- This was previously fixed with `showEvent` handler

**Solution:**
- Improved `showEvent` handler in `views/taxes_view.py`
- Removed unnecessary `hasattr(self, 'init_ui')` check
- Added `adjustSize()` call to force proper layout adjustment
- Scrollbar now appears correctly on initial tab load

**Files Modified:**
- `views/taxes_view.py:103-114` - Enhanced showEvent handler

---

#### 🔴 **Bug 4.4: Scratch Pad - Refresh Removes All Formatting**
**Status:** 📋 Todo | **Priority:** 🔴 High

**Issue:**
- When refresh button is pressed on Scratch Pad tab, all formatting is lost
- Headers, notes, and other user-added formatting disappear
- Only raw cell values/formulas remain

**Root Cause:**
- Refresh likely reloads from data storage without preserving formatting metadata
- May be treating Scratch Pad as pure data grid instead of rich text/formatted document
- Formatting might not be persisted to storage, only in-memory

**Expected Behavior:**
- Refresh should reload data WITHOUT removing user formatting
- Headers should remain headers
- Notes/text should remain styled
- Only recalculate formulas/values, preserve all visual formatting

**Next Steps:**
1. Check how formatting is stored (in-memory vs persisted)
2. Ensure refresh method preserves formatting metadata
3. If formatting not persisted, add to save/load logic

**Files to Check:**
- `views/scratch_pad_view.py` - Refresh logic
- Scratch Pad data model/storage

---

#### 🟡 **Bug 4.5: Week Tab - Starting/Ending Amounts Display Same**
**Status:** 📋 Todo | **Priority:** 🟡 Medium

**Issue:**
- Week tab displays starting money and final money as the same value
- This is a persistent issue, not just with negative spending
- Makes it hard to see what was actually spent during the week
- Layout may not be intuitive - unclear which number means what

**Example (Week 64):**
- Base allocation: $435.55
- Total spending: -$1465.33 (net negative due to -$1805.40 transaction)
- Expected remaining: $1900.88
- **But displays show same value for start and end** (unclear which is which)

**Root Cause:**
- Unclear which display element shows "starting" vs "current/remaining"
- May be calculation issue or display labeling issue
- Layout/UX design makes it hard to distinguish values

**Expected Behavior:**
- **Clear labels:** "Starting Amount" vs "Current Remaining" vs "Total Spent"
- **Visual hierarchy:** Make it obvious which number is which
- **Calculation transparency:**
  - Starting = Base allocation + rollovers + transfers in - transfers out
  - Spent = Sum of spending transactions (can be negative!)
  - Remaining = Starting - Spent

**Suggested Improvements:**
1. Add clear text labels (not just icons or positions)
2. Use different font sizes/weights for hierarchy
3. Consider vertical layout instead of horizontal
4. Add tooltip explanations for each value
5. Show calculation breakdown (expandable/collapsible)

**Next Steps:**
1. Audit weekly_view.py text display section
2. Identify which QLabel shows what value
3. Add clear, unambiguous labels
4. Test with various scenarios (positive/negative spending, rollovers, transfers)

**Files to Check:**
- `views/weekly_view.py` - `update_week_text_info()` method (lines 533-600)
- Look for QLabel widgets displaying financial amounts

---

</details>

---

<details>
<summary><h3>🎨 Theme System Fixes</h3></summary>

#### 🎨 **Bug 4.3: Theme Colors Not Updating on Theme Change**
**Status:** 📋 Todo | **Priority:** 🟡 Medium

**Issue:**
Multiple UI elements not updating colors when theme changes. Requires tab reload or app restart to see new theme.

**Affected Elements:**

**Bills/Savings Tabs:**
- "Sort by" label for dropdown
- Save Changes button on "See History" popups
- Table text color after clicking (changes from correct color to white)
- Current balance number in Edit Account/Bill dialogs
- Button hover/focus styling (appears to be global issue)

**Tax/Year Overview Tabs:**
- Year label text colors (only update when tab reloaded)
- Year tab background color (using theme color but may not be optimal choice)

**Hour Calculator:**
- Text color appears hardcoded (not using theme)
- Hover effects not using theme colors

**Scratch Pad:**
- Cell text (all 4 styles: H1, H2, Normal, Notes) not updating on theme change

**Expected Behavior:**
- ALL elements should update immediately when theme changes
- No reload/restart required

**Implementation Pattern:**
```python
def __init__(self):
    theme_manager.theme_changed.connect(self.on_theme_changed)

def on_theme_changed(self, theme_id):
    colors = theme_manager.get_colors()
    # Update ALL styled widgets here
    self.apply_theme_colors()
    self.refresh()
```

**Next Steps:**
1. Audit all tabs for missing `on_theme_changed` connections
2. Year tab - match background color approach to Taxes tab
3. Create theme color update checklist for future tabs

**Files to Check:**
- `views/bills_view.py` - Sort by label, buttons
- `views/savings_view.py` - Sort by label, buttons
- `views/dialogs/bill_transaction_history_dialog.py` - Save Changes button
- `views/dialogs/edit_account_dialog.py` - Current balance text
- `views/dialogs/edit_bill_dialog.py` - Current balance text
- `views/dialogs/hour_calculator.py` - Text colors, hover effects
- `views/taxes_view.py` - Year labels
- `views/year_overview_view.py` - Year labels, background color
- `views/scratch_pad_view.py` - Cell text styling

---

#### 🎨 **Bug 4.4: Theme Fonts Not Applied Consistently**
**Status:** 📋 Todo | **Priority:** 🟡 Medium

**Issue:**
- Not all text using theme fonts
- Fonts are defined in theme manager but not applied everywhere

**Available Font Types (in themes/theme_manager.py):**
- `main` - Body text
- `title` - Page titles
- `header` - Section headers
- `button` - Button text
- `button_small` - Small button text

**Note:** Fonts `subtitle`, `small`, `menu`, `nonspace` mentioned by user but need verification if in theme definitions.

**Expected Behavior:**
- ALL text should pull from corresponding theme font type
- Currently only visible in non-default themes (default has same font for all)

**Next Steps:**
1. Verify all font types exist in theme manager
2. Audit all views for hardcoded fonts
3. Create font application helper function
4. Test with Coffee theme (has distinct fonts)

---

#### 🎨 **Bug 4.5: Settings - Default Theme Changes Current Theme**
**Status:** 📋 Todo | **Priority:** 🟡 Medium

**Issue:**
- Changing "Default Theme" in Settings dialog applies immediately
- Should only affect next app load, not current session

**Current Controls:**
1. **Settings Dialog:** Default Theme (should apply on next launch only)
2. **Main App Dropdown:** Current Theme (should apply immediately)

**Expected Behavior:**
- Settings default theme = saved to `app_settings.json`, loaded on startup
- Main app dropdown = changes theme immediately for current session
- Two separate controls doing two separate things

**Next Steps:**
- Disconnect theme change trigger from Settings default theme dropdown
- Ensure app loads `default_theme` from settings on startup
- Keep main app theme selector as-is (immediate change)

**Files to Check:**
- `views/dialogs/settings_dialog.py` - Default theme dropdown
- `main.py` - Theme loading on startup

---

</details>

---

<details>
<summary><h3>✨ Feature Polish (Medium Priority)</h3></summary>

#### ✨ **Feature 4.6: Week Tab - Edit Transaction Dates**
**Status:** 📋 Todo | **Priority:** 🟡 Medium

**Purpose:**
Add ability to change transaction dates directly in weekly view transaction table.

**Current State:**
- Can edit description, amount, category
- Cannot edit date (requires using Transactions tab or re-creating transaction)

**Expected Behavior:**
- Date column editable like other fields
- Validation: Warn if moving transaction to different week
- Trigger rollover recalculation if date changes

**Implementation Notes:**
- Similar to existing editable fields in weekly transaction table
- Add date validation dialog
- Call `trigger_rollover_recalculation()` after save

**Files to Modify:**
- `views/weekly_view.py` - Transaction table editing

---

#### ✨ **Feature 4.7: Current Week/Paycheck Highlighting**
**Status:** ✅ Complete (2025-11-29) | **Priority:** 🟡 Medium

**Purpose:**
Visual indicator for current week in navigation dropdowns.

**Implementation Complete:**

**1. Pay Period Dropdown (Top of Week Tab):**
- ✅ Added ⭐ to right side of current pay period
- ✅ Determined by checking if today's date falls within period date range
- ✅ Star is right-aligned with spaces for visual separation
- ✅ Example: `"Pay Period 30          ⭐\n11/18/2024"`

**2. Week 1/Week 2 Sub-section Headers:**
- ✅ Added ⭐ to right side of current week header
- ✅ All week headers remain bold (original styling preserved)
- ✅ Determined by checking if today falls within week's date range
- ✅ Star is right-aligned with spaces for visual separation
- ✅ Example: `Week 1: 11/18/2024 - 11/24/2024          ⭐` vs `Week 2: 11/25/2024 - 12/01/2024`

**Date Detection Logic:**
- Uses `week.start_date <= today <= week.end_date` check
- Automatically updates when tab is refreshed or new week begins

**Files Modified:**
- `views/weekly_view.py:2080-2106` - Pay period star indicator
- `views/weekly_view.py:126-156` - Week header bold highlighting

---

#### ✨ **Feature 4.8: Categories Tab - "Include Abnormal" Checkbox**
**Status:** ✅ Complete (2025-11-29) | **Priority:** 🟡 Medium

**Purpose:**
Add checkbox to toggle abnormal spending in Categories tab analytics.

**Default State:**
- **Categories tab:** Include abnormal = ON (show all transactions)
- **Dashboard:** Include abnormal = OFF (hide abnormal spending)

**Rationale:**
- Abnormal spending (new car, medical bills) skews dashboard totals
- But Categories tab looks at granular transaction level, so include by default
- User can still toggle off if desired

**Implementation Complete:**
- ✅ Added checkbox to header with theme-aware styling
- ✅ Default: Checked (shows all transactions including abnormal)
- ✅ Refreshes all analytics when toggled
- ✅ Updated all data filtering methods:
  - Category details, histogram, weekly trends
  - Correlation plots, box plot, pie chart
  - Category stats and color mapping
- ✅ Theme updates apply to checkbox styling
- ✅ Fixed matplotlib warnings (xlim/ylim singular, correlation on constant arrays)

**Files Modified:**
- `views/categories_view.py:76-100` - Checkbox UI
- `views/categories_view.py:606-609` - Handler method
- `views/categories_view.py` - Updated 8 filtering methods
- `views/categories_view.py:1583-1600` - Theme styling

---

#### ✨ **Feature 4.9: Tab Reordering System**
**Status:** 💭 Design | **Priority:** 🟡 Medium

**Purpose:**
Reorder tabs for better workflow + allow user customization.

**Proposed Default Order:**
1. Dashboard
2. Weekly
3. Bills
4. Savings
5. Reimbursements
6. Categories
7. Year Overview
8. Taxes (optional)
9. Scratch Pad
10. Transactions (optional - admin tool)

**Bonus Feature:**
- Settings option to customize tab order
- Drag-and-drop or up/down arrows
- Save order to `app_settings.json`

**Implementation:**
- Change tab creation order in `main.py`
- Add custom order UI to Settings dialog
- Store as array: `["dashboard", "weekly", "bills", ...]`

**Files to Modify:**
- `main.py` - Tab creation order
- `views/dialogs/settings_dialog.py` - Custom order UI (optional)

---

#### ✨ **Feature 4.10: View Menu - Add Missing Tabs**
**Status:** 📋 Todo | **Priority:** 🟡 Medium

**Purpose:**
Add all tabs to View → Navigate menu dropdown.

**Currently Missing:**
- Reimbursements
- Scratch Pad
- Possibly others

**Expected Behavior:**
- View menu has entry for every visible tab
- Clicking navigates to that tab
- Disabled tabs (Transactions, Taxes) hidden from menu or grayed out

**Files to Modify:**
- `main.py` - View menu construction

---

#### ✨ **Feature 4.11: Scratch Pad - Case-Insensitive Functions/Cells**
**Status:** 📋 Todo | **Priority:** 🟡 Medium

**Purpose:**
Make Scratch Pad formulas case-insensitive for easier use.

**Expected Behavior:**
- Cell references: `K2` = `k2`
- Functions: `GET` = `get`, `SUM` = `sum`, `AVERAGE` = `average`
- Account names: Case-insensitive matching

**Implementation:**
- Convert all cell references to uppercase before lookup
- Convert function names to uppercase before evaluation
- Case-insensitive account name matching in GET function

**Files to Modify:**
- `services/workspace_calculator.py` - Formula parsing

---

#### ✨ **Feature 4.12: Scratch Pad - Advanced Copy/Paste Modes**
**Status:** 💭 Design | **Priority:** 🟡 Medium

**Purpose:**
Add Excel-like paste options for formulas.

**Three Paste Modes:**

**1. Normal Paste (Current Behavior):**
- Pastes formulas as-is
- Cell references update based on absolute position

**2. Shift+Paste (Values Only):**
- Pastes calculated values, not formulas
- Example: Copy `=SUM(A1:A10)` (result: 500) → Paste `500`

**3. Ctrl+Shift+V (Relative Paste):**
- Adjusts cell references relative to new position
- Both rows AND columns adjust
- Example:
  - Cell K2 contains `=A1+B1`
  - Copy K2, paste to M4 (moved right 2, down 2)
  - Result: `=C3+D3` (A→C, B→D, 1→3)

**Implementation Complexity:**
- Relative paste requires formula AST modification
- Need to track copy source position
- Recalculate dependencies after paste

**Files to Modify:**
- `views/scratch_pad_view.py` - Copy/paste handlers
- `services/workspace_calculator.py` - Formula adjustment logic

---

</details>

---

<details>
<summary><h3>⚙️ Settings Dialog Overhaul</h3></summary>

#### ⚙️ **Feature 4.13: Tab Visibility Toggles**
**Status:** 📋 Todo | **Priority:** 🟡 Medium

**Purpose:**
Allow users to hide tabs they don't use for cleaner interface.

**Always Visible (Core Tabs):**
- Dashboard
- Weekly
- Bills
- Savings

**Optional Tabs (Can Toggle Off):**
- Reimbursements (default: ON)
- Categories (default: ON)
- Year Overview (default: ON)
- Taxes (default: OFF - already toggleable)
- Scratch Pad (default: ON)
- Transactions (default: OFF - already toggleable, admin tool)

**Implementation:**
- Add checkboxes to Settings dialog
- Save to `app_settings.json`
- Show/hide tabs on setting change (or require restart?)

**Files to Modify:**
- `views/dialogs/settings_dialog.py` - Add toggles
- `main.py` - Conditional tab creation

---

#### ⚙️ **Feature 4.14: Settings - General Cleanup & Organization**
**Status:** 📋 Todo | **Priority:** 🟡 Medium

**Purpose:**
Reorganize Settings dialog into logical groups.

**Proposed Structure:**

**General:**
- Default theme (on next launch)
- Data directory location

**Tab Visibility:**
- Checkboxes for optional tabs (Feature 4.13)

**Features:**
- Enable Transactions Tab ✅ (already exists)
- Enable Taxes Tab ✅ (already exists)
- Testing/Debug Mode toggle
- Other feature flags

**Data Management:**
- Export All Data (Feature 4.15)
- Import All Data (Feature 4.16)

**Files to Modify:**
- `views/dialogs/settings_dialog.py` - Reorganize layout

---

#### ⚙️ **Feature 4.15: Export All Data**
**Status:** 💭 Design | **Priority:** 🟡 Medium

**Purpose:**
Export all app data for backup/sharing.

**Export Options (User Selects):**
- ☑ Settings (`app_settings.json`)
- ☑ Database (`.db` file or SQL dump)
- ☑ Scratch Pad Workspace (`scratch_pad_workspace.json`)
- ☑ Tax data (part of database?)
- ☑ Reimbursements (part of database)
- ☑ Year Overview data (calculated from database, not separate)

**Export Format:**
- **Option A:** Single ZIP file with all selected items
  - Pros: Easy to share, single file
  - Cons: User must unzip (can app auto-unzip on import?)

- **Option B:** Separate files in selected folder
  - Pros: Direct access to files
  - Cons: Multiple files to manage

**Decision:** Discuss when implementing (lean toward ZIP with auto-unzip on import)

**Files to Modify:**
- `views/dialogs/settings_dialog.py` - Export UI
- New utility: `utils/data_export.py` or similar

---

#### ⚙️ **Feature 4.16: Import All Data**
**Status:** 💭 Design | **Priority:** 🟡 Medium

**Purpose:**
Import exported data with conflict resolution.

**Import Conflict Handling:**

**Database:**
- Overwrite: Replace entire database
- Merge: Combine data (requires ID conflict resolution)
- Cancel: Abort import

**Settings:**
- Overwrite: Use imported settings
- Merge: Keep current settings, import only new keys
- Cancel: Keep current settings

**Scratch Pad:**
- Overwrite: Replace workspace
- Merge: Combine (how to handle cell conflicts?)
- Cancel: Keep current workspace

**Implementation:**
- Similar to Excel import (reference: `views/dialogs/import_transactions_dialog.py`)
- Show preview before committing
- Backup current data before import

**Files to Modify:**
- `views/dialogs/settings_dialog.py` - Import UI
- New utility: `utils/data_import.py` or similar

---

</details>

---

<details>
<summary><h3>🔧 Low Priority / Nice-to-Have</h3></summary>

#### 🔧 **Feature 4.17: Year Tab - Enhanced Bottom Visualizations**
**Status:** 💭 Design | **Priority:** 🟢 Low

**Issue:**
- Bottom 3-4 line plots are placeholders
- Don't display data well, no useful info can be pulled from them

**Expected Behavior:**
- Replace with better visualizations that show meaningful insights
- Moved from Phase 4.4 "Enhanced Year Overview" to active work

**Design Questions:**
- What data should they show? (Monthly trends? Category breakdowns by year?)
- What chart types work best? (Keep line plots or switch to bar/scatter?)
- Merge with existing "Enhanced Year Overview" ideas?

**Reference:**
- See Feature 4.4 in "Nice-to-Have Feature Ideas" section for enhancement ideas

---

#### 🔧 **Feature 4.18: Dashboard - Dynamic Sizing/Scrollbar**
**Status:** 💭 Design | **Priority:** 🟢 Low | **⚠️ FRAGILE**

**Issue:**
- Dashboard widgets don't adapt to window size
- Content can overflow without scrollbar

**Proposed Solutions:**
1. Add vertical scrollbar when content exceeds viewport
2. Dynamic widget sizing based on available space
3. Collapsible sections to save space

**Warning:**
- Dashboard layout is complex and fragile
- Changes could break existing functionality
- Requires careful testing

**Next Steps:**
- Test current overflow scenarios
- Prototype scrollbar solution first (safest)
- Consider dynamic sizing only if necessary

**Files to Modify:**
- `views/dashboard.py` - Layout and sizing logic

---

#### 🔧 **Feature 4.19: Testing Mode Popups Audit**
**Status:** 📋 Todo | **Priority:** 🟢 Low

**Purpose:**
Ensure all debug/testing popups respect testing mode toggle.

**Task:**
- Find all dialogs/popups with debug output
- Check if they're controlled by testing mode flag
- Ensure they don't appear when testing mode OFF

**Testing Mode Location:**
- Settings dialog (may be labeled "Debug Mode")

**Next Steps:**
1. Find testing mode flag in settings
2. Search codebase for debug dialogs
3. Verify flag is checked before showing

**Files to Check:**
- Search for `QMessageBox` and `print()` statements
- Check if wrapped in `if testing_mode:` conditions

---

#### 🔧 **Feature 4.20: "Other Income" Transaction Type**
**Status:** 💭 Design | **Priority:** 🟢 Low

**Purpose:**
Support non-paycheck income (refunds, reimbursements, gifts, account transfers) in a semantically clear way.

**Current Workaround:**
- User can enter negative spending (e.g., -$1805.40)
- Mathematically works: `remaining = starting - (-1805.40)` adds money
- But semantically confusing: "spending" implies money out, not in

**Proposed Solution:**
Add `OTHER_INCOME` transaction type that:
- Works like SPENDING but ADDS money instead of subtracting
- Displays clearly as "Income" in transaction tables
- Can be categorized (e.g., "Venmo Refund", "Gift", "Reimbursement")
- Marked as abnormal by default (won't skew normal spending analytics)

**Use Cases:**
1. Money regained from closed accounts
2. Venmo/PayPal refunds not from paychecks
3. Gifts/windfalls
4. Insurance reimbursements (separate from Reimbursements tab, which tracks pre-payment)
5. Credit card rewards/cashback

**Implementation:**
```python
class TransactionType(Enum):
    SPENDING = "spending"
    BILL_PAY = "bill_pay"
    SAVING = "saving"
    INCOME = "income"
    ROLLOVER = "rollover"
    OTHER_INCOME = "other_income"  # NEW
```

**Display:**
- Weekly tab: Show as green/positive entry (opposite of red spending)
- Transaction table: Clear "Other Income" label
- Analytics: Exclude by default (similar to abnormal spending)

**Alternative:**
- Keep current negative spending approach
- User already comfortable with it
- Easy to find (search for negative Venmo transactions)
- Only implement if polish phase has time

**Decision:** Defer until after critical bugs fixed

---

</details>

---

---

<details>
<summary><h3>🗄️ Database Migrations</h3></summary>

#### **Migration: add_transfer_group_id (December 2024)**

**Purpose:** Links paired Account-to-Account transfer transactions so they can be edited together.

**Background:**
- Week ↔ Account transfers: Single transaction (no linking needed)
- Account ↔ Account transfers: Two transactions created (need linking)
- `transfer_group_id` field stores a UUID that both transactions share

**Files Added:**
- `migrations/backup_database.py` - Database backup utility
- `migrations/add_transfer_group_id.py` - Migration script

**Model Changes:**
- `models/transactions.py` - Added `transfer_group_id` column (String(36), nullable, indexed)
- Added `is_paired_transfer` property

**Running the Migration (Machine A / Production):**

```bash
# 1. Pull latest code from GitHub
git pull

# 2. Run the migration script
python migrations/add_transfer_group_id.py
```

**What the Migration Does:**
1. Creates a timestamped backup in `backups/` folder
2. Adds `transfer_group_id` column to transactions table (safe - doesn't affect existing data)
3. Scans for existing Account-to-Account transfer pairs and links them:
   - Same date
   - Same absolute amount
   - Opposite signs (one positive, one negative)
   - Different account_ids
4. Verifies the migration succeeded

**Sample Output:**
```
============================================================
Migration: Add transfer_group_id to transactions table
============================================================

Step 1: Creating backup...
[OK] Database backed up to: backups/budget_app_backup_20241220_123456.db

Step 2: Adding transfer_group_id column...
[OK] Successfully added transfer_group_id field

Step 3: Linking existing transfer pairs...
   Found 8 saving transactions with account_id
   [LINKED] IDs 45 <-> 46: $200.00 (group: a1b2c3d4...)
   [LINKED] IDs 52 <-> 53: $75.00 (group: e5f6g7h8...)

   Pairs found: 2
   Pairs linked: 2

Step 4: Verifying migration...
[OK] transfer_group_id column exists
[OK] 4 transactions linked in 2 groups

============================================================
Migration complete!
============================================================
```

**Rollback (if needed):**
```bash
python migrations/backup_database.py restore backups/budget_app_backup_YYYYMMDD_HHMMSS.db
```

---

</details>

---

### 🌟 Nice-to-Have Feature Ideas (Lower Priority)

#### 📝 **Feature 4.1: Notes Field for Transactions**
**Priority:** 🟢 Nice-to-Have | **Status:** 💭 Idea

**Simple Implementation:**
- Add `notes` field to Transaction model
- Show as expandable text area in transaction dialogs
- Display as tooltip on hover in tables
- No attachments, just plain text

**Estimated Effort:** 🕐 Small (1-2 hours)

---

#### 🎮 **Feature 4.2: "What If" Scenario Planning**
**Priority:** 🟢 Nice-to-Have | **Status:** 💭 Idea

**Purpose:** Preview impact of potential transactions without committing.

**Example:**
```
What if I buy a $500 TV this week?
├─ Week 60 remaining: $767 → $267
├─ Week 61 starting: $454 + $267 = $721 (instead of $1,221)
└─ Emergency fund: +$721 (instead of +$1,221)
```

**Possible in Transaction Search Tab as simulation mode.**

---

#### ⌨️ **Feature 4.3: Keyboard Shortcuts**
**Priority:** 🟢 Nice-to-Have | **Status:** 💭 Idea

**Shortcuts to Add:**
- `Ctrl+N` - New Transaction
- `Ctrl+P` - Add Paycheck
- `Ctrl+T` - Transfer Money
- `Ctrl+1-6` - Navigate tabs
- `F5` - Refresh All
- `Ctrl+F` - Focus search (in Transactions tab)

---

#### ⚡ **Feature 4.4: Performance Optimizations for Tab Refreshing**
**Priority:** 🟡 Medium | **Status:** 💭 Observation/Future Work

**Context:**
Currently, tabs refresh on every switch (implemented Nov 2024). This ensures data consistency across tabs, but can be slow for tabs with heavy data/charts.

**Observed Bottlenecks:**
1. **Database Queries**: Loading AccountHistory entries (can be 50-200+ per account/bill)
2. **Chart Rendering**: matplotlib line plots recalculating and redrawing
3. **Data Processing**: Sorting, filtering, calculating running totals

**Optimization Ideas (Priority Order):**

**🔥 High Impact:**
1. **Query Limiting**: Show last N entries by default (e.g., 50 most recent)
   - Add "Show All" button for full history
   - Would reduce query size by 75-90%

2. **Conditional Refresh**: Only refresh if data actually changed
   - Add timestamp tracking to database writes
   - Check timestamp before re-querying
   - Skip refresh if no changes since last load

3. **Lazy Loading**: Don't load tab data until first viewed
   - Initial app load only loads Dashboard
   - Other tabs load on-demand
   - Reduces startup time significantly

**🟡 Medium Impact:**
4. **Background Threading**: Query data in background threads
   - UI stays responsive during queries
   - Show loading spinner while refreshing
   - Requires thread-safe database session handling

5. **Smart Caching**: Cache query results with invalidation
   - Cache AccountHistory per account/bill
   - Invalidate cache on relevant writes
   - Memory vs. speed tradeoff

**🟢 Low Impact:**
6. **Data-Only Refresh**: Separate "refresh data" from "refresh UI"
   - NOT recommended - data queries are the slow part, not UI
   - Charts need redraw anyway to show new data
   - Complexity not worth minimal gains

**Recommended First Steps (When Ready):**
1. Implement query limiting (last 50 entries) - easy win
2. Add conditional refresh with timestamp checks - moderate complexity
3. Consider lazy loading if startup time becomes issue

**Estimated Effort:** 🕐 Medium (4-6 hours for items 1-2)

---

#### 📊 **Feature 4.4: Enhanced Year Overview**
**Priority:** 🟢 Nice-to-Have | **Status:** 💭 Idea

**Additional Charts:**
- Seasonal spending patterns (which months cost more?)
- Category breakdown by year (not just totals)
- Bill increase trends (are bills getting more expensive?)
- Savings rate acceleration (is it improving?)

---

#### 🔄 **Feature 4.5: Editable Paycheck Amounts with Auto-Recalculation**
**Priority:** 🟡 Medium | **Status:** 💭 Future Enhancement

**Purpose:** Allow editing paycheck amounts in Transactions tab and automatically recalculate all dependent allocations.

**Current State:**
- Paychecks are locked (non-editable) in Transactions tab
- Reason: Changing paycheck amount doesn't trigger recalculation of:
  - Bill savings allocations (% or $ based)
  - Account auto-savings (% or $ based)
  - Week allocations
  - Rollovers

**Required Implementation:**
1. Add INCOME transaction support to `trigger_rollover_recalculation()`
2. Create `PaycheckProcessor.recalculate_paycheck_allocations(paycheck_id)`
3. When paycheck amount changes:
   - Recalculate all SAVING allocations for that paycheck's week
   - Update bill/account savings transactions
   - Trigger rollover recalculation for the entire pay period
4. Make Paycheck table rows editable (remove locked status)

**Estimated Effort:** 🕐 Medium (4-6 hours)

</details>

---

## ❌ Explicitly NOT Building

> These were considered and decided against.

| Feature | Reason |
|---------|--------|
| **Split Transactions** | User does the math (add 2 transactions) |
| **Pending/Cleared Status** | Use future dates instead |
| **Receipt Attachments** | Desktop app limitation, adds complexity |
| **Velocity Alerts (Hardcoded)** | Would be in Rules system if built |

---

## 🗺️ Implementation Priority

**Current Focus:** Phase 4 - Polish & Bug Fixes (just starting)

**Immediate Next Steps:**
1. Identify and fix bugs discovered during usage
2. Handle edge cases in existing features
3. UI refinements and consistency improvements
4. Performance optimizations if needed

**After Phase 4:**
- Return to Phase 3 - Complete Rules & Automation system (see RULES_PLANNING.md)
- Implement Goals, Warnings, and Automations with block-based UI builder
- Add recurring transaction templates

**Long-term Future Ideas:**
- Enhanced keyboard shortcuts
- Year overview enhancements
- Smart category detection
- Account archiving system
