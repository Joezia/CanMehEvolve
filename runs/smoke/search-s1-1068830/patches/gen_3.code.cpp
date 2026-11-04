    FIT_BOOL IsHrCalcTypeValid() const
    {
        const Field* field = GetField(5);
        return (field != FIT_NULL) && field->IsValueValid();
    }
