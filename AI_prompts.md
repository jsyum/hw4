# AI_prompts.md

A word-for-word log of what I typed to the AI assistant while building this project.
Prompts are copied exactly as sent — typos and all. Nothing here is read at runtime; it
is a record, not configuration.

**Each section has:**

1. The problem number and title
2. At least one prompt I typed
3. A follow-up prompt *only if one was needed*, with a brief note on what the first
   prompt was missing

A section with a single prompt and no follow-up means that prompt was enough on its own.

---

# Setup

*2026-10-06 — 2026-10-07*

The context I gave before any of the numbered problems began.

**Prompt 1**

> We will be working in the Assignment 4 folder in the AI foundations folder. Please create a .env file there.

**Prompt 2**

> Context
> We will be working in the Assignment 4 folder in the AI foundations folder.
> I am starting on a new project.
> For context, here is the scenario. We’re building a customer facing website for Yale merchandise for Campus Customs. We will use React + Vite + TypeScript frontend and a Python FastAPI backend with a PydanticAI agent powering the chatbot. I’ll use my own Anthropic API key for the agent, stored in a .env file.
> Customers should be able to browse merchandise, create an account, and chat with the chatbot assistant about products. The chatbot should be able to provide true (not invented!) answers using information from the local database about product information such as inventory and prices. If something isn’t in the database, it should say so rather than guess.
> The data is in a data/ folder. Study the database schema before making any queries.
> The project will be published to a public GitHub repo so it is very important that the .env file is never committed and the API key is not hard coded anywhere. A .gitignore already exists which excludes .env. We will need to add to the .gitignore file (without replacing anything) since the database and product images must never be committed., so add data/ to .gitignore.
> Other than the .gitignore edit don’t build anything yet. We’ll work through the problems one at a time.

---

# Problem 1: Vibe coder prompts

*2026-10-07*

**Prompt 1**

> This is for Problem 1: Vibe coder prompts
> First create AI_prompts.md in the Assignment 4 folder and keep it updated as I go along. This file will be a word for word log of only what I typed to you, the vibe coder. Every time I give you a prompt, add it to AI_prompts.md word for word before doing any work. There should be one section per problem. Each section should include the problem number and title, at least one prompt I typed to you, and one follow-up prompt if I needed it (with a brief explanation of what was lacking from the original prompt). You can log this prompt under Problem 1: Vibe coder prompts. Also add my earlier setup/context prompt at the top under a “Setup” section before the real problems begin.

---

# Problem 2: Analyze the database

*2026-10-07*

**Prompt 1**

> This is for Problem 2: Analyze the database
> Analyze the database at data/campus_customs.db. Inspect the database schema and understand the tables, how the tables relate to each other, and the fields it contains, especially the catalogue, inventory, and users tables. Throughout the duration of this project and in general, the database is the source of truth so do not assume or invent any fields or values.
> Create output/harness.md and document:
> 1) Each relevant database table, including, at a minimum, catalogue, inventory, and users
> 2) Every field/column in each table
> 3) For each field, write one concise clear sentence explaining what the field represents and why it matters for the customer facing shop and/or the AI chatbot.
> Keep the documentation concise and easy to read.
> This harness.md file will be expanded in later problems so structure it in a way that makes it easy to add additional sections later. Because this will be a public repo, do not copy any actual user data like emails or password hashes into harness.md.
> You are only analyzing and documenting data from the database, not altering anything about the database or data.
> And do not build later parts of the project yet. We will work through problems one at a time.
> Log this prompt in AI_prompts.md under Problem 2: Analyze the database.

---

# Problem 3: Build the Campus Customs website

*2026-10-07*

**Prompt 1**

