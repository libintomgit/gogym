# Requirements Document

## Introduction

GoGym MVP Backend is the Python FastAPI backend API for a mobile-first workout planning, scheduling, and logging application. This document covers the MVP scope: project scaffolding, database setup, user authentication, workout inventory CRUD (admin and user), workout plan CRUD (admin and user), workout scheduling, workout session logging, basic sharing, and workout history. Media upload, rest timer, frontend, and offline support are excluded from the MVP.

The backend uses FastAPI with PostgreSQL (via SQLAlchemy ORM), Alembic for database migrations, and JWT-based authentication. The API serves JSON responses in snake_case format.

## Glossary

- **API**: The GoGym FastAPI backend application
- **Admin**: A privileged user role with permissions to manage global content and approve user submissions
- **User**: A registered gym user who interacts with the API to manage workouts
- **Category**: A top-level grouping of exercises (e.g., Upper Body, Lower Body, Arms)
- **Sub_Category**: A second-level grouping within a Category (e.g., Chest, Back, Shoulders)
- **Exercise**: A single workout movement within a Sub_Category, containing name, description, and target muscles
- **Workout_Plan**: A structured collection of exercises organized across one or more Plan_Days
- **Plan_Day**: A single day within a Workout_Plan, containing an ordered list of exercises with prescribed sets and reps
- **Schedule**: A mapping of specific calendar dates to Plan_Days for a User
- **Workout_Session**: A record of a User performing exercises from a Plan_Day, capturing actual weights and completion status
- **Set_Log**: A single recorded set within a Workout_Session, storing reps performed and weight used
- **Sharing_Scope**: The visibility level of user-created content: Private (default), Shared (specific users), or Global (requires admin approval)
- **Approval_Queue**: User-submitted content awaiting admin review for global visibility

## Requirements

### Requirement 1: Project Setup and Configuration

**User Story:** As a developer, I want a well-structured FastAPI project with database connectivity and migration support, so that I can build features on a solid foundation.

#### Acceptance Criteria

1. THE API SHALL use a standard Python project structure with separate directories for routes, models, schemas, services, and configuration.
2. THE API SHALL load configuration values (database URL, JWT secret, token expiration) from environment variables or a `.env` file.
3. THE API SHALL connect to a PostgreSQL database using SQLAlchemy as the ORM.
4. THE API SHALL use Alembic for database schema migrations.
5. WHEN the API starts, THE API SHALL verify the database connection and raise a descriptive error if the connection fails.

---

### Requirement 2: User Authentication and Authorization

**User Story:** As a gym user, I want to register and log in to the API, so that I can access my personalized workout data securely.

#### Acceptance Criteria

1. WHEN a new user submits valid registration details (email, password, name), THE API SHALL create a new User account, hash the password using bcrypt, and return a JWT access token.
2. WHEN a registered User submits valid login credentials (email and password), THE API SHALL verify the credentials and return a JWT access token.
3. IF a User submits an email that is already registered, THEN THE API SHALL return a 409 Conflict response with a descriptive message.
4. IF a User submits invalid login credentials, THEN THE API SHALL return a 401 Unauthorized response with a descriptive message.
5. IF an unauthenticated request is made to a protected endpoint, THEN THE API SHALL return a 401 Unauthorized response.
6. IF a User attempts an action restricted to the Admin role, THEN THE API SHALL return a 403 Forbidden response.
7. THE API SHALL enforce role-based access control distinguishing between Admin and User roles for all protected endpoints.
8. THE API SHALL issue JWT tokens with a configurable expiration time.

---

### Requirement 3: Database Models and Migrations

**User Story:** As a developer, I want well-defined database models with proper relationships and migration support, so that the data layer is reliable and evolvable.

#### Acceptance Criteria

1. THE API SHALL define SQLAlchemy models for User, Category, Sub_Category, Exercise, Workout_Plan, Plan_Day, Plan_Day_Exercise (linking exercises to plan days with order, sets, reps), Schedule, Workout_Session, and Set_Log.
2. THE API SHALL enforce referential integrity between all related models using foreign key constraints.
3. THE API SHALL include created_at and updated_at timestamp columns on all models.
4. THE API SHALL use Alembic to generate and apply migration scripts for all schema changes.
5. THE API SHALL store a sharing_scope field (private, shared, global) and an owner_id foreign key on Category, Sub_Category, Exercise, and Workout_Plan models to distinguish admin-created global content from user-created content.
6. THE API SHALL store an approval_status field (pending, approved, rejected) on items submitted for global sharing.

---

### Requirement 4: Admin Workout Inventory Management

**User Story:** As an Admin, I want to create and manage a global workout inventory with categories, sub-categories, and exercises, so that all users have access to a curated exercise library.

#### Acceptance Criteria

