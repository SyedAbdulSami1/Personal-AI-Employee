# Skill: Invoice Generator
## Trigger
Jab user "invoice banao" ya client name mention kare

## Steps (No LLM needed)
1. Client name aur amount input lo
2. Invoice template fill karo
3. /Vault/Invoices/ mein save karo
4. Approval file banao /Pending_Approval/ mein

## Output Format
Invoice #: INV-{date}-{client}
Client: {name}
Amount: ${amount}
Due Date: {+30 days}
Status: Pending Approval

## Rules
- Hamesha approval maango pehle
- Invoice number auto-generate karo
- Log karo /Logs/ mein