> This is for Problem 3: Build the Campus Customs website
> In this problem, we will build the customer facing Campus Customs website.
> We will use React + Vite + TypeScript for the front end.
> Create a navigation bar at the top of the site that links to these main pages: Home, Products, About Us, Log In, and Create Account. Log In and Create Account can just be placeholders for now. We’ll add functionality in a later problem.
> Research yalebulldogblue.com for general context/content for the Home and About Us pages. Text should be in your words, not taken directly from the original site.
> Build a Products page using the actual product information from data/campus_customs.db. The database remains the source of truth so do not invent any product information.
> Display the product images using the image paths provided in the catalogue table. Each product card should show the product’s image, name, price, and short description. Each product card should be clickable and open the single-item’s product page. The item’s page should have a large product image on one side and the full product information on the other (including description, price, sizes, stock as available in the database).
> Add a chat interface in the bottom right corner of the site. A floating chat panel is fine. For the current problem 3, this is only the front end interface. It does not need to communicate with the PydanticAI agent yet. Create an appropriate stub/placeholder that can be connected to the backend later.
> Since the frontend needs to read product information from the database, create the API backend needed for this problem. You may start a simple FastAPI application in backend/main.py that serves the products and their images. Keep this backend structured so it can be expanded into an agent backend in later problems.
> Implement only what is required for Problem 3. Don’t build the PydanticAI agent or later functionality yet. We will work through the problems one at a time.
> Make sure the application runs correctly so far at its current stage. For example, make sure pages navigate correctly, the Products page and the individual product pages work and load correctly from the database.
> When you’re done, tell me how to start the backend and frontend so I can check the site myself.
> Log this prompt in AI_prompts.md under Problem 3: Build the Campus Customs website

---

# Problem 4: Create Account and Login

*2026-10-07*

**Prompt 1**

> This is for Problem 4: Create Account and Login
> In this problem, make the Create Account and Log In functionality of the Campus Customs website work with the existing users table in data/campus_customs.db.
> Set up a standard Create Account process with a form that collects first name, last name, email address, password, and a confirm password field. When a user creates an account, store the new account in the existing users table. Follow the actual database schema again without inventing fields.
> Passwords must be stored securely. Never store plaintext passwords in the database. Use secure password hashing compatible with the existing database and make sure the login/authentication can correctly verify the password hashes in the seed database.
> Set up a login process using email and password. The backend should find the appropriate user and verify the entered password against the stored password hash. A valid email/password combination should successfully log the user in while invalid credentials should be rejected with a message like “invalid email or password.” Also reject account creation if an email has already been registered (to prevent duplicate accounts) and check that the password and confirm password match.
> Also after logging in, there should be some indication in the nav bar that the user is logged in (perhaps with their name and a link to log out).
> Don’t unintentionally send private information like the password hash to the frontend.
> The seed database already contains this test user:
> Email: test@campuscustoms.yale.edu
> Password: password
> Test that this existing user can successfully log in.
> Also create a brand new account through the Create Account process that was set up and confirm that the new account is stored correctly and can log in successfully.
> Update output/harness.md with a concise explanation of how authentication works, including what information is stored for a user and how passwords are protected. Just add to the harness document, don’t replace any existing content in harness.md.
> Implement only what is required for Problem 4. We will work through the problems one at a time. Make sure the functionality implemented in previous problems continues to work and check that the application still runs correctly after these changes.
> Log this prompt in AI_prompts.md under Problem 4: Create Account and Login

---

# Problem 5: PydanticAI agent backend

*2026-10-07*

**Prompt 1**

> This is for Problem 5: PydanticAI agent backend
> In this problem, build the Campus Customs online store chatbot as a PydanticAI agent behind the existing FastAPI backend and connect it to the chat interface that we created in Problem 3.
> Keep the FastAPI application in backend/main.py. This should still be the file used to run the backend with Uvicorn. Keep the existing product and authentication functionality from previous problems.
> Structure the agent using these files next to main.py: backend/prompts/prompt.md (the agent’s system prompt), backend/agent.py (the PydanticAI agent entry/wiring), backend/tools.py (tools the agent can call), backend/models.py (Pydantic/PydanticAI structured types)
> In backend/prompts/prompt.md, create the initial system prompt for the chatbot. Give it an appropriate Campus Customs voice and basic safety instructions. As a reminder the agent should never invent prices, stock, or product details, as these should come from the database. If it can’t look something up, it should say so. This prompt file will be expanded in later problems, so structure it in a way that is easy to extend.
> In backend/models.py, create or update the structured types needed for chat replies and product cards.
> In backend/main.py, expose a chat route that accepts a message from the website, sends it to the PydanticAI agent, and returns the agent’s reply and any other necessary structured information to the frontend.
> Connect the existing frontend chat interface to this route so the shopper can send a message through the website and receive an actual response from the PydanticAI agent.
> Use my Anthropic API key for the agent stored in .env with a Claude model (tell me which model you chose). By the way, do not hard-code API keys.
> Update output/harness.md to document how the frontend communicates with FastAPI for chat, and how the PydanticAI agent is loaded (including the prompt file and model).
> Add this information to the existing harness.md. Do not replace or remove any documentation from previous problems.
> Make sure the backend can be run from the backend/ directory with “uvicorn main:app --reload --port 8000”
> Since the backend will run from the backend/ folder, make sure the database and .env file are found correctly.
> Implement only what is required for Problem 5. We will continue working through the problems one at a time.
> Make sure the application still runs correctly after these changes and that the functionality of the implementations in previous problems still work. Verify that the frontend can successfully send a chat message through FastAPI and display the PydanticAI agent’s response.
> Log this prompt in AI_prompts.md under Problem 5: PydanticAI agent backend

