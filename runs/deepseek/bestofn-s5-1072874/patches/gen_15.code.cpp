    FIT_UINT32 GetSurfaceInterval(void) const
    {
        const Field& field = GetField(4);
        if (field.GetNumValues() > 0)
        {
            return field.GetValueUINT32(0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
        }
        return 0;
    }
