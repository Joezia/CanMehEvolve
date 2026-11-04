    FIT_BOOL IsIdValid() const
    {
        const Field* field = GetField(14);
        return (FIT_NULL != field) && field->IsValueValid();
    }
