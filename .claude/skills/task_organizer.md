# Skill: Task Organizer
## Trigger
Jab user "tasks organize karo" ya "priority set karo" likhe

## Steps (No LLM needed)
1. Needs_Action/ folder scan karo
2. Priority ke hisaab se sort karo: high > medium > low
3. Type ke hisaab se group karo: email, whatsapp, file
4. Dashboard.md update karo
5. Done tasks /Done/ mein move karo

## Output Format
### 📋 Task Summary
**Total Tasks:** {count}
**High:** {count} | **Medium:** {count} | **Low:** {count}

### By Type:
- 📧 Email: {count}
- 💬 WhatsApp: {count}  
- 📁 Files: {count}

## Rules
- LLM call mat karo
- Auto-sort karo har 5 minute mein
- Duplicate tasks remove karo