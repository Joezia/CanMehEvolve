    FIT_BOOL IsMaxCadenceValid() const
    {
        const Field* field = GetField(18);
        return (FIT_NULL != field) && field->IsValueValid();
    }

