# Rules & Automation System Planning

**Status:** Planning Phase - Awaiting Flowchart
**Date:** November 3, 2024
**Phase:** Phase 3 of PROJECT_PLAN.md

---

## 📖 Key Terms & Definitions

| Term | Definition |
|------|------------|
| **Rule** | Generic term for any automation, goal, or warning in the system |
| **Goal** | Rule type with Condition → Output (positive reinforcement popup) |
| **Warning** | Rule type with Condition → Output (alert/reminder popup) |
| **Automation** | Rule type with Condition → Function (executes an action in the app) |
| **Condition** | The trigger that determines when a rule should fire (e.g., "spending > 50% income") |
| **Output** | What to show the user (popup message with custom text and icon) |
| **Function** | An action the app performs automatically (e.g., pay a bill, add transaction) |
| **Admin** | Settings/controls for managing a rule (difficulty, importance, repeat, enabled/disabled) |

---

## 🏗️ System Architecture

### Three Rule Types

```
┌─────────────────────────────────────────────────────────────┐
│ 1. GOAL                                                     │
│    Condition → Output (Positive reinforcement)              │
│    Example: "Spend < 50% income → 'Good job! Here's coffee'"│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. WARNING                                                  │
│    Condition → Output (Alert/Reminder)                      │
│    Example: "Savings < 10% goal → 'Slow down spending!'"   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3. AUTOMATION                                               │
│    Condition → Function (Execute action)                    │
│    Example: "Day = 2 → Pay Internet bill $35.00"           │
└─────────────────────────────────────────────────────────────┘
```

### Four Components

Every rule consists of **2-3 of these components**:

1. **Condition** (all rules have this)
2. **Output** (Goals & Warnings only)
3. **Function** (Automations only)
4. **Admin** (all rules have this)

---

## 🎯 Conditions (When to Trigger)

### Time-Based Conditions
- [ ] Day of month is X (1-31)
- [ ] Day of week is X (Monday-Sunday)
- [ ] Week number is X
- [ ] Paycheck number is X
- [ ] Specific date is/before/after X
- [ ] First week of month
- [ ] Between paychecks

**Questions:**
- Should "day" support both day of month AND day of week?
- Date ranges needed? (e.g., "between paycheck 5 and 10")

---

### Spending-Based Conditions
- [ ] Spending this week > X dollars
- [ ] Spending this week < X dollars
- [ ] Spending this week > X% of paycheck
- [ ] Spending this week < X% of paycheck
- [ ] Spending in category Y this week > X
- [ ] Total spending this paycheck period > X

**Questions:**
- What time period for income comparison? (current week, current paycheck, or user choice?)
- Compare against running totals or just new transactions?

---

### Account/Bill Balance Conditions
- [ ] Account X balance < Y dollars
- [ ] Account X balance > Y dollars
- [ ] Account X balance < Y% of goal (amount_to_save)
- [ ] Account X balance > Y% of goal
- [ ] Bill X balance > Y dollars (overpaid)
- [ ] Bill X balance < 0 (underpaid/in debt)
- [ ] Week remaining balance < X

**Questions:**
- Goal percentage compares to `amount_to_save` field?
- Support "falls below" AND "rises above"?

---

### Transaction Event Conditions
- [ ] Any transaction added
- [ ] Any bill was paid
- [ ] Bill X was paid
- [ ] Transfer to account Y occurred
- [ ] Transfer from account Y occurred
- [ ] Spending transaction added in category X

---

### Additional Condition Ideas (Optional/Future)
- [ ] Number of transactions this week > X
- [ ] Consecutive days with spending > X
- [ ] Abnormal transaction count > X
- [ ] Rollover amount > X
- [ ] Paycheck amount differs from expected by > X%

---

## 💬 Outputs (Goals & Warnings)

### Popup Message Components
- **Custom text** (user-defined, no dynamic variables)
- **Icon choice** (7 fun icons tied to emotions)
- **Button** (OK only, or OK + Cancel for function confirmations)

### Icon Types (7 total)
User will choose an icon type, which maps to actual emoji/image:
1. Fun/Playful (🎉 or plant image?)
2. Happy/Success (✨ or gift box?)
3. Sad/Disappointed (😔 or worm?)
4. Motivation/Encouragement (💪 or rocket?)
5. Warning/Caution (⚠️ or stop sign?)
6. Achievement/Victory (🏆 or trophy?)
7. Neutral/Info (ℹ️ or clipboard?)

**Note:** Icons are decorative flair, NOT the standard popup symbols (⚠️ ❗ ❓ ✓)

**Future Expansion (not now):**
- Dashboard notification badges
- Tab color highlights
- Status bar messages
- Email notifications
- Log entries

---

## ⚙️ Functions (Automations Only)

### Financial Actions
- [ ] Pay bill X for $Y
- [ ] Pay bill X for typical_amount
- [ ] Add spending transaction (amount, category, description, week)
- [ ] Add saving transaction (to account X, amount Y)
- [ ] Transfer money (week → account, amount)
- [ ] Transfer money (account → account, amount)
- [ ] Transfer money (week → bill, amount)

