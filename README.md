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

# Convention space ideas.
- QR Code for artists to print for their table to show URL for query for their offers.
- QR Code for vending space which has URL for query for offers at the convention.
- Convention can have a landing page with some customization that is more friendly than a query page.
- Let people request commissions before vendors open via QR Code.
  - Let creators make offers that will publish in the future. (needs new field)
    - Let offers that are to-be-open still Publish but be closed for requests so that users can read about the offer beforehand.