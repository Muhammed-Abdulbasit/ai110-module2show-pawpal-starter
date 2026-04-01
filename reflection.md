# PawPal+ Project Reflection

## 1. System Design

Three core actions a user should be able to perform with the PawPal+ scheduler:
- Add a pet's schedule (feeding, walks, vet appointments).
- View the schedule for a specific pet or all pets.
- Edit or delete existing schedule entries.

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design included three main classes: `Pet`, `Task`, and `Scheduler`. The `Pet` class had attributes like name, type, and age, and methods to manage pet information. The `Task` class included attributes such as task name, duration, priority, and time constraints, along with methods to manage task details. The `Scheduler` class was responsible for generating the daily schedule based on the tasks and their constraints.

- What classes did you include, and what responsibilities did you assign to each?
The classed I included were:
1. `Pet`: Responsible for storing pet information and managing pet-related data.
2. `Task`: Responsible for storing task details and managing task-related data.
3. `Scheduler`: Responsible for generating the daily schedule based on the tasks and their constraints. It also included methods for adding, editing, and deleting tasks, as well as generating the schedule.

**b. Design changes**

- Did your design change during implementation?
Yes, my design did change during implementation.

- If yes, describe at least one change and why you made it.
One change I made was to add a `User` class to manage user preferences and constraints more effectively. Initially, I had planned to include user preferences directly within the `Scheduler` class, but I realized that separating user-related data into its own class would make the design cleaner and more modular. This change allowed for better organization of code and made it easier to manage user-specific information without cluttering the scheduling logic.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
It considers time constraints (when tasks can be performed), task priority (which tasks are more important), and user preferences (specific times for certain tasks or avoiding certain times).

- How did you decide which constraints mattered most?
I decided that time constraints and task priority were the most critical factors for the scheduler. Time constraints ensure that tasks are scheduled at appropriate times, while task priority helps to ensure that more important tasks are completed first. User preferences were also considered but were given slightly less weight than the other two constraints, as they can be more flexible and may not always be feasible to accommodate.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
One tradeoff my scheduler makes is that it prioritizes high-priority tasks over user preferences. For example, if a user prefers to have a walk scheduled in the evening but has a high-priority task that must be completed during that time, the scheduler will prioritize the high-priority task and schedule the walk at a different time.

- Why is that tradeoff reasonable for this scenario?
It is reasonable because ensuring that high-priority tasks are completed is essential for the well-being of the pet. While user preferences are important, they can often be adjusted to accommodate critical tasks. In this scenario, it is more important to ensure that essential care tasks are completed on time rather than strictly adhering to user preferences, which may be more flexible.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI tools primarily for design brainstorming and debugging. During the design phase, I used AI to generate ideas for how to structure the classes and their relationships. I also used AI to help identify potential edge cases and constraints that I might have overlooked. During implementation, I used AI to assist with debugging by providing suggestions for how to fix errors and optimize code.

- What kinds of prompts or questions were most helpful?
Prompts that asked for specific design patterns or best practices in object-oriented programming were particularly helpful. Additionally, prompts that encouraged me to think about edge cases and potential user scenarios helped me to create a more robust scheduler.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One moment where I did not accept an AI suggestion as-is was when the AI recommended a specific algorithm for scheduling tasks. The suggested algorithm was a simple first-come, first-served approach, which I felt would not adequately account for task priorities and time constraints. Instead of implementing the suggested algorithm, I decided to design a custom scheduling algorithm that would better meet the needs of the pet owner and ensure that high-priority tasks were scheduled appropriately.

- How did you evaluate or verify what the AI suggested?
I evaluated the AI's suggestion by considering how well it aligned with the requirements of the project and the constraints I had identified. I also thought about how the suggested algorithm would perform in different scenarios, such as when there are multiple high-priority tasks or when user preferences conflict with task priorities. Ultimately, I determined that the AI's suggestion did not adequately address these complexities, which is why I chose to design a custom solution instead.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested several key behaviors of the scheduler, including:
1. The ability to add, edit, and delete tasks correctly.
2. The scheduler's ability to generate a daily plan that respects time constraints and task priorities.
3. The scheduler's handling of edge cases, such as when there are conflicting tasks or when user preferences cannot be fully accommodated.

- Why were these tests important?
These tests were important because they verify that the core functionality of the scheduler works as intended. Ensuring that tasks can be managed correctly is fundamental to the usability of the app. Additionally, testing the scheduling logic is crucial to confirm that the scheduler can generate plans that meet the specified constraints and priorities, which is the primary purpose of the app.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am reasonably confident that my scheduler works correctly based on the tests I have implemented. The tests cover a range of scenarios and edge cases, which gives me confidence that the scheduler can handle various situations effectively. However, I acknowledge that there may still be unforeseen edge cases or scenarios that I have not tested, so there is always room for improvement and further testing.

- What edge cases would you test next if you had more time?
If I had more time, I would test additional edge cases such as:
1. Scheduling tasks for multiple pets with overlapping care needs.
2. Handling tasks that have dependencies (e.g., a walk must happen before feeding).
3. Testing the scheduler's performance with a large number of tasks and pets to ensure it remains responsive and efficient.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with the overall design and implementation of the scheduling logic. I believe that the custom scheduling algorithm I developed effectively balances task priorities and time constraints, which is a critical aspect of the app's functionality. Additionally, I am pleased with how the classes are structured and how they interact with each other, as this has made the code more modular and easier to maintain.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If I had another iteration, I would improve the user interface to make it more intuitive and user-friendly. While the core functionality of the scheduler is solid, I believe that enhancing the UI could significantly improve the user experience. This could include features such as drag-and-drop scheduling, visual representations of the schedule, and more interactive elements to allow users to easily manage their pet care tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
One important thing I learned about designing systems is the importance of flexibility in design. While it's essential to have a clear structure and defined responsibilities for each class, it's also crucial to be open to making changes as you implement the system. The design process is iterative, and being willing to adapt your design based on new insights or challenges can lead to a more robust and effective solution. Additionally, when working with AI, it's important to critically evaluate suggestions and not accept them blindly, as AI can provide valuable insights but may not always align perfectly with the specific requirements of your project.
