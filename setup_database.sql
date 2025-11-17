-- Songs List Database Setup Script
-- This script creates the database and table structure needed for the songs list application

-- Create database (uncomment if you want to create a new database)
-- CREATE DATABASE IF NOT EXISTS songs_list_db;
-- USE songs_list_db;

-- Create the songs table
CREATE TABLE IF NOT EXISTS songs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artist VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    proficiency VARCHAR(10) DEFAULT '☆☆☆☆☆',
    link TEXT,
    lyrics_link TEXT,
    chords_link TEXT,
    notes TEXT,
    last_played DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_artist (artist),
    INDEX idx_title (title),
    INDEX idx_artist_title (artist, title),
    INDEX idx_last_played (last_played)
);

-- Insert sample data (optional - comment out if you don't want sample data)
INSERT INTO songs (artist, title, proficiency, link, lyrics_link, chords_link, last_played) VALUES
('3 Door Down', 'Kryptonite', '☆☆☆☆☆', 'https://www.youtube.com/watch?v=xPU8OAjjS4k', 'https://www.google.com/search?q=Kryptonite+3+Door+Down+lyrics', 'https://www.ultimate-guitar.com/search.php?search_type=title&value=Kryptonite+3+Door+Down', NULL),
('Nirvana', 'About a girl', '★☆☆☆☆', 'https://www.youtube.com/watch?v=AhcttcXcRYY', 'https://www.google.com/search?q=Nirvana+About+a+girl+lyrics', 'https://www.ultimate-guitar.com/search.php?search_type=title&value=Nirvana+About+a+girl+chords', NULL),
('Ben Folds Five', 'Song For The Dumped', '☆☆☆☆☆', 'https://www.youtube.com/watch?v=XVk_e31dnlE', 'https://www.google.com/search?q=Song+For+The+Dumped+Ben+Folds+Five+lyrics', 'https://www.ultimate-guitar.com/search.php?search_type=title&value=Song+For+The+Dumped+Ben+Folds+Five+chords', NULL),
('Ben Folds Five', 'Battle Of Who Could Care Less', '☆☆☆☆☆', 'https://www.youtube.com/watch?v=0Y1wm7CFRCQ', 'https://www.google.com/search?q=Battle+Of+Who+Could+Care+Less+Ben+Folds+Five+lyrics', 'https://www.ultimate-guitar.com/search.php?search_type=title&value=Battle+Of+Who+Could+Care+Less+Ben+Folds+Five+chords', NULL);