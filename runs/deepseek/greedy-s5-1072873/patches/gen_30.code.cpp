    FIT_BOOL IsTimestampValid() const
    {
        const Field* field = GetFieldByIndex(0);
        if( FIT_NULL != field && field->GetNum() == 253 )
        {
            return field->IsValueValid();
        }

        const FIT_UINT8 num_fields = GetNumFields();
        for( FIT_UINT8 i = 1; i < num_fields; ++i )
        {
            field = GetFieldByIndex(i);
            if( FIT_NULL != field && field->GetNum() == 253 )
            {
                return field->IsValueValid();
            }
        }

        return FIT_FALSE;
    }
