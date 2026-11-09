
```cpp
    FIT_BOOL IsTimestampValid() const
    {
        const Field* field = GetField(253);
        return (field != FIT_NULL) && field->IsValueValid();
    }
