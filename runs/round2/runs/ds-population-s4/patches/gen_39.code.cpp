    FIT_UINT16 GetRepetitionNum(void) const
    {
        const FIT_FIELD* field = GetField(61);
        if (field && (field->GetType() == FIT_BASE_TYPE_UINT16))
        {
            return field->GetValueUINT16(0);
        }
        return FIT_UINT16_INVALID;
    }
