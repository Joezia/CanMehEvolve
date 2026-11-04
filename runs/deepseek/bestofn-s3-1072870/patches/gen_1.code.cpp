    void SetTotalFractionalAscent(FIT_FLOAT32 totalFractionalAscent)
    {
        static int fieldIndex = -1;
        if (fieldIndex < 0)
        {
            for (int i = 0; i < static_cast<int>(fields.size()); ++i)
            {
                if (fields[i].GetNum() == 89)
                {
                    fieldIndex = i;
                    break;
                }
            }
        }
        if (fieldIndex >= 0)
        {
            fields[fieldIndex].SetValue(&totalFractionalAscent, sizeof(totalFractionalAscent), 0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
        }
    }
