
```cpp
    FIT_BOOL IsFavoriteValid() const
    {
        const Field* field = GetField(8);
        return (field != FIT_NULL) ? field->IsValueValid() : FIT_FALSE;
    }
