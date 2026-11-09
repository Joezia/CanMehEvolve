
    void SetTimestamp(FIT_DATE_TIME timestamp)
    {
        SetFieldUINT32Value(253, static_cast<std::uint32_t>(timestamp), 0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
    }