---

# Problem 6: Tools: product info and stock

*2026-10-07*

**Prompt 1**

> This is for Problem 6: Tools: product info and stock
> In this problem, you will give the Campus Customs PydanticAI agent tools that allow it to look up real product information from data/campus_customs.db. The tools should read only from the database and never modify it.
> Add the appropriate tools to backend/tools.py. These tools should allow the agent to retrieve from the database the product descriptions, prices, current stock quantities (including stock by size when the customer asks about a particular size).
> The agent must use the database for questions about product information, prices, and stock rather than inventing or assuming this information. The tools should let the agent find products by name or description like “blue hoodie” or “bulldog hat.” If several products match, the agent should ask the user which one they mean. If there’s no match, the agent should say so. If a requested size is out of stock, the agent should clearly tell the customer that it is out of stock.
> Use the database schema established in the earlier problems and do not invent database fields, product, prices, sizes, quantities, or other product information. The database is the source of truth for customer questions.
> Add to backend/prompts/prompt.md so the agent knows when to call these tools, especially for product information, price, and stock questions. Preserve the previous Campus Customs voice and safety instructions.
> Add or update the Pydantic/PydanticAI structured return types in backend/models.py for the lookup results as needed.
> Update output/harness.md by adding a section for Problem 6 that lists each tool you plan to provide to the agent, explain what each tool does, and list the model fields you chose for the lookup results and briefly explain why you chose those fields.
> Preserve all existing content in output/harness.md (add to it rather than replacing anything).
> Then implement the tools and connect them to the existing PydanticAI agent so they can actually be called during customer conversations.
> Test the agent with product information, price, stock, and size stock questions and confirm that the answers reflect the actual database values and not invented information. Include a test where a product is not in the catalogue and one where the requested size is out of stock.
> Implement only what is required for Problem 6. We will work through the problems one at a time.
> Log this prompt in AI_prompts.md under Problem 6: Tools: product info and stock

**Prompt 2** *(follow-up)*

> yes fix it. Just don't invent descriptions. When a description is a placeholder, hide it or show something neutral like "Details coming soon" on the cards and detail pages.

*What the first prompt was missing: Problem 6 scoped the work to the agent's tools, so
the fix for placeholder descriptions only reached the chatbot. The storefront pages built
in Problem 3 were still printing the raw `"Vision blocked; filename-based stub"` text on
the three affected products. This follow-up extended the same fix to the website.*

---

# Problem 7: Chat search that updates the page

*2026-10-07*

**Prompt 1**

> This is for Problem 7: Chat search that updates the page
> In this problem, make the Campus Customs chatbot capable of searching for products based on the customer’s chat request and dynamically displaying the matching products on the website.
> For example, if a customer asks the chatbot “What hoodies do you have?” the agent should search the actual product catalogue in data/campus_customs.db and return the matching products. As a reminder, do not invent products or product information.
> The agent should return the product matches as structured data through the existing FastAPI chat API rather than just mentioning the products in its text response. Include the necessary information needed for the frontend to render each matching product as a product card (including its image, name, price, and short product information) using the actual database fields and image paths. The product card should come directly from the database results, not written by the agent.
> Update the frontend so when the chat API returns matching products, the website dynamically displays those matches as product cards on the main area of the page. Also when a customer clicks a card and opens its product page, the chat conversation should persist and stay intact.
> Preserve the single item product behavior implemented in Problem 3. Each dynamically displayed product card should be clickable and should open the large image and full product information.
> Update backend/prompts/prompt.md so the agent knows when and how to perform product searches and return product matches for the frontend. Add to the existing prompt rather than replacing previous instructions
> Update output/harness.md with a concise explanation of how product search results travel from the agent through FastAPI to the frontend and become dynamically rendered product cards. Preserve all the existing harness content and just append to the file rather than replacing anything.
> Make sure the functionality from the previous problems continues to work. Test the complete pipeline by making product search requests, verifying that the correct database backed product cards dynamically appear on the page and that clicking those cards opens the correct individual pages.
> Implement only what is required for Problem 7. We will work through the problems one at a time.
> Log this prompt in AI_prompts.md under Problem 7: Chat search that updates the page

