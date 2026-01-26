# Sequence Diagrams (Current Implementation)

These diagrams cover the API flows that are currently implemented. All API paths are
under `/api/v1` unless noted otherwise.

## Health Check

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    Client->>API: GET /health
    API-->>Client: 200 {"status":"ok"}
```

## Auth - Google Login

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant LoginUC as GoogleLoginUseCase
    participant OAuth as GoogleOAuthClient (mock)
    Client->>API: GET /api/v1/auth/google/login
    API->>LoginUC: execute(state)
    LoginUC->>OAuth: get_authorization_url(state)
    OAuth-->>LoginUC: authorization_url
    LoginUC-->>API: authorization_url
    API-->>Client: 307 Redirect to authorization_url
```

## Auth - Google Callback

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant CallbackUC as GoogleCallbackUseCase
    participant OAuth as GoogleOAuthClient (mock)
    participant UserRepo as UserRepository
    participant TokenMgr as TokenManager
    participant DB as PostgreSQL
    Client->>API: GET /api/v1/auth/google/callback?code=...
    API->>CallbackUC: execute(code)
    CallbackUC->>OAuth: get_user_info(code)
    OAuth-->>CallbackUC: user_info
    CallbackUC->>UserRepo: find_by_oauth(provider, oauth_user_id)
    UserRepo->>DB: SELECT users
    DB-->>UserRepo: row or none
    alt user exists
        UserRepo-->>CallbackUC: User
    else user missing
        CallbackUC->>UserRepo: save(User)
        UserRepo->>DB: INSERT users
        DB-->>UserRepo: ok
    end
    CallbackUC->>TokenMgr: create_access_token(user_id, email)
    CallbackUC->>TokenMgr: create_refresh_token(user_id)
    TokenMgr-->>CallbackUC: tokens
    CallbackUC-->>API: tokens
    API-->>Client: 307 Redirect + Set-Cookie(access_token, refresh_token)
```

## Auth - Get Current User

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant AuthUC as GetCurrentUserUseCase
    participant TokenMgr as TokenManager
    participant UserRepo as UserRepository
    participant DB as PostgreSQL
    Client->>API: GET /api/v1/auth/me (cookie access_token)
    API->>AuthUC: execute(access_token)
    AuthUC->>TokenMgr: verify_token(access_token)
    TokenMgr-->>AuthUC: payload
    AuthUC->>UserRepo: find_by_id(user_id)
    UserRepo->>DB: SELECT users
    DB-->>UserRepo: user row
    UserRepo-->>AuthUC: User
    AuthUC-->>API: User
    API-->>Client: 200 UserResponse
```

## Auth - Logout

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant LogoutUC as LogoutUseCase
    Client->>API: POST /api/v1/auth/logout
    API->>LogoutUC: execute()
    LogoutUC-->>API: Ok
    API-->>Client: 200 + delete cookies
```

## Milestone - Create

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant CreateUC as CreateMilestoneUseCase
    participant MilestoneRepo as MilestoneRepository
    participant DB as PostgreSQL
    Client->>API: POST /api/v1/milestones (cookie, JSON)
    Note over API: Auth dependency resolves current user
    API->>CreateUC: execute(input)
    CreateUC->>MilestoneRepo: save(Milestone)
    MilestoneRepo->>DB: INSERT milestones
    DB-->>MilestoneRepo: ok
    CreateUC-->>API: Milestone
    API-->>Client: 201 MilestoneResponse
```

## Milestone - List

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant ListUC as GetMilestonesUseCase
    participant MilestoneRepo as MilestoneRepository
    participant DB as PostgreSQL
    Client->>API: GET /api/v1/milestones (cookie)
    Note over API: Auth dependency resolves current user
    API->>ListUC: execute(user_id)
    ListUC->>MilestoneRepo: find_by_user_id(user_id)
    MilestoneRepo->>DB: SELECT milestones
    DB-->>MilestoneRepo: rows
    ListUC-->>API: milestones
    API-->>Client: 200 [MilestoneResponse]
```

## Milestone - Update

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant UpdateUC as UpdateMilestoneUseCase
    participant MilestoneRepo as MilestoneRepository
    participant DB as PostgreSQL
    Client->>API: PUT /api/v1/milestones/{id} (cookie, JSON)
    Note over API: Auth dependency resolves current user
    API->>UpdateUC: execute(input)
    UpdateUC->>MilestoneRepo: find_by_id(id)
    MilestoneRepo->>DB: SELECT milestones
    DB-->>MilestoneRepo: row
    UpdateUC->>MilestoneRepo: save(updated)
    MilestoneRepo->>DB: UPDATE milestones
    DB-->>MilestoneRepo: ok
    UpdateUC-->>API: Milestone
    API-->>Client: 200 MilestoneResponse
```

