# Track

Track is an application that assits users in tracking their savings towards their goals. Users can sign up to the app and create goals. When a user deposits and withdraws savings, these are stored in the users savings history and the user instantly recieves savings insights.

The app is writen using Python and Flask for the backend, wired up to MongoDB. On the frontend, HTML5, CSS3 and JavaScript/jQuery provide an interactive user interface.  The app provides full CRUD functionality for user profiles and user savings goals.

The application will be deployed to Heroku and will be accessible here: </>. 

## Contents
1. [UX](#ux)
  - [Users](#users)
  - [User Stories](#user-stories)
  - [Goals](#resulting-goals)
  - [Wireframes](#wireframes)

## UX
### Users
Track's users are likely to be casual savers who have specific goals in mind. These goals might be short-term or long-term goals, and with targets of any value (think new playstation vs new house). Users will need to be able to register for and sign in to their user account so that their individal profile and goals data persists after ending the session. 

These users will need to be able to create goals and keep track of their savings ("deposits" and "withdrawals"). Circumstances change, and users will need the ability to extend their goal's end date into the future or bring it forwards if it looks like they'll meet their goal early. Alternatively, users might choose to increase or decrease their goal's target amount. 

### User Stories 

1. "I've always dreamed of buying an old VW camper van. It's a long-term goal but I want to start making progress towards it. I want to save a little bit here and there, and work out when my goal might be achievable."
2. "I want to buy a house this time next year. I know how much I need to save in total, and I'm happy to save a little extra each month to meet my goal if I need to."
3. "My kids really want to go to Disneyland. They get an allowance for helping around the house and they save it towards their dream holiday. At the moment we keep track of it on paper, but it'd be great to do this on an app so that they could see their savings grow towards their goal in a more visual way." 
4. "Usually I'm saving towards three or four different things. A couple are usually smaller goals that I can meet quite quickly, while others might be a bit more long term with higher amounts needed to be saved. It'd be great to track my savings for all of these in a single app, and keep a record of the goals I've achieved to keep me motivated."

### Resulting Goals

Based on the four user stories set out above, there are five main goals for this project: 
- Allow users to deposit/withdraw savings towards three or four different goals
- Store a history of user savings activity
- Provide visual indications of savings progress
- Allow users to increase/decrease their goal total
- Allow uesrs to extend/bring forwards their end date


