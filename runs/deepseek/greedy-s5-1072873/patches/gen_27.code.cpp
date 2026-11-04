    void SetHeliumContent(FIT_UINT8 heliumContent)
    {
        Field* pField = GetField(0);
        if (pField != FIT_NULL)
        {
            pField->SetUINT8Value(heliumContent);
        }
    }
