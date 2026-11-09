
    FIT_BOOL IsIdValid() const
    {
        const Field* field = GetField(14);
        return (field != FIT_NULL) && field->IsValueValid();
    }
