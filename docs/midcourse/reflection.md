# Reflection — Mid-Course Project

I used Claude for most of this project. It was involved throughout the different stages of development, including planning the two features, writing the models and validators, making changes related to storage and routes, creating tests, and implementing the frontend modal, filter, and card code. Using it helped me move through different parts of the project and provided assistance while building and connecting the different pieces together.

One moment where AI genuinely helped was during the break test on `due_date`. Weakening the validation on the input model revealed that the problem was not only at the input stage; the invalid value caused a deeper issue later in the application because another model still expected valid data. This helped me understand that validation needs to be considered across the different parts of the system, not only where the data first enters.

One moment where it slowed me down or required correction was the first approach to computing `overdue`. The initial solution was more complicated than necessary, so I reviewed it and simplified the logic to make it more straightforward.

One place where my own review changed the final result was when I checked the behavior of tag casing. After reviewing it, I decided to keep the behavior case-sensitive instead of accepting the default behavior. This was a decision made after looking at the implementation and choosing the behavior that I wanted for the project.

Overall, Claude was useful throughout the project, but reviewing the generated work and making decisions about the final implementation was still an important part of the process.
