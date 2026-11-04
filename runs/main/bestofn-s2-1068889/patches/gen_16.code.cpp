
    FIT_CONNECTIVITY_CAPABILITIES GetConnectivitySupported(void) const
    {
        return static_cast<FIT_CONNECTIVITY_CAPABILITIES>(GetFieldUINT32ZValue(23, 0, FIT_SUBFIELD_INDEX_MAIN_FIELD));
    }