---

# Problem 8: Customer memory

*2026-10-07*

**Prompt 1**

> This is for Problem 8: Customer memory
> In this problem, add customer memory and context to the Campus Customs chatbot.
> When a shopper is logged in, save their chat history in the database in an appropriate table associated with that user. When the same user returns, reload their saved chat history so their previous conversations persist. Guests should still be able to use the chatbot but the chat history only needs to persist in the database for logged in users.
> When a shopper is logged in, make sure the PydanticAI agent knows who is chatting (including the customer’s name and email address). Pass this info to the agent using agent dependencies (deps) or an equivalent clear PydanticAI pattern. Use the actual logged in user information from the database rather than inventing customer information.
> This is for privacy. Determine the logged in user on the backend, not from a user ID or email sent by the frontend, so no one can load another customer’s chat history. The agent should only see the current user’s information.
> Pass enough information about the shopper’s current page to the agent that it can understand contextual references. For example when a shopper is viewing an individual product page and asks something like “do you have this in pink?” the agent should know which product “this” refers to. In other words, pass the relevant current page/product context into the agent rather than requiring the customer to repeat the product name explicitly.
> Preserve the functionality from previous problems such as the authentication, product search (price, inventory, etc.) and chat.
> Update backend/prompts/prompt.md so the agent knows how to appropriately use the available customer, conversation, and page context. Just add to the existing prompt rather than replacing any previous instructions.
> Update output/harness.md to document how and where logged in users’ chat history is stored, how saved chat history is associated with a user and reloaded when they return, which customer fields the agent receives, how customer info is passed to the agent, how current page/product context is passed from the frontend to the agent.
> Preserve all existing content in output/harness.md (just add to this documentation rather than replacing any previous sections).
> Test the complete flow. Confirm that a logged in user’s chat history is saved and restored, that the agent receives the correct logged in customer information, that guests can still chat without requiring persistent history, and that contextual questions from an individual product page are interpreted correctly and refer to the correct product. 
> Implement only what is required for Problem 8. We will work through the problems one at a time.
> Log this prompt in AI_prompts.md under Problem 8: Customer memory

---

# Problem 9: Usability Improvements

*2026-10-07*

**Prompt 1**

> This is for Problem 9: Usability Improvements
> Before building anything, review the current code and tell me which of these ideas are already implemented (partly, fully, not at all). And let me know if you have smart creative ideas to add. Don’t build anything yet.
> Front end improvements:
> 1. Filter and sort. Let customers filter by category or price or sort by price (low to high or high to low).
> 2. Search bar on the Products page, so customers can search without using the chatbot.
> 3. Put stock related badges on product cards like “in stock,” “low stock,” “out of stock.”
> 4. Recently viewed products. Show customers products they’ve looked at recently.
>  
> Backend improvements:
> 5. Suggest in stock alternatives. If something is out of stock, the agent will find and suggest a similar in stock product.
> 6. Conversation summarization. Compress older chat history so persistent conversations use fewer model tokens (faster/cheaper).
> 7. Skip the LLM for deterministic requests. Handle stuff like direct product retrieval through normal API and database logic when AI reasoning isn’t needed (eliminates a model call).
> 8. Use a smaller model for simple requests. Route easy requests to a cheaper/faster model and harder requests to the stronger model (reduces token/model cost).
> 9. Parallelize independent tool calls. Combine related database queries, like retrieving description, price, and inventory in one query when appropriate. If price and stock require independent lookups for example, retrieve them concurrently. Reduces latency and fewer database round trips
> 10. Use SQL for filtering instead of the LLM. For example WHERE price < 50, etc., rather than giving the catalogue to AI and asking it to filter (faster and cheaper). SQL does the searching and AI does the understanding.
> 11. Set sensible output limits. Keep ordinary shopping responses concise (uses fewer output tokens).
> Log this prompt in AI_prompts.md under Problem 9: Usability Improvements

