# ER-диаграмма Блога про Селедку

```mermaid
erDiagram
    users {
        int id PK
        string email UK
        string login UK  
        string password
        timestamp created_at
        timestamp updated_at
    }

    posts {
        int id PK
        int author_id FK
        string title
        text content
        timestamp created_at
        timestamp updated_at
    }

    categories {
        int id PK
        string name UK
    }

    comments {
        int id PK
        int user_id FK
        int post_id FK
        text content
        timestamp created_at
    }

    favorites {
        int user_id PK,FK
        int post_id PK,FK
        timestamp created_at
    }

    subscriptions {
        int subscriber_id PK,FK
        int target_user_id PK,FK
        timestamp created_at
    }

    post_categories {
        int post_id PK,FK
        int category_id PK,FK
    }

    users ||--o{ posts : "автор постов"
    users ||--o{ comments : "автор комментариев"
    users ||--o{ favorites : "добавляет в избранное"
    users ||--o{ subscriptions : "подписывается"
    posts ||--o{ comments : "имеет комментарии"
    posts ||--o{ favorites : "в избранном"
    posts }o--o{ categories : "имеет категории"