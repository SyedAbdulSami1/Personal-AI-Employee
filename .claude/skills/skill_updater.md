# Skill: Skill Updater
## Trigger
Jab user koi naya kaam kare jo pehle nahi tha

## Steps
1. New task detect karo
2. LLM se ek baar solution lo
3. Solution ko steps mein todho
4. Nai skill file banao .claude/skills/ mein
5. server.py mein register karo
6. Next baar LLM call nahi hogi

## Example
User: "Website banao"
- LLM se pehli baar solution lo
- Steps: frontend_skill.md, backend_skill.md, database_skill.md
- Agle baar directly skills use hongi

## Rules
- Har naye kaam ki skill banao
- Skills folder mein save karo
- LLM sirf pehli baar call karo