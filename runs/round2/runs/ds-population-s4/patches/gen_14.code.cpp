    FIT_BOOL IsIdValid() const
    {
        const FIT_UINT8 numFields = GetNumFields();
        if (numFields == 0)
        {
            return FIT_FALSE;
        }

        const Field* field = GetFieldByIndex(0);
        if (FIT_NULL == field)
        {
            return FIT_FALSE;
        }

        for (FIT_UINT8 i = 0; i < numFields; ++i)
        {
            if (*reinterpret_cast<const FIT_UINT8*>(field + i) == 14)
            {
                return (field + i)->IsValueValid();
            }
        }

        return FIT_FALSE;
    }
