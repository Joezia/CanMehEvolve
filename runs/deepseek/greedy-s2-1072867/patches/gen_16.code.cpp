    FIT_CONNECTIVITY_CAPABILITIES GetConnectivitySupported(void) const
    {
        const Field* field = GetField(23);
        if (field != FIT_NULL)
        {
            FIT_UINT32 value = 0;
            field->GetValue(value, 0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
            return value;
        }
        return 0;
    }
