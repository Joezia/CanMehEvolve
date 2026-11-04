
```cpp
    FIT_BOOL IsOdometerRolloverValid() const
    {
        const Field* field = GetField(7);
        return (field != FIT_NULL) ? field->IsValueValid() : FIT_FALSE;
    }
