erDiagram
    users {
        int id PK
        string email UK
        string login UK  
        string hashed_password
        boolean is_active
        boolean is_admin
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

    likes {
        int id PK
        int user_id FK
        int post_id FK
        timestamp created_at
    }

    favorites {
        int user_id PK,FK
        int post_id PK,FK
        timestamp created_at
    }

    users ||--o{ posts : "автор постов"
    users ||--o{ likes : "ставит лайки"
    users ||--o{ favorites : "добавляет в избранное"
    posts ||--o{ likes : "имеет лайки"
    posts ||--o{ favorites : "в избранном"