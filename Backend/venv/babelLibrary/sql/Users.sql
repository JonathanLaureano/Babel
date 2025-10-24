-- Enable the pgcrypto extension for gen_random_uuid() if not already enabled.
-- This is typically required if you want to use UUIDs as default primary keys.
-- You might need superuser privileges to run this command.
-- CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Function to update 'updated_at' columns automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

---
--- User and Permissions Tables
---

-- Table: Roles
-- Defines different user roles within the system.
CREATE TABLE Roles (
    role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE, -- e.g., 'Reader', 'Premium Reader', 'Admin', 'Author'
    description TEXT
);

-- Table: Users
-- Stores basic user information and links to their assigned role.
CREATE TABLE Users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255), -- Stores hashed and salted password, nullable for social logins
    google_id VARCHAR(255) UNIQUE, -- For Google OAuth
    role_id UUID NOT NULL, -- Foreign key linking to the Roles table
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES Roles(role_id) ON DELETE RESTRICT -- Prevent deleting roles that are still assigned to users
);

-- Trigger to automatically update 'updated_at' for Users table
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON Users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- Table: Permissions
-- Lists all possible actions or resources that can be controlled.
CREATE TABLE Permissions (
    permission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE, -- e.g., 'access_premium_chapters', 'view_admin_dashboard'
    description TEXT
);


-- Table: RolePermissions (Junction Table)
-- Creates the many-to-many relationship between Roles and Permissions.
CREATE TABLE RolePermissions (
    role_id UUID NOT NULL,
    permission_id UUID NOT NULL,
    PRIMARY KEY (role_id, permission_id), -- Composite primary key
    FOREIGN KEY (role_id) REFERENCES Roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES Permissions(permission_id) ON DELETE CASCADE
);



