    FIT_UINT16 GetProcessingInterval(void) const
    {
        FIT_UINT16 processingInterval = FIT_UINT16_INVALID;
        GetFieldValue(0, 0, FIT_SUBFIELD_INDEX_MAIN_FIELD, &processingInterval, static_cast<FIT_UINT8>(sizeof(processingInterval)));
        return processingInterval;
    }