## Milestone - Delete

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant DeleteUC as DeleteMilestoneUseCase
    participant MilestoneRepo as MilestoneRepository
    participant DB as PostgreSQL
    Client->>API: DELETE /api/v1/milestones/{id} (cookie)
    Note over API: Auth dependency resolves current user
    API->>DeleteUC: execute(milestone_id, user_id)
    DeleteUC->>MilestoneRepo: find_by_id(id)
    MilestoneRepo->>DB: SELECT milestones
    DB-->>MilestoneRepo: row
    DeleteUC->>MilestoneRepo: delete(id)
    MilestoneRepo->>DB: DELETE milestones
    DB-->>MilestoneRepo: ok
    DeleteUC-->>API: Ok
    API-->>Client: 200 {"message":"Milestone deleted successfully"}
```

## Verification - Start

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant StartUC as StartVerificationUseCase
    participant MilestoneRepo as MilestoneRepository
    participant VerificationRepo as VerificationRepository
    participant DB as PostgreSQL
    Client->>API: POST /api/v1/verifications (cookie, milestone_id)
    Note over API: Auth dependency resolves current user
    API->>StartUC: execute(milestone_id, user_id)
    StartUC->>MilestoneRepo: find_by_id(milestone_id)
    MilestoneRepo->>DB: SELECT milestones
    DB-->>MilestoneRepo: row
    StartUC->>VerificationRepo: save(Verification)
    VerificationRepo->>DB: INSERT verifications
    DB-->>VerificationRepo: ok
    StartUC-->>API: Verification
    API-->>Client: 201 VerificationResponse
```

## Verification - Submit Location

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant SubmitUC as SubmitLocationUseCase
    participant VerificationRepo as VerificationRepository
    participant DB as PostgreSQL
    Client->>API: POST /api/v1/verifications/{id}/location (cookie, lat, lon)
    Note over API: Auth dependency resolves current user
    API->>SubmitUC: execute(verification_id, user_id, location)
    SubmitUC->>VerificationRepo: find_by_id(verification_id)
    VerificationRepo->>DB: SELECT verifications + sensor_data
    DB-->>VerificationRepo: row
    SubmitUC->>VerificationRepo: save(updated Verification)
    VerificationRepo->>DB: UPDATE verifications + INSERT sensor_data
    DB-->>VerificationRepo: ok
    SubmitUC-->>API: Verification
    API-->>Client: 200 VerificationResponse
```

## Verification - Complete

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant CompleteUC as CompleteVerificationUseCase
    participant VerificationRepo as VerificationRepository
    participant MilestoneRepo as MilestoneRepository
    participant AchRepo as AchievementRepository
    participant GPS as GPSVerificationService
    participant DB as PostgreSQL
    Client->>API: POST /api/v1/verifications/{id}/complete (cookie)
    Note over API: Auth dependency resolves current user
    API->>CompleteUC: execute(verification_id, user_id)
    CompleteUC->>VerificationRepo: find_by_id(verification_id)
    VerificationRepo->>DB: SELECT verifications + sensor_data
    DB-->>VerificationRepo: row
    CompleteUC->>MilestoneRepo: find_by_id(milestone_id)
    MilestoneRepo->>DB: SELECT milestones
    DB-->>MilestoneRepo: row
    alt no sensor data
        CompleteUC->>VerificationRepo: save(failed Verification)
        VerificationRepo->>DB: UPDATE verifications
        DB-->>VerificationRepo: ok
        CompleteUC->>AchRepo: save(Achievement failure)
        AchRepo->>DB: INSERT achievement_records
        DB-->>AchRepo: ok
    else sensor data present
        CompleteUC->>GPS: verify(last_location, criteria)
        GPS-->>CompleteUC: VerificationResult
        CompleteUC->>VerificationRepo: save(completed Verification)
        VerificationRepo->>DB: UPDATE verifications
        DB-->>VerificationRepo: ok
        CompleteUC->>AchRepo: save(Achievement success/failure)
        AchRepo->>DB: INSERT achievement_records
        DB-->>AchRepo: ok
        CompleteUC->>MilestoneRepo: save(milestone completed/failed)
        MilestoneRepo->>DB: UPDATE milestones
        DB-->>MilestoneRepo: ok
    end
    CompleteUC-->>API: (Verification, Achievement)
    API-->>Client: 200 CompleteVerificationResponse
```
