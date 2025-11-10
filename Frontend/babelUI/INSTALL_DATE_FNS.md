# Install date-fns

The Comments component now uses `date-fns` for accurate relative time formatting.

## Installation

Run the following command in the `Frontend/babelUI` directory:

```bash
npm install date-fns
```

## Why date-fns?

The previous implementation used approximate values for time intervals:
- 30 days for a month (ignores different month lengths)
- 365 days for a year (ignores leap years)

date-fns provides:
- Accurate date calculations
- Proper handling of leap years
- Correct month lengths
- Better internationalization support
- Smaller bundle size (tree-shakeable)

## Usage in Comments Component

The `getTimeSince()` method now uses `formatDistanceToNow()` from date-fns:

```typescript
import { formatDistanceToNow } from 'date-fns';

getTimeSince(dateString: string): string {
  try {
    const date = new Date(dateString);
    return formatDistanceToNow(date, { addSuffix: true });
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'recently';
  }
}
```

This provides output like:
- "2 minutes ago"
- "5 hours ago"
- "3 days ago"
- "about 1 month ago"
- "over 1 year ago"

With proper handling of edge cases and more natural language output.
