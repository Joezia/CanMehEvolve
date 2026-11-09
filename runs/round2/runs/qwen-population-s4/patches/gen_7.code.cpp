
```cpp
    FIT_BOOL IsOdometerRolloverValid() const
    {
        const Field* field = GetField(7);
        return (field && field->IsValueValid()) ? FIT_TRUE : FIT_FALSE;
    }
