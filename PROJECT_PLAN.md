# 🚀 BudgetApp V2 - Project Roadmap

**Last Updated:** November 19, 2025
**Current Phase:** Phase 3 - Reimbursements & Automation

---

## 📊 Progress Overview

```
Phase 1: Core UI & Transfer System     [████████████████████] 100% ✅
Phase 2: Transactions Tab              [████████████████████] 100% ✅
Phase 3: Reimbursements & Automation   [██████████░░░░░░░░░░]  50%
Phase 4: Polish & Future Features      [░░░░░░░░░░░░░░░░░░░░]   0% 💡
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

<details>
<summary><h2>💡 Phase 4: Polish & Future Features</h2></summary>

### 🎯 Goals
Quality-of-life improvements and nice-to-have features.

### 🌟 Feature Ideas

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

**Current Focus:** Phase 3 - Reimbursements & Automation (50% complete)

**Next Steps:**
1. Begin automation features (Recurring Transaction Templates)
2. Consider Account Archiving System (requires architecture decisions)
3. Evaluate Rules/Templates system scope

**Deferred to Phase 4:**
- Performance optimizations for tab refreshing
- Enhanced keyboard shortcuts
- Year overview enhancements
