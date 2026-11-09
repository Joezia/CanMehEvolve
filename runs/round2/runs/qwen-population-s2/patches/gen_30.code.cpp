    FIT_MESSAGE_INDEX GetMessageIndex(void) const
    {
        return (fields.size() > 254) ? static_cast<FIT_MESSAGE_INDEX>(fields[254].value.ui16) : 0;
    }
