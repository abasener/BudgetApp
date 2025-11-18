# 🚀 BudgetApp V2 - Project Roadmap

> **Last Updated:** November 1, 2024
> **Current Phase:** Phase 2 - Transactions Tab Implementation 🔄

---

## 📊 Progress Overview

```
Phase 1: Core UI & Transfer System    [████████████████████] 100% ✅
Phase 2: Transactions Tab              [████████████████████] 100% ✅
Phase 3: Rules & Automation            [░░░░░░░░░░░░░░░░░░░░]   0% 📅
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

#### 🔍 **Original Feature 2.1: Transaction Search/Filter Tab**
**Priority:** 🔥 High | **Status:** ✅ **IMPLEMENTED AS TRANSACTIONS TAB**

<details>
<summary>Click to expand details</summary>

**Purpose:** Dedicated tab for viewing ALL transactions with advanced filtering and search.

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Search: [_____________]  📅 Date: [From] [To]  💰 Amount │
│ 🏷️ Category: [All ▼]  🚫 Include Abnormal: [☐]              │
│ [Clear Filters] [Export CSV]                    [Add New +] │
├─────────────────────────────────────────────────────────────┤
│ ID  │ Date       │ Category    │ Amount    │ Week │ Notes  │
│ 234 │ 10/28/2024 │ Groceries   │ $   45.67 │  60  │ ...    │
│ 233 │ 10/27/2024 │ Gas         │ $   35.00 │  60  │ ...    │
│ 232 │ 10/26/2024 │ Coffee      │ $    5.50 │  60  │ ...    │
│     │            │             │           │      │        │
├─────────────────────────────────────────────────────────────┤
│ 📊 Filtered: 145 transactions | Total: $3,456.78            │
└─────────────────────────────────────────────────────────────┘
```

**Filter Options:**
- [x] **Text Search:** Search in description/notes field
- [x] **Category Filter:** Dropdown with all categories + "All"
- [x] **Date Range:** From/To date pickers
- [x] **Amount Range:** Min/Max dollar amounts
- [x] **Transaction Type:** Spending/Bill Pay/Saving/Income/Rollover
- [x] **Abnormal Flag:** Include/exclude abnormal transactions
- [x] **Account Filter:** Filter by specific account/bill

**Features:**
- [x] Sortable columns (click header to sort)
- [x] Click row to edit transaction
- [x] Export filtered results to CSV/Excel
- [x] Summary stats at bottom (count, total, average)
- [x] Right-click menu: Edit, Delete, Mark as Abnormal

**Technical Decisions Needed:**
> **Question 1:** Should this show rollover transactions?
> - Option A: Show all (including rollovers) ✅ Recommended
> - Option B: Hide rollovers (like Weekly tab does)
>
> **Question 2:** Should this show paycheck transactions?
> - Option A: Show all (including income) ✅ Recommended
> - Option B: Only spending/bills
>
> **Question 3:** Default filter state?
> - Option A: Show all transactions (no filters)
> - Option B: Default to current month only
> - Option C: Default to last 100 transactions

**Implementation Steps:**
- [ ] Create `views/transactions_view.py`
- [ ] Design filter UI with QComboBox, QDateEdit, QLineEdit
- [ ] Implement transaction table with sorting
- [ ] Add export to CSV functionality
- [ ] Wire up to main tab system
- [ ] Add to View menu navigation

**Estimated Effort:** 🕐 Medium (4-6 hours)

</details>

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
<summary><h2>📅 Phase 3: Rules & Automation (FUTURE)</h2></summary>

### 🎯 Goals
Implement intelligent automation and recurring transaction management.

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

## 🗺️ Recommended Implementation Order

### 🥇 **Next Up: Transaction Search Tab**
**Why first?**
- High user value (you said "I like it")
- Independent feature (won't conflict with other work)
- Helps with testing other features
- Moderate complexity

**Start Date:** TBD
**Est. Completion:** 1-2 days

---

### 🥈 **After That: Account Archiving**
**Why second?**
- Need to finalize architecture first (array vs JSON)
- Moderate complexity
- Affects paycheck processor (need to test carefully)

**Prerequisites:**
- [ ] Decide on data structure (Option A vs B)
- [ ] Answer the 3 architecture questions above
- [ ] Design UI mockups

---

### 🥉 **Later: Rules/Templates**
**Why last?**
- Can start simple (templates only)
- Can expand later (full rules engine)
- Least urgent

---

## 📚 Learning Resources

<details>
<summary><b>Advanced Markdown Tricks Used in This Doc</b></summary>

1. **Progress Bars:**
   ```markdown
   [████████░░] 80%
   ```

2. **Collapsible Sections:**
   ```markdown
   <details>
   <summary>Title</summary>
   Content
   </details>
   ```

3. **Tables with Complex Content:**
   ```markdown
   <table><tr><td>
   Multi-line content
   </td></tr></table>
   ```

4. **Blockquotes with Style:**
   ```markdown
   > **Note:** Important info
   ```

5. **Task Lists:**
   ```markdown
   - [x] Done
   - [ ] Todo
   ```

6. **Emojis:**
   - 🎯 Goal
   - ✅ Done
   - 📋 Planning
   - 🔥 Priority
   - 💡 Idea

7. **Code Blocks with Language:**
   ````markdown
   ```python
   code here
   ```
   ````

8. **Nested Lists:**
   ```markdown
   - Item
     - Sub-item
       - Sub-sub-item
   ```

</details>

---

## 🤔 Decision Points Needed

### High Priority Decisions
1. **Transaction Search Tab:**
   - [ ] Should it show rollover transactions?
   - [ ] Should it show paycheck transactions?
   - [ ] What's the default filter state?

2. **Account Archiving:**
   - [ ] Array-based or JSON-based history?
   - [ ] When to update history (paycheck vs manual)?
   - [ ] UI for activation/deactivation?

### Medium Priority Decisions
3. **Rules System:**
   - [ ] Start with simple templates or build full engine?
   - [ ] Scope for Phase 3?

---

## 📞 How to Use This Document

1. **Review regularly** - Check what's next before starting work
2. **Check boxes** as you complete tasks - Visual progress tracking
3. **Expand sections** you're working on - Use `<details>` for focus
4. **Update status** - Change 📋 → 🔄 → ✅ as you progress
5. **Add notes** - Document decisions and learnings
6. **Cross off completed phases** - Celebrate wins!

---

## 🎉 Recent Wins

- [x] Transfer Money system working smoothly
- [x] Menubar reorganization complete
- [x] Category colors consistent across all charts
- [x] Tab-local toolbars for Bills and Savings
- [x] Documentation fully updated

---

**Ready to start Phase 2?** Let's make decisions on the architecture questions! 🚀
