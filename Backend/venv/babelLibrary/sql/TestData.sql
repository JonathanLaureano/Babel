INSERT INTO Genre (name) VALUES
('Action'),
('Adventure'),
('Comedy'),
('Detective'),
('Drama'),
('Fantasy'),
('Mystery'),
('Regression'),
('Romance'),
('Slice of Life'),
('Thriller')
ON CONFLICT (name) DO NOTHING;

-- Retrieve the UUIDs for the inserted/existing genres
WITH inserted_genres AS (
    INSERT INTO Genre (name) VALUES
    ('Action'),
    ('Adventure'),
    ('Comedy'),
    ('Detective'),
    ('Drama'),
    ('Fantasy'),
    ('Mystery'),
    ('Regression'),
    ('Romance'),
    ('Slice of Life'),
    ('Thriller')
    ON CONFLICT (name) DO NOTHING
    RETURNING genre_id, name
)
SELECT genre_id, name FROM Genre
WHERE name IN ('Action', 'Adventure', 'Comedy', 'Detective', 'Drama', 'Fantasy', 'Mystery', 'Regression', 'Romance', 'Slice of Life', 'Thriller');

-- Insert 10 test series
WITH new_series AS (
    INSERT INTO Series (title, description, cover_image_url, status) VALUES
    ('The Crimson Blade', 'A legendary warrior rises to defend the realm from encroaching darkness.', 'https://placehold.co/400x600/FF0000/FFFFFF?text=Crimson+Blade', 'Ongoing'),
    ('Whispers in the Library', 'A young detective unravels ancient secrets hidden within a forgotten library.', 'https://placehold.co/400x600/000080/FFFFFF?text=Whispers', 'Completed'),
    ('Back to My 18th Life', 'After a tragic accident, a salaryman returns to his high school days with future knowledge.', 'https://placehold.co/400x600/800080/FFFFFF?text=18th+Life', 'Ongoing'),
    ('My Quiet Corner Cafe', 'Heartwarming tales of daily life and simple joys at a cozy neighborhood cafe.', 'https://placehold.co/400x600/008000/FFFFFF?text=Cafe+Life', 'Ongoing'),
    ('Echoes of the Forgotten Empire', 'An adventurer discovers a lost civilization and its powerful, dangerous relics.', 'https://placehold.co/400x600/800000/FFFFFF?text=Lost+Empire', 'Hiatus'),
    ('The Case of the Missing Artifact', 'A brilliant but eccentric investigator takes on a case that baffles the police.', 'https://placehold.co/400x600/0000FF/FFFFFF?text=Missing+Artifact', 'Ongoing'),
    ('Reborn as a Duke''s Scion', 'A modern person finds themselves reincarnated into a noble family in a fantasy world.', 'https://placehold.co/400x600/4B0082/FFFFFF?text=Duke+Scion', 'Ongoing'),
    ('School Life Comedy', 'Follows the hilarious antics of a group of friends navigating their unpredictable school days.', 'https://placehold.co/400x600/FFFF00/000000?text=School+Comedy', 'Completed'),
    ('Shadows Over Silverwood', 'A dark secret looms over a peaceful town as strange events begin to unfold.', 'https://placehold.co/400x600/36454F/FFFFFF?text=Silverwood', 'Ongoing'),
    ('The Second Chance Chef', 'A renowned chef loses everything and starts anew, rediscovering his passion for cooking and life.', 'https://placehold.co/400x600/A52A2A/FFFFFF?text=Second+Chef', 'Ongoing')
    RETURNING series_id, title
)
-- Link series to genres
-- This section retrieves the IDs of the newly inserted series and existing/new genres
-- then inserts records into the SeriesGenre junction table.
INSERT INTO SeriesGenre (series_id, genre_id)
SELECT ns.series_id, g.genre_id
FROM new_series ns, Genre g
WHERE (ns.title = 'The Crimson Blade' AND g.name IN ('Action', 'Fantasy'))
   OR (ns.title = 'Whispers in the Library' AND g.name IN ('Mystery', 'Thriller'))
   OR (ns.title = 'Back to My 18th Life' AND g.name IN ('Regression', 'Fantasy'))
   OR (ns.title = 'My Quiet Corner Cafe' AND g.name IN ('Slice of Life', 'Romance'))
   OR (ns.title = 'Echoes of the Forgotten Empire' AND g.name IN ('Action', 'Fantasy', 'Adventure'))
   OR (ns.title = 'The Case of the Missing Artifact' AND g.name IN ('Mystery', 'Detective'))
   OR (ns.title = 'Reborn as a Duke''s Scion' AND g.name IN ('Regression', 'Fantasy', 'Adventure'))
   OR (ns.title = 'School Life Comedy' AND g.name IN ('Slice of Life', 'Comedy'))
   OR (ns.title = 'Shadows Over Silverwood' AND g.name IN ('Mystery', 'Thriller'))
   OR (ns.title = 'The Second Chance Chef' AND g.name IN ('Slice of Life', 'Drama'));

