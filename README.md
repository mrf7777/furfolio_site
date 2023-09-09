# Value
- Publish commissions.
- Automate commission managmenet.
  - lifecycle includes commission creation all the way to closure of commission
- Automate commission details gathering (with structured data?).
  - This is also achived agile-like with chat. Consider using chat instead.
- Facilitate communication between commissioner and commissionee

# Tasks
- [ ] Offer CRUD
  - [x] Create
    - [x] Can create offer
  - [ ] Read
    - [ ] Card list view of offers and maybe suboffers
      - [ ] Styled?
    - [x] Can read offer details on one page
      - [ ] Styled?
      - [ ] Signed in author sees link to update details
  - [ ] Update
    - [x] Author can access an update offer/suboffer page
    - [ ] Styled?
  - [ ] Delete
    - [ ] Author can click a delete button

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
