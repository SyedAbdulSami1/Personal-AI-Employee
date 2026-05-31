---
type: email
from: Google AI Studio <googleaistudio-noreply@google.com>
subject: [Action Required] Migrate to Gemini 3.1 Flash Lite
received: 2026-05-12T08:56:18-07:00
priority: low
status: pending
watcher: GmailWatcher
---
## Content
The Gemini 3.1 Flash Lite Preview model will be discontinued on May 25,  
2026.







Hello Syed,

We're officially moving Gemini 3.1 Flash Lite available in Gemini API and  
Google AI Studio out of preview and into General Availability (GA).

Because of this transition, we'll be discontinuing the Gemini 3.1 Flash  
Lite Preview model on May 25, 2026. Any API requests sent to the preview  
model will start to fail after this date.

The GA version of the Service utilizes the identical underlying model  
architecture as the Preview version. Accordingly, no modifications to  
user-defined prompts or application logic are required for continued  
operation; the Customer need only update the model identifier string to  
gemini-3.1-flash-lite within the applicable API configurations.

For your reference, here is the project where you're currently calling the  
preview model:


gen-lang-client-0975020858

Ensure to point your application to the new GA model before May 25, 2026 to  
keep everything running.

If you have questions, visit the Gemini AI community or check out the  
Gemini API documentation.

Thanks for choosing Google AI Studio and Gemini API.




– The Gemini Team





© 2026 Google LLC 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA
This email was sent to samiwpp@gmail.com because you signed up to try the  
Gemini API and Google AI Studio.







## Suggested Actions
- [ ] Read and understand the email
- [ ] Determine appropriate response
- [ ] Draft reply (requires approval for new contacts)
- [ ] Move to /Done/ when complete
