-- Enable the pgcrypto extension for gen_random_uuid() if not already enabled.
-- This is typically required if you want to use UUIDs as default primary keys.
-- You might need superuser privileges to run this command.
-- CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Table: Series
-- Stores information about each novel series.
CREATE TABLE Series (
    series_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    cover_image_url VARCHAR(2048), -- URL for the series cover image
    status VARCHAR(50) NOT NULL DEFAULT 'Ongoing', -- e.g., 'Ongoing', 'Completed', 'Hiatus'
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Optional: Add a trigger to automatically update 'updated_at' column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_series_updated_at
BEFORE UPDATE ON Series
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- Table: Genre
-- Stores unique genre categories.
CREATE TABLE Genre (
    genre_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE -- Ensure genre names are unique
);


-- Table: SeriesGenre (Junction Table)
-- Resolves the many-to-many relationship between Series and Genre.
CREATE TABLE SeriesGenre (
    series_genre_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- Unique ID for the relationship
    series_id UUID NOT NULL,
    genre_id UUID NOT NULL,
    UNIQUE (series_id, genre_id), -- Ensures a series cannot have the same genre more than once
    FOREIGN KEY (series_id) REFERENCES Series(series_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) ON DELETE CASCADE
);


-- Table: Chapter
-- Stores details for each chapter within a series.
CREATE TABLE Chapter (
    chapter_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    series_id UUID NOT NULL, -- Foreign key linking to the Series table
    chapter_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL, -- The full text content of the chapter
    word_count INT,
    publication_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES Series(series_id) ON DELETE CASCADE,
    -- Add a unique constraint to ensure chapter numbers are unique within a series
    UNIQUE (series_id, chapter_number)
);

-- Optional: Add a trigger to automatically update 'updated_at' column for Chapter
CREATE TRIGGER update_chapter_updated_at
BEFORE UPDATE ON Chapter
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

