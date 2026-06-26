# Decisions

Hello hello

The most important issue in the backloog should be FR-002
There are no returns, without a working return flow.

I've decided to use a different ticket although, to get familiar with the project first.

- Decision: Starting with BR-001 · Complete the mapper gaps
- Rationale: Before I start adding things, I will have a look at what is there and what was the intention behind the code

I've updated the test fixtures to be more alligned with the order data provided.


- Decision: Next issue handled is SEC-001
- Rationale: It's a simple win
- Info: I've decided to add an aditional validation in the api and leave the service as is,
in case that the function will be used from a different place, for example for an "admin" or different user with the right permissions.
    Update: the API seems to not be used at all in this implementation.
    For now I will be using Django.

TODO: check if the API endpoints are required / in use by 3rd party app - before cleanup.
If the api endpoints are needed, I would move the validation logic to a service, and use that for both the htmx implementation and API.



- Decision: Next isssue handled is FR-002
- Rationale: There are no returns, without a working return flow - completing this seems the highest priority.
As the project is using htmx, I will stay, for now, in the same coding style.
Using django form for validation to not dupllicate it in javascript, as much as possible.
Alternative would have been to handle the frontend changes in javascript files - as I didn't worked with htmx/alpine before, I'm not sure what are the best practices, but from the looks of it, it's straight forward to create components controlled from the django view. For now I will focus on having a working solution first.

The other ticket that is on the top of the list, is the eligibility functionality.
As there is already a "working" solution for flow, I've decided to handle it after.


TODOs left:
- implementation of the return service: delivery vendor call, any additional return logic needed.
- implementation of the steps to handle the return (instructions PDF)
- implementation of the email notification

For the above I would need more information about the delivery vendors setup.
It would be interesting if there is an option to automatically select specific vendors based on the weight of the package (for example).
Return cost handled by the merchant or by the user? Would this depend on the Loyality Tier?


- Decision: Next issue handled is FR-001, looks like a fast win and it will be great to have the overall feedback of the UX at once. 
TODO: check (before the actual implementation) the KPI related to this feature, and what should be tracked and measured.





- Eligibility:

I've assumed that the categories provided with the orders are already mapped to some meta categories provided by parcelLab.
Based on this I was thinking to have 2 types of rules:
1. default rules that are controlled via OPS / are univerally available for all merchants
2. custom rules that the merchants can set based on: country, category, loyalty tiers

Maybe I got a bit too complicated with all the rules and regulations.
I had the idea to handle the following cases, in this specific order:
1. rules that block return by default - customization, perisable, opened consumables
2. rules that allow returns by default - a minimum period, based on country
3. merchant level customization - loaded via an api or local admin
4. loyalty tier - available just for the merchants that offer this
5. custom rules: for example high return rate. Although I dont think that it has a legal basis, and I've changed my mind with this one - maybe it's better handled at purchase event.

I've added some template rules in data/eligibility_rules_raw.json

The branch is not merged as I don't feel that is something that I will deploy
I still have to add tests and review the rules, and review that code a bit more.

I wanted to provide this also, as it was work in progress.



