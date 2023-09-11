# Glossary
| Term         | Definition                                                                                                                                                                 |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
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

# Tasks
- [ ] Offer CRUD
  - [ ] Fields support
    - [ ] Price range
    - [ ] Description
  - [x] Create
    - [x] Can create offer
  - [ ] Read
    - [x] Card list view of offers
      - [x] Styled?
    - [x] Can read offer details on one page
      - [ ] Styled?
      - [x] Signed in author sees link to update details
  - [ ] Update
    - [x] Author can access an update offer page
    - [ ] Styled?
  - [x] Delete
    - [x] Author can click a delete button

- [ ] User CRUD
  - [ ] Read
    - [x] User public profile page
    - [ ] Styled?
  - [ ] Create
    - [x] User sign-up
    - [ ] Styled?
  - [ ] Update
    - [ ] Update email
    - [ ] Update profile picture
    - [ ] Update user page description
    - [ ] change password
    - [ ] Styled edit page?
  - [ ] Delete
    - [ ] User can delete account.
    - [ ] Styled delete?

# Notes
## iteration 1 of offer modeling
- Offer fields ideas
  - name
  - description
  - thumbnail NULL
  - cutoff date

- Suboffer fields ideas
  - name
  - description
  - thumbnail NULL
  - turnaround time NULL
  - min price NULL
  - max price NULL

## iteration 2 of offer modeling
- Offer
  - name
  - description
  - event NULL
  - thumbnail NULL

- CommissionField
  - offer references Offer
  - name
  - request (a question or a resource that the commissioner must provide)
  - type : singe-line-text, radio enum, file, datetime, boolean, number
  - optional bool

- CommissionFieldEnumChoice
  - commission_field references CommissionField
  - text

- Commission
  - commissioner references user
  - commissionee references user
  - offer references Offer
  - status : Review, Accpeted, InProgress, Closed

## iteration 3 of offer modeling
If not using the Suboffer concept, would an offer have repetition?
If there is repetition, consider other tools to help artists write offers
quicker.

- Offer
  - name
  - description
  - min_price NULL
  - max_price NULL
  - event NULL
  - thumbnail NULL
  - turnaround_time duration NULL
  - legal text NULL
  - 

Then just use the chat functionallity to get the requirements.

- Commission
  - commissioner references user
  - commissionee references user
  - offer references Offer
  - status : Review, Accpeted, InProgress, Closed

- ChatRoom
  - commission references Commission
  - archived bool

- ChatRoomMessage
  - chat_room references ChatRoom
  - text NULL
  - file NULL

# Events

- Event fields ideas
  - name
  - description
  - event start date
  - event end date
  - url
  - thumbnail

# Offer template idea
## iteration 1
Assume that a creator on the platform frequently creates the same offer every
month. A template can help the creator get an offer up and running quickly.

- Why this feature?
  - What is the problem?
    - Authors may create offers that are very similar
      - Because of schedule.
      - Because they want to provide a set of similar offers at once.
      - Because there is a detail that is common in all of their types of offers (like license and legal).
  - Maybe when a user goes to create an offer, they can use multiple templates which define presets for different fields.
    - One template for legal and one for description, so that the author can mix and match templates to quickly prototype an offer.
  - Author may want to create a template based on an existing offer that they made.
  - Built in templates can be made to give user a taste of the power of templates.
- For whom?
  - Commissioners

# Example offers
# using iteration 1 of offer modeling
- I will draw a portriat
  - Sketch
    - $40-50
  - Flat colored
    - $80-90
  - Shaded
    - $200-$200

# using iteration 3 of offer modeling
- I will draw sketck portrat
  - $40-200
  - during FWA 2024
