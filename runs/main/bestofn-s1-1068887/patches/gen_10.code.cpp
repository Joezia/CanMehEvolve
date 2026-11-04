
    void SetMessageIndex(FIT_MESSAGE_INDEX messageIndex)
    {
        this->SetFieldUINT16Value(254, messageIndex, 0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
    }
