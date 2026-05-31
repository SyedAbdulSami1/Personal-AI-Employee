# Skill: Email Summary
## Trigger
Jab user "emails summarize karo" ya "inbox summary" likhe

## Steps (No LLM needed)
1. Needs_Action/ folder se sab EMAIL_*.md files read karo
2. Har file se: from, subject, priority extract karo
3. Group karo: High, Medium, Low priority
4. Summary banao aur dashboard update karo

## Output Format
### 📧 Email Summary
**High Priority:** {count}
- From: {sender} | {subject}

**Medium Priority:** {count}  
- From: {sender} | {subject}

**Low Priority:** {count}
- From: {sender} | {subject}

## Rules
- LLM mat call karo — sirf file reading
- Max 10 emails show karo
- Unread count dashboard pe update karo