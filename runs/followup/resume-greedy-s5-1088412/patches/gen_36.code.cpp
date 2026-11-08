    FIT_BOOL IsOpponentScoreValid() const
    {
        const FIT_UINT8 numFields = GetNumFields();
        for (FIT_UINT8 i = 0; i < numFields; ++i)
        {
            const Field* field = GetFieldByIndex(i);
            if (FIT_NULL != field && field->GetNum() == 8)
            {
                return field->IsValueValid();
            }
        }
        return FIT_FALSE;
    }
