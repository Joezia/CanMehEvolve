    FIT_UINT32 GetSurfaceInterval(void) const
    {
        const Field* field = GetField(4);
        if (field == NULL)
            return 0;
        return field->GetValueUINT32();
    }
