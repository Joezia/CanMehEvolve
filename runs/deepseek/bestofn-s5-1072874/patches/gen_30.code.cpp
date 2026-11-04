    FIT_BOOL IsTimestampValid() const
    {
        const FIT_UINT8 numFields = GetNumFields();
        for( FIT_UINT8 i = 0; i < numFields; ++i )
        {
            const Field* field = GetFieldByIndex(i);
            if( field != FIT_NULL && field->GetNum() == 253 )
            {
                return field->IsValueValid();
            }
        }

        return FIT_FALSE;
    }
