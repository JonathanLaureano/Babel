# Profile Hub Feature

This document describes the new Profile Hub feature that has been implemented in the Babel UI application.

## Overview

The Profile Hub transforms the user profile page into a comprehensive dashboard with multiple tabs for managing user data and activity.

## Features

### 1. Tabbed Interface
The profile page now has three accessible tabs:
- **Profile Info** - View and edit user information
- **Comments** - View all user comments with like counts and replies
- **Bookmarks** - View bookmarked series with quick resume functionality

### 2. Profile Info Tab
- View and edit username and email
- View user role and registration date
- Logout functionality
- Account deletion option
- Accessible with keyboard navigation

### 3. Comments Activity Tab
- Displays all user comments across the platform
- Shows like counts and reply counts for each comment
- Links to the series or chapter where the comment was made
- Click on series/chapter names to navigate directly to them

### 4. Bookmarks Tab
- Grid display of bookmarked series with cover images
- Shows last read chapter for each bookmarked series
- **Continue Reading** button - navigates directly to the last viewed chapter
- **View Series** button - navigates to the series page
- **Remove** button - removes the bookmark
- Displays reading progress for each series

### 5. Reading History Tracking
- Automatically tracks the last viewed chapter when a user reads
- Works seamlessly in the background for logged-in users
- Enables "resume reading" functionality across the application
- Stored per series, so users can pick up where they left off

## New Files Created

### Models
- `src/app/models/user-data.ts` - Defines interfaces for:
  - `Bookmark` - User's bookmarked series
  - `ReadingHistory` - Last viewed chapters per series
  - `UserComment` - Extended comment data with series/chapter info

### Services
- `src/app/services/user-data.service.ts` - Handles API calls for:
  - Fetching user bookmarks
  - Creating/deleting bookmarks
  - Fetching/updating reading history
  - Fetching user comments

### Components
- `src/app/components/Users/profile/tabs/profile-info-tab.ts` - Profile editing tab
- `src/app/components/Users/profile/tabs/profile-info-tab.html`
- `src/app/components/Users/profile/tabs/profile-info-tab.css`
- `src/app/components/Users/profile/tabs/comments-tab.ts` - Comments activity tab
- `src/app/components/Users/profile/tabs/comments-tab.html`
- `src/app/components/Users/profile/tabs/comments-tab.css`
- `src/app/components/Users/profile/tabs/bookmarks-tab.ts` - Bookmarks management tab
- `src/app/components/Users/profile/tabs/bookmarks-tab.html`
- `src/app/components/Users/profile/tabs/bookmarks-tab.css`

### Updated Files
- `src/app/components/Users/profile/profile.ts` - Main profile component with tab management
- `src/app/components/Users/profile/profile.html` - Tabbed interface layout
- `src/app/components/Users/profile/profile.css` - Styles for tabs and navigation
- `src/app/components/Chapters/chapter-page/chapter-page.ts` - Added reading history tracking

## Backend API Requirements

The frontend expects the following backend API endpoints:

### Bookmarks
- `GET /api/bookmarks/?user={userId}` - Get user's bookmarks
- `POST /api/bookmarks/` - Create a bookmark
  - Body: `{ "series": "series_id" }`
- `DELETE /api/bookmarks/{bookmarkId}/` - Delete a bookmark

### Reading History
- `GET /api/reading-history/?user={userId}&ordering=-last_read_at` - Get user's reading history
- `GET /api/reading-history/?user={userId}&series={seriesId}` - Get history for specific series
- `POST /api/reading-history/` - Update reading history
  - Body: `{ "series": "series_id", "chapter": "chapter_id" }`

### Comments
- `GET /api/comments/by_user/?user={userId}&ordering=-created_at` - Get user's comments

## Usage

### For Users
1. Navigate to `/profile` after logging in
2. Use the tab buttons to switch between different views
3. In the Bookmarks tab, click "Continue Reading" to jump to your last read chapter
4. Reading history is automatically tracked as you read chapters

### For Developers
The profile hub is fully accessible and follows Angular best practices:
- Standalone components
- Proper ARIA labels for accessibility
- Keyboard navigation support
- Responsive design
- Type-safe with TypeScript interfaces

## Accessibility Features
- Proper ARIA roles and labels on tabs
- Keyboard navigation support
- Focus indicators on interactive elements
- Semantic HTML structure

## Future Enhancements
Consider adding:
- Bookmark folders/collections
- Reading statistics (chapters read, time spent)
- Export reading history
- Bookmark import/export
- Social features (share bookmarks with friends)
