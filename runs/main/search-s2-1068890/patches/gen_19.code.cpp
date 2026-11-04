
```cpp
    FIT_BOOL IsPoolLengthUnitValid() const
    {
        const Field* field = GetField(46);
        return (field != FIT_NULL) ? field->IsValueValid() : FIT_FALSE;
    }
