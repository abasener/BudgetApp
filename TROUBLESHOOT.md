# Troubleshooting Log Template

## Purpose
This file serves as a structured log for documenting debugging sessions. When encountering a problem that requires extended troubleshooting, the user should instruct the AI: **"Read TROUBLESHOOT.md and fill it out with our current issue"**

## Target Audience
This document is formatted for AI consumption, not human readability. It should contain all technical details, code references, attempted solutions, and learned patterns that would help an AI assistant quickly understand the current problem state and past debugging attempts.

## What to Include When Filling Out

### Problem Statement
- Clear description of the current issue
- Expected behavior vs actual behavior
- When the problem started occurring
- Any error messages or unexpected outputs

### Current Status
- What is working ✅
- What is not working ❌
- Current hypothesis about root cause

### File Locations
- List all relevant files with line number references
- Key functions/methods involved
- Database tables/models affected

### Technical Architecture
- Data flow diagrams (in text form)
- Dependencies between components
- Database schema details relevant to the issue
- Excel file structure (if applicable)

### Attempted Solutions
- What has been tried (with specific code changes or commands)
- Why each attempt failed
- What was learned from each attempt

### Key Technical Details
- Important patterns discovered
- Data type conversions
- Query structures
- API/function signatures
- Edge cases to handle

### Code Patterns That Work
- Include working code snippets with explanations
- Proven query patterns
- Successful data transformations

### Code Patterns That Don't Work
- Anti-patterns discovered
- Failed approaches with reasons why
- Common pitfalls to avoid

### Current Debugging Steps
- Checkpoint validations
- Diagnostic queries/commands
- Log output analysis
- Test procedures

### Helper Scripts/Tools Created
- Debugging scripts written
- Test data files created
- Validation utilities

### Next Steps When Resuming
- Immediate action items
- Required validations
- Known blockers
- Suggested approaches to try

---

## Template Sections (Fill These In)

**Note:** Delete this template section and fill in actual debugging information when an issue arises.
