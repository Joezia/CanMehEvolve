    FIT_BOOL IsOpponentScoreValid() const
    {
        const Field* field = GetField(8);
        return (FIT_NULL != field) ? field->IsValueValid() : FIT_FALSE;
    }
