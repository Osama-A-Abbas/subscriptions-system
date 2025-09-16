# Reflection & Explanations  

This is a mix of self-reflection and explanations for certain parts of the project.

---

## Project Experience  

Working on this project was quite exciting. I wanted to make a few things clear, as the long documentation and hundreds of lines of code may not fully show.

---

## Why the Renewal Date Can Be in the Past  
…and why the Start Date can be in the past or future:

- **User perspective:**  
  If I were to use this kind of app, I’d want to be able to add my old subscriptions or subscriptions I may have in the future, with maximum flexibility.

- **Virtual-payments feature:**  
  This small feature calculates how many payments there will be for a subscription based on the `start_date`, `billing_cycles` (monthly/yearly), and the `periods` (how long).  
  It acts as a simple payments calculator—how much you will pay, how much you have paid, and so on.

  I know this feature still needs improvement, but I chose a scalable approach and decided to go with it.  
  Restricting renewal dates from the past would disable this extra functionality.

---

## What I Would Improve If I Had More Time  

- Integrate the app with real subscriptions and services.  
- Improve the subscription plans comparison to suggest detailed saving plans.  
- Create a standalone app for easier usage.

---

## AI Usage and AI Tools  

- I used **ChatGPT** extensively to help with idea filtering, problem-solving, brainstorming, and general coding/project assistance.  

- I used **Cursor** as my main IDE.  
  The Cursor AI enabled me to accomplish this project within three days.  
  I would often plan entire features in detail for it to build step by step.  
  I would then do the steps myself—creating files, pasting code blocks, and reviewing everything—which gave me a deep understanding of the project.

- To be honest, at some points I was short on time but full of ideas, so I focused on planning, reviewing, and analyzing progress while it handled the coding part.

- One small note: it cannot fully fix Django template syntax.

---

## Final Thoughts  

Either way, it was a fun journey 👌
