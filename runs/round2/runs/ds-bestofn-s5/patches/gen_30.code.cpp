    FIT_BOOL IsTimestampValid() const
    {
        const Field* const field = GetField(253);
        return (FIT_NULL != field) ? field->IsValueValid() : FIT_FALSE;
    }
