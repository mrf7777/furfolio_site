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
    - [x] honeypot
- [x] limit thumbnail aspect ratio and size
- [ ] guard against large uploads
  - [ ] consider dockerfile with nginx
- [x] guard against spam
  - [x] cool down for all creates (priority)
- [ ] consider other storage and CDN options (low priority)
- [x] implement email for production
- [x] allow account disabling?
  - django already solved this
- [ ] beta release features
  - [x] separate chat
  - [ ] notifications instead of emails
  - [ ] trouble ticket system
  - [ ] (optional) transparent commission for self-managed commissions
  - [ ] (optional) client-size file upload size detection

# search ideas

## tags
- what would be a good ontology for the tags?
- senses -> medium -> product -> properties/specifics
  - senses: physical, visual, audio, gustatory, olfactory, informational
  - medium: digital_art, digital, clothing, body_suit, pencil, pen, stretch_fur, clay, silicone, wax, acustic_insturments, 
  - product: fursuit, full_fursuit, partial_fursuit, character_portrait, song, asmr, background_music candle, perfume, video_game, website, essay, cookies, comic_strip, manga, animation, video
  - implications: full_fursuit -> fursuit, character_portrait -> digital_art, digital_art -> digital, digital_art -> visual, fursuit -> clothing, clothing -> physical
  - properties: male, blue, red, tall_character,
- what about use intention (business, personal, charitable, etc.)
  - most artists on the platform would not care
- 
- senses -> medium -> (function/role + product)
- tag implication models
  - Tag
  - Implication(Tag, Tag)
- what about models for implications that require 2 or more tags to be present?
  - Tag
  - Implication(consequent: Tag)
  - ImpicationAntecedent(implication: Implication, tag: Tag)
  - assume implication a, b -> c (a and b together implies c), how do we resolve implication?
    - Implication.objects.filter(implication_antecedent__tag=a).filter(implication_antecedent__tag=b).distinct()

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
  - for disputes between you and others

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
- What about offers that have the same name? How to distinguish?
  - What we have: cutoff date, created date,
  - can simply add time till closing. simple.

# buyer engagement
- buyer engagement encurages creators to engage too
- what would increse buyer engagement?
  - notified when creator creates offer
    - implement a "follow" system where users can follow creators
  - notified when offer has slots and is about to close ("about to" is different for different creators)
    - implement a "follow offer" system where users can track offers

# public events
- commissions can be at a high during an in-person convention
- creators congregate at a convention
  - they are marketed together as the convention published the dealers and artists
- having a landing page for a public event would help engagement with the platform
- if demand from creators and buyers is high, provide a B2B solution for cons to manage commissions.
- another search vector to find offers faster
- CRUD
  - Create
    - Who has the authority to publish an event?
    - Maybe just let the event organizer contact an admin and then verify the contact.
  - Read
    - Have an event page with ongoing events.
  - Update
    - Contact an admin
  - Delete
    - Ideally, should never happen. Events should simply "expire".
- How can a creator make offers to associate with an event?
  - Make event organizer provide a list of legitimate furfolio users who can add offers to the event.
- use-cases:
  - need to search for offers at convention or event
  - need a landing page to put context around the offers
  - event organizer (EO) manages an event
  - creators publish offers that are affiliated with the event
  - EO hard-limits number of offers (ever) to be associated with event.
    - open and closed offers should count!
    - by limiting offers per creator per event, clutter can be managed
  - EO limits number of offers per creator
    - definitely a later feature under subscription

## event implementation ideas

### iteration 1

- 

# monetization ideas

## subscription
- provide lax limits and extra features
  - up active offer limit
  - up max in review per offer limit
  - up max number of offer templates
  - ability to associate offers to certain events
  - ability to manage events

# search design
- there are many things a user, based on role, would want to search with
- buyer
  - offers
    - text
    - price min and max
    - user
    - date created
- creator
  - offers
    - active
  - commissions
    - state
    - offer
    - sort
    - filter

## commission search design
- single search bar
  - examples
    - search for commissions from offer
      - offer:22
    - search rejected commissions of offer
      - offer:31 state:rejected
    - search for in progress or accepted commissions
      - state:in_progress state:accepted
    - search for all commissions sorted by created date in desending order
      - sort:created_date order:desending
    - search for commissions where user "test" is the commissioner
      - commissioner:test

# emails vs in-app notifications
- emails
  - pros
    - simply just works for notifications
    - readable by 3rd party software
  - cons
    - costs for high-volume transactional emails
    - flooding of inbox
    - spam filtering issues
- in-app notification
  - pros
    - much cheaper than email
    - not prone to 3rd party spam
    - CRUD on notifications as objects
    - does not clutter email inbox
  - cons
    - does not immediately notify user
    - user has to sign-in to see notification

# creating requirements per offer
- what about offer templates if those are a thing

# ToS creation 
- allow user to create ToS as a separate object
- encourage new creators to create a ToS as their first step.

# trouble center it1
- trouble ticket
  - a trouble ticket is for users to submit requests and resolve conflicts
    - what kind of problems?
      - forgot password
      - change username
      - report breach of ToS by another user
      - report abuse