**Prompt 2**

> This is for Problem 9: Usability Improvements (continued)
> Implement these two front end and two backend usability improvements:
> Front end 1: Filter and sort on the Products page (by category and price, sort by price low to high and high to low)
> Front end 2: Search bar on the Products page
> Backend 1: Fix the cheapest-item bug by adding price filtering and sorting to the agent’s search tool in SQL. Use shared product query logic so the Products page and the chatbot always agree.
> Backend 2: Route simple requests to a smaller, cheaper model and harder ones to the stronger model.
> As the improvements are implemented, concisely explain in output/usability.md what was added and why it helps a shopper or the business. Make sure each implementation shows up in the running app. And make sure to preserve functionality of all previous problems.
> Log this prompt in AI_prompts.md under Problem 9: Usability Improvements

---

# Problem 10: Style the website

*2026-10-07*

**Prompt 1**

> This is for Problem 10: Style the website
> I want the page to look like a classic university library late at night, with Yale blue as the primary color with warm accents like wood color or gold. Maybe there could be some architecture pieces like a window with a starry night for example.
> Add some bulldog touches but don’t use external images or any official Yale logos for example. Create original bulldog and paw illustrations in SVG for example. It would be cute if the cursor were a paw print with two states (normal browsing one, and then a different one when hovering over clickable things). Maybe there could be a lamp-like glow when hovering over a product card. The chat box could be like a reference desk with “Ask the Librarian” and maybe the chatbot’s avatar could be a bulldog wearing glasses. And maybe there could also be a line that says “Open late. Ask the librarian any time.” When the chatbot is not being used, the avatar should switch to sleeping and it should change to the awake bulldog when being used. Also, maybe when the agent is “thinking” there could be some kind of paw print walking effect like how chatbots sometimes display ellipses when they are “thinking.”
> If products are out of stock, restyle with “Checked out” stamps over them, going along with the library theme.
> In output/design.md, concisely write what changed and why it helps customers stick around and buy.
> Make sure that all functionality from previous problems still works after the redesign and also verify that the new design elements are displaying correctly.
> Implement only what is required for Problem 10. We will work through the problems one at a time.
> Log this prompt in AI_prompts.md under Problem 10: Style the website

**Prompt 2** *(follow-up)*

> This is for Problem 10 (continued):
> Here are some refinements upon seeing the site that were lacking in my last prompt. I feel the chatbot is too subtle. Maybe make it a bit larger and also can you make a lamp light animated effect that fades in an out to draw attention to the chatbot button? Also, could you have little animated Zs that come out of the chatbot button when he is sleeping/not currently utilized? 
> Also on the Home page where it says “Open late. Ask the librarian anytime.” Maybe that could trigger the chatbot opening. 
> Also could you put the prices in small brass plaques?
> Also maybe the top navbar could have an explicitly wood-looking background?
> And please remove the footer that says this is a build for MGT 409 and that it’s not a real shop. 
> Also update output/design.md with a description of what you changed and why it helps customers stick around and buy. 
> Log this prompt in AI_prompts.md under Problem 10: Style the website

*What the first prompt was missing: it described the theme but not the weight each
element should carry. Seeing it built showed the reference desk read as decoration
rather than an invitation, the "Open late" line looked clickable but wasn't, and
prices and the navigation were still generic dark-mode surfaces rather than the
brass and oak the rest of the room was made of.*

---

# Problem 11: Site testing (app check)

*2026-10-07*

**Prompt 1**

> This is for Problem 11: Site testing (app check)
> Test the actual running Campus Customs site and document the results in output/app_check.html.
> Include clear screenshots and captions for these three checks (Use a browser such as Playwright to open the running site, perform each check, and save the screenshots):
> 1. Use the chatbot to check the inventory level of an item and demonstrate honest and factual stock/price information from the database.
> 2. Ask a category question (e.g. “What hoodies do you have?”) and show the dynamic search result product cards appearing on the page
> 3. Demonstrate one of the usability features implemented in Problem 9:
> In particular demonstrate the filter and sort feature from Problem 9. Show the Products page filtered to hoodies and sorted low to high, alongside the chatbot’s answer to “What’s your cheapest hoodie?” So the two visibly match. 
> Actually test each feature in the running application and capture screenshots showing that it works.
> Make app_check.html easy to grade. For each check, include a clear heading, the screenshot, and a concise explanation of what the screenshot proves. For the inventory check, also show the matching values from the database next to the chat screenshot so a grader could see that the answer is indeed accurate.
> Save the screenshot image files in output/app_check_images/ and link them from app_check.html using relative paths such as app_check_images/inventory.png. Make sure the screenshots display correctly when app_check.html is opened.
> Make sure to preserve the existing application and all functionality from previous problems.
> Log this prompt in AI_prompts.md under Problem 11: Site testing (app check)

