# Frontend Implementation: Ratings and View Tracking

This document describes the frontend implementation for displaying ratings, author information, and view counts for series and chapters.

## Overview

The following features have been implemented on the frontend:

1. **Star Rating Display** - Visual display of 1-5 star ratings with full, half, and empty stars
2. **Rating Submission** - Interactive component for logged-in users to rate series
3. **Author Display** - Shows the author name on the series page
4. **View Count Display** - Shows unique view counts for both series and chapters
5. **Automatic View Tracking** - Tracks views when users visit series or chapter pages

## Components Created

### 1. StarRatingComponent
**Location:** `src/app/components/shared/star-rating/star-rating.ts`

A reusable component that displays star ratings visually.

**Features:**
- Displays 5 stars total
- Full stars (★) for whole numbers
- Half stars for decimals ≥ 0.5
- Empty stars (☆) for remaining
- Optional numeric value display
- Color-coded: Gold (#ffc107) for filled, Gray (#e0e0e0) for empty

**Usage:**
```html
<app-star-rating 
  [rating]="3.5" 
  [showValue]="true"
></app-star-rating>
```

**Example Output:** ★★★★☆ 3.5

### 2. RatingSubmitComponent
**Location:** `src/app/components/shared/rating-submit/rating-submit.ts`

An interactive component for submitting ratings.

**Features:**
- Interactive star selector (hover and click)
- Submit button
- Loading state during submission
- Success message after rating
- Error handling for already rated / not authenticated
- Emits event when rating is successfully submitted

**Usage:**
```html
<app-rating-submit 
  [seriesId]="series.series_id"
  (ratingSubmitted)="onRatingSubmitted()"
></app-rating-submit>
```

## Updated Components

### 1. Series Page
**Location:** `src/app/components/Series/series-page/`

**Changes:**
- Added author display below title
- Added star rating display in series info section
- Added view count display in meta section
- Added rating submission form (for logged-in users)
- Added "login to rate" prompt (for anonymous users)
- Automatic view tracking on page load
- Refreshes data after rating submission to show updated average

**Layout:**
```
Series Page
├── Title
├── Author (if available)
├── Meta Info (Status, Chapter Count, View Count)
├── Star Rating Display (average_rating)
├── Genres
├── Description
├── Dates
└── Rating Submission (if logged in) / Login Prompt
```

### 2. Chapter Page
**Location:** `src/app/components/Series/chapter-page/`

**Changes:**
- Added view count display at the top alongside chapter meta
- Automatic view tracking on page load
- Updates view count in real-time after tracking

**Layout:**
```
Chapter Header
├── Title
└── Info Bar
    ├── Chapter Number & Series
    └── View Count (👁 123 views)
```

## Service Updates

### LibraryService
**Location:** `src/app/services/library.service.ts`

**New Methods:**

1. **`rateSeriesRating(seriesId: string, rating: number): Observable<any>`**
   - Submits a user rating for a series
   - Requires authentication
   - Returns rating details on success

2. **`trackSeriesView(seriesId: string): Observable<any>`**
   - Tracks a unique view for a series
   - Works for both authenticated and anonymous users
   - Returns updated view count

3. **`trackChapterView(chapterId: string): Observable<any>`**
   - Tracks a unique view for a chapter
   - Works for both authenticated and anonymous users
   - Returns updated view count

## Model Updates

### Series Interface
**Location:** `src/app/models/series.ts`

**New Fields:**
```typescript
export interface Series {
  // ... existing fields
  author?: string;
  average_rating: number;
  total_view_count: number;
}
```

### Chapter Interface
**Location:** `src/app/models/chapter.ts`

**New Field:**
```typescript
export interface Chapter {
  // ... existing fields
  view_count: number;
}

export interface ChapterListItem {
  // ... existing fields
  view_count: number;
}
```

## CSS Styling

### Star Rating Styles
- Gold stars (#ffc107) for filled
- Light gray stars (#e0e0e0) for empty
- Inline display with proper spacing
- Responsive font sizing (1.5rem for stars)

### Rating Submission Styles
- Light gray background (#f8f9fa)
- Blue submit button (#007bff)
- Large interactive stars (2rem)
- Hover effects for interactivity
- Error messages in red (#dc3545)
- Success messages in green (#28a745)

### View Count Styles
- Eye emoji (👁) for visual indicator
- Gray text color (#666 for series, #888 for chapter)
- Flexbox layout for alignment
- Small, unobtrusive font size

## User Flow

### Rating a Series

1. **Anonymous User:**
   - Sees average rating display
   - Sees prompt: "Please log in to rate this series"
   - Can click link to navigate to login page

2. **Logged-in User:**
   - Sees average rating display
   - Sees rating submission form
   - Hovers over stars to preview selection
   - Clicks star to select rating
   - Clicks "Submit Rating" button
   - Sees success message
   - Page refreshes to show updated average rating

3. **Already Rated:**
   - User who already rated sees success message
   - Cannot submit another rating

### View Tracking

1. **Series Page:**
   - View tracked automatically on page load
   - View count displayed in meta section
   - Updates in real-time after tracking

2. **Chapter Page:**
   - View tracked automatically on page load
   - View count displayed at top of page
   - Updates in real-time after tracking

3. **Unique Views:**
   - Authenticated users: tracked by user ID
   - Anonymous users: tracked by session/IP
   - Same visitor won't increment count on refresh

## Error Handling

All view tracking and rating operations include error handling:

- **View Tracking Errors:** Silently logged to console (not shown to user)
- **Rating Errors:** Displayed to user with clear messages
  - "You have already rated this series"
  - "Please log in to rate this series"
  - "Failed to submit rating. Please try again."

## Responsive Design

All components are responsive and work well on:
- Desktop (≥992px)
- Tablet (768px - 991px)
- Mobile (<768px)

The series page adjusts its grid layout for smaller screens, and all text remains readable across devices.

## Testing

To test the features:

1. **View Series Page:**
   - Navigate to any series
   - Verify author, rating, and view count display
   - Refresh page and verify view count doesn't increment (already counted)

2. **Rate a Series:**
   - Log in to the application
   - Navigate to a series
   - Hover over stars to preview
   - Click a star to select rating
   - Click submit and verify success message
   - Verify average rating updates

3. **View Chapter Page:**
   - Navigate to any chapter
   - Verify view count displays at top
   - Refresh page and verify view count doesn't increment

## Browser Compatibility

The components use standard Angular and CSS features and are compatible with:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

Star emojis (★ and ☆) are supported across all modern browsers.
