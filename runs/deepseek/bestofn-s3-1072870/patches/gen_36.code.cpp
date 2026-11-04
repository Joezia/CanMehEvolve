    FIT_BOOL IsAvgCombinedPedalSmoothnessValid() const
    {
        const Field* field = GetField(63);
        return (FIT_NULL != field) && field->IsValueValid();
    }