1. WHEN an Admin creates a new Category, THE API SHALL store the Category with sharing_scope set to global and make it available to all Users.
2. WHEN an Admin creates a new Sub_Category within an existing Category, THE API SHALL associate the Sub_Category with the parent Category and set sharing_scope to global.
3. WHEN an Admin creates a new Exercise within a Sub_Category, THE API SHALL store the Exercise with its name, description, and target muscles, with sharing_scope set to global.
4. WHEN an Admin updates an existing Category, Sub_Category, or Exercise, THE API SHALL persist the changes.
5. WHEN an Admin deletes a Category, THE API SHALL remove the Category and its associated Sub_Categories and Exercises.
6. WHEN an Admin deletes a Sub_Category, THE API SHALL remove the Sub_Category and its associated Exercises.
7. WHEN an Admin deletes an Exercise, THE API SHALL remove the Exercise from the inventory.

---

### Requirement 5: User Workout Inventory Management

**User Story:** As a User, I want to create my own exercises with categories and sub-categories, so that I can customize my workout library.

#### Acceptance Criteria

1. WHEN a User creates a new Category, Sub_Category, or Exercise, THE API SHALL store the item with sharing_scope set to private and owner_id set to the creating User.
2. WHEN a User retrieves the workout inventory, THE API SHALL return all global items combined with the User's own private and shared items.
3. WHEN a User updates a self-created Category, Sub_Category, or Exercise, THE API SHALL persist the changes.
4. WHEN a User deletes a self-created Category, Sub_Category, or Exercise, THE API SHALL remove the item.
5. IF a User attempts to modify or delete an item owned by another User or by an Admin, THEN THE API SHALL return a 403 Forbidden response.

---

### Requirement 6: Workout Inventory Sharing

**User Story:** As a User, I want to share my custom exercises with specific users or request global availability, so that others can benefit from my exercises.

#### Acceptance Criteria

1. WHEN a User shares a Category, Sub_Category, or Exercise with specific users by providing email addresses, THE API SHALL grant read access to those specified Users and set sharing_scope to shared.
2. WHEN a User submits an inventory item for global sharing, THE API SHALL set the approval_status to pending and add the item to the Approval_Queue.
3. WHEN an Admin approves a pending item, THE API SHALL set the item's sharing_scope to global and approval_status to approved.
4. WHEN an Admin rejects a pending item, THE API SHALL set the approval_status to rejected.
5. WHEN an Admin retrieves the Approval_Queue, THE API SHALL return all pending items with the ability to filter by status (pending, approved, rejected).

---

### Requirement 7: Admin Workout Plan Management

**User Story:** As an Admin, I want to create structured workout plans from the inventory, so that users have professionally designed plans to follow.

#### Acceptance Criteria

1. WHEN an Admin creates a Workout_Plan, THE API SHALL store the plan with a name, description, number of Plan_Days, and sharing_scope set to global.
2. WHEN an Admin adds exercises to a Plan_Day, THE API SHALL associate each Exercise with prescribed sets, reps, and a display order within that Plan_Day.
3. WHEN an Admin updates an existing Workout_Plan or its Plan_Days, THE API SHALL persist the changes.
4. WHEN an Admin deletes a Workout_Plan, THE API SHALL remove the plan and its associated Plan_Days and Plan_Day_Exercise records.
5. THE API SHALL make all Admin-created Workout_Plans available to every registered User.

---

### Requirement 8: User Workout Plan Management

**User Story:** As a User, I want to create my own workout plans from available exercises, so that I can design training programs tailored to my goals.

#### Acceptance Criteria

1. WHEN a User creates a Workout_Plan, THE API SHALL store the plan with a name, description, number of Plan_Days, sharing_scope set to private, and owner_id set to the creating User.
2. WHEN a User adds exercises from the workout inventory (global and personal) to a Plan_Day, THE API SHALL associate each Exercise with prescribed sets, reps, and a display order.
3. WHEN a User retrieves workout plans, THE API SHALL return all global plans combined with the User's own private and shared plans.
4. WHEN a User updates a self-created Workout_Plan, THE API SHALL persist the changes.
5. WHEN a User deletes a self-created Workout_Plan, THE API SHALL remove the plan and its associated Plan_Days.
6. IF a User attempts to modify or delete a Workout_Plan owned by another User or by an Admin, THEN THE API SHALL return a 403 Forbidden response.

---

### Requirement 9: Workout Plan Sharing

**User Story:** As a User, I want to share my workout plans with specific users or request global availability, so that I can help others follow effective training programs.

#### Acceptance Criteria

1. WHEN a User shares a Workout_Plan with specific users by providing email addresses, THE API SHALL grant read access to those specified Users and set sharing_scope to shared.
2. WHEN a User submits a Workout_Plan for global sharing, THE API SHALL set the approval_status to pending and add the plan to the Approval_Queue.
3. WHEN an Admin approves a pending Workout_Plan, THE API SHALL set the plan's sharing_scope to global and approval_status to approved.
4. WHEN an Admin rejects a pending Workout_Plan, THE API SHALL set the approval_status to rejected.

---

### Requirement 10: Workout Scheduling

**User Story:** As a User, I want to assign workout plans to specific dates on my calendar, so that I can organize my training schedule in advance.

#### Acceptance Criteria

