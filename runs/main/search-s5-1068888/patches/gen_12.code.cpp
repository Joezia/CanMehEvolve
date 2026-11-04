    FIT_BOOL IsStandardDeviationValid() const
    {
        const Field* field = GetField(6);
        return (field != FIT_NULL) ? field->IsValueValid() : FIT_FALSE;
    }
