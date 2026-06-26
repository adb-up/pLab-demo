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