**Questions:**
- Should automations require confirmation popup before running?
- Or run silently and just log the action?
- Dry-run/test mode?

---

### Data Actions (Additional Ideas)
- [ ] Adjust auto_save amount for account X to Y
- [ ] Mark last transaction as abnormal
- [ ] Export data to file
- [ ] Process paycheck early
- [ ] Recalculate rollovers for week X

---

### Additional Function Ideas (Optional/Future)
- [ ] Send email/notification
- [ ] Create recurring reminder
- [ ] Pause auto_save for account X
- [ ] Change bill typical_amount to X
- [ ] Backup database

---

## 🛠️ Admin Settings

Every rule has these administrative controls:

### Core Settings
- [x] **Enabled/Disabled** - Toggle to turn off without deleting
- [x] **Difficulty** - User mental marker (1-5 stars?) for goal complexity
- [x] **Importance** - User priority level (1-5 stars?)
- [x] **Repeat Options**:
  - Once (delete after completion)
  - When finished (re-check immediately after trigger)
  - Daily
  - Weekly
  - Per paycheck
  - Monthly
  - Yearly

### Purpose of Difficulty/Importance
- **Difficulty**: Mental tracking - "this is a hard goal to achieve"
- **Importance**: Mental tracking - "this matters more to me"
- May add sorting/filtering logic later, but for now just user reference

**Future Expansion (not now):**
- History/logging of when rules triggered
- Last triggered timestamp
- Trigger count
- Success/failure tracking

---

## 🖥️ User Interface Design

### Block-Based Builder (Dropdown Cascades)

```
┌─────────────────────────────────────────────────────────┐
│ RULE TYPE:  [Goal ▼]  [Warning]  [Automation]          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ CONDITION:                                              │
│   Type: [Spending-Based ▼]                             │
│         ↓                                               │
│   Compare: [Spending this week ▼]                      │
│         ↓                                               │
│   Operator: [Greater than ▼]                           │
│         ↓                                               │
│   Value: [50] [% of income ▼]                          │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ OUTPUT: (if Goal/Warning)                              │
│   Icon: [🎉 Fun/Playful ▼]                             │
│   Message: [Good job saving! You have won your         │
│             favorite coffee from ___ next week!]       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ADMIN:                                                  │
│   Difficulty: [⭐⭐⭐☆☆]                                 │
│   Importance: [⭐⭐⭐⭐☆]                                 │
│   Repeat: [Weekly ▼]                                   │
│   Enabled: [✓]                                         │
│                                                         │
│         [Save Rule]  [Cancel]  [Test Now]              │
└─────────────────────────────────────────────────────────┘
```

### Tab Layout
- New "Rules" tab in main application
- List view showing all rules (like Bills/Savings tabs)
- "Add Rule" button opens builder dialog
- Each rule shows: Type, Condition summary, Enabled status
- Edit/Delete buttons per rule
- "Test" button to manually trigger rule check

---

## ⚡ Rule Execution Strategy

### Performance Considerations

**Problem:** Checking rules on every action could slow down the app.

**Proposed Solution:** Smart trigger tracking array

```python
# Example tracking array
rule_check_needed = [
    0,  # Index 0: Date changed (new day)
    0,  # Index 1: Transaction added/modified
    0,  # Index 2: Bill paid
    1,  # Index 3: Account balance changed ← needs check!
    0,  # Index 4: Week changed
]

# On any app action:
if rule_check_needed[action_type] == 1:
    check_rules_for_trigger_type(action_type)
```

**Trigger Types to Track:**
1. Date/time changed (new day detected)
2. Transaction added/modified
3. Bill paid
4. Account balance changed
5. Week/paycheck changed
6. Manual trigger (user clicked "Test")

**Trade-off:** Filtering overhead vs. unnecessary rule checks - need to benchmark.

**Alternative:** Just check all rules on any data change (simpler, potentially slower)

---

## 💾 Data Storage

**Proposed:** New `Rule` table in database with JSON fields

```python
class Rule(Base):
    __tablename__ = 'rules'

    id = Column(Integer, primary_key=True)
    rule_type = Column(String)  # 'goal', 'warning', 'automation'
    name = Column(String)  # User-friendly name
    enabled = Column(Boolean, default=True)

    # JSON fields for flexibility
    condition = Column(JSON)  # {type: 'spending', operator: '>', value: 50, ...}
    output = Column(JSON)     # {icon: 'fun', message: '...'}  (Goals/Warnings)
    function = Column(JSON)   # {action: 'pay_bill', bill_id: 2, ...}  (Automations)
    admin = Column(JSON)      # {difficulty: 3, importance: 4, repeat: 'weekly'}

    # Metadata
    created_date = Column(Date)
    last_triggered = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
```

**Note:** Final structure TBD - will refine during implementation.

---

## 📋 Design Constraints

### What We're NOT Doing (Keep It Simple)
- ❌ **No boolean logic** - Single conditions only (no AND/OR chains)
- ❌ **No dynamic variables** - Popup text is static user input
- ❌ **No complex messaging** - Just popups for now (no badges, emails, etc.)
- ❌ **No history/logging** - Too fancy for v1
- ❌ **No AI/smart suggestions** - User defines all rules manually

