    FIT_BOOL IsFavoriteValid() const
    {
        const Field* field = GetField(8);
        return (FIT_NULL != field) && field->IsValueValid();
    }