1. WHEN a User assigns a Workout_Plan to a date range, THE API SHALL create Schedule entries mapping each date to the corresponding Plan_Day in sequence.
2. WHEN a User assigns a single Plan_Day to a specific date, THE API SHALL create a Schedule entry for that date.
3. WHEN a User updates a scheduled date, THE API SHALL modify the Schedule entry to reflect the new date or Plan_Day assignment.
4. WHEN a User deletes a scheduled workout from a date, THE API SHALL remove the corresponding Schedule entry.
5. IF a User attempts to schedule a workout on a date that already has a scheduled workout, THEN THE API SHALL return a 409 Conflict response.
6. WHEN a User retrieves their schedule for a date range, THE API SHALL return all Schedule entries within that range with associated Plan_Day and Workout_Plan details.

---

### Requirement 11: Daily Workout Endpoint

**User Story:** As a User, I want to retrieve my scheduled workout for today, so that I can quickly see what exercises I need to perform.

#### Acceptance Criteria

1. WHEN a User requests the daily workout endpoint, THE API SHALL return the Workout_Plan and Plan_Day scheduled for the current date, including all exercises in their prescribed order with sets and reps.
2. IF no workout is scheduled for the current date, THEN THE API SHALL return a response indicating no workout is planned for today.
3. WHEN a User requests the detail for a specific Plan_Day, THE API SHALL return all exercises in their prescribed order with name, target muscles, prescribed sets, and prescribed reps.

---

### Requirement 12: Workout Session Logging

**User Story:** As a User, I want to log my performance (weight lifted per set) during a workout session, so that I can track my progress over time.

#### Acceptance Criteria

1. WHEN a User starts a Workout_Session for a scheduled Plan_Day, THE API SHALL create a new Workout_Session record linked to the User, the Plan_Day, and the current date.
2. WHEN a User logs a Set for an Exercise, THE API SHALL store the Set_Log with the exercise reference, set number, reps performed, and weight used.
3. IF a User submits a non-positive or non-numerical weight value, THEN THE API SHALL return a 422 Unprocessable Entity response with a validation error.
4. WHEN a User requests the previous performance for an Exercise, THE API SHALL return the most recent Set_Logs for that Exercise from past Workout_Sessions.
5. WHEN a User completes all prescribed sets for all exercises in a Workout_Session, THE API SHALL mark the Workout_Session as completed with a completion timestamp.
6. THE API SHALL allow a User to end a Workout_Session early, marking it as partially completed.

---

### Requirement 13: Workout History and Progress Tracking

**User Story:** As a User, I want to view my past workout sessions and track weight progression, so that I can monitor my fitness improvements.

#### Acceptance Criteria

1. THE API SHALL store all Workout_Session records with date, completion status, and associated Set_Logs.
2. WHEN a User retrieves their workout history, THE API SHALL return a paginated chronological list of completed and partially completed Workout_Sessions.
3. WHEN a User retrieves a specific Workout_Session, THE API SHALL return the full details including each Exercise performed, sets completed, reps, and weights.
4. WHEN a User requests progress for a specific Exercise, THE API SHALL return the weight history for that Exercise across past Workout_Sessions, ordered by date.

---

### Requirement 14: API Data Serialization

**User Story:** As a developer, I want all API payloads to serialize and deserialize consistently, so that data integrity is maintained across client-server communication.

#### Acceptance Criteria

1. THE API SHALL serialize all responses as JSON using snake_case field naming.
2. THE API SHALL deserialize all request bodies from JSON and validate against Pydantic schemas.
3. FOR ALL valid API data models, serializing to JSON then deserializing back SHALL produce an equivalent object (round-trip property).
4. IF a request body fails schema validation, THEN THE API SHALL return a 422 Unprocessable Entity response with field-level error details.

---

## Non-Functional Requirements

### Requirement 15: API Response Performance

**User Story:** As a User, I want the API to respond quickly, so that my workout sessions are not interrupted by slow loading.

#### Acceptance Criteria

1. THE API SHALL respond to read requests (GET) within 500 milliseconds under normal load (up to 100 concurrent users).
2. THE API SHALL respond to write requests (POST, PUT, DELETE) within 1000 milliseconds under normal load.

---

### Requirement 16: Data Persistence and Integrity

**User Story:** As a User, I want my workout data to be reliably stored, so that I do not lose my training history or plans.

#### Acceptance Criteria

1. THE API SHALL persist all data in a PostgreSQL relational database.
2. THE API SHALL enforce referential integrity between all related entities using foreign key constraints.
3. IF a database write operation fails, THEN THE API SHALL roll back the transaction and return an error response without partial data corruption.

---

### Requirement 17: Security

**User Story:** As a User, I want my account and data to be secure, so that unauthorized users cannot access my personal workout information.

#### Acceptance Criteria

1. THE API SHALL hash all User passwords using bcrypt before storing them.
2. THE API SHALL use JWT tokens for authentication with a configurable expiration time.
3. THE API SHALL validate and sanitize all User inputs to prevent SQL injection attacks.
4. THE API SHALL enforce HTTPS for all communication in production environments.
