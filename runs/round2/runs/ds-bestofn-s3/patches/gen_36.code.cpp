    FIT_BOOL IsAvgCombinedPedalSmoothnessValid() const
    {
        const Field* field = GetField(63);
        return (FIT_NULL == field) ? FIT_FALSE : field->IsValueValid();
    }
