    FIT_UINT8 GetNumLeaderType(void) const
    {
        for (FIT_UINT8 i = 0; i < numFields; ++i)
        {
            if (field[i].Field() == 7)
            {
                return field[i].GetNumValues();
            }
        }
        return 0;
    }
