    FIT_BOOL IsTimestampValid() const
    {
        const size_t count = fields.size();
        if( count > 0 && fields[0].GetNum() == 253 )
        {
            return fields[0].IsValueValid();
        }

        for( size_t i = 1; i < count; ++i )
        {
            if( fields[i].GetNum() == 253 )
            {
                return fields[i].IsValueValid();
            }
        }

        return FIT_FALSE;
    }
