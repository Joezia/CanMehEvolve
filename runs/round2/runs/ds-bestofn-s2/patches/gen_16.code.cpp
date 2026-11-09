    FIT_CONNECTIVITY_CAPABILITIES GetConnectivitySupported(void) const
    {
        return GetFieldUINT32ZValue(23, 0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
    }
