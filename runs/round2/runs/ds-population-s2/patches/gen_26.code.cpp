    FIT_MESSAGE_INDEX GetMessageIndex(void) const
    {
        const FIT_UINT8 fieldArrayIndex = GetFieldArrayIndex(254, FIT_SUBFIELD_INDEX_MAIN_FIELD);
        if (fieldArrayIndex != FIT_UINT8_INVALID)
        {
            return GetFieldUINT16ValueByIndex(fieldArrayIndex, 0);
        }
        return FIT_UINT16_INVALID;
    }
