    FIT_UINT32 GetSurfaceInterval(void) const
    {
        const FIT_UINT32* value = GetFieldPtr(4, 0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
        return value ? *value : 0;
    }
