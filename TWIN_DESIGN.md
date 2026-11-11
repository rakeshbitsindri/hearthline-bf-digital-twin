# Twin

The stepper for this dataset is a filtered replay. At time t the filtered state is the latest measurement with `available_at` at or before t. Silicon is included only when its cast time is at or before t.

A smoothed series is not used for the ghost comparison. Scenario branches copy the filtered snapshot and apply an explicit blast or temperature delta. They are labelled scenario and keep the 2013–2016 clock.

Zone inventories are omitted. The profile is not dimensioned beyond the paper's 2,000 m³ assumption, which is labelled assumed.

The independent truth generator is not this replay. Tests that only round-trip the same file are software tests.
