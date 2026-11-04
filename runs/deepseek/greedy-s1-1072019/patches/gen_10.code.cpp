    void SetMessageIndex(FIT_MESSAGE_INDEX messageIndex)
    {
        const FIT_UINT8 numFields = GetNumFields();
        for (FIT_UINT8 fieldIndex = 0; fieldIndex < numFields; ++fieldIndex)
        {
            FitField &field = GetField(fieldIndex);
            if (field.GetFieldDefNum() == 254)
            {
                field.SetUINT16Value(messageIndex, 0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
                return;
            }
        }
    }
