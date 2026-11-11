# Time

EVRAZ `dt` is stored as recorded. The API field `timezone` is `unconfirmed`. `available_at` for the public file is the dataset publication date `2025-09-15T21:34:04Z`, except that historical replay uses event time as the as-of clock for measurements that were the plant's own record. A laboratory silicon value is visible at its cast timestamp because the file does not contain a separate release time. The UI says the release time was not provided.

An as-of query drops rows with `event_time` after the requested instant.