### What We ARE Doing (Core Focus)
- ✅ **Simple condition builder** - Dropdown cascades, easy to understand
- ✅ **Fun user experience** - Custom icons, personalized messages
- ✅ **Flexible foundation** - Easy to extend later with more features
- ✅ **Reliable execution** - Smart trigger detection, minimal performance impact

---

## 🔍 Open Questions for Flowchart

1. **UI Flow:**
   - How many screens in the Add Rule wizard?
   - Can user preview rule before saving?
   - How to edit existing rules?

2. **Condition Builder:**
   - Exact dropdown structure for each condition type?
   - How to handle numeric inputs (text box, slider, spinner)?
   - Date picker for time-based conditions?

3. **Function Confirmations:**
   - Which automations need OK/Cancel vs. silent execution?
   - How to show what automation did after it runs?

4. **Rule Priority:**
   - If multiple rules trigger at once, show all popups sequentially?
   - Or combine into single popup?
   - Respect importance level for ordering?

5. **Testing:**
   - "Test Now" button - simulate condition being true?
   - Or check if condition is actually true right now?

---

## 🚀 Implementation Priority

**Phase 1 (Foundation):**
1. Create Rule table in database
2. Build basic Rules tab UI (list view)
3. Implement simple condition: "Day of month = X"
4. Implement simple output: Popup with custom text + icon
5. Test end-to-end: Create rule → Trigger → Show popup

**Phase 2 (Expand Conditions):**
1. Add spending-based conditions
2. Add account balance conditions
3. Add transaction event conditions

**Phase 3 (Add Automations):**
1. Implement function execution framework
2. Add "Pay bill" automation
3. Add "Add transaction" automation
4. Add confirmation dialogs for automations

**Phase 4 (Polish):**
1. Rule editing/deletion
2. Enable/disable toggle
3. Repeat logic
4. Difficulty/importance UI

---

## 📝 Example Rule Scenarios (For Testing)

### Goal Example 1:
```
Type: Goal
Condition: Spending this week < 50% of paycheck
Output: Icon=🎉, Message="Good job saving! You have won your favorite coffee from ___ next week!"
Admin: Difficulty=3, Importance=4, Repeat=Weekly, Enabled=Yes
```

### Warning Example 1:
```
Type: Warning
Condition: Safety Savings account balance < 10% of goal
Output: Icon=⚠️, Message="You have been using a lot of your Safety Savings. Take a breath and make sure you are spending intentionally."
Admin: Difficulty=2, Importance=5, Repeat=Daily, Enabled=Yes
```

### Automation Example 1:
```
Type: Automation
Condition: Day of month = 2
Function: Pay Internet bill for $35.00
Admin: Difficulty=1, Importance=5, Repeat=Monthly, Enabled=Yes
```

### Goal Example 2:
```
Type: Goal
Condition: Spending in Groceries this week < $100
Output: Icon=✨, Message="You stayed on budget for groceries! Treat yourself to a movie night!"
Admin: Difficulty=3, Importance=3, Repeat=Weekly, Enabled=Yes
```

### Warning Example 2:
```
Type: Warning
Condition: Week remaining balance < $50
Output: Icon=🛑, Message="You're running low on funds this week. Consider skipping non-essentials."
Admin: Difficulty=2, Importance=4, Repeat=Once, Enabled=Yes
```

---

## 🔮 Future Enhancements (Not Now - For Later)

**Stored here so we don't forget, but NOT implementing in Phase 3:**

### Advanced Conditions
- Boolean logic (AND/OR chains)
- Multiple conditions per rule
- Percentage change over time (e.g., "spending increased 20% vs. last week")
- Streak tracking (e.g., "saved money for 7 consecutive weeks")

### Advanced Outputs
- Dashboard badges with counters
- Tab color highlights
- Status bar persistent messages
- Email/SMS notifications
- Custom sounds

### Advanced Functions
- Chain multiple actions
- Conditional actions (if X then do Y, else do Z)
- Scheduled delays (do X in 3 days)
- Recurring task creation

### Advanced Admin
- Rule templates/presets
- Import/export rules
- Rule groups/categories
- Trigger history with full logs
- Success rate tracking
- A/B testing for goals

### Integration Ideas
- Connect to calendar for date-based rules
- Connect to weather API (e.g., "if raining, suggest saving on gas")
- Connect to bank API for real-time balance checks
- Machine learning suggestions for rule creation

---

## 📌 Next Steps

1. **USER ACTION:** Create flowchart showing:
   - Add Rule UI flow (dropdown cascades)
   - Rule trigger detection logic
   - Output/Function execution flow
   - Edit/Delete rule flow

2. **REVIEW:** Discuss flowchart and finalize:
   - Exact condition types list
   - Exact function types list
   - UI screen mockups
   - Database schema

3. **IMPLEMENT:** Start Phase 1 (Foundation)

---

**End of Planning Document**
**Awaiting Flowchart for Next Steps**
