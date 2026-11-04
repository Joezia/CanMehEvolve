    FIT_BOOL IsTimestampValid() const
    {
        const Field* field = GetField(253);
        return (FIT_NULL == field) ? FIT_FALSE : field->IsValueValid();
    }
