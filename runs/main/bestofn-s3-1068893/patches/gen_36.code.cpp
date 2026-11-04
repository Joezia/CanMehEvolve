
```cpp
    FIT_BOOL IsAvgCombinedPedalSmoothnessValid() const
    {
        return (GetField(63) != FIT_NULL) && GetField(63)->IsValueValid();
    }
