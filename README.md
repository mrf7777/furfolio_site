# Glossary
| Term         | Definition                                                                                                                                                                 |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| User         | An agent that uses the application.                                                                                                                                        |
| Creator      | A user role that expresses that the user primarily creates offers and intends to fulfill commissions made from those offers.                                               |
| Commissioner | In the context of a commission, the one who initiated the commission.                                                                                                      |
| Commissionee | In the context of a commission, the one who fulfills the request defined by the commission and the customer.                                                               |
| Commission   | A request initiated by a commissioner directed towards a commissionee to fulfill requirements as defined by the commissioner and the offer associated with the commission. |

# Value
- Publish commissions.
- Automate commission managmenet.
  - lifecycle includes commission creation all the way to closure of commission
- Automate commission details gathering (with structured data?).
  - This is also achived agile-like with chat. Consider using chat instead.
- Facilitate communication between commissioner and commissionee

# Deployment notes
  - The digital ocean CDN seems to give a 417 error back when trying to upload any file. Using the orign endpoint is a workaround.

# Tasks
- [x] limit commissions per offer
  - [x] limit buyer commissions in review status
  - [x] consider making an exception for commissions by creator
- [x] resize avatar
- [ ] prevent deleted usernames from being taken again to prevent impersonation
- [ ] prevent spam accounts
  - [ ] consider recaptch v3
  - [ ] consider other approaches and tools
    - [ ] Email verification.
- [x] limit thumbnail aspect ratio and size
- [ ] guard against large uploads
  - [ ] consider dockerfile with nginx
- [ ] guard against spam
  - [x] cool down for all creates (priority)
  - [ ] cool down for all updates
- [ ] consider other storage and CDN options (low priority)
- [x] implement email for production
- [x] allow account disabling?
  - django already solved this

# Legal documents on website

## Terms of Service

### When is ToS accepted and how is it enforced
- account creation
- public use

### What happens when ToS is modified
- notify users via email

### Account creation
- content rating and age
- fabrication and fraud
- after banned account creation
- warnings
- bans
- avatar policy

### User created content
- service abuse
- spam
- links to 3rd party sites
- rating
  - definition of general
  - definition of adult
  - if unsure, use adult rating
- offer content
  - must be about a service, product, performance, or other item created and delivered by a creator.
    - anything else is not allowed
  - citations must be present
    - must abide by copyright law
  - duplicate offers only allowed if at most one offer is not closed
  - AI is prohibited
  - prohibited:
    - blogging
    - questions
    - updates
    - journalism
    - violation of copyright
      - Content that is not yours

### User conduct
- expected of users and non-user visitors
- regarding user-to-user interaction
- spam
  - overloading with file uploads
  - bots
- abuse
  - threats
  - harassment
  - stalking

### Limited Liability
- we are not responsible
  - but we do provide mitigation tools

### Enforcement
- community moderation and reporting
- user content
- user interaction
- staff perform actions to address reports

## Privacy Policy

### What happens when Privacy Policy is updated?
- email users

### handling of PII such as username and email address
- we do not distribute

### Cookies
- we use cookies for
  - the capture of your timezone settings on the device you use our site

# Convention space ideas.
- QR Code for artists to print for their table to show URL for query for their offers.
- QR Code for vending space which has URL for query for offers at the convention.
- Convention can have a landing page with some customization that is more friendly than a query page.
- Let people request commissions before vendors open via QR Code.
  - Let creators make offers that will publish in the future. (needs new field)
    - Let offers that are to-be-open still Publish but be closed for requests so that users can read about the offer beforehand.

# Offer price range

## iteration 1: use two fields for start and end.
- easy to implement regardless of database
- django supports out of the box the use of non-range types
- make min and max price mandatory
- cons:
  - manual implementation of interval intersection

# repatitive/reoccuring offers ideas
- use-cases:
  - a creator has a service that they open regurally
  - a creator usually provides only one or two services
- solutions:
  - template
    - reduces boilerplate
    - allows creator to draft an offer quicker
    - what about customization of cutoff time, thumbnail, etc.
      - do not store cutoff time and thumbnail in template
    - typing in cutoff time is time intensive
      - an offer template can store a duration rather than a cutoff time
    - should all fields be optional?
      - If yes, I like that since the creator does not have to 
      - If no, what if the creator does not want 

# buyer engagement
- buyer engagement encurages creators to engage too
- what would increse buyer engagement?
  - notified when creator creates offer
    - implement a "follow" system where users can follow creators
  - notified when offer has slots and is about to close ("about to" is different for different creators)
    - implement a "follow offer" system where users can track offers