-- You might also want to insert some sample chapters for these series
WITH series_and_chapters AS (
    SELECT series_id, title
    FROM Series
    WHERE title IN (
        'The Crimson Blade', 'Whispers in the Library', 'Back to My 18th Life',
        'My Quiet Corner Cafe', 'Echoes of the Forgotten Empire', 'The Case of the Missing Artifact',
        'Reborn as a Duke''s Scion', 'School Life Comedy', 'Shadows Over Silverwood', 'The Second Chance Chef'
    )
)
INSERT INTO Chapter (series_id, chapter_number, title, content, word_count, publication_date) VALUES
((SELECT series_id FROM series_and_chapters WHERE title = 'The Crimson Blade'), 1, 'The First Trial', 'The searing heat of the desert wind...', 1500, CURRENT_TIMESTAMP - INTERVAL '10 days'),
((SELECT series_id FROM series_and_chapters WHERE title = 'The Crimson Blade'), 2, 'Ambush in the Oasis', 'Water, a mirage in the shifting sands...', 1800, CURRENT_TIMESTAMP - INTERVAL '8 days'),
((SELECT series_id FROM series_and_chapters WHERE title = 'Whispers in the Library'), 1, 'Dusty Tomes and Dark Secrets', 'The old library creaked with forgotten tales...', 1200, CURRENT_TIMESTAMP - INTERVAL '7 days'),
((SELECT series_id FROM series_and_chapters WHERE title = 'Back to My 18th Life'), 1, 'Waking Up in My Old Uniform', 'The blaring alarm clock was familiar, too familiar...', 2000, CURRENT_TIMESTAMP - INTERVAL '5 days'),
((SELECT series_id FROM series_and_chapters WHERE title = 'My Quiet Corner Cafe'), 1, 'First Brew of the Day', 'The aroma of freshly ground coffee beans...', 900, CURRENT_TIMESTAMP - INTERVAL '3 days'),
((SELECT series_id FROM series_and_chapters WHERE title = 'Echoes of the Forgotten Empire'), 1, 'The Lost City', 'Rumors of a city swallowed by the jungle...', 2200, CURRENT_TIMESTAMP - INTERVAL '6 days'),
((SELECT series_id FROM series_and_chapters WHERE title = 'The Case of the Missing Artifact'), 1, 'The Empty Pedestal', 'The museum curator paced frantically...', 1300, CURRENT_TIMESTAMP - INTERVAL '4 days'),
((SELECT series_id FROM series_and_chapters WHERE title = 'Reborn as a Duke''s Scion'), 1, 'A New Life, A New Name', 'He opened his eyes to a lavish canopy...', 1900, CURRENT_TIMESTAMP - INTERVAL '2 days'),
((SELECT series_id FROM series_and_chapters WHERE title = 'School Life Comedy'), 1, 'The Exploding Volcano Project', 'Our science fair project had a minor hiccup...', 1000, CURRENT_TIMESTAMP - INTERVAL '1 day'),
((SELECT series_id FROM series_and_chapters WHERE title = 'Shadows Over Silverwood'), 1, 'The Old Mill', 'The moon cast long shadows over the abandoned mill...', 1600, CURRENT_TIMESTAMP - INTERVAL '9 days'),
((SELECT series_id FROM series_and_chapters WHERE title = 'The Second Chance Chef'), 1, 'A Dish Called Hope', 'He held the worn spatula, his hands trembling...', 1100, CURRENT_TIMESTAMP - INTERVAL '0 days'); -- Today

INSERT INTO roles (role_id, name, description) VALUES 
    (gen_random_uuid(), 'Admin', 'System administrator with full access to all features and management capabilities'),
    (gen_random_uuid(), 'Reader', 'Standard user with access to read series and chapters');