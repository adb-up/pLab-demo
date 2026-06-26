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
in case that the function will be used from a different place, for example for an "admin" or 
different user with the right permissions.