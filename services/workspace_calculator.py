"""
Workspace Calculator - Formula parsing and evaluation for Scratch Pad tab

Supports:
- Basic math: +, -, *, /
- Functions: SUM(range), AVERAGE(range)
- Cell references: A1, B5, etc.
- Cell ranges: A1:A10
- External variables: GET(variable_name)
- Date arithmetic: 11/25/2025 - CURRENT_DATE
- Current date: CURRENT_DATE

Formula must start with = to be evaluated, otherwise treated as literal text/number/date.
"""

import re
from datetime import datetime, date
from typing import Dict, Any, Set, List, Tuple, Optional


class CircularReferenceError(Exception):
    """Raised when circular cell references are detected"""
    pass


class WorkspaceCalculator:
    """Handles formula parsing, evaluation, and dependency tracking"""

    def __init__(self, transaction_manager=None):
        self.transaction_manager = transaction_manager
        self.cells = {}  # {cell_ref: {"formula": str, "value": Any, "type": str, "format": str}}
        self.dependencies = {}  # {cell_ref: set of cells this depends on}

    def parse_cell_reference(self, ref: str) -> Optional[Tuple[int, int]]:
        """Convert A1 notation to (row, col) tuple. Returns None if invalid."""
        match = re.match(r'^([A-Z]+)(\d+)$', ref.upper())
        if not match:
            return None

        col_str, row_str = match.groups()

        # Convert column letters to number (A=0, B=1, ..., Z=25)
        col = 0
        for char in col_str:
            col = col * 26 + (ord(char) - ord('A'))

        row = int(row_str) - 1  # Convert to 0-indexed

        # Validate bounds (A-Z = 0-25, rows 1-50 = 0-49)
        if col > 25 or row > 49 or row < 0:
            return None

        return (row, col)

    def cell_ref_to_str(self, row: int, col: int) -> str:
        """Convert (row, col) tuple to A1 notation"""
        # Convert column number to letters
        col_str = ""
        temp_col = col
        while True:
            col_str = chr(ord('A') + (temp_col % 26)) + col_str
            temp_col = temp_col // 26
            if temp_col == 0:
                break
            temp_col -= 1  # Adjust for 0-indexing

        return f"{col_str}{row + 1}"

    def parse_range(self, range_str: str) -> List[str]:
        """Parse range like A1:A10 into list of cell references"""
        match = re.match(r'^([A-Z]+\d+):([A-Z]+\d+)$', range_str.upper())
        if not match:
            return []

        start_ref, end_ref = match.groups()
        start_pos = self.parse_cell_reference(start_ref)
        end_pos = self.parse_cell_reference(end_ref)

        if not start_pos or not end_pos:
            return []

        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # Generate all cells in range
        cells = []
        for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
            for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
                cells.append(self.cell_ref_to_str(row, col))

        return cells

    def get_external_variable(self, var_name: str) -> Optional[float]:
        """Get value from external app data (account balances, goals, etc.)

        NEW Syntax: GET(account_name, property)
        Examples:
            GET(Safety Saving, balance)
            GET(Rent, goal)
            GET(Education, typical)
            GET(CURRENT_DATE)  - special case, no comma

        Properties:
            Accounts: balance, goal, auto_save
            Bills: balance, goal, auto_save, typical
        """
        if not self.transaction_manager:
            return None

        try:
            from models import get_db, Account, Bill, Week
            db = get_db()

            # Special case: CURRENT_DATE (no comma)
            if var_name.strip().upper() == "CURRENT_DATE":
                db.close()
                return (datetime.now().date() - date(1970, 1, 1)).days

            # Parse the variable name - expect "account_name, property" format
            if ',' not in var_name:
                db.close()
                return None

            parts = [p.strip() for p in var_name.split(',', 1)]
            if len(parts) != 2:
                db.close()
                return None

            account_name, property_name = parts
            account_name_lower = account_name.lower()
            property_lower = property_name.lower().replace('_', ' ')

            # Try to find matching account (savings)
            accounts = db.query(Account).all()
            for account in accounts:
                if account.name.lower() == account_name_lower:

                    # Account balance
                    if property_lower == "balance":
                        balance = account.get_current_balance()
                        db.close()
                        return float(balance) if balance else 0.0

                    # Account goal (field: goal_amount)
                    elif property_lower in ["goal", "goal amount", "goal_amount"]:
                        goal = account.goal_amount if account.goal_amount else 0
                        db.close()
                        return float(goal)

                    # Account auto-save (field: auto_save_amount)
                    elif property_lower in ["auto save", "auto_save", "auto save amount", "auto_save_amount"]:
                        auto_save = account.auto_save_amount if account.auto_save_amount else 0
                        db.close()
                        return float(auto_save)

                    else:
                        valid_props = "balance, goal, auto_save"
                        db.close()
                        return ("ERROR", f"Property '{property_name}' not valid for account '{account.name}'. Valid properties: {valid_props}")

            # Try to find matching bill
            bills = db.query(Bill).all()
            for bill in bills:
                if bill.name.lower() == account_name_lower:

                    # Bill balance
                    if property_lower == "balance":
                        balance = bill.get_current_balance()
                        db.close()
                        return float(balance) if balance else 0.0

                    # Bill goal (field: amount_to_save)
                    elif property_lower in ["goal", "auto save", "auto_save", "amount to save", "amount_to_save"]:
                        goal = bill.amount_to_save if bill.amount_to_save else 0
                        db.close()
                        return float(goal)

                    # Bill typical amount (field: typical_amount)
                    elif property_lower in ["typical", "typical amount", "typical_amount", "amount"]:
                        typical = bill.typical_amount if bill.typical_amount else 0
                        db.close()
                        return float(typical)

                    # Bill payment frequency
                    elif property_lower in ["frequency", "payment frequency", "payment_frequency"]:
                        db.close()
                        return bill.payment_frequency if bill.payment_frequency else ""

                    # Bill last payment date
                    elif property_lower in ["last payment", "last payment date", "last_payment_date"]:
                        db.close()
                        return bill.last_payment_date if bill.last_payment_date else None

                    # Bill type
                    elif property_lower in ["type", "bill type", "bill_type"]:
                        db.close()
                        return bill.bill_type if bill.bill_type else ""

                    # Bill is_variable
                    elif property_lower in ["variable", "is variable", "is_variable"]:
                        db.close()
                        return "Yes" if bill.is_variable else "No"

                    else:
                        valid_props = "balance, amount, frequency, type, auto_save, variable"
                        db.close()
                        return ("ERROR", f"Property '{property_name}' not valid for bill '{bill.name}'. Valid properties: {valid_props}")
            db.close()
            return None

        except Exception as e:
            return None

    def parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string in format MM/DD/YYYY"""
        try:
            return datetime.strptime(date_str, "%m/%d/%Y").date()
        except:
            return None

    def evaluate_formula(self, formula: str, cell_ref: str, visited: Set[str] = None) -> Any:
        """Evaluate a formula and return the result"""
        # Normalize cell reference to uppercase
        cell_ref = cell_ref.upper()

        if visited is None:
            visited = set()

        # Check for circular reference
        if cell_ref in visited:
            raise CircularReferenceError(f"Circular reference detected involving {cell_ref}")

        visited.add(cell_ref)

        # If doesn't start with =, it's a literal
        if not formula.startswith('='):
            # Try to parse as number
            try:
                return float(formula)
            except:
                pass

            # Try to parse as date
            parsed_date = self.parse_date(formula)
            if parsed_date:
                return parsed_date

            # Otherwise it's a string
            return formula

        # Remove = and strip whitespace
        expr = formula[1:].strip()

        # Track dependencies for this cell
        self.dependencies[cell_ref] = set()

        # Handle CURRENT_DATE() - if it's the only thing in the formula, return date directly
        if expr.upper().strip() == "CURRENT_DATE()":
            return datetime.now().date()

        # Replace CURRENT_DATE with actual date value for use in calculations
        if "CURRENT_DATE" in expr.upper():
            current = datetime.now().date()
            days_since_epoch = (current - date(1970, 1, 1)).days
            expr = re.sub(r'CURRENT_DATE\(\)', str(days_since_epoch), expr, flags=re.IGNORECASE)

        # Replace GET() functions
        get_pattern = r'GET\(([^)]+)\)'
        get_matches = list(re.finditer(get_pattern, expr, re.IGNORECASE))

        # Special case: if the entire expression is just a single GET call, return its value directly
        if len(get_matches) == 1 and expr.strip() == get_matches[0].group(0):
            var_name = get_matches[0].group(1).strip().strip('"\'')
            value = self.get_external_variable(var_name)

            # Check if it's an error tuple
            if isinstance(value, tuple) and len(value) == 2 and value[0] == "ERROR":
                return value  # Return the error as-is
            elif value is not None:
                return value  # Return string, number, or date directly
            else:
                # Better error message for GET failures
                if ',' not in var_name:
                    return ("ERROR", f"GET requires format: GET(account, property). Got: GET({var_name})")
                else:
                    parts = var_name.split(',', 1)
                    account_name = parts[0].strip()
                    return ("ERROR", f"Cannot find account or bill named '{account_name}'")

        # Otherwise, replace GET calls with their values for calculation
        for match in get_matches:
            var_name = match.group(1).strip().strip('"\'')
            value = self.get_external_variable(var_name)

            # Check if it's an error tuple
            if isinstance(value, tuple) and len(value) == 2 and value[0] == "ERROR":
                return value  # Return the error as-is
            elif value is not None:
                # Only numeric values can be used in calculations
                if isinstance(value, (int, float)):
                    expr = expr.replace(match.group(0), str(value))
                else:
                    return ("ERROR", f"Cannot use non-numeric value '{value}' in calculation")
            else:
                # Better error message for GET failures
                if ',' not in var_name:
                    return ("ERROR", f"GET requires format: GET(account, property). Got: GET({var_name})")
                else:
                    parts = var_name.split(',', 1)
                    account_name = parts[0].strip()
                    return ("ERROR", f"Cannot find account or bill named '{account_name}'")

        # Replace SUM() and AVERAGE() functions
        sum_pattern = r'SUM\(([^)]+)\)'
        for match in re.finditer(sum_pattern, expr, re.IGNORECASE):
            range_or_cells = match.group(1).strip()

            # Check if it's a range (A1:A10)
            if ':' in range_or_cells:
                cells = self.parse_range(range_or_cells)  # Already returns uppercase
            else:
                # Individual cells separated by comma - normalize to uppercase
                cells = [c.strip().upper() for c in range_or_cells.split(',')]

            # Get values and sum
            total = 0
            for cell in cells:
                self.dependencies[cell_ref].add(cell)
                cell_value = self.get_cell_value(cell, visited.copy())
                if isinstance(cell_value, (int, float)):
                    total += cell_value

            expr = expr.replace(match.group(0), str(total))

        avg_pattern = r'AVERAGE\(([^)]+)\)'
        for match in re.finditer(avg_pattern, expr, re.IGNORECASE):
            range_or_cells = match.group(1).strip()

            # Check if it's a range (A1:A10)
            if ':' in range_or_cells:
                cells = self.parse_range(range_or_cells)  # Already returns uppercase
            else:
                # Individual cells separated by comma - normalize to uppercase
                cells = [c.strip().upper() for c in range_or_cells.split(',')]

            # Get values and average
            values = []
            for cell in cells:
                self.dependencies[cell_ref].add(cell)
                cell_value = self.get_cell_value(cell, visited.copy())
                if isinstance(cell_value, (int, float)):
                    values.append(cell_value)

            avg = sum(values) / len(values) if values else 0
            expr = expr.replace(match.group(0), str(avg))

        # Replace individual cell references (case-insensitive)
        cell_pattern = r'\b([A-Za-z]+\d+)\b'
        for match in re.finditer(cell_pattern, expr):
            cell = match.group(1).upper()  # Normalize to uppercase
            original_match = match.group(1)  # Keep original for replacement
            if self.parse_cell_reference(cell):  # Validate it's a real cell
                self.dependencies[cell_ref].add(cell)
                cell_value = self.get_cell_value(cell, visited.copy())

                # Replace with value (use original match text to ensure correct replacement)
                if isinstance(cell_value, (int, float)):
                    expr = expr.replace(original_match, str(cell_value), 1)
                elif isinstance(cell_value, date):
                    # Convert date to days since epoch for calculations
                    days = (cell_value - date(1970, 1, 1)).days
                    expr = expr.replace(original_match, str(days), 1)

        # Evaluate the expression
        try:
            result = eval(expr)

            # Convert back from days to date if appropriate
            if isinstance(result, float) and result > 10000:  # Likely a date value
                try:
                    result_date = date(1970, 1, 1) + __import__('datetime').timedelta(days=int(result))
                    return result_date
                except:
                    pass

            return result
        except ZeroDivisionError:
            return ("ERROR", "Division by zero")
        except NameError as e:
            # Extract variable name from error message
            error_str = str(e)
            if "'" in error_str:
                var_name = error_str.split("'")[1]
                return ("ERROR", f"Cell or variable '{var_name}' not found")
            return ("ERROR", "Invalid cell reference or variable name")
        except TypeError as e:
            return ("ERROR", "Type mismatch - check if you're mixing dates/numbers/strings incorrectly")
        except SyntaxError:
            return ("ERROR", "Invalid formula syntax")
        except Exception as e:
            return ("ERROR", f"Unexpected error: {str(e)}")

    def get_cell_value(self, cell_ref: str, visited: Set[str] = None) -> Any:
        """Get the evaluated value of a cell"""
        # Normalize cell reference to uppercase for consistent lookups
        cell_ref = cell_ref.upper()

        if cell_ref not in self.cells:
            return 0  # Empty cell = 0

        cell_data = self.cells[cell_ref]

        # If already evaluated and stored, return it
        if "value" in cell_data and cell_data["value"] is not None:
            return cell_data["value"]

        # Otherwise evaluate the formula
        formula = cell_data.get("formula", "")
        return self.evaluate_formula(formula, cell_ref, visited)

    def set_cell_formula(self, cell_ref: str, formula: str, format_type: str = "P"):
        """Set a cell's formula and evaluate it

        Args:
            cell_ref: Cell reference like "A1"
            formula: The formula or value
            format_type: Format type - "H1", "H2", "P" (default), or "n"
        """
        # Normalize cell reference to uppercase for consistent storage
        cell_ref = cell_ref.upper()

        # Evaluate the formula
        try:
            value = self.evaluate_formula(formula, cell_ref)

            # Check if value is an error tuple
            if isinstance(value, tuple) and len(value) == 2 and value[0] == "ERROR":
                cell_type = "error"
                error_message = value[1]

                self.cells[cell_ref] = {
                    "formula": formula,
                    "value": value,  # Store tuple
                    "error_message": error_message,
                    "type": cell_type,
                    "format": format_type
                }
                return value

            # Determine type
            if formula.startswith('='):
                cell_type = "formula"
            elif isinstance(value, date):
                cell_type = "date"
            elif isinstance(value, (int, float)):
                cell_type = "number"
            else:
                cell_type = "string"

            self.cells[cell_ref] = {
                "formula": formula,
                "value": value,
                "type": cell_type,
                "format": format_type
            }

            return value

        except CircularReferenceError as e:
            error_message = f"Circular reference involving {cell_ref}"
            self.cells[cell_ref] = {
                "formula": formula,
                "value": ("ERROR", error_message),
                "error_message": error_message,
                "type": "error"
            }
            return ("ERROR", error_message)

    def get_dependent_cells(self, cell_ref: str) -> Set[str]:
        """Get all cells that depend on this cell"""
        # Normalize cell reference to uppercase
        cell_ref = cell_ref.upper()

        dependents = set()
        for cell, deps in self.dependencies.items():
            if cell_ref in deps:
                dependents.add(cell)
        return dependents

    def recalculate_cell(self, cell_ref: str):
        """Recalculate a cell and all cells that depend on it"""
        # Normalize cell reference to uppercase
        cell_ref = cell_ref.upper()

        if cell_ref not in self.cells:
            return

        # Recalculate this cell
        formula = self.cells[cell_ref]["formula"]
        self.set_cell_formula(cell_ref, formula)

        # Recursively recalculate dependent cells
        for dependent in self.get_dependent_cells(cell_ref):
            self.recalculate_cell(dependent)

    def recalculate_all(self):
        """Recalculate all cells (useful after external variable changes)"""
        # Clear all dependencies and recalculate in order
        self.dependencies = {}

        for cell_ref in list(self.cells.keys()):
            formula = self.cells[cell_ref]["formula"]
            format_type = self.cells[cell_ref].get("format", "P")  # Preserve existing format
            self.set_cell_formula(cell_ref, formula, format_type)
