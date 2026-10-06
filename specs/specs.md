# TARGET
Build an application that helps an agent to process customers tickets.

## Context
The customer support team receives a large number of free-text support requests.
They want a small internal application that helps support agents classify incoming requests and draft a suggested answer using an AI service.

# Requirements
## Functional requirements
UI is friendly and intuitive
Frontend support followings use case :
- List of tickets is displayed on UI
  - One row per ticket
- User can filter tickets based on tickets attributes
- User select a ticket that is fully displayed
- User may acquire the ticket in order to process it
- User submit ticket acquired ticket
- User may reset UI state

## Technical requirements
### BACKEND
- All business logic is processed into backend
- FastAPI
- a working health endpoint;
- basic project configuration.

### Tickets structure
The allowed values for `category` are:

```text
billing
technical
account
other
```


The allowed values for `priority` are:
```text
low
medium
high
```

A ticket has the followings attributes
- A unique ID
- UserID in charge of ticket processing
- Priority
- Category
- Updated text issued from AI text generation
- A state among :
  - pending
  - reviewed
  - processing
  - closed

### FSM transitions
- pending -> reviewed
- reviewed -> processing
- processing -> closed
- pending -> pending
- reviewed -> reviewed
- processing -> processing
- closed -> closed

### FRONTEND
- React + TypeScript
- Vite for tooling

### API

```http
POST /backend/api/triage : classify incoming requests and draft a suggested answer using an AI service
GET  /backend/api/tickets : get the list of tickets from backend
POST /backend/api/update : submit a ticket with its updated state
POST /backend/api/filter : send filter parameters and return the list of filtered tickets
```
### SCOPE
- check along with `scope` skill

# Acceptance criterias
- Check along with  `dod` skill