---

# Problem 12: Audit trail, safety, finish harness

*2026-10-07*

**Prompt 1**

> This is for Problem 12: Audit trail, safety, finish harness
> In this problem, complete the audit trail, agent safety rules, and final output/harness.md documentation.
> For the audit trail, create and maintain an add-only output/audit_trail.json file that records agent activity. Each record should include time, tool name, arguments/result, stop reason. Keep the arguments and results concise and don’t record customer emails, names, chat content, password hashes, API keys, etc. since this will be a public repo. The audit trail will be append only so do not wipe, overwrite, or reset between runs.
> For safety, add appropriate safety rules for the Campus Customs agent to backend/prompts/prompt.md. Add these rules to the existing prompt without removing or replacing any of its current content. Some example safety rules: never invent prices, stock information, or products; never reveal another customer’s information or API keys; stay on Campus Customs topics and kindly redirect truly off-topic requests (maybe apologize for not being able to answer them).
> Regarding finishing the harness, complete output/harness.md so that it clearly explains how the final application works. Make sure, if it doesn’t already, that it documents the model fields in backend/models.py and why each was chosen, the agent’s tools, the agent’s safety rules, and other specifications like agent loop limits (max tool calls per message), result caps (max number of products a tool returns), models used, and how to run both the frontend and the backend. By the way if the loop limits or result caps aren’t implemented yet, please add them before documenting them.
> Preserve all the existing content in output/harness.md and update it as needed so it reflects the final implementations.
> Make sure that the functionality from previous problems is preserved and that the application still runs correctly after all these changes. Send a few chat messages and confirm that new entries appear in audit_trail.json without erasing earlier ones.
> Log this prompt in AI_prompts.md under Problem 12: Audit trail, safety, finish harness

---

# Problem 13: Push to GitHub and submit the URL

*2026-10-07*

**Prompt 1**

> This is for Problem 13: Push to GitHub and submit the URL
> Before you work on this, please log this prompt in AI_prompts.md under Problem 13: Push to GitHub and submit the URL
>
> Please prepare the project for submission and make sure the files are organized according to this file tree. This is so that the project can conform to a required structure and be easy to grade. Compare the existing project against this layout, create and organize anything missing. Also the Assignment 4 folder is the hw4/ root. Don’t rename or move it. Name the GitHub repo hw4.
>
>
> hw4/
> ├── AI_prompts.md
> ├── requirements.txt
> ├── .env.example
> ├── .gitignore
> ├── README.md
> ├── frontend/          # Vite React TypeScript app
> ├── backend/
> │   ├── main.py        # FastAPI app, run with: uvicorn main:app --reload
> │   ├── agent.py
> │   ├── models.py
> │   ├── tools.py
> │   └── prompts/
> │       └── prompt.md
> └── output/
>     ├── harness.md
>     ├── design.md
>     ├── usability.md
>     ├── app_check.html
>     ├── app_check_images/   # screenshots linked from app_check.html
>     └── audit_trail.json
>
> Local-only data pack (not in git):
> data/
> ├── campus_customs.db
> └── products/          # images referenced by the catalogue
>
>
> Treat the data/ folder as local only and do not commit it. Make sure .gitignore excludes the real .env, data/campus_customs.db, and data/products/product images. Do not delete the local files. Just keep them out of git. 
> Make sure .env.example has placeholder values only and no real API keys or secrets.
>
> Make sure README.md clearly explains how to run the frontend and backend after placing the local data pack in the appropriate location. 
> Before pushing, verify that no real .env, database file, product images, or API keys are included in the commit. 
> Make sure AI_prompts.md is up to date with this prompt before pushing. 
> Then commit the completed hw4 project and push it to a public GitHub repository. When finished, give me the public Github repo URL that I should submit on Canvas.
